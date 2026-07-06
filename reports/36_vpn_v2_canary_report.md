# 36 VPN V2 Canary Report
## Цель
Подтвердить готовность controlled V2 canary без массового переключения legacy пользователей.

## Выполненные шаги
- Собраны и зафиксированы baseline отчёты:
  - `reports/30_competitor_pattern_analysis.md`
  - `reports/31_ru_gateway_audit.md`
  - `reports/32_port_ownership_and_migration_plan.md`
- Выполнен backup gate:
  - MAIN: `/root/backups/peskovp-platform-prechange-20260706-121952`
  - RF: `/root/backups/peskovp-platform-prechange-20260706-122147`
- Подготовлен rollback runbook:
  - `infra/rollback/VPN_V2_ROLLBACK.md`
- Реализован canary logic stack:
  - `packages/vpn-routing/*`
  - `apps/api/src/vpn_v2_api/*`
  - `apps/api/src/main.py`
  - `apps/web/public/telegram-miniapp-v2.html`

## Canary readiness evidence
- DNS split подтверждён:
  - MAIN domains -> `91.202.0.193`
  - RF domains (`ru`, `relay-ru`) -> `138.16.181.33`
- Cohort simulation (5%):
  - `CANARY_PERCENT_REAL=4.50` на 1000 synthetic users.
- API preview flow:
  - отрабатывает lane/policy/profile selection для V2 canary.

## Ограничения (осознанные)
- Массовая подписка не переключалась.
- Legacy service ownership на MAIN не менялся.
- Port reclaim не запускался до production canary traffic.

## Canary decision
- Статус: `READY_FOR_ADMIN_TEST`.
- Разрешено:
  - admin/test users only,
  - hidden V2 subscription endpoint,
  - мониторинг fail-rate до расширения cohort.
- Запрещено:
  - массовый switch существующих пользователей,
  - отключение legacy ports до отдельного gate.

