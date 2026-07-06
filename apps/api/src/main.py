from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI

ROOT = Path(__file__).resolve().parents[3]
VPN_ROUTING_SRC = ROOT / "packages" / "vpn-routing" / "src"
if str(VPN_ROUTING_SRC) not in sys.path:
    sys.path.insert(0, str(VPN_ROUTING_SRC))

from vpn_v2_api.config import VPNV2Settings
from vpn_v2_api.schemas import (
    SubscriptionPreviewRequest,
    SubscriptionPreviewResponse,
    TelegramMiniAppSessionRequest,
    TelegramMiniAppSessionResponse,
)
from vpn_v2_api.service import VPNV2Service

settings = VPNV2Settings.from_env()
service = VPNV2Service.build_default(settings)

app = FastAPI(
    title="PESKOVP API (VPN V2 contour)",
    description="Minimal API contour for controlled VPN V2 rollout.",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "service": "apps/api",
        "env": settings.app_env,
        "canary_percent": settings.canary_rollout_percent,
        "rf_gateway_enabled": settings.enable_rf_gateway,
    }


@app.get("/v2/nodes")
def list_nodes() -> list[dict[str, object]]:
    return [node.model_dump() for node in service.list_nodes()]


@app.post("/v2/subscription/preview", response_model=SubscriptionPreviewResponse)
def preview_subscription(request: SubscriptionPreviewRequest) -> SubscriptionPreviewResponse:
    return service.preview_subscription(request)


@app.post("/v2/telegram/miniapp/session", response_model=TelegramMiniAppSessionResponse)
def telegram_session(request: TelegramMiniAppSessionRequest) -> TelegramMiniAppSessionResponse:
    return service.create_telegram_session(user_id=request.user_id, locale=request.locale)

