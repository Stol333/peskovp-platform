# PHASE 29.12 — Controlled rollout decision
## Goal
Принять контролируемое rollout-решение без прыжка к массовому прод-режиму.
## Read
- `PESKOVP_PHASE29_PRODUCTION_LAUNCH_PLAN_V7.md` (секция PHASE 29.12).
- `reports/46_phase29_web_api_admin_production_validation.md`.
- `reports/47_phase29_telegram_payment_validation.md`.
- `reports/48_phase29_full_e2e_flow.md`.
- `reports/44_phase29_foreign_exit_decision.md`.
- `artifacts/phase29_11/20260710-144346/phase29_11_summary.json`.
- `artifacts/phase29_12/20260710-144406/rollout_inputs_raw.txt`.
- `artifacts/phase29_12/20260710-144406/github_mcp_snapshot.json`.
## Plan
- Проверить фактическую стабильность canary-среза (`health`, `error budget`, support pressure).
- Сопоставить состояние с rollout ladder V7 и зафиксировать безопасную ступень.
- Формализовать правила эскалации/стопа и rollback-ready контур.
## Risk check
- Риск преждевременной эскалации при неполной observability-window.
- Риск продуктового оверпромиса при отсутствии dedicated foreign-exit для premium multi-route.
- Риск деградации legacy-контуров при агрессивном росте процента canary.
## Backup / rollback check
- PHASE 29.3 backup refresh ранее закрыт.
- PHASE 29.11 runbooks/scripts готовы (`OPERATIONS`, `BACKUP_RESTORE`, `INCIDENT_RESPONSE`, `phase29_*` scripts).
- Rollback path зафиксирован: `infra/rollback/PHASE29_PRODUCTION_ROLLBACK.md`.
## Execute
### Stability inputs
- Снят свежий snapshot:
  - `artifacts/phase29_12/20260710-144406/rollout_inputs_raw.txt`.
- GitHub support burden через MCP:
  - `artifacts/phase29_12/20260710-144406/github_mcp_snapshot.json`.
- Сформирован summary artifact:
  - `artifacts/phase29_12/20260710-144406/phase29_12_summary.json`.
## Verify
### Core runtime stability
- API health:
  - `status=ok`
  - `canary_percent=5`
  - `rf_gateway_enabled=true`
  - `vpn_write_enabled=false`
  - `vpn_provisioning_dry_run=true`
- Web VPN health:
  - `legacy=healthy`
  - `v2Canary=ready_for_admin_test`
- Error budget (`20m`):
  - `API_ERRORS_20M=0`
  - `WEB_ERRORS_20M=0`
  - `NGINX_ERRORS_20M=0`
### Support burden snapshot
- Open issues: `0`.
- Open PRs: `2` (`#11`, `#10`).
- Новых production incident-signal в открытых issues нет.
### Rollout decision
- `PHASE29_12_DECISION=LIMITED_CANARY_5_HOLD`.
- Текущее безопасное состояние:
  - оставить `VPN_V2_CANARY_PERCENT=5`;
  - не эскалировать до `10/25/50/100` в этом gate;
  - держать legacy fallback активным.
- Условия следующего эскалационного шага (после отдельного owner review):
  - подтверждённое стабильное окно без роста complaint/error давления;
  - без регрессий `app/admin/api/panel/sub/www`;
  - сохранён fail-closed security posture (`RBAC`, webhook secrets/signatures, initData validation).
## Record
- Created:
  - `reports/49_phase29_rollout_decision.md`
  - `artifacts/phase29_12/20260710-144406/github_mcp_snapshot.json`
  - `artifacts/phase29_12/20260710-144406/phase29_12_summary.json`
## Gate
- `PHASE 29.12 = PASSED`.
- Decision label: `LIMITED_CANARY_5_HOLD`.
- Next gate: `PHASE_29_12_PASSED_READY_FOR_PHASE29_13`.
