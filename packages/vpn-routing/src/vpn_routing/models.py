from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

NodeRole = Literal["main", "rf", "backup"]
PolicyLane = Literal["direct", "proxy", "block"]


@dataclass(slots=True, frozen=True)
class HealthMetrics:
    latency_ms: float
    error_rate: float
    uptime_ratio: float
    load_ratio: float
    last_updated_utc: str


@dataclass(slots=True, frozen=True)
class NodeDescriptor:
    node_id: str
    role: NodeRole
    region: str
    domain: str
    port: int
    transport: str
    active: bool = True
    health: HealthMetrics | None = None


@dataclass(slots=True, frozen=True)
class PolicyDecision:
    lane: PolicyLane
    reason: str
    matched_rule: str | None = None


@dataclass(slots=True, frozen=True)
class SubscriptionProfile:
    profile_id: str
    display_name: str
    transports: tuple[str, ...]
    include_legacy: bool
    direct_domains: tuple[str, ...] = ()
    blocked_protocols: tuple[str, ...] = ()
    metadata: dict[str, str] = field(default_factory=dict)

