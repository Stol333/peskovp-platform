from __future__ import annotations

from vpn_routing.canary_rollout import CanaryRolloutManager


def test_admin_always_goes_to_v2_canary() -> None:
    manager = CanaryRolloutManager(rollout_percent=1, salt="test-seed")
    decision = manager.should_use_v2(user_id="admin-1", is_admin=True)
    assert decision.lane == "v2_canary"
    assert decision.reason == "admin_override"


def test_stable_bucket_for_regular_user() -> None:
    manager = CanaryRolloutManager(rollout_percent=5, salt="seed")
    d1 = manager.should_use_v2(user_id="user-42")
    d2 = manager.should_use_v2(user_id="user-42")
    assert d1.bucket == d2.bucket
    assert d1.lane in {"legacy", "v2_canary"}

