# VPN V2 Architecture (Controlled Re-Architecture)
## Цели
- Добавить V2 data-plane без деградации текущего production legacy-контура.
- Разделить ownership: MAIN как control-plane/edge, RF как canary data-plane.
- Ввести policy-based routing, health scoring и canary rollout для профилей.

## Компоненты
### Control plane (MAIN)
- `x-ui` + текущий subscription stack остаются источником legacy-конфига.
- Новый V2 subscription endpoint работает в скрытом режиме для admin/test.
- Nginx/SSH/fail2ban/UFW остаются с текущими инвариантами.

### Data plane (RF)
- Отдельные V2 transport endpoints (поэтапно: stable TCP -> gRPC/xHTTP -> HY2).
- Минимально открытый firewall per-port.
- Health telemetry для маршрутизации профилей.

### Routing and rollout engine
- Модуль `packages/vpn-routing`:
  - реестр нод;
  - policy engine (direct/proxy/block);
  - health scoring;
  - canary percentage rollout;
  - subscription profile presets.

### Product contours
- API (`apps/api`):
  - выбор профиля для пользователя,
  - preview V2 subscription,
  - canary-decision endpoint,
  - Telegram Mini App session bootstrap.
- Web/Admin (`apps/web`):
  - UI-контур управления canary rollout и просмотров профилей.
- Telegram Mini App:
  - быстрый выбор профиля/диагностики подключения для canary users.

## Routing policy tiers
- `direct`:
  - RU/локальные ресурсы и критичные whitelist-домены.
- `proxy`:
  - прочий user traffic через выбранную здоровую ноду.
- `block`:
  - известные нежелательные классы (например, bittorrent policy lane).

## Rollout strategy
- Stage 0: admin-only canary.
- Stage 1: `1%` новых пользователей.
- Stage 2: `5%`.
- Stage 3: `25%`.
- Stage 4: default для новых пользователей, opt-in для существующих.
- Каждый stage включает:
  - health metrics check,
  - error budget check,
  - rollback readiness.

## Инварианты безопасности
- Не публиковать compose-порты `80/443` на MAIN.
- Не менять массовую legacy подписку до canary pass.
- Не раскрывать скрытые panel paths и креды.
- Все ключи/UUID/shortId/serverName/path генерировать заново.

## Артефакты контроля качества
- `reports/35_vpn_v2_test_matrix.md`
- `reports/36_vpn_v2_canary_report.md`
- `reports/37_port_reclaim_report.md`
- `infra/rollback/VPN_V2_ROLLBACK.md`

