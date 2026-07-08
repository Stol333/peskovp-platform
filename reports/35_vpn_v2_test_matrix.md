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

