from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True, frozen=True)
class VPNSystemStatus:
    status: str
    panel_version: str | None = None
    xray_version: str | None = None
    active_services: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()


@dataclass(slots=True, frozen=True)
class VPNInbound:
    tag: str
    protocol: str
    enabled: bool
    up_bytes: int
    down_bytes: int
    clients_online: int = 0


@dataclass(slots=True, frozen=True)
class VPNSubscription:
    client_id: str
    label: str
    expires_at_utc: str | None
    days_left: int | None
    active: bool
    transport: str | None = None


@dataclass(slots=True, frozen=True)
class VPNReadOnlySnapshot:
    collected_at_utc: str
    status: str
    inbounds_total: int
    inbounds_enabled: int
    clients_online_total: int
    subscriptions_total: int
    subscriptions_expiring_soon: int
    panel_version: str | None = None
    xray_version: str | None = None
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "collected_at_utc": self.collected_at_utc,
            "status": self.status,
            "inbounds_total": self.inbounds_total,
            "inbounds_enabled": self.inbounds_enabled,
            "clients_online_total": self.clients_online_total,
            "subscriptions_total": self.subscriptions_total,
            "subscriptions_expiring_soon": self.subscriptions_expiring_soon,
            "panel_version": self.panel_version,
            "xray_version": self.xray_version,
            "notes": list(self.notes),
        }
