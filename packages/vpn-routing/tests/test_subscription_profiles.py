from __future__ import annotations

from vpn_routing.canary_rollout import CanaryDecision
from vpn_routing.subscription_profiles import SubscriptionProfileCatalog


def test_catalog_returns_legacy_only_for_legacy_lane() -> None:
    catalog = SubscriptionProfileCatalog()
    decision = CanaryDecision(
        user_id="u1",
        lane="legacy",
        rollout_percent=5,
        reason="outside_rollout_bucket",
        bucket=98,
    )
    profiles = catalog.pick_for_decision(decision)
    assert len(profiles) == 1
    assert profiles[0].profile_id == "legacy"


def test_catalog_returns_canary_bundle_for_v2_lane() -> None:
    catalog = SubscriptionProfileCatalog()
    decision = CanaryDecision(
        user_id="u2",
        lane="v2_canary",
        rollout_percent=5,
        reason="percentage_rollout",
        bucket=1,
    )
    profiles = catalog.pick_for_decision(decision)
    ids = {profile.profile_id for profile in profiles}
    assert "canary" in ids
    assert "legacy" in ids

