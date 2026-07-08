from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class AIResponseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str = Field(min_length=1, max_length=128)
    user_id: str = Field(min_length=1, max_length=128)
    message: str = Field(min_length=1)
    template_name: str | None = Field(default=None, max_length=128)
    model: str | None = Field(default=None, max_length=128)
    allow_destructive_tools: bool = False
    approved_by_human: bool = False
    approver: str | None = Field(default=None, max_length=128)
    metadata: dict[str, Any] = Field(default_factory=dict)


class UsageInfo(BaseModel):
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None


class AIResponsePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str
    user_id: str
    model: str
    template_name: str
    response: str
    usage: UsageInfo = Field(default_factory=UsageInfo)


class StructuredResponseRequest(AIResponseRequest):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    output_schema: dict[str, Any] = Field(
        alias="schema",
        serialization_alias="schema",
    )


class StructuredResponsePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str
    user_id: str
    model: str
    template_name: str
    data: dict[str, Any]
    usage: UsageInfo = Field(default_factory=UsageInfo)


class HistoryItem(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp_utc: str


class ToolApprovalRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool_name: str = Field(min_length=1, max_length=128)
    payload: dict[str, Any] = Field(default_factory=dict)
    requested_by: str = Field(min_length=1, max_length=128)
    approved_by_human: bool = False
    approver: str | None = Field(default=None, max_length=128)


class ToolApprovalResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["safe", "blocked", "approved"]
    reason: str
    requires_human_approval: bool


class LogSummaryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str = Field(min_length=1, max_length=128)
    user_id: str = Field(min_length=1, max_length=128)
    log_text: str = Field(min_length=1)
    source: str = Field(default="application", max_length=128)
    metadata: dict[str, Any] = Field(default_factory=dict)


class LogSummaryPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str
    user_id: str
    source: str
    summary: str
    highlights: list[str]
    recommendations: list[str]
    redacted_excerpt: str
