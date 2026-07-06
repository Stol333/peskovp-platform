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
[ ] PHASE 18 — LOCAL SERVER DEPLOY WITHOUT PUBLIC NGINX ROUTE
[ ] PHASE 19 — RF GATEWAY CANARY DEPLOY
[ ] PHASE 20 — V2 SUBSCRIPTION CANARY
[ ] PHASE 21 — HOST NGINX ROUTE FOR WEB/API/ADMIN
[ ] PHASE 22 — PAYMENT TO SUBSCRIPTION SMOKE TEST
[ ] PHASE 23 — CANARY VPN PROVISIONING GATE
[ ] PHASE 24 — CONTROLLED PRODUCTION ROLLOUT
[ ] PHASE 25 — PORT RECLAMATION
[ ] PHASE 26 — CI/CD
[ ] PHASE 27 — FINAL SECURITY REVIEW
[ ] PHASE 28 — FINAL TEST MATRIX
[ ] PHASE 29 — FINAL REPORT AND OWNER SUMMARY
## Current gate
PHASE_17_PASSED
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
