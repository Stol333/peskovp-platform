from __future__ import annotations

import json
from typing import Any
from urllib import request

import pytest

from vpn_readonly.errors import VPNConfigurationError
from vpn_readonly.provider import ReadOnlyHTTPProvider


class _DummyResponse:
    def __init__(self, payload: dict[str, Any], status: int = 200) -> None:
        self.status = status
        self._payload = payload

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self) -> "_DummyResponse":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
        return False


def test_provider_uses_get_and_authorization_header(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def _fake_urlopen(req: request.Request, timeout: float, context: object = None) -> _DummyResponse:
        captured["method"] = req.get_method()
        captured["url"] = req.full_url
        captured["auth"] = req.headers.get("Authorization")
        captured["timeout"] = timeout
        return _DummyResponse({"status": "ok", "obj": {"status": "ok"}})

    monkeypatch.setattr("urllib.request.urlopen", _fake_urlopen)
    provider = ReadOnlyHTTPProvider(
        base_url="https://vpn.example.com",
        api_token="secret-token",
        timeout_seconds=8.0,
        verify_tls=True,
    )

    payload = provider.fetch_system_status()
    assert payload["status"] == "ok"
    assert captured["method"] == "GET"
    assert captured["url"].endswith("/api/system/status")
    assert captured["auth"] == "Bearer secret-token"
    assert captured["timeout"] == 8.0


def test_provider_blocks_non_allowlist_path() -> None:
    provider = ReadOnlyHTTPProvider(base_url="https://vpn.example.com")
    with pytest.raises(VPNConfigurationError):
        provider._get_json("/api/admin/restart")
