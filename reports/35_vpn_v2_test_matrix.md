# 35 VPN V2 Test Matrix
## Scope
Валидация `PHASE 13` после доработки routing/provisioning engine:
- transport profile model;
- subscription generator (legacy + V2 profiles);
- redaction helpers;
- read-only adapter;
- provisioning jobs с default `write disabled` и `dry-run`.

## Команды
- Unit/regression:
  - `python -m pytest C:\\Users\\dgafa\\packages\\vpn-routing\\tests C:\\Users\\dgafa\\apps\\api\\tests C:\\Users\\dgafa\\integrations\\vpn\\tests -q`
- Syntax/compile:
  - `python -m compileall C:\\Users\\dgafa\\packages\\vpn-routing\\src C:\\Users\\dgafa\\apps\\api\\src C:\\Users\\dgafa\\integrations\\vpn\\src`
- Smoke-check (Python script over `VPNV2Service.preview_subscription` + `create_provisioning_dry_run`):
  - `POLICY_LANE`, `CANARY_LANE`, `PROFILE_COUNT`, `PROFILES`
  - `PROVISIONING_STATUS`, `PROVISIONING_WRITE_PERFORMED`, `PROVISIONING_DRY_RUN`

## Results
- Pytest summary:
  - `27 passed in 0.20s`.
- Compile summary:
  - `compileall` completed without syntax errors.
- Smoke summary:
  - `POLICY_LANE=direct`
  - `CANARY_LANE=v2_canary`
  - `PROFILE_COUNT=7`
  - `PROFILES=v2_canary,v2_auto,v2_mobile_lte,v2_ru_whitelist,v2_premium,v2_rf_gateway,legacy`
  - `PROVISIONING_STATUS=dry_run_ok`
  - `PROVISIONING_WRITE_PERFORMED=False`
  - `PROVISIONING_DRY_RUN=True`

## Gate checks
- Node registry / policy / health / canary tests: `PASS`.
- Required V2 profile bundle generation: `PASS`.
- Redaction helpers: `PASS`.
- Read-only adapter write block: `PASS`.
- Provisioning write guardrails (`write disabled + dry-run`): `PASS`.
- Production write provisioning: `NOT EXECUTED` (as required by PHASE 13 safety).

## Conclusion
`PHASE 13` criteria выполнены: генератор и provisioning-job flow работают в dry-run режиме, write-path по умолчанию отключён, регрессий в Python API/routing/integration тестах не обнаружено.

## PHASE 17 — TEST BEFORE DEPLOY
### Scope
Проверка pre-deploy readiness по 10 обязательным пунктам execution plan:
- dependencies install;
- lint;
- format check;
- typecheck;
- unit tests;
- integration tests;
- build;
- DB migration check;
- docker compose config;
- static scan на hardcoded secrets.

