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
## PHASE 23 — Canary VPN provisioning gate
### Inputs reviewed
- `reports/35_vpn_v2_test_matrix.md` (legacy/V2 test comparison baseline).
- `reports/36_vpn_v2_canary_report.md` (`PHASE 19` и `PHASE 20` evidence).
- `reports/37_port_reclaim_report.md` (reclaim policy + rollback drill precondition).
- `infra/rollback/VPN_V2_ROLLBACK.md`, `infra/rollback/V6_ROLLBACK.md`, `infra/rollback/V6_PORT_MIGRATION_ROLLBACK.md`.
### Fresh precheck snapshot
- RF runtime (read-only recheck):
  - `xray` status: `active`;
  - `xray -test`: `Configuration OK`;
  - listen ports: `22`, `443`, `2087`, `2084`;
  - firewall: только `OpenSSH`, `443/tcp`, `2087/tcp`, `2084/tcp` (+ v6).
- MAIN legacy safety (read-only recheck):
  - `nginx`, `x-ui`, `peskovp-sub`, `peskovp-hy2*`: `active`;
  - критичные listen sockets соответствуют baseline (`80/443/8443/9255`, `127.0.0.1:9443`, `127.0.0.1:10443`, `127.0.0.1:18080`).
- Backup readiness:
  - `MAIN_BACKUP_PRESENT=yes` (`/root/backups/peskovp-platform-prechange-20260706-121952`);
  - `RF_BACKUP_PRESENT=yes` (`/root/backups/peskovp-platform-prechange-20260706-122147`).
### Compatibility / support burden / known issues
- Client compatibility:
  - runtime import+connect подтверждён для `NekoRay/nekobox_core` (`PASS`);
  - для `HAPP`, `v2rayTun`, `Streisand`, `V2Box` production-evidence пока отсутствует.
- Support burden snapshot:
  - GitHub tracker: open issues `0`, open PRs `0`, closed bug/incident issues `0`.
- Known constraints:
  - telemetry window пока ограничена (`admin/test + synthetic cohort`);
  - подтверждённый rollback drill для rollout-фазы ещё не зафиксирован как completed.
### Canary decision (PHASE 23)
- `PHASE23_DECISION=INTERNAL_ONLY`
- Decision rationale:
  - RF health и rollback artifacts готовы;
  - V2 canary functional, но client compatibility и support telemetry ещё недостаточны для `READY_FOR_GRADUAL_ROLLOUT`.
- Policy:
  - Разрешено: internal/admin/test usage и controlled validation.
  - Запрещено: массовый/gradual rollout и изменения legacy base до дополнительной валидации.
### Gate decision
- `PHASE 23`: `PASSED` (принято честное rollout decision в рамках gate-критерия фазы).
## PHASE 24 — Controlled production rollout
### Pre-step safety
- Перед изменением rollout выполнен fresh backup:
  - `/root/backups/peskovp-phase24-rollout-20260708-123302`
- Сохранён pre-change env snapshot для rollback:
  - `prod.env.phase22.bak`
### Apply
- Выполнен минимальный controlled rollout step на MAIN:
  - `VPN_V2_CANARY_PERCENT` увеличен `1 -> 2`.
- Перезапущены только `api` и `web-app`.
- Legacy/VPN safety flags не менялись:
  - `vpn_write_enabled=false`
  - `vpn_provisioning_dry_run=true`
### Post-apply verify
- Core health:
  - `apps/api /health`: `canary_percent=2`, status `ok`;
  - `web /api/health`: `healthy`;
  - `web /api/ready`: `api=true`, `database=true`, `redis=true`;
  - `web /api/vpn/health`: `legacy=healthy`, `v2Canary=ready_for_admin_test`.
- Route regression:
  - `app/admin/api/api-health` -> `200`;
  - `panel/sub` -> `404` (expected hidden-path behavior);
  - `www` -> `403` (default route preserved).
- Monitoring window:
  - API error lines (20m): `0`;
  - Web error lines (20m): `0`;
  - Nginx `-p err` entries: `no entries`.
- Node health score snapshot:
  - `main-control=100.0`
  - `rf-primary-tcp=97.05`
  - `rf-secondary-grpc=91.84`
- Cohort distribution after apply (`100` synthetic users):
  - `legacy=98`
  - `v2_canary=2`
### Support burden / decision
- GitHub tracker snapshot:
  - open issues `0`
  - open PRs `0`
- Rollout decision:
  - `PHASE24_DECISION=LIMITED_CANARY`
  - Массовый rollout не включался, legacy не отключался.
### Gate decision
- `PHASE 24`: `PASSED` (controlled limited-canary step стабилен).
## PHASE 24 — Controlled production rollout (step update 2% -> 5%)
### Pre-step safety
- Fresh backup перед изменением:
  - `/root/backups/peskovp-phase24-rollout-step2to5-20260708-131157`
- В backup сохранён pre-change rollout state:
  - `VPN_V2_CANARY_PERCENT=2`
### Apply
- На MAIN выполнен следующий controlled step:
  - `VPN_V2_CANARY_PERCENT` увеличен `2 -> 5`.
- Перезапущены только `api` и `web-app`.
- Safety flags не изменялись:
  - `VPN_WRITE_ENABLED=false`
  - `VPN_PROVISIONING_DRY_RUN=true`
### Post-apply verify
- Health:
  - API `/health`: `canary_percent=5`, status `ok`;
  - Web `/api/health`: `healthy`;
  - Web `/api/ready`: `api=true`, `database=true`, `redis=true`;
  - Web `/api/vpn/health`: `legacy=healthy`, `v2Canary=ready_for_admin_test`.
- Route regression:
  - `app/admin/api/api-health` -> `200`;
  - `panel/sub` -> `404` (expected hidden-path behavior);
  - `www` -> `403` (default route preserved).
- Monitoring:
  - API error lines (20m): `0`;
  - Web error lines (20m): `0`;
  - Nginx error entries: `no entries`;
  - Node scores: `100.0 / 97.05 / 91.84`.
- Cohort distribution after apply (`200` synthetic users):
  - `legacy=189`
  - `v2_canary=11`
### Support burden / rollback
- GitHub tracker snapshot:
  - open issues `0`
  - open PRs `0`
- Rollback readiness:
  - current env: `VPN_V2_CANARY_PERCENT=5`
  - backup env: `VPN_V2_CANARY_PERCENT=2`
### Rollout decision (updated)
- `PHASE24_DECISION=LIMITED_CANARY_5`
- Массовый rollout не включался; legacy grace period сохранён.
### Gate decision
- `PHASE 24`: `PASSED` (step `5%` стабилен).
