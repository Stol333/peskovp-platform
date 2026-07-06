from __future__ import annotations

from vpn_v2_api.config import VPNV2Settings
from vpn_v2_api.schemas import SubscriptionPreviewRequest
from vpn_v2_api.service import VPNV2Service


def _settings() -> VPNV2Settings:
    return VPNV2Settings(
        app_env="test",
        canary_rollout_percent=5,
        canary_salt="test-salt",
        registry_path="apps/api/src/vpn_v2_api/sample_nodes.json",
        telegram_miniapp_url="https://t.me/peskovp_bot/app",
        hidden_subscription_path="/v2/subscription/canary",
        enable_rf_gateway=True,
    )


def test_subscription_preview_returns_profiles() -> None:
    service = VPNV2Service.build_default(_settings())
    response = service.preview_subscription(
        SubscriptionPreviewRequest(
            user_id="user-123",
            domain="video.yandex.ru",
            protocol="http",
            transport="tcp",
        )
    )
    assert response.policy_lane in {"direct", "proxy", "block"}
    assert len(response.profiles) >= 1
    assert response.subscription_path == "/v2/subscription/canary"


def test_telegram_session_contains_lane_and_url() -> None:
    service = VPNV2Service.build_default(_settings())
    response = service.create_telegram_session(user_id="user-42", locale="ru")
    assert response.launch_url.startswith("https://t.me/peskovp_bot/app")
    assert response.lane in {"legacy", "v2_canary"}

