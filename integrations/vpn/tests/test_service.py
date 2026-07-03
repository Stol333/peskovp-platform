from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from vpn_readonly.service import VPNReadOnlyService


class _StubProvider:
    def fetch_system_status(self) -> dict[str, Any]:
        return {
            "obj": {
                "status": "ok",
                "panelVersion": "3.4.2",
                "xrayVersion": "26.2.6",
                "activeServices": ["nginx", "x-ui", "peskovp-hy2"],
            }
        }

    def fetch_inbounds(self) -> dict[str, Any]:
        return {
            "obj": {
                "items": [
                    {"tag": "reality-main", "protocol": "vless", "enabled": True, "up": 120, "down": 90, "online": 12},
                    {"tag": "hy2-canary", "protocol": "hysteria2", "enabled": False, "up": 20, "down": 10, "online": 0},
                ]
            }
        }

    def fetch_subscriptions(self) -> dict[str, Any]:
        return {
            "obj": {
                "items": [
                    {"clientId": "u-1", "label": "alpha", "daysLeft": 2, "active": True, "transport": "vless+reality"},
                    {"clientId": "u-2", "label": "beta", "daysLeft": 30, "active": True, "transport": "hy2"},
                ]
            }
        }


def test_collect_snapshot_calculates_metrics() -> None:
    fixed_now = datetime(2026, 7, 3, 14, 50, 0, tzinfo=timezone.utc)
    service = VPNReadOnlyService(provider=_StubProvider(), now_fn=lambda: fixed_now)

    snapshot = service.collect_snapshot(expiring_within_days=7)
    assert snapshot.status == "ok"
    assert snapshot.inbounds_total == 2
    assert snapshot.inbounds_enabled == 1
    assert snapshot.clients_online_total == 12
    assert snapshot.subscriptions_total == 2
    assert snapshot.subscriptions_expiring_soon == 1
    assert snapshot.panel_version == "3.4.2"
    assert snapshot.xray_version == "26.2.6"


def test_collect_snapshot_degrades_when_no_enabled_inbounds() -> None:
    class _NoEnabledProvider(_StubProvider):
        def fetch_inbounds(self) -> dict[str, Any]:
            return {"obj": {"items": [{"tag": "disabled", "protocol": "vless", "enabled": False}]}}

    service = VPNReadOnlyService(provider=_NoEnabledProvider())
    snapshot = service.collect_snapshot()
    assert snapshot.status == "degraded"
    assert any("Нет активных inbound-профилей." in note for note in snapshot.notes)
