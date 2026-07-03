from __future__ import annotations

import math
import threading
import time
from dataclasses import dataclass


@dataclass
class _Window:
    started_at: float
    requests: int


class InMemoryRateLimiter:
    def __init__(self, *, max_requests: int, window_seconds: int) -> None:
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._state: dict[str, _Window] = {}
        self._lock = threading.Lock()

    def allow(self, key: str) -> tuple[bool, int]:
        now = time.time()
        with self._lock:
            current = self._state.get(key)
            if current is None or (now - current.started_at) >= self._window_seconds:
                self._state[key] = _Window(started_at=now, requests=1)
                return True, 0

            if current.requests < self._max_requests:
                current.requests += 1
                return True, 0

            retry_after = math.ceil(self._window_seconds - (now - current.started_at))
            return False, max(retry_after, 1)
