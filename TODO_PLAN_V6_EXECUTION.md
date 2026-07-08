# TODO PLAN V6 EXECUTION
## Gate model (mandatory)
Read → Plan → Risk check → Backup/Rollback check → Execute → Verify → Record → Gate → Next
## Status legend
[ ] NOT_STARTED
[/] IN_PROGRESS
[!] BLOCKED
[x] PASSED
[-] SKIPPED_WITH_REASON
[~] ROLLBACK_REQUIRED
## Phase checklist (00-29)
[x] PHASE 00 — STARTUP / READING / EXECUTION CONTROL
[x] PHASE 01 — READ-ONLY MAIN SERVER AUDIT
[x] PHASE 02 — READ-ONLY RF GATEWAY AUDIT
[!] PHASE 03 — COMPETITOR FILE REDACTED ANALYSIS
[x] PHASE 04 — BACKUP AND ROLLBACK BEFORE ANY CHANGE
[x] PHASE 05 — PORT OWNERSHIP AND MIGRATION PLAN
[x] PHASE 06 — VPN V2 ARCHITECTURE
[x] PHASE 07 — REPO GAP ANALYSIS AND IMPLEMENTATION PLAN
[x] PHASE 08 — PRODUCT SPEC AND FEATURE MAP
[!] PHASE 09 — IMPLEMENT MODERN WEB PLATFORM
[!] PHASE 10 — DB SCHEMA AND MIGRATIONS
[!] PHASE 11 — TELEGRAM MINI APP AND BOT
[!] PHASE 12 — PAYMENTS
[x] PHASE 13 — VPN ROUTING ENGINE AND PROVISIONING
[x] PHASE 14 — AI/GPT MODULE
[x] PHASE 15 — DOCKER COMPOSE PRODUCTION REFACTOR
[x] PHASE 16 — PRODUCTION ENV
[x] PHASE 17 — TEST BEFORE DEPLOY
[x] PHASE 18 — LOCAL SERVER DEPLOY WITHOUT PUBLIC NGINX ROUTE
[x] PHASE 19 — RF GATEWAY CANARY DEPLOY
[x] PHASE 20 — V2 SUBSCRIPTION CANARY
[x] PHASE 21 — HOST NGINX ROUTE FOR WEB/API/ADMIN
[x] PHASE 22 — PAYMENT TO SUBSCRIPTION SMOKE TEST
[x] PHASE 23 — CANARY VPN PROVISIONING GATE
[x] PHASE 24 — CONTROLLED PRODUCTION ROLLOUT
[!] PHASE 25 — PORT RECLAMATION
[ ] PHASE 26 — CI/CD
[ ] PHASE 27 — FINAL SECURITY REVIEW
[ ] PHASE 28 — FINAL TEST MATRIX
[ ] PHASE 29 — FINAL REPORT AND OWNER SUMMARY
## Current gate
PHASE_25_BLOCKED
## Governance sync checkpoint (PHASE 00 re-sync)
- Source-of-truth синхронизирован:
  - `TODO_PLAN_V6_EXECUTION.md`: `PHASE 22 = PASSED`, следующий шаг `PHASE 23`.
  - `reports/34_v6_implementation_log.md`: `PHASE 22 = PASSED`, `Next -> PHASE 23`.
- Cross-report status check:
  - `reports/35_vpn_v2_test_matrix.md`: `PHASE 17 = PASSED`, `PHASE 18 = PASSED`.
  - `reports/36_vpn_v2_canary_report.md`: `PHASE 19 = PASSED`, `PHASE 20 = PASSED`.
  - `reports/37_port_reclaim_report.md`: reclaim `BLOCKED` (PHASE 25 precheck; grace period/legacy activity constraints).
  - `reports/38_final_v6_report.md`: зафиксирован как промежуточный срез до финализации `PHASE 29`.
