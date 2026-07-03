from __future__ import annotations

import json

from .config import VPNIntegrationSettings
from .provider import ReadOnlyHTTPProvider
from .service import VPNReadOnlyService


def build_service_from_env() -> VPNReadOnlyService:
    settings = VPNIntegrationSettings.from_env()
    provider = ReadOnlyHTTPProvider(
        base_url=settings.api_base_url,
        api_token=settings.api_token,
        timeout_seconds=settings.timeout_seconds,
        verify_tls=settings.verify_tls,
    )
    return VPNReadOnlyService(provider=provider)


def main() -> None:
    service = build_service_from_env()
    snapshot = service.collect_snapshot()
    print(json.dumps(snapshot.to_dict(), ensure_ascii=False))


if __name__ == "__main__":
    main()
