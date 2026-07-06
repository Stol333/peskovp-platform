from __future__ import annotations

from .canary_rollout import CanaryDecision
from .models import SubscriptionProfile


class SubscriptionProfileCatalog:
    def __init__(self) -> None:
        self._profiles = {
            "legacy": SubscriptionProfile(
                profile_id="legacy",
                display_name="Legacy Stable",
                transports=("vless_reality_main", "hy2_main"),
                include_legacy=True,
                metadata={"tier": "stable"},
            ),
            "v2_auto": SubscriptionProfile(
                profile_id="v2_auto",
                display_name="V2 Auto",
                transports=("vless_rf_tcp", "vless_rf_grpc", "vless_rf_xhttp"),
                include_legacy=True,
                metadata={"tier": "v2"},
            ),
            "lte_safe": SubscriptionProfile(
                profile_id="lte_safe",
                display_name="LTE Safe",
                transports=("vless_rf_tcp",),
                include_legacy=True,
                metadata={"tier": "v2_safe"},
            ),
            "ru_direct": SubscriptionProfile(
                profile_id="ru_direct",
                display_name="RU Direct + Proxy Mix",
                transports=("vless_rf_tcp", "vless_rf_grpc"),
                include_legacy=True,
                direct_domains=("ru", "su", "xn--p1ai", "yandex.ru", "vk.com"),
                blocked_protocols=("bittorrent",),
                metadata={"tier": "v2_policy"},
            ),
            "rf_gateway": SubscriptionProfile(
                profile_id="rf_gateway",
                display_name="RF Gateway",
                transports=("vless_rf_tcp", "hy2_rf"),
                include_legacy=False,
                metadata={"tier": "rf_only"},
            ),
            "canary": SubscriptionProfile(
                profile_id="canary",
                display_name="V2 Canary",
                transports=("vless_rf_tcp", "vless_rf_grpc", "hy2_rf"),
                include_legacy=True,
                blocked_protocols=("bittorrent",),
                metadata={"tier": "canary"},
            ),
        }

    def get(self, profile_id: str) -> SubscriptionProfile | None:
        return self._profiles.get(profile_id)

    def list_all(self) -> tuple[SubscriptionProfile, ...]:
        return tuple(self._profiles.values())

    def pick_for_decision(self, decision: CanaryDecision) -> tuple[SubscriptionProfile, ...]:
        legacy = self._profiles["legacy"]
        if decision.lane == "legacy":
            return (legacy,)
        return (
            self._profiles["canary"],
            self._profiles["v2_auto"],
            self._profiles["lte_safe"],
            self._profiles["ru_direct"],
            legacy,
        )

