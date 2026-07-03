from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from .config import AISettings
from .guardrails import GuardrailViolation, validate_user_message
from .history_store import InMemoryHistoryStore
from .openai_responses_client import OpenAIResponsesClient
from .prompt_templates import PromptTemplateRegistry
from .rate_limiter import InMemoryRateLimiter
from .schemas import (
    AIResponsePayload,
    AIResponseRequest,
    StructuredResponsePayload,
    StructuredResponseRequest,
    ToolApprovalRequest,
    ToolApprovalResponse,
    UsageInfo,
)
from .usage_logger import UsageLogger


class RateLimitExceeded(PermissionError):
    def __init__(self, retry_after_seconds: int) -> None:
        self.retry_after_seconds = retry_after_seconds
        super().__init__(f"Rate limit exceeded. Retry after {retry_after_seconds}s.")


DESTRUCTIVE_TOOLS = {
    "run_shell",
    "delete_user",
    "delete_subscription",
    "drop_database",
    "reset_vpn_node",
    "flush_cache",
}


class AIService:
    def __init__(
        self,
        *,
        settings: AISettings,
        client: OpenAIResponsesClient,
        templates: PromptTemplateRegistry,
        history: InMemoryHistoryStore,
        usage_logger: UsageLogger,
        limiter: InMemoryRateLimiter,
    ) -> None:
        self._settings = settings
        self._client = client
        self._templates = templates
        self._history = history
        self._usage_logger = usage_logger
        self._limiter = limiter

    def respond(self, request: AIResponseRequest) -> AIResponsePayload:
        self._apply_rate_limit(request.user_id)
        validate_user_message(
            request.message,
            max_chars=self._settings.ai_max_prompt_chars,
            allow_destructive_tools=request.allow_destructive_tools,
        )
        messages, template_name = self._build_messages(request)
        text, usage = self._client.create_response(messages=messages, model=request.model)

        self._history.append(request.session_id, "user", request.message, request.metadata)
        self._history.append(request.session_id, "assistant", text, {"model": request.model or self._settings.ai_model})
        self._usage_logger.log(
            {
                "event": "respond",
                "session_id": request.session_id,
                "user_id": request.user_id,
                "template_name": template_name,
                "model": request.model or self._settings.ai_model,
                "usage": usage,
            }
        )

        return AIResponsePayload(
            session_id=request.session_id,
            user_id=request.user_id,
            model=request.model or self._settings.ai_model,
            template_name=template_name,
            response=text,
            usage=UsageInfo(**usage),
        )

    def stream(self, request: AIResponseRequest) -> Iterator[str]:
        self._apply_rate_limit(request.user_id)
        validate_user_message(
            request.message,
            max_chars=self._settings.ai_max_prompt_chars,
            allow_destructive_tools=request.allow_destructive_tools,
        )
        messages, template_name = self._build_messages(request)

        chunks: list[str] = []
        for chunk in self._client.stream_response(messages=messages, model=request.model):
            chunks.append(chunk)
            yield chunk

        final_text = "".join(chunks).strip()
        self._history.append(request.session_id, "user", request.message, request.metadata)
        self._history.append(
            request.session_id,
            "assistant",
            final_text,
            {"model": request.model or self._settings.ai_model, "stream": True},
        )
        self._usage_logger.log(
            {
                "event": "respond_stream",
                "session_id": request.session_id,
                "user_id": request.user_id,
                "template_name": template_name,
                "model": request.model or self._settings.ai_model,
                "streamed_chars": len(final_text),
            }
        )

    def respond_structured(self, request: StructuredResponseRequest) -> StructuredResponsePayload:
        self._apply_rate_limit(request.user_id)
        validate_user_message(
            request.message,
            max_chars=self._settings.ai_max_prompt_chars,
            allow_destructive_tools=request.allow_destructive_tools,
        )
        messages, template_name = self._build_messages(request)
        data, usage = self._client.create_structured_response(
            messages=messages,
            schema=request.schema,
            model=request.model,
        )
        self._history.append(request.session_id, "user", request.message, request.metadata)
        self._history.append(
            request.session_id,
            "assistant",
            str(data),
            {"model": request.model or self._settings.ai_model, "structured": True},
        )
        self._usage_logger.log(
            {
                "event": "respond_structured",
                "session_id": request.session_id,
                "user_id": request.user_id,
                "template_name": template_name,
                "model": request.model or self._settings.ai_model,
                "usage": usage,
            }
        )

        return StructuredResponsePayload(
            session_id=request.session_id,
            user_id=request.user_id,
            model=request.model or self._settings.ai_model,
            template_name=template_name,
            data=data,
            usage=UsageInfo(**usage),
        )

    def get_history(self, session_id: str, limit: int = 20) -> list[dict[str, Any]]:
        return [item.model_dump() for item in self._history.get(session_id, limit=limit)]

    def evaluate_tool_approval(self, request: ToolApprovalRequest) -> ToolApprovalResponse:
        tool = request.tool_name.strip().lower()
        destructive = tool in DESTRUCTIVE_TOOLS

        if not destructive:
            return ToolApprovalResponse(
                status="safe",
                reason="Tool классифицирован как non-destructive.",
                requires_human_approval=False,
            )

        if request.approved_by_human and request.approver:
            return ToolApprovalResponse(
                status="approved",
                reason=f"Destructive tool одобрен человеком: {request.approver}.",
                requires_human_approval=True,
            )

        return ToolApprovalResponse(
            status="blocked",
            reason="Для destructive tool требуется human approval (approved_by_human + approver).",
            requires_human_approval=True,
        )

    def _apply_rate_limit(self, user_id: str) -> None:
        allowed, retry_after = self._limiter.allow(user_id)
        if not allowed:
            raise RateLimitExceeded(retry_after)

    def _build_messages(self, request: AIResponseRequest) -> tuple[list[dict[str, str]], str]:
        template_name, system_prompt = self._templates.get(request.template_name)
        history = self._history.get(request.session_id, limit=12)

        messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
        for item in history:
            if item.role in {"user", "assistant"}:
                messages.append({"role": item.role, "content": item.content})
        messages.append({"role": "user", "content": request.message})
        return messages, template_name
