from __future__ import annotations

import os
from dataclasses import dataclass

from .errors import VPNConfigurationError


@dataclass(slots=True, frozen=True)
class VPNIntegrationSettings:
    api_base_url: str
    api_token: str | None = None
    timeout_seconds: float = 10.0
    verify_tls: bool = True

    @classmethod
    def from_env(cls) -> "VPNIntegrationSettings":
        base_url = os.getenv("VPN_API_BASE_URL", "").strip()
        if not base_url:
            raise VPNConfigurationError("VPN_API_BASE_URL is required for read-only VPN integration.")

        timeout_raw = os.getenv("VPN_HTTP_TIMEOUT_SECONDS", "10").strip()
        try:
            timeout_seconds = float(timeout_raw)
        except ValueError as exc:
            raise VPNConfigurationError("VPN_HTTP_TIMEOUT_SECONDS must be a number.") from exc
        if timeout_seconds <= 0:
            raise VPNConfigurationError("VPN_HTTP_TIMEOUT_SECONDS must be > 0.")

        verify_tls_raw = os.getenv("VPN_VERIFY_TLS", "true").strip().lower()
        verify_tls = verify_tls_raw not in {"0", "false", "no", "off"}

        token = os.getenv("VPN_API_TOKEN")
        if token is not None:
            token = token.strip() or None

        return cls(
            api_base_url=base_url.rstrip("/"),
            api_token=token,
            timeout_seconds=timeout_seconds,
            verify_tls=verify_tls,
        )
