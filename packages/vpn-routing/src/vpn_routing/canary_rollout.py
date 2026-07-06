from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class CanaryDecision:
    user_id: str
    lane: str
    rollout_percent: int
    reason: str
    bucket: int


class CanaryRolloutManager:
    def __init__(self, *, rollout_percent: int, salt: str = "peskovp-v2") -> None:
        self._rollout_percent = _normalize_percent(rollout_percent)
        self._salt = salt

    @property
    def rollout_percent(self) -> int:
        return self._rollout_percent

    def should_use_v2(
        self,
        *,
        user_id: str,
        is_admin: bool = False,
        force_opt_in: bool = False,
    ) -> CanaryDecision:
        if is_admin:
            return CanaryDecision(
                user_id=user_id,
                lane="v2_canary",
                rollout_percent=self._rollout_percent,
                reason="admin_override",
                bucket=0,
            )

        if force_opt_in:
            bucket = _stable_bucket(user_id=user_id, salt=self._salt)
            return CanaryDecision(
                user_id=user_id,
                lane="v2_canary",
                rollout_percent=self._rollout_percent,
                reason="user_opt_in",
                bucket=bucket,
            )

        bucket = _stable_bucket(user_id=user_id, salt=self._salt)
        if bucket < self._rollout_percent:
            return CanaryDecision(
                user_id=user_id,
                lane="v2_canary",
                rollout_percent=self._rollout_percent,
                reason="percentage_rollout",
                bucket=bucket,
            )

        return CanaryDecision(
            user_id=user_id,
            lane="legacy",
            rollout_percent=self._rollout_percent,
            reason="outside_rollout_bucket",
            bucket=bucket,
        )


def _stable_bucket(*, user_id: str, salt: str) -> int:
    payload = f"{salt}:{user_id}".encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()
    value = int(digest[:8], 16)
    return value % 100


def _normalize_percent(value: int) -> int:
    if value < 0:
        return 0
    if value > 100:
        return 100
    return value