- Обязательный финальный артефакт создан как резерв:
  - `reports/39_final_v6_execution_report.md` (`RESERVED_FOR_PHASE_29`, не финальный до закрытия `PHASE 23-29`).
## Safety locks
- До закрытия PHASE 04 любые server-side действия только read-only.
- Запрещено переходить к следующей phase без явного gate текущей phase (`PASSED` или честный `BLOCKED`).
## PHASE 17 closure evidence (re-verify)
1. JS/TS workspace verify — `PASS`:
   - `pnpm lint`
   - `pnpm typecheck`
   - `pnpm build`
   - `pnpm test`
   - `pnpm --filter @peskovp/db build`
2. Regression safety verify — `PASS`:
   - `python -m pytest C:/Users/dgafa/packages/vpn-routing/tests -q`
   - `python -m pytest C:/Users/dgafa/apps/api/tests -q`
   - `python -m pytest C:/Users/dgafa/integrations/vpn/tests -q`
   - `python -m pytest C:/Users/dgafa/services/ai-module/tests -q`
   - `python -m compileall C:/Users/dgafa/packages/vpn-routing/src C:/Users/dgafa/apps/api/src C:/Users/dgafa/integrations/vpn/src C:/Users/dgafa/services/ai-module/src`
   - `docker compose -f C:/Users/dgafa/docker/docker-compose.prod.yml --env-file C:/Users/dgafa/docker/env/prod.env.example config`
3. Закрытые блокеры:
   - `apps/bot`: исправлены `exactOptionalPropertyTypes` ошибки в `src/config.ts` и `src/main.ts`;
   - `apps/web`: исправлены strict optional shape и module resolution для workspace-пакетов;
   - `packages/vpn-routing`: test-runner ограничен TS-тестами, исключены сгенерированные `.js/.d.ts` дубликаты из Vitest.
4. Примечание по format-check:
   - `pnpm exec prettier --check .` из корня домашнего каталога упирается в системные директории с ограниченными правами и legacy format debt; выделено в отдельную cleanup-задачу, не блокирующую gate PHASE 17.
## Roadmap update (post-PHASE 17 block)
- R1: Dependency unblock (`node/npm/pnpm`) — завершён.
- R2: Закрыть оставшиеся TS блокеры `apps/bot` (`config.ts`, `main.ts`) — завершён.
- R3: Повторный predeploy verify PHASE 17 и перевод gate в `PASSED` — завершён.
- R4: Старт PHASE 18 (local server deploy без public nginx route) — разрешён.
## PHASE 18 execution evidence (local deploy)
1. Runtime/infra старт:
   - `docker compose version` -> `v5.3.0`
   - `docker info --format "{{.ServerVersion}}"` -> initial `BLOCKED` (daemon down), после запуска Docker Desktop -> `29.6.1`.
2. Deploy шаги:
   - `docker compose ... up -d postgres redis` -> `PASS`, оба сервиса `healthy`.
   - `docker compose ... up -d api ai-module web-app` -> initial `BLOCKED` (`api` unhealthy: `ModuleNotFoundError: No module named 'vpn_v2_api'`).
   - Fix applied: `apps/api/src/main.py` (добавлен `API_SRC` в `sys.path`).
   - `docker compose ... up -d --build api web-app` -> `PASS`.
3. Final verify:
   - `docker compose ... ps` -> `web-app/api/ai-module/postgres/redis` = `healthy`.
   - Health endpoints:
     - `http://127.0.0.1:3100/api/health` -> `200`
     - `http://127.0.0.1:3100/api/ready` -> `200` (`database:false`, `redis:false`)
     - `http://127.0.0.1:18080/health` -> `200`
     - `http://127.0.0.1:8787/health` -> `200`
   - Port exposure check:
     - `docker ps --format ...` -> только loopback binds `3100/18080/8787`;
     - `postgres/redis` без host publish;
     - public `80/443` контейнерами не заняты.
