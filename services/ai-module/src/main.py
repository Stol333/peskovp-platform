from __future__ import annotations

import json
from collections.abc import Iterator

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from .config import AISettings
from .guardrails import GuardrailViolation
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
)
from .service import AIService, RateLimitExceeded
from .usage_logger import UsageLogger

settings = AISettings()
templates = PromptTemplateRegistry(
    prompt_dir=settings.ai_prompt_dir,
    default_template=settings.ai_default_template,
)
history_store = InMemoryHistoryStore(max_items_per_session=settings.ai_history_limit)
usage_logger = UsageLogger(path=settings.ai_usage_log_path)
rate_limiter = InMemoryRateLimiter(max_requests=settings.ai_rate_limit_rpm, window_seconds=60)
openai_client = OpenAIResponsesClient(
    api_key=settings.openai_api_key,
    base_url=settings.openai_base_url,
    default_model=settings.ai_model,
)
ai_service = AIService(
    settings=settings,
    client=openai_client,
    templates=templates,
    history=history_store,
    usage_logger=usage_logger,
    limiter=rate_limiter,
)

app = FastAPI(
    title="PESKOVP AI Module",
    description="Phase 7 AI module (server-side only).",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "env": settings.app_env,
        "provider": settings.ai_provider,
        "model": settings.ai_model,
        "openai_ready": openai_client.is_ready,
        "openai_init_error": openai_client.init_error,
    }


@app.post("/v1/ai/respond", response_model=AIResponsePayload)
def respond(request: AIResponseRequest) -> AIResponsePayload:
    try:
        return ai_service.respond(request)
    except GuardrailViolation as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RateLimitExceeded as exc:
        raise HTTPException(status_code=429, detail=f"Rate limit exceeded. Retry after {exc.retry_after_seconds}s.") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/v1/ai/respond/stream")
def respond_stream(request: AIResponseRequest) -> StreamingResponse:
    if not settings.ai_streaming_enabled:
        raise HTTPException(status_code=400, detail="Streaming disabled by configuration.")

    def event_stream() -> Iterator[str]:
        try:
            for delta in ai_service.stream(request):
                yield f"data: {json.dumps({'delta': delta}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        except GuardrailViolation as exc:
            yield f"event: error\ndata: {json.dumps({'detail': str(exc)}, ensure_ascii=False)}\n\n"
        except RateLimitExceeded as exc:
            yield f"event: error\ndata: {json.dumps({'detail': f'Rate limit exceeded. Retry after {exc.retry_after_seconds}s.'}, ensure_ascii=False)}\n\n"
        except Exception as exc:  # pragma: no cover - runtime safety
            yield f"event: error\ndata: {json.dumps({'detail': str(exc)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/v1/ai/respond/structured", response_model=StructuredResponsePayload)
def respond_structured(request: StructuredResponseRequest) -> StructuredResponsePayload:
    try:
        return ai_service.respond_structured(request)
    except GuardrailViolation as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RateLimitExceeded as exc:
        raise HTTPException(status_code=429, detail=f"Rate limit exceeded. Retry after {exc.retry_after_seconds}s.") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/v1/ai/history/{session_id}")
def get_history(session_id: str, limit: int = 20) -> dict[str, object]:
    return {"session_id": session_id, "items": ai_service.get_history(session_id, limit=limit)}


@app.post("/v1/ai/tools/approval-check", response_model=ToolApprovalResponse)
def tool_approval_check(request: ToolApprovalRequest) -> ToolApprovalResponse:
    return ai_service.evaluate_tool_approval(request)
