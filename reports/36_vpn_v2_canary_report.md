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
## PHASE 19 — RF gateway canary deploy
### Выполнено
- Разблокирован non-interactive SSH доступ к RF (`138.16.181.33`) через ключ `id_ed25519_138_16_181_33_ru`.
- Подтверждён backup precondition из PHASE 04:
  - `/root/backups/peskovp-platform-prechange-20260706-122147`
- На RF установлен и запущен `xray` (`26.3.27`).
- Применён canary config с transport candidates:
  - `VLESS Reality TCP` (`443/tcp`)
  - `VLESS Reality gRPC` (`2087/tcp`)
  - `VLESS Reality xHTTP` (`2084/tcp`, supported)
- Все canary credentials сгенерированы заново на RF; чужие credentials не использовались.
### Проверка
- `xray run -test -config /usr/local/etc/xray/config.json` -> `PASS`.
- `systemctl is-active xray` -> `active`.
- `ss -tuln` на RF -> listen `443`, `2087`, `2084`.
- `ufw status numbered` -> активны только правила:
  - `OpenSSH`
  - `443/tcp`
  - `2087/tcp`
  - `2084/tcp`
- External TCP connectivity:
  - `Test-NetConnection 138.16.181.33 -Port 443` -> `True`
  - `Test-NetConnection 138.16.181.33 -Port 2087` -> `True`
  - `Test-NetConnection 138.16.181.33 -Port 2084` -> `True`
### Артефакты
- Remote evidence:
  - `/root/backups/peskovp-phase19-canary-20260707-130538`
- Local evidence copy:
  - `artifacts/phase19_v6_rf/peskovp-phase19-canary-20260707-130538`
### Ограничения/инварианты
- Массовая legacy подписка не изменялась.
- PHASE 20+ шаги не запускались в рамках этого обновления.
### Gate decision
- `PHASE 19`: `PASSED`.
- Статус canary readiness: `READY_FOR_PHASE_20_SUBSCRIPTION_CANARY`.
## PHASE 20 — V2 subscription canary
### Выполнено
- Подтверждена ролевая модель:
  - RU canary gateway: `138.16.181.33`
  - MAIN foreign consolidator/control-plane: `91.202.0.193`
- Выполнены canary preview проверки:
  - `phase20-admin-01` (`is_admin=true`) -> `v2_canary`
  - `phase20-optin-01` (`force_opt_in=true`) -> `v2_canary`
  - `phase20-regular-01` -> `legacy`
- Подтверждён полный canary profile bundle:
  - `v2_canary`, `v2_auto`, `v2_mobile_lte`, `v2_ru_whitelist`, `v2_premium`, `v2_rf_gateway`, `legacy`
- Policy behavior:
  - RU domain (`video.yandex.ru`) -> `direct`
  - default external (`example.org`) -> `proxy`
  - blocked protocol (`bittorrent`) -> `block`
- Проверены link/QR prerequisites:
  - URLs в формате `https://...`
  - токен в отчётах redacted
  - длина payload подходит для QR
### Legacy and isolation checks
- Legacy subscription unchanged:
  - `/api/subscriptions/current` -> `profile=legacy`
  - `/api/vpn/health` -> `legacy=healthy`, `v2Canary=ready_for_admin_test`
- MAIN не затронут:
  - `nginx/x-ui/peskovp-sub/hy2*` active
  - RF canary artifacts отсутствуют на MAIN
- RU runtime стабилен:
  - `xray active`, `xray -test` = `Configuration OK`
  - `443/2087/2084` listening
  - `ufw` только `OpenSSH`, `443/tcp`, `2087/tcp`, `2084/tcp`
### Rollout monitor snapshot
- Config canary percent: `1%`
- Synthetic sample (`200` users):
  - `legacy=196`
  - `v2_canary=4`
### Ограничения
- По клиентам:
  - `NekoRay` установлен (`4.0.1`);
  - `HAPP`, `v2rayTun`, `Streisand`, `V2Box` недоступны.
- GUI-evidence для остальных клиентов пока отсутствует, но обязательный критерий client import+connect закрыт через реальный runtime тест NekoRay/nekobox_core.
### Артефакты
- `artifacts/phase20_v6/phase20_subscription_checks.json`
- `artifacts/phase20_v6/nekobox_client_runtime_test.json`
- `artifacts/phase20_v6/nekobox_runtime_run.log`
- `artifacts/phase20_v6/nekobox_runtime_run.err.log`
- `artifacts/phase20_v6/phase20_nekobox_runtime_connect_evidence.txt`
### Gate decision
- `PHASE 20`: `PASSED`
- Основание: подтверждён runtime import+connect минимум в одном реальном клиенте (`NekoRay`/`nekobox_core`), включая успешный connect через SOCKS и trace egress через RU gateway.
