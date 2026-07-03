from __future__ import annotations

from collections import defaultdict, deque
from datetime import UTC, datetime
from typing import Any

from .schemas import HistoryItem


class InMemoryHistoryStore:
    def __init__(self, *, max_items_per_session: int) -> None:
        self._max_items = max_items_per_session
        self._sessions: dict[str, deque[HistoryItem]] = defaultdict(
            lambda: deque(maxlen=self._max_items)
        )

    def append(self, session_id: str, role: str, content: str, metadata: dict[str, Any] | None = None) -> None:
        item = HistoryItem(
            role=role,
            content=content,
            metadata=metadata or {},
            timestamp_utc=datetime.now(UTC).isoformat(),
        )
        self._sessions[session_id].append(item)

    def get(self, session_id: str, *, limit: int = 20) -> list[HistoryItem]:
        items = list(self._sessions.get(session_id, deque()))
        return items[-limit:]