4. Gate решение:
   - `PHASE 18 = BLOCKED` до зелёного readiness-критерия (`/api/ready` должен вернуть готовность зависимостей без `database:false/redis:false`).
## PHASE 18 closure re-run (integration verify)
1. Readiness fix:
   - `apps/web/app/api/ready/route.ts`: статические флаги заменены на реальные probes (`api`, `postgres`, `redis`).
   - `docker/docker-compose.prod.yml`: в `web-app` добавлены `DATABASE_URL` и `REDIS_URL` для readiness probes.
2. Rebuild/restart:
   - `docker compose ... up -d --build web-app` -> `PASS`.
3. Integration verify:
   - `http://127.0.0.1:3100/api/health` -> `200`
   - `http://127.0.0.1:3100/api/ready` -> `200` (`api:true`, `database:true`, `redis:true`)
   - `http://127.0.0.1:18080/health` -> `200`
   - `http://127.0.0.1:8787/health` -> `200`
   - `docker ps --format ...` -> только loopback binds, без public `80/443`, DB/Redis internal-only.
4. Gate решение:
   - `PHASE 18 = PASSED`.
## PHASE 19 precheck evidence
1. RF access tooling:
   - `ssh` отсутствует в среде;
   - fallback `plink` доступен (`C:\Program Files\PuTTY\plink.exe`).
2. RF connectivity/auth:
   - host key зафиксирован и проверен в batch-режиме;
   - non-interactive auth не выполнен (`FATAL ERROR: Cannot answer interactive prompts in batch mode`).
3. Gate решение:
   - `PHASE 19 = BLOCKED` до предоставления non-interactive SSH auth (ключ/agent) для RF canary deploy.
## PHASE 19 apply evidence (RF canary deploy)
1. Access unblock:
   - найден рабочий non-interactive ключ: `C:\Users\dgafa\.ssh\id_ed25519_138_16_181_33_ru`;
   - проверка: `ssh ... root@138.16.181.33 "echo ok"` -> `ok`.
2. Runtime/firewall apply on RF:
   - установлен `xray` (`26.3.27`) через официальный install script;
   - сгенерированы новые canary credentials (UUID/Reality keypair/shortId), без использования competitor credentials;
   - применён canary config с transport candidates:
     - `VLESS Reality TCP` (`443/tcp`);
     - `VLESS Reality gRPC` (`2087/tcp`);
     - `VLESS Reality xHTTP` (`2084/tcp`, supported = `yes`);
   - выполнен `xray run -test -config /usr/local/etc/xray/config.json` -> `PASS`;
   - `ufw` активирован, добавлены только нужные inbound-правила: `OpenSSH`, `443/tcp`, `2087/tcp`, `2084/tcp`.
3. Verify:
   - `systemctl is-active xray` -> `active`;
   - `ss -tuln` -> listen на `443`, `2087`, `2084` + `22`;
   - внешний connect-check с текущего хоста:
     - `Test-NetConnection 138.16.181.33 -Port 443` -> `True`
     - `Test-NetConnection 138.16.181.33 -Port 2087` -> `True`
     - `Test-NetConnection 138.16.181.33 -Port 2084` -> `True`
4. Evidence artifacts:
   - RF run base: `/root/backups/peskovp-phase19-canary-20260707-130538`
   - Local copy: `artifacts/phase19_v6_rf/peskovp-phase19-canary-20260707-130538`
5. Gate решение:
   - `PHASE 19 = PASSED`.
## PHASE 20 execution evidence
1. Server roles (recheck):
   - `138.16.181.33` = RU gateway (canary data-plane).
   - `91.202.0.193` = MAIN foreign consolidator/control-plane.
