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
- JS/toolchain and predeploy checks:
  - `node --version; npm --version; pnpm --version; pnpm install; pnpm lint; pnpm exec prettier --check .; pnpm typecheck; pnpm build; pnpm --filter @peskovp/db build`
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
  - `node`: not recognized.
  - `npm`: not recognized.
  - `pnpm`: not recognized.
- Python tests:
  - `packages/vpn-routing/tests`: `18 passed in 0.10s`.
  - `apps/api/tests`: `3 passed in 0.13s`.
  - `integrations/vpn/tests`: `6 passed in 0.05s`.
  - `services/ai-module/tests`: `17 passed, 1 warning in 1.28s`.
- Python compile:
  - `compileall` completed without syntax errors.
- Docker:
  - explicit status marker: `DOCKER_COMPOSE_CONFIG_OK`.
- Secret scan:
  - `gitleaks` отсутствует в окружении.
  - Regex match найден только в тестовых фикстурах:
    - `services/ai-module/tests/test_main_auth_api.py`
    - `services/ai-module/tests/test_service_phase14.py`
    - `services/ai-module/tests/test_log_summarizer.py`
    - `services/ai-module/tests/test_redaction.py`
    - `integrations/vpn/tests/test_provider.py`
  - В source (`services/ai-module/src`, `integrations/vpn/src`) совпадений не найдено.

### Gate checks (PHASE 17)
- Install dependencies: `BLOCKED` (нет `pnpm`).
- Lint: `BLOCKED` (нет `pnpm`).
- Format check: `BLOCKED` (нет `pnpm`).
- Typecheck: `BLOCKED` (нет `pnpm`).
- Unit tests: `PASS`.
- Integration tests: `PASS`.
- Build: `BLOCKED` для JS/TS контура (`pnpm` отсутствует), `PASS` для Python compile.
- DB migration check: `BLOCKED` (невозможно выполнить пакетный DB-check без `pnpm`).
- Docker compose config: `PASS`.
- Static hardcoded secrets scan: `PASS` для source-кода (совпадения только в synthetic test fixtures).

### Conclusion
`PHASE 17` зафиксирован как `BLOCKED`: критичный blocker — отсутствие `node/npm/pnpm`, что блокирует обязательные JS/TS проверки и DB migration check. Переход к PHASE 18 запрещён до установки toolchain и повторного полного verify.

