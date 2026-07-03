from __future__ import annotations

import pytest

from vpn_readonly.config import VPNIntegrationSettings
from vpn_readonly.errors import VPNConfigurationError


def test_config_from_env_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VPN_API_BASE_URL", "https://vpn.example.com/")
    monkeypatch.setenv("VPN_API_TOKEN", " token ")
    monkeypatch.setenv("VPN_HTTP_TIMEOUT_SECONDS", "15")
    monkeypatch.setenv("VPN_VERIFY_TLS", "false")

    cfg = VPNIntegrationSettings.from_env()
    assert cfg.api_base_url == "https://vpn.example.com"
    assert cfg.api_token == "token"
    assert cfg.timeout_seconds == 15
    assert cfg.verify_tls is False


def test_config_requires_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("VPN_API_BASE_URL", raising=False)
    with pytest.raises(VPNConfigurationError):
        VPNIntegrationSettings.from_env()
