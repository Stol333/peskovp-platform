from __future__ import annotations

import json
import sys
from urllib import error, request

HEALTH_URL = "http://127.0.0.1:8787/health"


def main() -> int:
    try:
        with request.urlopen(HEALTH_URL, timeout=4) as response:
            if response.status != 200:
                return 1
            payload = json.loads(response.read().decode("utf-8"))
    except (error.URLError, TimeoutError, json.JSONDecodeError):
        return 1

    return 0 if payload.get("status") == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
