from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SubscriptionPreviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: str = Field(min_length=1, max_length=128)
    domain: str = Field(default="", max_length=255)
    protocol: str | None = Field(default=None, max_length=64)
    transport: str | None = Field(default=None, max_length=64)
    udp_port: int | None = Field(default=None, ge=1, le=65535)
    is_admin: bool = False
    force_opt_in: bool = False


class SubscriptionProfilePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile_id: str
    display_name: str
    transports: list[str]
    include_legacy: bool
    metadata: dict[str, str] = Field(default_factory=dict)


class NodePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    node_id: str
    role: str
    region: str
    domain: str
    port: int
    transport: str
    active: bool
    score: float | None = None


class SubscriptionPreviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: str
    policy_lane: Literal["direct", "proxy", "block"]
    canary_lane: str
    canary_reason: str
    canary_bucket: int
    subscription_path: str
    profiles: list[SubscriptionProfilePayload]
    preferred_nodes: list[NodePayload]


class TelegramMiniAppSessionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: str = Field(min_length=1, max_length=128)
    locale: str | None = Field(default=None, max_length=16)


class TelegramMiniAppSessionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: str
    launch_url: str
    canary_percent: int
    lane: str
    message: str

