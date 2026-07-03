# VPN Integration (Phase 8, read-only)
## Назначение
Модуль `integrations/vpn` реализует безопасную read-only интеграцию с VPN-контуром для сбора статуса, inbound-метрик и состояния подписок без изменения production-конфигурации.

## Гарантии безопасности
- Только HTTP `GET` запросы к allowlist endpoint-ам.
- Нет методов создания/изменения/удаления объектов.
- Нет shell/system действий.
- Секреты не хранятся в коде; токен берётся только из env.

## Структура
- `src/vpn_readonly` — пакет интеграции.
- `schemas/vpn_readonly_snapshot.schema.json` — JSON Schema итогового snapshot.

## Поддерживаемые endpoint-ы (allowlist)
- `/api/system/status`
- `/api/inbounds/list`
- `/api/subscriptions/list`

## Переменные окружения
- `VPN_API_BASE_URL` — базовый URL панели/API (обязательно).
- `VPN_API_TOKEN` — bearer token (опционально, если endpoint требует auth).
- `VPN_HTTP_TIMEOUT_SECONDS` — timeout HTTP-запросов, по умолчанию `10`.
- `VPN_VERIFY_TLS` — проверка TLS (`true/false`), по умолчанию `true`.

## Быстрый запуск
1. Скопировать `integrations/vpn/.env.example` и задать переменные окружения.
2. Запустить из корня репозитория:
   - `python integrations/vpn/run_snapshot.py`
3. На выходе будет JSON snapshot в stdout.

## Пример результата
```json
{
  "collected_at_utc": "2026-07-03T14:50:00+00:00",
  "status": "ok",
  "inbounds_total": 12,
  "inbounds_enabled": 12,
  "clients_online_total": 74,
  "subscriptions_total": 120,
  "subscriptions_expiring_soon": 9,
  "panel_version": "3.4.2",
  "xray_version": "26.2.6",
  "notes": []
}
```
