from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from .redaction import redact_object


class UsageLogger:
    def __init__(self, path: str) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, record: dict[str, Any]) -> None:
        payload = redact_object(
            {
                "timestamp_utc": datetime.now(UTC).isoformat(),
                **record,
            }
        )
        with self._path.open("a", encoding="utf-8") as fp:
            fp.write(json.dumps(payload, ensure_ascii=False) + "\n")
