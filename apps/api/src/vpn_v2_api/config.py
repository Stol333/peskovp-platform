from __future__ import annotations

import os
from dataclasses import dataclass


def _as_bool(raw: str | None, default: bool = False) -> bool:
    if raw is None:
        return default
    value = raw.strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    return default


@dataclass(slots=True, frozen=True)
class VPNV2Settings:
    app_env: str
    canary_rollout_percent: int
    canary_salt: str
    registry_path: str
    telegram_miniapp_url: str
    hidden_subscription_path: str
    enable_rf_gateway: bool

    @classmethod
    def from_env(cls) -> "VPNV2Settings":
        return cls(
            app_env=os.getenv("APP_ENV", "development"),
            canary_rollout_percent=max(0, min(100, int(os.getenv("VPN_V2_CANARY_PERCENT", "1")))),
            canary_salt=os.getenv("VPN_V2_CANARY_SALT", "peskovp-v2-default-salt"),
            registry_path=os.getenv("VPN_V2_REGISTRY_PATH", "apps/api/src/vpn_v2_api/sample_nodes.json"),
            telegram_miniapp_url=os.getenv("VPN_V2_TELEGRAM_MINIAPP_URL", "https://t.me/peskovp_bot/app"),
            hidden_subscription_path=os.getenv("VPN_V2_HIDDEN_SUBSCRIPTION_PATH", "/v2/subscription/canary"),
            enable_rf_gateway=_as_bool(os.getenv("VPN_V2_ENABLE_RF_GATEWAY"), default=True),
        )

