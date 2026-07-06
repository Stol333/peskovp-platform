from __future__ import annotations

from vpn_routing.node_registry import NodeRegistry


def test_registry_from_dict_and_filters() -> None:
    registry = NodeRegistry.from_dict(
        {
            "nodes": [
                {
                    "node_id": "main-control",
                    "role": "main",
                    "region": "eu",
                    "domain": "panel.peskovp.com",
                    "port": 443,
                    "transport": "tcp",
                    "active": True,
                    "health": {
                        "latency_ms": 21,
                        "error_rate": 0.01,
                        "uptime_ratio": 0.999,
                        "load_ratio": 0.2,
                        "last_updated_utc": "2026-07-06T09:00:00Z",
                    },
                },
                {
                    "node_id": "rf-gateway",
                    "role": "rf",
                    "region": "ru",
                    "domain": "ru.peskovp.com",
                    "port": 443,
                    "transport": "tcp",
                    "active": True,
                },
            ]
        }
    )

    assert len(registry.list_nodes()) == 2
    assert registry.get_node("rf-gateway") is not None
    assert len(registry.list_active(role="rf")) == 1
    assert len(registry.list_active(region="ru")) == 1

