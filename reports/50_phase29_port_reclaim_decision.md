# PHASE 29.13 — Port reclamation decision (no execution)
## Goal
Принять безопасное решение по reclaim legacy-портов без выполнения destructive-шагов.
## Read
- `PESKOVP_PHASE29_PRODUCTION_LAUNCH_PLAN_V7.md` (секция PHASE 29.13).
- `reports/37_port_reclaim_report.md`.
- `reports/49_phase29_rollout_decision.md`.
- `artifacts/phase25_monitoring/latest_phase25_monitoring_summary.json`.
- `artifacts/phase29_12/20260710-144406/phase29_12_summary.json`.
## Plan
- Проверить, выполнены ли строгие prerequisites для reclaim.
- Зафиксировать decision-only outcome с явным запретом на apply при недостаточном evidence.
- Документировать следующий безопасный путь к reclaim-кандидату.
## Risk check
- Риск сломать active legacy/service contour при преждевременном reclaim.
- Риск потери rollback safety при запуске reclaim без fresh pre-step backup окна.
- Риск деградации user connectivity для legacy клиентов.
## Backup / rollback check
- PHASE 25 подтверждён как `SKIPPED_WITH_REASON (OWNER WAIVER)`; reclaim apply исторически не запускался.
- Актуальные backup/rollback контуры присутствуют (`PHASE 29.3` + `PHASE 29.11` runbooks).
## Execute
- Выполнена decision-переоценка на основе:
  - исторического PHASE 25 monitoring evidence;
  - текущего rollout-state (`LIMITED_CANARY_5_HOLD`);
  - safety-правил PHASE 29.13.
- Сформирован summary artifact:
  - `artifacts/phase29_13/20260710-144759/phase29_13_summary.json`.
## Verify
### Criteria check
- `PHASE 25` strict-window `48/48` в явном виде не зафиксирован как закрытый reclaim-gate.
- Reclaim-step ранее не выполнялся; owner waiver относился к phase transition, не к destructive reclaim apply.
- Текущая launch-позиция остаётся limited canary (`5%`) с активным legacy fallback.
- Критичные контуры (`TCP 8443`, `UDP 443/2443/3443`, host nginx `80/443`) остаются частью рабочей прод-модели.
### Decision outcome
- `PHASE29_13_DECISION=NO_RECLAIM_YET`.
- Разрешено только:
  - продолжать read-only monitoring;
  - готовить single-step reclaim план отдельно после полного safety evidence и owner approval.
- Запрещено в этом gate:
  - выполнять любое фактическое отключение/освобождение legacy портов.
## Record
- Created:
  - `reports/50_phase29_port_reclaim_decision.md`
  - `artifacts/phase29_13/20260710-144759/phase29_13_summary.json`
## Gate
- `PHASE 29.13 = PASSED`.
- Decision label: `NO_RECLAIM_YET`.
- Next gate: `PHASE_29_13_PASSED_READY_FOR_PHASE29_14`.