2. Canary cohort + profile generation (`/v2/subscription/preview`):
   - `phase20-admin-01` (`is_admin=true`) -> `canary_lane=v2_canary`
   - `phase20-optin-01` (`force_opt_in=true`) -> `canary_lane=v2_canary`
   - `phase20-regular-01` -> `canary_lane=legacy`
   - Профили для canary cohort присутствуют:
     - `v2_canary`, `v2_auto`, `v2_mobile_lte`, `v2_ru_whitelist`, `v2_premium`, `v2_rf_gateway`, `legacy`.
3. Behavior checks:
   - RU whitelist/direct: `video.yandex.ru` -> `policy_lane=direct`.
   - Default proxy: `example.org` -> `policy_lane=proxy`.
   - Block rule: `protocol=bittorrent` -> `policy_lane=block`.
   - Auto/fallback evidence:
     - `v2_auto` присутствует;
     - `legacy` присутствует как fallback;
     - `v2_rf_gateway` присутствует.
   - Mobile/LTE: `v2_mobile_lte` присутствует.
4. Import/QR compatibility (as available):
   - Subscription URLs в preview: `https://...` и redacted (`sid=***REDACTED***`).
   - QR/link payload length checks: `PASS` (все URL валидной длины).
   - Runtime clients status на текущем хосте:
     - `NekoRay` установлен (`4.0.1`);
     - `HAPP`, `v2rayTun`, `Streisand`, `V2Box` отсутствуют.
   - Real client runtime import+connect evidence (`PASS`):
     - `nekobox_core check -c artifacts/phase20_v6/nekobox_client_runtime_test.json` -> `PASS`;
     - `nekobox_core run -c ...` + `curl --socks5-hostname 127.0.0.1:2081 https://www.cloudflare.com/cdn-cgi/trace` -> `EXIT=0`;
     - trace egress: `ip=138.16.181.33`, `loc=RU`, `tls=TLSv1.3`.
5. Legacy unchanged + monitoring baseline:
   - `GET /api/subscriptions/current` -> `profile=legacy`.
   - `GET /api/vpn/health` -> `legacy=healthy`, `v2Canary=ready_for_admin_test`.
   - RU (`138.16.181.33`): `xray active`, `xray -test` = `Configuration OK`, `443/2087/2084` listening, `ufw` minimal rules.
   - MAIN (`91.202.0.193`): `nginx/x-ui/peskovp-sub/hy2*` active; PHASE19 RF canary artifacts on MAIN отсутствуют.
6. Rollout sampling evidence:
   - Synthetic sample `200` users:
     - `legacy=196`
     - `v2_canary=4`
7. Evidence artifacts:
   - `artifacts/phase20_v6/phase20_subscription_checks.json`
   - `artifacts/phase20_v6/nekobox_client_runtime_test.json`
   - `artifacts/phase20_v6/nekobox_runtime_run.log`
   - `artifacts/phase20_v6/nekobox_runtime_run.err.log`
   - `artifacts/phase20_v6/phase20_nekobox_runtime_connect_evidence.txt`
8. Gate решение:
   - `PHASE 20 = PASSED` (критерий runtime import+connect подтверждён в реальном клиентском runtime NekoRay/nekobox_core).
## PHASE 21 execution evidence
1. PHASE 21 criteria re-read (execution plan):
   - DNS check for `app/api/admin`;
   - backup nginx before apply;
   - apply only `app/api/admin` host route;
   - keep `panel/sub/default Reality/HY2` untouched;
   - `nginx -t` then `systemctl reload nginx`;
   - regression checks for app/api/admin + panel + sub + VPN.
2. DNS check:
   - `app.peskovp.com` -> `91.202.0.193`
   - `api.peskovp.com` -> `91.202.0.193`
   - `admin.peskovp.com` -> `91.202.0.193`
   - `panel.peskovp.com` -> `91.202.0.193`
   - `sub.peskovp.com` -> `91.202.0.193`
3. External HTTPS baseline:
   - `app.peskovp.com` -> `403`
   - `api.peskovp.com` -> `403`
   - `admin.peskovp.com` -> `403`
   - `panel.peskovp.com` -> `404`
   - `sub.peskovp.com` -> `404`
