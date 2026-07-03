from __future__ import annotations

import json
import ssl
from dataclasses import dataclass
from typing import Any
from urllib import error, request

from .errors import VPNConfigurationError, VPNResponseError

READ_ONLY_ENDPOINTS = frozenset(
    {
        "/api/system/status",
        "/api/inbounds/list",
        "/api/subscriptions/list",
    }
)


@dataclass(slots=True)
class ReadOnlyHTTPProvider:
    base_url: str
    api_token: str | None = None
    timeout_seconds: float = 10.0
    verify_tls: bool = True

    def __post_init__(self) -> None:
        self.base_url = self.base_url.rstrip("/")
        if not self.base_url.startswith(("http://", "https://")):
            raise VPNConfigurationError("VPN base_url must start with http:// or https://")
        if self.timeout_seconds <= 0:
            raise VPNConfigurationError("timeout_seconds must be > 0")

    def fetch_system_status(self) -> dict[str, Any]:
        return self._get_json("/api/system/status")

    def fetch_inbounds(self) -> dict[str, Any]:
        return self._get_json("/api/inbounds/list")

    def fetch_subscriptions(self) -> dict[str, Any]:
        return self._get_json("/api/subscriptions/list")

    def _get_json(self, path: str) -> dict[str, Any]:
        if path not in READ_ONLY_ENDPOINTS:
            raise VPNConfigurationError(f"Path is not allowed in read-only mode: {path}")

        url = f"{self.base_url}{path}"
        headers = {"Accept": "application/json"}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"

        req = request.Request(url=url, headers=headers, method="GET")
        ssl_context = None
        if url.startswith("https://") and not self.verify_tls:
            ssl_context = ssl._create_unverified_context()

        try:
            with request.urlopen(req, timeout=self.timeout_seconds, context=ssl_context) as response:
                status_code = getattr(response, "status", 200)
                body = response.read().decode("utf-8")
        except error.HTTPError as exc:
            raise VPNResponseError(f"HTTP error for {path}: {exc.code}") from exc
        except error.URLError as exc:
            raise VPNResponseError(f"Connection error for {path}: {exc.reason}") from exc

        if status_code >= 400:
            raise VPNResponseError(f"API returned status {status_code} for {path}")

        if not body:
            return {}
        try:
            payload = json.loads(body)
        except json.JSONDecodeError as exc:
            raise VPNResponseError(f"Invalid JSON from {path}") from exc
        if not isinstance(payload, dict):
            raise VPNResponseError(f"JSON root must be object for {path}")
        return payload
