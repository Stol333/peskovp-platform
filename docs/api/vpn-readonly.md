# VPN Read-only API Contract
Актуально для `integrations/vpn` после Phase 13.
## Назначение
Собирать snapshot состояния VPN-контура без изменения production-конфигурации.
## Security contract
- Разрешены только `GET` вызовы к allowlist endpoint-ам.
- Любые create/update/delete операции запрещены.
- Секреты берутся только из env.
## Allowlist endpoints
- `/api/system/status`
- `/api/inbounds/list`
- `/api/subscriptions/list`
## Выходные данные
- Итог — JSON snapshot, валидируемый схемой:
  - `integrations/vpn/schemas/vpn_readonly_snapshot.schema.json`
## Эксплуатационные переменные
- `VPN_API_BASE_URL`
- `VPN_API_TOKEN` (опционально)
- `VPN_HTTP_TIMEOUT_SECONDS`
- `VPN_VERIFY_TLS`
## Валидация
- Unit/regression: `python -m pytest integrations/vpn/tests`.
- Compile sanity: `python -m compileall integrations/vpn/src/vpn_readonly`.