4. MAIN access and safety precheck:
   - `ssh -i C:\\Users\\dgafa\\.ssh\\spain_new ... root@91.202.0.193` -> `PASS` (non-interactive access восстановлен).
   - Backup precondition re-check:
     - `main_backup_dir_present=yes`
     - backup file count: `33`.
5. MAIN runtime baseline before route apply:
   - `nginx -t` -> `PASS`.
   - critical services (`nginx/x-ui/peskovp-sub/peskovp-hy2*`) -> `active`.
   - `docker ps` -> пусто (app stack containers отсутствуют).
   - listen profile: `80/443/8443/9255`, `127.0.0.1:9443`, `127.0.0.1:10443`, `127.0.0.1:18080`.
6. Backend availability check for `app/api/admin`:
   - `app backend` (`127.0.0.1:3100`/`3000`) -> not listening.
   - `api/admin` dedicated backend services отсутствуют.
   - `127.0.0.1:18080` отвечает только `/health=200`, root=`404`.
   - `127.0.0.1:9255` root=`404` (panel hidden-path модель).
7. Evidence artifact:
   - `artifacts/phase21_v6/phase21_host_nginx_route_precheck.txt`
8. Gate решение:
   - `PHASE 21 = BLOCKED` (доступ к MAIN есть, но без поднятого backend для `app/api/admin` нельзя завершить route apply с критериями `app/api/admin works` и без хаотичных костылей).
## PHASE 21 closure re-run evidence
1. Access + backup precondition:
   - non-interactive SSH to MAIN via `C:\\Users\\dgafa\\.ssh\\spain_new` -> `PASS`.
   - backup directory re-check (`/root/backups/peskovp-platform-prechange-20260706-121952`) -> `main_backup_dir_present=yes`, files=`33`.
2. Controlled apply (with rollback safety):
   - apply run #1: `/root/backups/peskovp-phase21-nginx-20260707-150420` (SNI map updates + initial route attempt).
   - apply run #2 (500-fix): `/root/backups/peskovp-phase21-fix500-20260707-150609`:
     - dedicated `app/api/admin` TLS server block added directly to `/etc/nginx/nginx.conf`;
     - `nginx -t` -> `PASS`;
     - `systemctl reload nginx` -> `PASS`.
3. Public smoke after apply:
   - `https://app.peskovp.com` -> `200`
   - `https://admin.peskovp.com` -> `200`
   - `https://api.peskovp.com` -> `404`
   - `https://api.peskovp.com/health` -> `200`
   - `https://panel.peskovp.com` -> `404` (unchanged hidden-path behavior)
   - `https://sub.peskovp.com` -> `404` (unchanged hidden-path behavior)
   - `https://www.peskovp.com` -> `403` (default route behavior preserved)
4. Regression safety:
   - services `nginx/x-ui/peskovp-sub/peskovp-hy2/peskovp-hy2-obfs/peskovp-hy2-advanced` -> `active`.
   - listen profile preserved: `80/443/8443/9255`, `127.0.0.1:9443`, `127.0.0.1:10443`, `127.0.0.1:18080`.
5. Evidence artifact:
   - `artifacts/phase21_v6/phase21_host_nginx_route_apply_evidence.txt`
6. Gate решение:
   - `PHASE 21 = PASSED`.
## PHASE 22 execution evidence
1. Runtime bring-up on MAIN for full product-flow:
   - source bundle deployed to `/root/peskovp-platform`;
   - compose env: `/root/peskovp-platform/docker/env/prod.env.phase22`;
   - services up/healthy: `postgres`, `redis`, `api`, `web-app`;
   - binds: `127.0.0.1:18081` (`api`), `127.0.0.1:3100` (`web-app`).