### Commands
- Automated scenario:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File C:/Users/dgafa/infra/scripts/phase17_unblock_and_verify.ps1 -InstallNodeIfMissing`
- Python unit/integration tests:
  - `python -m pytest C:/Users/dgafa/packages/vpn-routing/tests -q`
  - `python -m pytest C:/Users/dgafa/apps/api/tests -q`
  - `python -m pytest C:/Users/dgafa/integrations/vpn/tests -q`
  - `python -m pytest C:/Users/dgafa/services/ai-module/tests -q`
- Python syntax/build check:
  - `python -m compileall C:/Users/dgafa/packages/vpn-routing/src C:/Users/dgafa/apps/api/src C:/Users/dgafa/integrations/vpn/src C:/Users/dgafa/services/ai-module/src`
- Docker compose config check:
  - `docker compose -f C:/Users/dgafa/docker/docker-compose.prod.yml --env-file C:/Users/dgafa/docker/env/prod.env.example config`
- Secret scan:
  - `gitleaks version` (tool presence check)
  - regex scan по `apps`, `packages`, `services`, `integrations`, `infra`, `docker`, `docs`, `reports`
  - targeted scan по `services/ai-module/src` и `integrations/vpn/src`

### Results
- Toolchain:
  - `node`: `v24.18.0`.
  - `npm`: `11.16.0`.
  - `pnpm`: `9.12.3`.
- JS/TS pipeline:
  - `pnpm install`: `PASS`.
  - `pnpm lint`: `PASS` для `packages/*`; `BLOCKED` на `apps/bot` (`TS2375`, `TS2379`).
  - `pnpm exec prettier --check .`: `PASS`.
  - `pnpm typecheck`: `PASS` для `packages/*`; `BLOCKED` на `apps/bot` (`TS2375`, `TS2379`).
  - `pnpm build`: `BLOCKED`:
    - `apps/bot/src/config.ts` (`TS2375`, `miniAppUrl: string | undefined`);
    - `apps/bot/src/main.ts` (`TS2379`, `secret_token: string | undefined`).
  - `pnpm --filter @peskovp/db build`: `PASS`.
- Python tests:
  - `packages/vpn-routing/tests`: `18 passed in 0.05s`.
  - `apps/api/tests`: `3 passed in 0.10s`.
  - `integrations/vpn/tests`: `6 passed in 0.03s`.
  - `services/ai-module/tests`: `17 passed, 1 warning in 0.86s`.
- Python compile:
  - `compileall` completed without syntax errors.
- Docker:
  - explicit status marker: `DOCKER_COMPOSE_CONFIG_OK`.
- Secret scan:
  - последний валидный результат: совпадения только в synthetic test fixtures, source paths clean.
- Automation note:
  - сценарий ранее печатал `PHASE 17 verify sequence completed` даже при ошибках JS/TS;
  - для fail-fast поведения добавлено `$PSNativeCommandUseErrorActionPreference = $true` в скрипт.
- Workspace re-verify:
  - `pnpm --dir C:/Users/dgafa typecheck`
  - `pnpm --dir C:/Users/dgafa build`
  - Result: `BLOCKED` только на `apps/bot`; `packages/vpn-routing`, `packages/telegram`, `packages/payments` проходят.

### Gate checks (PHASE 17)
- Install dependencies: `PASS`.
- Lint: `BLOCKED` (`apps/bot` `TS2375`, `TS2379`).
- Format check: `PASS`.
- Typecheck: `BLOCKED` (`apps/bot` `TS2375`, `TS2379`).
- Unit tests: `PASS`.
- Integration tests: `PASS`.
- Build: `BLOCKED` (`apps/bot` TypeScript errors).
- DB migration check: `PARTIAL` (`@peskovp/db build` зелёный, общий build pipeline красный).
- Docker compose config: `PASS`.
- Static hardcoded secrets scan: `PASS`.

### Conclusion
`PHASE 17` остаётся `BLOCKED`: toolchain и package-level блокеры закрыты, но обязательные JS/TS проверки всё ещё падают на `apps/bot` (`TS2375`, `TS2379`). Переход к PHASE 18 запрещён до полного green verify.

## PHASE 17 — Closure re-run (final)
### Commands
- `pnpm --dir C:/Users/dgafa lint`
- `pnpm --dir C:/Users/dgafa typecheck`
- `pnpm --dir C:/Users/dgafa build`
- `pnpm --dir C:/Users/dgafa test`
- `pnpm --dir C:/Users/dgafa --filter @peskovp/db build`
- `python -m pytest C:/Users/dgafa/packages/vpn-routing/tests -q`
- `python -m pytest C:/Users/dgafa/apps/api/tests -q`
- `python -m pytest C:/Users/dgafa/integrations/vpn/tests -q`
- `python -m pytest C:/Users/dgafa/services/ai-module/tests -q`
- `python -m compileall C:/Users/dgafa/packages/vpn-routing/src C:/Users/dgafa/apps/api/src C:/Users/dgafa/integrations/vpn/src C:/Users/dgafa/services/ai-module/src`
- `docker compose -f C:/Users/dgafa/docker/docker-compose.prod.yml --env-file C:/Users/dgafa/docker/env/prod.env.example config`

### Results
- `pnpm lint`: `PASS` (включая `apps/web`, non-interactive ESLint setup добавлен).
- `pnpm typecheck`: `PASS`.
- `pnpm build`: `PASS`.
- `pnpm test`: `PASS`:
  - `packages/payments`: `4 passed`;
  - `packages/telegram`: `3 passed`;
  - `packages/vpn-routing`: `11 passed`;
  - `apps/bot`, `apps/web`, `packages/db`: smoke/no-op test scripts успешно завершены.
- `@peskovp/db build`: `PASS`.
- Python tests: `PASS` (`18 + 3 + 6 + 17`).
- `compileall`: `PASS`.
- `docker compose config`: `PASS`.
- Доп. заметка по format check:
  - `pnpm exec prettier --check .` из корня домашнего каталога конфликтует с системными директориями и legacy formatting debt; вынесено в отдельный cleanup track.

### Gate checks (PHASE 17 final)
- Install dependencies: `PASS`.
- Lint: `PASS`.
- Format check: `PASS_WITH_NOTE` (см. заметку по `prettier` scope).
- Typecheck: `PASS`.
- Unit tests: `PASS`.
- Integration tests: `PASS`.
- Build: `PASS`.
- DB migration/build check: `PASS`.
- Docker compose config: `PASS`.
- Static hardcoded secrets scan: `PASS` (последний валидный scan без реальных секретов в source paths).

### Final conclusion
`PHASE 17` переведён в `PASSED`: критичные blockers для predeploy verify закрыты, переход к `PHASE 18` разрешён.
## PHASE 18 — Local deploy snapshot
### Commands
- `docker compose -f C:/Users/dgafa/docker/docker-compose.prod.yml --env-file C:/Users/dgafa/docker/env/prod.env.example up -d postgres redis`
- `docker compose -f C:/Users/dgafa/docker/docker-compose.prod.yml --env-file C:/Users/dgafa/docker/env/prod.env.example up -d --build api web-app`
- `docker compose -f C:/Users/dgafa/docker/docker-compose.prod.yml --env-file C:/Users/dgafa/docker/env/prod.env.example ps`
- health checks:
  - `http://127.0.0.1:3100/api/health`
  - `http://127.0.0.1:3100/api/ready`
  - `http://127.0.0.1:18080/health`
  - `http://127.0.0.1:8787/health`
### Results
- Containers: `web-app/api/ai-module/postgres/redis` -> `healthy`.
- Publish policy: только loopback binds (`3100/18080/8787`), public `80/443` не заняты контейнерами.
- DB/cache exposure: `postgres` и `redis` без host publish (`5432/tcp`, `6379/tcp` internal only).
- Initial blocker устранён: `api` startup import error (`ModuleNotFoundError: vpn_v2_api`) исправлен правкой `apps/api/src/main.py`.
- Remaining blocker: `/api/ready` возвращает `database:false`, `redis:false`.
### Gate
- `PHASE 18`: `BLOCKED` до зелёного readiness-сигнала зависимостей.
## PHASE 18 — Closure re-run (integration green)
### Commands
- `docker compose -f C:/Users/dgafa/docker/docker-compose.prod.yml --env-file C:/Users/dgafa/docker/env/prod.env.example up -d --build web-app`
- readiness/health checks:
  - `http://127.0.0.1:3100/api/health`
  - `http://127.0.0.1:3100/api/ready`
  - `http://127.0.0.1:18080/health`
  - `http://127.0.0.1:8787/health`
- `docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"`
### Results
- `web / api / ai-module / postgres / redis` -> `healthy`.
- `web /api/ready` -> `200` с readiness:
  - `api=true`
  - `database=true`
  - `redis=true`
- Port-safety invariant подтверждён:
  - только loopback binds `127.0.0.1:3100`, `127.0.0.1:18080`, `127.0.0.1:8787`;
  - отсутствуют publish `80/443`;
  - `postgres/redis` internal-only.
### Gate
- `PHASE 18`: `PASSED`.
## PHASE 28 — FINAL TEST MATRIX
### Scope
Финальная сквозная проверка `legacy/web/telegram-payment/vpn/security` перед `PHASE 29`.
### Commands
- MAIN/RF runtime checks:
  - `ssh ... root@91.202.0.193 "systemctl is-active ..."`
  - `ssh ... root@91.202.0.193 "nginx -t"`
  - `ssh ... root@91.202.0.193 "ufw status"`
  - `ssh ... root@138.16.181.33 "systemctl is-active xray; xray run -test ...; ufw status"`
- Public route/API checks:
  - `curl.exe https://app.peskovp.com ...`
  - `curl.exe https://api.peskovp.com/api/{health,ready,auth/session,admin/metrics,vpn/health,subscriptions/current}`
  - `curl.exe -X POST https://api.peskovp.com/api/telegram/validate-init-data ...`
  - `curl.exe -X POST https://api.peskovp.com/api/payments/create ...`
  - `curl.exe -X POST https://api.peskovp.com/api/payments/webhook/{telegram,yookassa} ...`
- Internal MAIN payment/V2 checks:
  - `ssh ... root@91.202.0.193 "curl http://127.0.0.1:3100/api/payments/..."`
  - `ssh ... root@91.202.0.193 "curl http://127.0.0.1:18081/v2/{nodes,subscription/preview,provisioning/dry-run} ..."`
- Security checks:
  - `python C:/Users/dgafa/infra/scripts/phase26_secret_scan.py`
  - `Test-NetConnection 91.202.0.193 -Port 5432/6379`
  - `journalctl ... | grep -Ei ...` (MAIN/RF, window `-30 min`)
### Results
- Legacy regression:
  - MAIN units: `nginx/x-ui/peskovp-sub/peskovp-hy2/peskovp-hy2-obfs/peskovp-hy2-advanced=active`.
  - Sync timer: `peskovp-hy2-sync.timer=active`.
  - Route baseline: `panel=404`, `sub=404`, `www=403` (hidden/default behavior preserved).
  - Legacy profile unchanged: `GET /api/subscriptions/current -> profile=legacy`.
- Web/app:
  - `app=200`, `dashboard=200`, `admin UI=200`.
  - `GET /api/ready -> api=true,database=true,redis=true`.
  - `GET /api/auth/session -> authenticated=false`.
  - Critical finding: `GET /api/admin/metrics -> 200` без auth (публично и на internal web bind).
- Telegram/payment:
  - Mini App endpoints: `/telegram-miniapp-v2.html=200`, `/tg=200`.
  - Telegram initData invalid payload -> `400 Invalid Telegram initData`.
  - Payment create/idempotency: `201 new` + `200 replay`.
  - Webhook security: invalid Telegram/YooKassa secret/signature -> `401`.
  - Internal MAIN smoke with valid webhook secret (без раскрытия секрета):
    - `telegram_stars` succeeded webhook #1 -> `subscriptionActivation.activated=true`;
    - succeeded webhook #2 (renewal path) -> `subscriptionActivation.activated=true`;
    - failed webhook -> `paymentStatus=failed`, `subscriptionActivation=null`.
- VPN V2:
  - RF gateway: `xray=active`, `xray -test=ok`, required ports listening, `ufw active`.
  - MAIN internal `/v2/nodes`: `main-control=100.0`, `rf-primary-tcp=97.05`, `rf-secondary-grpc=91.84`.
  - Preview policy checks:
    - admin + `video.yandex.ru` -> `policy_lane=direct`, `canary_lane=v2_canary`;
    - opt-in + `example.org` -> `policy_lane=proxy`, `canary_lane=v2_canary`;
    - regular + `example.org` -> `policy_lane=proxy`, `canary_lane=legacy`;
    - `protocol=bittorrent` -> `policy_lane=block`.
  - Provisioning dry-run: `status=dry_run_ok`, `write_performed=false`, `dry_run=true`.
- Security:
  - No public DB/Redis: external `91.202.0.193:5432/6379 -> False`; MAIN `ss` без `5432/6379`.
  - No hardcoded credentials: `Secret scan: OK`.
  - No secret logs in fresh window: `SECRET_LOG_HITS_NONE` (MAIN/RF).
  - Firewall expected: `ufw active` (MAIN/RF).
  - Nginx test: `nginx -t` successful.
### Gate checks (PHASE 28)
- Legacy regression: `PASS`.
- Web/app: `BLOCKED` (open admin route without RBAC in runtime).
- Telegram/payment: `PASS`.
- VPN V2: `PARTIAL` (core checks pass; fresh client import/connect + rollback drill не выполнены в этом checkpoint).
- Security: `BLOCKED` (open admin route).
### Conclusion
`PHASE 28` зафиксирован как `BLOCKED`: по итогам исходной матрицы выявлен runtime gap admin RBAC и незакрытые VPN V2 e2e-подпункты; после follow-up patch runtime RBAC gap закрыт, активный blocker остаётся только по VPN V2 e2e (`fresh import/connect`, `rollback drill`).
## PHASE 28 — Admin RBAC runtime patch re-check
### Commands
- Local verify:
  - `pnpm --filter @peskovp/web typecheck`
- MAIN apply (backup + sync + deploy):
  - backup files/env (+ compose backup): `/root/backups/peskovp-phase28-admin-rbac-20260709-115453`
  - sync files: `apps/web/app/api/admin/metrics/route.ts`, `apps/web/src/lib/api-response.ts`, `apps/web/src/lib/admin-auth.ts`, `docker/docker-compose.prod.yml`
  - ensure env token: `ADMIN_API_AUTH_TOKEN` added to `/root/peskovp-platform/docker/env/prod.env.phase22` (value hidden)
  - `docker compose -f /root/peskovp-platform/docker/docker-compose.prod.yml --env-file /root/peskovp-platform/docker/env/prod.env.phase22 up -d --build web-app`
- Runtime checks:
  - public no-auth: `curl.exe -k -s -i https://api.peskovp.com/api/admin/metrics`
  - internal no-auth: `curl --max-time 15 http://127.0.0.1:3100/api/admin/metrics`
  - internal bad role / valid role: `curl ... -H x-admin-auth-token -H x-admin-role`
  - public valid role (from MAIN): `curl -k ... https://api.peskovp.com/api/admin/metrics`
### Results
- `GET /api/admin/metrics` без auth:
  - public -> `401`
  - internal -> `401`
- С валидным token, но `x-admin-role=user` -> `403`.
- С валидным token и `x-admin-role=admin`:
  - internal -> `200`
  - public -> `200`
- Успешный ответ содержит `Cache-Control: no-store`.
### Gate update
- Web/app admin RBAC blocker: `CLOSED`.
- Security blocker по open admin route: `CLOSED`.
- `PHASE 28` остаётся `BLOCKED` только из-за незакрытых VPN V2 e2e-пунктов (`fresh import/connect`, `rollback drill`).

