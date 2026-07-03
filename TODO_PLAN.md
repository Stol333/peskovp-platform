# TODO PLAN — PESKOVP Production Platform

## Execution Rules
- Work strictly by phases.
- Do not skip audit, backup, rollback, validation, reporting.
- Do not modify production VPN components before approved audit + backup + rollback plan.
- Do not expose secrets, tokens, private keys, real subscription IDs, passwords or hidden panel paths.

## Phases
- [x] 00 Bootstrap без изменений
- [x] 01 Read-only server audit
- [x] 02 Official docs research
- [x] 03 Backup and rollback
- [x] 04 Stable server update
- [x] 05 Architecture decision
- [x] 06 Project scaffold
- [x] 07 AI module
- [x] 08 Read-only VPN integration
- [x] 09 Docker Compose infrastructure
- [x] 10 Nginx/SSL/domain integration
- [ ] 11 Security hardening
- [ ] 12 Testing
- [ ] 13 Node-by-node debugging
- [ ] 14 Documentation
- [ ] 15 Final report

## Current Gate
Phase 10 completed (Nginx/SSL/domain artifacts implemented and regression-tested). Next phase: 11 Security hardening.

## Phase 6 Preflight (ready)
- Input baseline fixed: Phase 0-5 closed and validated.
- Mandatory references: `reports/04_architecture_decision_record.md`, `reports/06_security_review.md`, `reports/07_test_matrix.md`, `reports/09_final_report.md`.
- Start objective for Phase 6: scaffold project structure and implementation tracks without production-destructive actions.