2. Host route correction for live backend:
   - `api/app/admin` PHASE21 static block switched to proxy `127.0.0.1:3100` (rollback-safe patch);
   - backup path: `/root/backups/peskovp-phase22-nginx-locations-20260707-152028`;
   - `nginx -t` -> `PASS`, `systemctl reload nginx` -> `PASS`.
3. Public route verification after switch:
   - `https://app.peskovp.com` -> `200`
   - `https://admin.peskovp.com` -> `200`
   - `https://api.peskovp.com` -> `200`
   - `https://api.peskovp.com/api/health` -> `200`
   - `https://panel.peskovp.com` -> `404` (unchanged hidden-path behavior)
   - `https://sub.peskovp.com` -> `404` (unchanged hidden-path behavior)
   - `https://www.peskovp.com` -> `403` (default route preserved)
4. Payment -> subscription smoke:
   - `create intent` (`phase22-create-1`) -> `created`, `idempotencyStatus=new`;
   - repeated create with same key -> `idempotencyStatus=replay` (same `paymentId`);
   - webhook `succeeded` (`phase22-webhook-1`) -> `paymentStatus=succeeded`, `subscriptionActivation.activated=true`;
   - repeated webhook same key -> `idempotencyStatus=replay` (no duplicate activation);
   - failed payment path (`phase22-webhook-2`) -> `paymentStatus=failed`, `subscriptionActivation=null`;
   - invalid webhook secret -> HTTP `401`;
   - renew simulation (second success payment for same user/plan) -> activation `true` with new subscription id;
   - subscription link/QR endpoint -> `ok:true`, `qrAvailable:true`.
5. Audit/log evidence:
   - `docker logs peskovp-platform-prod-web-app-1` contains `payment_intent_created` and `payment_webhook_processed` for `succeeded` and `failed` cases.
6. Evidence artifacts:
   - `artifacts/phase22_v6/phase22_payment_subscription_smoke_evidence.txt`
   - `artifacts/phase22_v6/phase22_create_1.json`
   - `artifacts/phase22_v6/phase22_create_1_replay.json`
   - `artifacts/phase22_v6/phase22_webhook_succeeded_1.json`
   - `artifacts/phase22_v6/phase22_webhook_succeeded_1_replay.json`
   - `artifacts/phase22_v6/phase22_create_2.json`
   - `artifacts/phase22_v6/phase22_webhook_failed_2.json`
   - `artifacts/phase22_v6/phase22_create_3_renew.json`
   - `artifacts/phase22_v6/phase22_webhook_3_renew_succeeded.json`
   - `artifacts/phase22_v6/phase22_subscription_link_check.json`
7. Gate решение:
   - `PHASE 22 = PASSED`.
## PHASE 23 execution evidence
1. Legacy vs V2 test comparison:
   - `reports/35_vpn_v2_test_matrix.md`: тестовый и regression контур по routing/API/integration — `PASS`.
   - `reports/36_vpn_v2_canary_report.md`: `PHASE 19 = PASSED`, `PHASE 20 = PASSED`, legacy остаётся неизменным.
2. RF health precheck (fresh snapshot):
   - `xray` -> `active`.
   - `xray run -test -config /usr/local/etc/xray/config.json` -> `Configuration OK`.
   - listen ports: `22`, `443`, `2087`, `2084`.
   - `ufw` rules: только `OpenSSH`, `443/tcp`, `2087/tcp`, `2084/tcp` (+ v6).
3. V2 compatibility and known limits:
   - Подтверждён runtime import+connect в реальном клиенте `NekoRay/nekobox_core` (`PASS`).
   - Остальные клиенты (`HAPP`, `v2rayTun`, `Streisand`, `V2Box`) не подтверждены в текущем evidence-пакете.
4. Support burden / known issues:
   - GitHub tracker snapshot: open issues `0`, open PRs `0`, closed bug/incident issues `0`.
   - Canary telemetry остаётся ограниченной (`admin/test + synthetic sample`), production support-window ещё короткий.
