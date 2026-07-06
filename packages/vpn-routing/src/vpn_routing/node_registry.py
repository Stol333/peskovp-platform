from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .models import HealthMetrics, NodeDescriptor, NodeRole


class NodeRegistry:
    def __init__(self, nodes: list[NodeDescriptor]) -> None:
        self._nodes = tuple(nodes)
        self._index = {node.node_id: node for node in nodes}
        if len(self._nodes) != len(self._index):
            raise ValueError("Duplicate node_id detected in registry.")

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "NodeRegistry":
        raw_nodes = payload.get("nodes")
        if not isinstance(raw_nodes, list):
            raise ValueError("Registry payload must contain list field 'nodes'.")

        nodes: list[NodeDescriptor] = []
        for raw in raw_nodes:
            if not isinstance(raw, dict):
                continue
            node_id = str(raw.get("node_id", "")).strip()
            if not node_id:
                raise ValueError("node_id is required for each node.")
            role = _coerce_role(raw.get("role"))
            region = str(raw.get("region", "")).strip() or "unknown"
            domain = str(raw.get("domain", "")).strip()
            port = int(raw.get("port", 0))
            transport = str(raw.get("transport", "tcp")).strip() or "tcp"
            active = bool(raw.get("active", True))

            health = None
            raw_health = raw.get("health")
            if isinstance(raw_health, dict):
                health = HealthMetrics(
                    latency_ms=float(raw_health.get("latency_ms", 0.0)),
                    error_rate=float(raw_health.get("error_rate", 0.0)),
                    uptime_ratio=float(raw_health.get("uptime_ratio", 1.0)),
                    load_ratio=float(raw_health.get("load_ratio", 0.0)),
                    last_updated_utc=str(raw_health.get("last_updated_utc", "")),
                )

            nodes.append(
                NodeDescriptor(
                    node_id=node_id,
                    role=role,
                    region=region,
                    domain=domain,
                    port=port,
                    transport=transport,
                    active=active,
                    health=health,
                )
            )
        return cls(nodes=nodes)

    @classmethod
    def from_json_file(cls, path: str | Path) -> "NodeRegistry":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Registry JSON root must be an object.")
        return cls.from_dict(payload)

    def to_dict(self) -> dict[str, object]:
        return {"nodes": [asdict(node) for node in self._nodes]}

    def list_nodes(self) -> tuple[NodeDescriptor, ...]:
        return self._nodes

    def get_node(self, node_id: str) -> NodeDescriptor | None:
        return self._index.get(node_id)

    def list_active(self, role: NodeRole | None = None, region: str | None = None) -> tuple[NodeDescriptor, ...]:
        out: list[NodeDescriptor] = []
        for node in self._nodes:
            if not node.active:
                continue
            if role is not None and node.role != role:
                continue
            if region is not None and node.region != region:
                continue
            out.append(node)
        return tuple(out)


def _coerce_role(raw: object) -> NodeRole:
    value = str(raw or "backup").lower().strip()
    if value in {"main", "rf", "backup"}:
        return value  # type: ignore[return-value]
    return "backup"

