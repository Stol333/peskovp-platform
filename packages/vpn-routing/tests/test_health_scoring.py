from __future__ import annotations

from vpn_routing.health_scoring import HealthScorer
from vpn_routing.models import HealthMetrics, NodeDescriptor


def test_health_scorer_prefers_lower_latency_and_error() -> None:
    scorer = HealthScorer()
    healthy = NodeDescriptor(
        node_id="rf-1",
        role="rf",
        region="ru",
        domain="ru.peskovp.com",
        port=443,
        transport="tcp",
        health=HealthMetrics(
            latency_ms=25.0,
            error_rate=0.01,
            uptime_ratio=0.999,
            load_ratio=0.2,
            last_updated_utc="2026-07-06T09:00:00Z",
        ),
    )
    degraded = NodeDescriptor(
        node_id="rf-2",
        role="rf",
        region="ru",
        domain="relay-ru.peskovp.com",
        port=8443,
        transport="grpc",
        health=HealthMetrics(
            latency_ms=280.0,
            error_rate=0.08,
            uptime_ratio=0.94,
            load_ratio=0.7,
            last_updated_utc="2026-07-06T09:00:00Z",
        ),
    )

    assert scorer.score(healthy) > scorer.score(degraded)
    ranked = scorer.rank((degraded, healthy))
    assert ranked[0].node_id == "rf-1"