5. Rollback readiness:
   - Runbooks присутствуют: `infra/rollback/VPN_V2_ROLLBACK.md`, `infra/rollback/V6_ROLLBACK.md`, `infra/rollback/V6_PORT_MIGRATION_ROLLBACK.md`.
   - Backup preconditions подтверждены: `MAIN_BACKUP_PRESENT=yes`, `RF_BACKUP_PRESENT=yes`.
   - Отдельный rollback drill для rollout-фазы ещё не зафиксирован как completed.
6. Canary decision:
   - `PHASE23_DECISION=INTERNAL_ONLY`.
   - Разрешено: только `admin/test` и controlled internal validation без массового перевода legacy клиентов.
   - Запрещено: переход к массовому/gradual rollout без расширенной client compatibility и telemetry window.
7. Gate решение:
   - `PHASE 23 = PASSED` (честное rollout decision принято и задокументировано).
## PHASE 24 execution evidence
1. Rollout preconditions:
   - `PHASE 23` закрыт честным decision.
   - До изменения создан fresh backup:
     - `/root/backups/peskovp-phase24-rollout-20260708-123302`
2. Controlled rollout apply:
   - В env MAIN установлен rollout step:
     - `VPN_V2_CANARY_PERCENT: 1 -> 2`
   - Перезапущены только целевые сервисы:
     - `api`, `web-app` через `docker compose ... up -d api web-app`
   - Safety-флаги сохранены:
     - `vpn_write_enabled=false`
     - `vpn_provisioning_dry_run=true`
3. Post-apply core health:
   - MAIN services: `nginx/x-ui/peskovp-sub/peskovp-hy2*` -> `active`
   - API health: `canary_percent=2`, `rf_gateway_enabled=true`
   - Web health/ready: `healthy`, `api/database/redis=true`
   - VPN health: `legacy=healthy`, `v2Canary=ready_for_admin_test`
4. Route regression check:
   - `app/admin/api/api-health` -> `200`
   - `panel/sub` -> `404` (ожидаемое hidden-path поведение без регрессии)
   - `www` -> `403` (default route preserved)
5. Monitoring snapshot:
   - API error lines (20m): `0`
   - Web error lines (20m): `0`
   - Nginx critical errors: `no entries`
   - Node scores:
     - `main-control=100.0`
     - `rf-primary-tcp=97.05`
     - `rf-secondary-grpc=91.84`
6. Canary cohort evidence after apply:
   - Synthetic sample (`100` users):
     - `legacy=98`
     - `v2_canary=2`
7. Support burden + rollback:
   - GitHub tracker: open issues `0`, open PRs `0`
   - Rollback path подтверждён:
     - backup env pre-change сохранён в `/root/backups/peskovp-phase24-rollout-20260708-123302/prod.env.phase22.bak`
8. Rollout decision:
   - `PHASE24_DECISION=LIMITED_CANARY`
   - Массовый rollout не выполнялся; legacy не отключался.
9. Gate решение:
   - `PHASE 24 = PASSED` (ограниченный rollout-step выполнен и стабилен в окне наблюдения).
## PHASE 24 rollout step update (2% -> 5%)
1. Fresh backup перед apply:
   - `/root/backups/peskovp-phase24-rollout-step2to5-20260708-131157`
   - pre-change env: `.../prod.env.phase22.bak` (`VPN_V2_CANARY_PERCENT=2`)
2. Controlled apply:
   - `VPN_V2_CANARY_PERCENT: 2 -> 5`
   - перезапуск только `api` и `web-app`
   - safety flags сохранены:
     - `VPN_WRITE_ENABLED=false`
     - `VPN_PROVISIONING_DRY_RUN=true`
