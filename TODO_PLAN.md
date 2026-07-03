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
- [x] 11 Security hardening
- [ ] 12 Testing
- [ ] 13 Node-by-node debugging
- [ ] 14 Documentation
- [ ] 15 Final report

## Current Gate
Phase 12 in progress (local regression passed, security regression passed, compose runtime-check blocked by unavailable Docker runtime).
## Phase 12 Preparation
- Entry condition confirmed: Phase 11 hardening завершён, верифицирован и влит в `master`.
- Test scope for Phase 12:
  - regression/unit проверки `services/ai-module` и `integrations/vpn`;
  - инфраструктурные проверки compose/edge при доступном Docker runtime;
  - security regression-проверки инвариантов SSH/Nginx/Fail2ban/UFW после hardening.
- Evidence update requirements:
  - фиксировать результаты в `reports/07_test_matrix.md`;
  - фиксировать ход выполнения в `reports/05_implementation_log.md`.
## Phase 12 Progress
- Локальный regression/unit прогон: `services/ai-module/tests` (`3 passed`), `integrations/vpn/tests` (`6 passed`).
- Compile check: `services/ai-module/src` и `integrations/vpn/src/vpn_readonly` — успешно.
- Security regression (server-side, read-only): `ssh/nginx/fail2ban active`, hardening-конфиги присутствуют, `sshd -t`/`nginx -t` успешны, `ufw` содержит `22/tcp LIMIT IN`, `fail2ban sshd` jail активен.
- Инфраструктурный compose smoke-check: blocked (Docker runtime недоступен в текущем окружении).

## Phase 6 Preflight (ready)
- Input baseline fixed: Phase 0-5 closed and validated.
- Mandatory references: `reports/04_architecture_decision_record.md`, `reports/06_security_review.md`, `reports/07_test_matrix.md`, `reports/09_final_report.md`.
- Start objective for Phase 6: scaffold project structure and implementation tracks without production-destructive actions.
