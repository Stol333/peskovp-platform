from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any, Protocol

from .schemas import VPNInbound, VPNReadOnlySnapshot, VPNSubscription, VPNSystemStatus


class VPNReadOnlyProvider(Protocol):
    def fetch_system_status(self) -> dict[str, Any]:
        ...

    def fetch_inbounds(self) -> dict[str, Any]:
        ...

    def fetch_subscriptions(self) -> dict[str, Any]:
        ...


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _unwrap_payload(payload: Any) -> Any:
    if isinstance(payload, dict):
        for key in ("obj", "data", "result"):
            if key in payload:
                return payload[key]
    return payload


def _to_int(value: Any, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return default
        try:
            return int(float(value))
        except ValueError:
            return default
    return default


def _to_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off"}:
            return False
    return default


def _normalize_status(value: Any) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in {"ok", "healthy", "up", "running", "true", "1"}:
        return "ok"
    if normalized in {"degraded", "error", "failed", "down", "false", "0"}:
        return "degraded"
    return "unknown"


def _coerce_datetime_utc(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    candidate = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _days_left(raw_item: dict[str, Any], now_utc: datetime) -> int | None:
    for key in ("days_left", "daysLeft", "expire_days", "expireDays"):
        if key in raw_item:
            return _to_int(raw_item.get(key), default=None)  # type: ignore[arg-type]

    expires_raw = raw_item.get("expires_at") or raw_item.get("expiresAt") or raw_item.get("expiry")
    expires_dt = _coerce_datetime_utc(expires_raw)
    if expires_dt is None:
        return None
    delta = expires_dt - now_utc
    return int(delta.total_seconds() // 86400)


def _string_or_none(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return str(value)


class VPNReadOnlyService:
    def __init__(
        self,
        provider: VPNReadOnlyProvider,
        now_fn: Callable[[], datetime] | None = None,
    ) -> None:
        self._provider = provider
        self._now_fn = now_fn or (lambda: datetime.now(timezone.utc))

    def get_system_status(self) -> VPNSystemStatus:
        raw = self._provider.fetch_system_status()
        body = _unwrap_payload(raw)
        source = body if isinstance(body, dict) else {}

        status_value = source.get("status", raw.get("status"))
        status = _normalize_status(status_value)
        panel_version = _string_or_none(
            source.get("panel_version") or source.get("panelVersion") or source.get("version")
        )
        xray_version = _string_or_none(source.get("xray_version") or source.get("xrayVersion"))

        services_raw = source.get("active_services") or source.get("activeServices") or []
        active_services: tuple[str, ...]
        if isinstance(services_raw, list):
            active_services = tuple(str(item) for item in services_raw if str(item).strip())
        else:
            active_services = ()

        notes: list[str] = []
        if status == "unknown":
            notes.append("Не удалось однозначно определить статус VPN API.")
        if not active_services:
            notes.append("Список активных сервисов не предоставлен.")

        return VPNSystemStatus(
            status=status,
            panel_version=panel_version,
            xray_version=xray_version,
            active_services=active_services,
            notes=tuple(notes),
        )

    def list_inbounds(self) -> list[VPNInbound]:
        raw = self._provider.fetch_inbounds()
        body = _unwrap_payload(raw)

        rows: list[dict[str, Any]]
        if isinstance(body, list):
            rows = [item for item in body if isinstance(item, dict)]
        elif isinstance(body, dict):
            candidates = (
                body.get("items"),
                body.get("list"),
                body.get("rows"),
                body.get("inbounds"),
            )
            rows = []
            for candidate in candidates:
                if isinstance(candidate, list):
                    rows = [item for item in candidate if isinstance(item, dict)]
                    if rows:
                        break
        else:
            rows = []

        inbounds: list[VPNInbound] = []
        for row in rows:
            tag = _string_or_none(row.get("tag") or row.get("remark") or row.get("name")) or "unknown"
            protocol = _string_or_none(row.get("protocol")) or "unknown"
            enabled = _to_bool(row.get("enabled", not row.get("disable", False)), default=True)
            up_bytes = _to_int(row.get("up") or row.get("up_bytes") or row.get("uplink"), default=0)
            down_bytes = _to_int(row.get("down") or row.get("down_bytes") or row.get("downlink"), default=0)
            clients_online = _to_int(
                row.get("clients_online") or row.get("online") or row.get("onlineClients"),
                default=0,
            )
            inbounds.append(
                VPNInbound(
                    tag=tag,
                    protocol=protocol,
                    enabled=enabled,
                    up_bytes=max(up_bytes, 0),
                    down_bytes=max(down_bytes, 0),
                    clients_online=max(clients_online, 0),
                )
            )

        return inbounds

    def list_subscriptions(self) -> list[VPNSubscription]:
        raw = self._provider.fetch_subscriptions()
        body = _unwrap_payload(raw)
        now_utc = self._now_fn().astimezone(timezone.utc)

        rows: list[dict[str, Any]]
        if isinstance(body, list):
            rows = [item for item in body if isinstance(item, dict)]
        elif isinstance(body, dict):
            candidates = (
                body.get("items"),
                body.get("list"),
                body.get("rows"),
                body.get("subscriptions"),
            )
            rows = []
            for candidate in candidates:
                if isinstance(candidate, list):
                    rows = [item for item in candidate if isinstance(item, dict)]
                    if rows:
                        break
        else:
            rows = []

        subscriptions: list[VPNSubscription] = []
        for row in rows:
            client_id = _string_or_none(row.get("client_id") or row.get("clientId") or row.get("id")) or "unknown"
            label = _string_or_none(row.get("label") or row.get("email") or row.get("remark")) or client_id

            expires_raw = row.get("expires_at") or row.get("expiresAt") or row.get("expiry")
            expires_dt = _coerce_datetime_utc(expires_raw)
            expires_at_utc = expires_dt.replace(microsecond=0).isoformat() if expires_dt else None

            days_left = _days_left(row, now_utc)
            active = _to_bool(row.get("active", not row.get("disabled", False)), default=True)
            transport = _string_or_none(row.get("transport") or row.get("network"))

            subscriptions.append(
                VPNSubscription(
                    client_id=client_id,
                    label=label,
                    expires_at_utc=expires_at_utc,
                    days_left=days_left,
                    active=active,
                    transport=transport,
                )
            )

        return subscriptions

    def collect_snapshot(self, expiring_within_days: int = 7) -> VPNReadOnlySnapshot:
        status = self.get_system_status()
        inbounds = self.list_inbounds()
        subscriptions = self.list_subscriptions()

        inbounds_total = len(inbounds)
        inbounds_enabled = sum(1 for inbound in inbounds if inbound.enabled)
        clients_online_total = sum(inbound.clients_online for inbound in inbounds)
        expiring_soon = sum(
            1 for sub in subscriptions if sub.days_left is not None and sub.days_left <= expiring_within_days
        )

        final_status = status.status
        notes = list(status.notes)
        if final_status == "ok" and inbounds_enabled == 0:
            final_status = "degraded"
            notes.append("Нет активных inbound-профилей.")

        return VPNReadOnlySnapshot(
            collected_at_utc=_utc_now_iso(),
            status=final_status,
            inbounds_total=inbounds_total,
            inbounds_enabled=inbounds_enabled,
            clients_online_total=clients_online_total,
            subscriptions_total=len(subscriptions),
            subscriptions_expiring_soon=expiring_soon,
            panel_version=status.panel_version,
            xray_version=status.xray_version,
            notes=tuple(notes),
        )
