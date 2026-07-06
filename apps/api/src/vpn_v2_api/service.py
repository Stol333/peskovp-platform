from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from vpn_routing.canary_rollout import CanaryRolloutManager
from vpn_routing.health_scoring import HealthScorer
from vpn_routing.node_registry import NodeRegistry
from vpn_routing.policy_engine import RoutingPolicyEngine
from vpn_routing.subscription_profiles import SubscriptionProfileCatalog

from .config import VPNV2Settings
from .schemas import (
    NodePayload,
    SubscriptionPreviewRequest,
    SubscriptionPreviewResponse,
    SubscriptionProfilePayload,
    TelegramMiniAppSessionResponse,
)


@dataclass(slots=True, frozen=True)
class ServiceBundle:
    registry: NodeRegistry
    policy: RoutingPolicyEngine
    scorer: HealthScorer
    canary: CanaryRolloutManager
    profiles: SubscriptionProfileCatalog
    settings: VPNV2Settings


class VPNV2Service:
    def __init__(self, bundle: ServiceBundle) -> None:
        self._bundle = bundle

    @classmethod
    def build_default(cls, settings: VPNV2Settings) -> "VPNV2Service":
        root = Path(__file__).resolve().parents[4]
        registry_path = Path(settings.registry_path)
        if not registry_path.is_absolute():
            registry_path = root / registry_path

        bundle = ServiceBundle(
            registry=NodeRegistry.from_json_file(registry_path),
            policy=RoutingPolicyEngine(),
            scorer=HealthScorer(),
            canary=CanaryRolloutManager(
                rollout_percent=settings.canary_rollout_percent,
                salt=settings.canary_salt,
            ),
            profiles=SubscriptionProfileCatalog(),
            settings=settings,
        )
        return cls(bundle=bundle)

    def list_nodes(self) -> list[NodePayload]:
        ranked = self._bundle.scorer.rank(self._bundle.registry.list_active())
        out: list[NodePayload] = []
        for node in ranked:
            out.append(
                NodePayload(
                    node_id=node.node_id,
                    role=node.role,
                    region=node.region,
                    domain=node.domain,
                    port=node.port,
                    transport=node.transport,
                    active=node.active,
                    score=round(self._bundle.scorer.score(node), 2),
                )
            )
        return out

    def preview_subscription(self, request: SubscriptionPreviewRequest) -> SubscriptionPreviewResponse:
        policy = self._bundle.policy.decide(
            domain=request.domain,
            protocol=request.protocol,
            transport=request.transport,
            udp_port=request.udp_port,
        )
        canary = self._bundle.canary.should_use_v2(
            user_id=request.user_id,
            is_admin=request.is_admin,
            force_opt_in=request.force_opt_in,
        )
        profile_models = self._bundle.profiles.pick_for_decision(canary)

        preferred_nodes = self._bundle.scorer.rank(self._bundle.registry.list_active(role="rf"))[:3]
        if not preferred_nodes:
            preferred_nodes = self._bundle.scorer.rank(self._bundle.registry.list_active())[:3]

        return SubscriptionPreviewResponse(
            user_id=request.user_id,
            policy_lane=policy.lane,
            canary_lane=canary.lane,
            canary_reason=canary.reason,
            canary_bucket=canary.bucket,
            subscription_path=self._bundle.settings.hidden_subscription_path,
            profiles=[
                SubscriptionProfilePayload(
                    profile_id=model.profile_id,
                    display_name=model.display_name,
                    transports=list(model.transports),
                    include_legacy=model.include_legacy,
                    metadata=model.metadata,
                )
                for model in profile_models
            ],
            preferred_nodes=[
                NodePayload(
                    node_id=node.node_id,
                    role=node.role,
                    region=node.region,
                    domain=node.domain,
                    port=node.port,
                    transport=node.transport,
                    active=node.active,
                    score=round(self._bundle.scorer.score(node), 2),
                )
                for node in preferred_nodes
            ],
        )

    def create_telegram_session(self, *, user_id: str, locale: str | None = None) -> TelegramMiniAppSessionResponse:
        canary = self._bundle.canary.should_use_v2(user_id=user_id, is_admin=False, force_opt_in=False)
        token = self._session_token(user_id=user_id, lane=canary.lane)
        launch_url = f"{self._bundle.settings.telegram_miniapp_url}?sid={token}&lane={canary.lane}"
        if locale:
            launch_url = f"{launch_url}&lang={locale}"

        message = "V2 canary lane enabled." if canary.lane == "v2_canary" else "Legacy lane fallback."
        return TelegramMiniAppSessionResponse(
            user_id=user_id,
            launch_url=launch_url,
            canary_percent=self._bundle.canary.rollout_percent,
            lane=canary.lane,
            message=message,
        )

    def _session_token(self, *, user_id: str, lane: str) -> str:
        digest = hashlib.sha256(f"{user_id}:{lane}:{self._bundle.settings.canary_salt}".encode("utf-8")).hexdigest()
        return digest[:24]