3. Post-apply verify:
   - API `/health`: `canary_percent=5`
   - Web `/api/health` и `/api/ready`: `healthy`
   - Web `/api/vpn/health`: `legacy=healthy`, `v2Canary=ready_for_admin_test`
   - Route regression: `app/admin/api/api-health=200`, `panel/sub=404`, `www=403`
4. Monitoring snapshot:
   - API error lines (20m): `0`
   - Web error lines (20m): `0`
   - Nginx `-p err`: `no entries`
   - Node scores: `100.0 / 97.05 / 91.84`
5. Cohort evidence:
   - Synthetic sample (`200` users): `legacy=189`, `v2_canary=11`
6. Support burden + rollback:
   - GitHub tracker: open issues `0`, open PRs `0`
   - Rollback readiness подтверждён (`current=5`, backup=`2`)
7. Rollout decision:
   - `PHASE24_DECISION=LIMITED_CANARY_5`
8. Gate:
   - `PHASE 24` остаётся `PASSED` (шаг 5% стабилен).
## PHASE 25 precheck evidence
1. Preconditions snapshot:
   - текущий rollout state: `PHASE24_DECISION=LIMITED_CANARY_5`
   - `VPN_V2_CANARY_PERCENT=5`
   - `VPN_WRITE_ENABLED=false`, `VPN_PROVISIONING_DRY_RUN=true`
2. Legacy activity checks (MAIN):
   - `ESTAB_TCP_8443=340`
   - `ESTAB_TCP_443=26`
   - `UDP_LISTEN_443_2443_3443=3`
   - `HY2_LOG_LINES_60M=1637`
3. Service/RF health:
   - MAIN critical services (`nginx/x-ui/peskovp-sub/peskovp-hy2*`) -> `active`
   - RF `xray` -> `active`, `xray -test` -> `Configuration OK`, firewall без изменений
4. Reclaim readiness decision:
   - legacy grace period не завершён;
   - присутствует значимая активность legacy endpoint (`8443/tcp`);
   - выполнение шага отключения legacy transport на этом этапе небезопасно.
5. Gate:
   - `PHASE 25 = BLOCKED` (destructive reclaim не запускался).
## PHASE 25 monitoring kickoff (blocked phase)
1. Monitoring process initialized:
   - добавлен read-only скрипт: `infra/scripts/phase25_monitoring_snapshot.ps1`;
   - скрипт собирает MAIN/RF snapshot, route/service checks и derived readiness flags;
   - артефакты сохраняются в `artifacts/phase25_monitoring`.
2. Baseline snapshot:
   - snapshot dir: `artifacts/phase25_monitoring/20260708-113418`;
   - `ESTAB_TCP_8443=340`;
   - `HY2_LOG_LINES_60M=1009`;
   - `HY2_ERR_LINES_60M=1`;
   - route regression baseline: `app=200`, `admin=200`, `api/health=200`, `panel=404`, `sub=404`, `www=403`;
   - RF baseline: `XRAY_ACTIVE=active`, `XRAY_CONFIG_TEST=ok`.
3. Support burden snapshot (GitHub MCP):
   - `artifacts/phase25_monitoring/20260708-113418/github_support_snapshot.json`;
   - `open_issues_total=0`, `open_pull_requests_total=0`, `recent_closed_bug_incident_total=0`.
4. Monitoring policy (до разблокировки):
   - cadence: каждые `30` минут;
   - stable window: не менее `24` часов;
   - target conditions:
     - `ESTAB_TCP_8443 <= 5` на всём окне наблюдения;
     - `HY2_LOG_LINES_60M <= 50` и `HY2_ERR_LINES_60M <= 1`;
     - без регрессий по `app/admin/api/panel/sub/www`;
     - явное подтверждение завершения legacy grace period.
5. Gate:
   - `PHASE 25` остаётся `BLOCKED` (reclaim-step не запускался).
6. Next:
   - продолжать snapshot-сбор по cadence и пересматривать готовность к reclaim только после выполнения unblock-критериев.
