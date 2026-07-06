from __future__ import annotations

from .models import NodeDescriptor


class HealthScorer:
    def __init__(
        self,
        *,
        latency_budget_ms: float = 400.0,
        max_error_rate: float = 0.2,
        min_uptime_ratio: float = 0.9,
    ) -> None:
        self._latency_budget_ms = latency_budget_ms
        self._max_error_rate = max_error_rate
        self._min_uptime_ratio = min_uptime_ratio

    def score(self, node: NodeDescriptor) -> float:
        if node.health is None:
            return 0.0

        latency_penalty = min(node.health.latency_ms / self._latency_budget_ms, 1.0)
        error_penalty = min(node.health.error_rate / self._max_error_rate, 1.0) if self._max_error_rate > 0 else 1.0
        uptime_bonus = min(max(node.health.uptime_ratio, 0.0), 1.0)
        load_penalty = min(max(node.health.load_ratio, 0.0), 1.0)

        score = 100.0
        score -= latency_penalty * 30.0
        score -= error_penalty * 40.0
        score -= load_penalty * 20.0
        score += uptime_bonus * 10.0

        if node.health.uptime_ratio < self._min_uptime_ratio:
            score -= 15.0

        return max(0.0, min(score, 100.0))

    def rank(self, nodes: tuple[NodeDescriptor, ...]) -> tuple[NodeDescriptor, ...]:
        ranked = sorted(nodes, key=self.score, reverse=True)
        return tuple(ranked)

