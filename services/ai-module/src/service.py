from __future__ import annotations

from collections.abc import Iterator
from typing import Any, TypeVar

from .audit_logger import AuditLogger
from .config import AISettings
from .guardrails import GuardrailViolation, validate_user_message
from .history_store import InMemoryHistoryStore
from .log_summarizer import summarize_logs as summarize_logs_locally
from .openai_responses_client import OpenAIResponsesClient
from .prompt_templates import PromptTemplateRegistry
from .rate_limiter import InMemoryRateLimiter
from .redaction import redact_object, redact_text
from .schemas import (
    AIResponsePayload,
    AIResponseRequest,
    LogSummaryPayload,
    LogSummaryRequest,
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

RequestT = TypeVar("RequestT", bound=AIResponseRequest)


class AIService:
    def __init__(
        self,
        *,
        settings: AISettings,
        client: OpenAIResponsesClient,
        templates: PromptTemplateRegistry,
        history: InMemoryHistoryStore,
        usage_logger: UsageLogger,
        audit_logger: AuditLogger,
        limiter: InMemoryRateLimiter,
    ) -> None:
        self._settings = settings
        self._client = client
        self._templates = templates
        self._history = history
        self._usage_logger = usage_logger
        self._audit_logger = audit_logger
        self._limiter = limiter

    def respond(self, request: AIResponseRequest) -> AIResponsePayload:
        self._apply_rate_limit(request.user_id)
        self._assert_destructive_approval(request)
        validate_user_message(
            request.message,
            max_chars=self._settings.ai_max_prompt_chars,
            allow_destructive_tools=request.allow_destructive_tools,
        )

        sanitized_request, changed = self._sanitize_request(request)
        if changed:
            self._audit_logger.log(
                {
                    "event": "prompt_redacted",
                    "session_id": request.session_id,
                    "user_id": request.user_id,
                }
            )

        messages, template_name = self._build_messages(sanitized_request)
        text, usage = self._client.create_response(messages=messages, model=request.model)
        safe_text = redact_text(text)

        self._history.append(
            request.session_id,
            "user",
            sanitized_request.message,
            sanitized_request.metadata,
        )
        self._history.append(
            request.session_id,
            "assistant",
            safe_text,
            {"model": request.model or self._settings.ai_model},
        )

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
        self._audit_logger.log(
            {
                "event": "respond",
                "session_id": request.session_id,
                "user_id": request.user_id,
                "template_name": template_name,
            }
        )

        return AIResponsePayload(
            session_id=request.session_id,
            user_id=request.user_id,
            model=request.model or self._settings.ai_model,
            template_name=template_name,
            response=safe_text,
            usage=UsageInfo(**usage),
        )

    def respond_support(self, request: AIResponseRequest) -> AIResponsePayload:
        return self.respond(request.model_copy(update={"template_name": "support_assistant"}))

    def respond_admin(self, request: AIResponseRequest) -> AIResponsePayload:
        return self.respond(request.model_copy(update={"template_name": "admin_actions"}))

    def summarize_logs(self, request: LogSummaryRequest) -> LogSummaryPayload:
        self._apply_rate_limit(request.user_id)
        summary, highlights, recommendations, redacted_excerpt = summarize_logs_locally(
            request.log_text,
            max_chars=self._settings.ai_log_summary_max_chars,
            max_lines=self._settings.ai_log_summary_max_lines,
        )

        self._history.append(
            request.session_id,
            "user",
            f"[log-summary:{request.source}] {redacted_excerpt[:200]}",
            redact_object(request.metadata),
        )
        self._history.append(
            request.session_id,
            "assistant",
            summary,
            {"source": request.source, "mode": "log_summary"},
        )

        self._usage_logger.log(
            {
                "event": "log_summarize",
                "session_id": request.session_id,
                "user_id": request.user_id,
                "source": request.source,
                "input_chars": len(request.log_text),
                "redacted_chars": len(redacted_excerpt),
            }
        )
        self._audit_logger.log(
            {
                "event": "log_summarize",
                "session_id": request.session_id,
                "user_id": request.user_id,
                "source": request.source,
            }
        )

        return LogSummaryPayload(
            session_id=request.session_id,
            user_id=request.user_id,
            source=request.source,
            summary=summary,
            highlights=highlights,
            recommendations=recommendations,
            redacted_excerpt=redacted_excerpt[:4000],
        )

    def stream(self, request: AIResponseRequest) -> Iterator[str]:
        self._apply_rate_limit(request.user_id)
        self._assert_destructive_approval(request)
        validate_user_message(
            request.message,
            max_chars=self._settings.ai_max_prompt_chars,
            allow_destructive_tools=request.allow_destructive_tools,
        )

        sanitized_request, changed = self._sanitize_request(request)
        if changed:
            self._audit_logger.log(
                {
                    "event": "prompt_redacted",
                    "session_id": request.session_id,
                    "user_id": request.user_id,
                    "mode": "stream",
                }
            )

        messages, template_name = self._build_messages(sanitized_request)
        chunks: list[str] = []
        redacted_chunks = 0
        for chunk in self._client.stream_response(messages=messages, model=request.model):
            safe_chunk = redact_text(chunk)
            if safe_chunk != chunk:
                redacted_chunks += 1
            chunks.append(safe_chunk)
            yield safe_chunk

        final_text = "".join(chunks).strip()
        self._history.append(
            request.session_id,
            "user",
            sanitized_request.message,
            sanitized_request.metadata,
        )
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
        self._audit_logger.log(
            {
                "event": "respond_stream",
                "session_id": request.session_id,
                "user_id": request.user_id,
                "template_name": template_name,
                "redacted_chunks": redacted_chunks,
            }
        )

    def respond_structured(self, request: StructuredResponseRequest) -> StructuredResponsePayload:
        self._apply_rate_limit(request.user_id)
        self._assert_destructive_approval(request)
        validate_user_message(
            request.message,
            max_chars=self._settings.ai_max_prompt_chars,
            allow_destructive_tools=request.allow_destructive_tools,
        )

        sanitized_request, changed = self._sanitize_request(request)
        if changed:
            self._audit_logger.log(
                {
                    "event": "prompt_redacted",
                    "session_id": request.session_id,
                    "user_id": request.user_id,
                    "mode": "structured",
                }
            )

        messages, template_name = self._build_messages(sanitized_request)
        data, usage = self._client.create_structured_response(
            messages=messages,
            schema=request.output_schema,
            model=request.model,
        )
        safe_data = redact_object(data)

        self._history.append(
            request.session_id,
            "user",
            sanitized_request.message,
            sanitized_request.metadata,
        )
        self._history.append(
            request.session_id,
            "assistant",
            str(safe_data),
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
        self._audit_logger.log(
            {
                "event": "respond_structured",
                "session_id": request.session_id,
                "user_id": request.user_id,
                "template_name": template_name,
            }
        )

        return StructuredResponsePayload(
            session_id=request.session_id,
            user_id=request.user_id,
            model=request.model or self._settings.ai_model,
            template_name=template_name,
            data=safe_data,
            usage=UsageInfo(**usage),
        )

    def get_history(self, session_id: str, limit: int = 20) -> list[dict[str, Any]]:
        return [item.model_dump() for item in self._history.get(session_id, limit=limit)]

    def evaluate_tool_approval(self, request: ToolApprovalRequest) -> ToolApprovalResponse:
        tool = request.tool_name.strip().lower()
        destructive = tool in DESTRUCTIVE_TOOLS

        if not destructive:
            self._audit_logger.log(
                {
                    "event": "tool_approval_safe",
                    "tool": tool,
                    "requested_by": request.requested_by,
                }
            )
            return ToolApprovalResponse(
                status="safe",
                reason="Tool классифицирован как non-destructive.",
                requires_human_approval=False,
            )

        if request.approved_by_human and request.approver:
            self._audit_logger.log(
                {
                    "event": "tool_approval_granted",
                    "tool": tool,
                    "requested_by": request.requested_by,
                    "approver": request.approver,
                }
            )
            return ToolApprovalResponse(
                status="approved",
                reason=f"Destructive tool одобрен человеком: {request.approver}.",
                requires_human_approval=True,
            )

        self._audit_logger.log(
            {
                "event": "tool_approval_blocked",
                "tool": tool,
                "requested_by": request.requested_by,
            }
        )
        return ToolApprovalResponse(
            status="blocked",
            reason="Для destructive tool требуется human approval (approved_by_human + approver).",
            requires_human_approval=True,
        )

    def _apply_rate_limit(self, user_id: str) -> None:
        allowed, retry_after = self._limiter.allow(user_id)
        if not allowed:
            self._audit_logger.log(
                {
                    "event": "rate_limit_exceeded",
                    "user_id": user_id,
                    "retry_after_seconds": retry_after,
                }
            )
            raise RateLimitExceeded(retry_after)

    def _build_messages(self, request: AIResponseRequest) -> tuple[list[dict[str, str]], str]:
        template_name, system_prompt = self._templates.get(request.template_name)
        history = self._history.get(request.session_id, limit=12)

        messages: list[dict[str, str]] = [{"role": "system", "content": redact_text(system_prompt)}]
        for item in history:
            if item.role in {"user", "assistant"}:
                messages.append({"role": item.role, "content": redact_text(item.content)})
        messages.append({"role": "user", "content": redact_text(request.message)})
        return messages, template_name

    def _sanitize_request(self, request: RequestT) -> tuple[RequestT, bool]:
        sanitized_message = redact_text(request.message)
        sanitized_metadata = redact_object(request.metadata)
        changed = (sanitized_message != request.message) or (sanitized_metadata != request.metadata)
        sanitized_request = request.model_copy(
            update={
                "message": sanitized_message,
                "metadata": sanitized_metadata,
            }
        )
        return sanitized_request, changed

    def _assert_destructive_approval(self, request: AIResponseRequest) -> None:
        if not request.allow_destructive_tools:
            return
        if request.approved_by_human and request.approver:
            self._audit_logger.log(
                {
                    "event": "destructive_prompt_approved",
                    "session_id": request.session_id,
                    "user_id": request.user_id,
                    "approver": request.approver,
                }
            )
            return

        self._audit_logger.log(
            {
                "event": "destructive_prompt_blocked",
                "session_id": request.session_id,
                "user_id": request.user_id,
            }
        )
        raise GuardrailViolation(
            "Destructive режим разрешается только после human approval (approved_by_human + approver)."
        )