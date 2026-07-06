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
- [x] 12 Testing
- [x] 13 Node-by-node debugging
- [x] 14 Documentation
- [x] 15 Final report

## Current Gate
Phase cycle `00-15` completed. Current gate: PR `#4` находится в review.
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
- Compose dependency resolution: установлен `Docker.DockerCompose` (v5.3.0), `docker compose ... config` (base/override + profiles) проходит с кодом `0`.
- Локальный Docker runtime: `docker compose ... up -d ai-module nginx-gateway` завершился ошибкой `Docker Desktop is unable to start`, `docker desktop status` = `stopped`.
- По решению пользователя Docker runtime smoke-check на текущем хосте пропущен (waiver), Phase 12 закрыта.
## Phase 13 Progress
- Узловая read-only диагностика production-контура выполнена: `systemctl --failed` пусто, критичные сервисы (`nginx/x-ui/peskovp-sub/peskovp-hy2/peskovp-hy2-obfs/peskovp-hy2-advanced/fail2ban/ssh`) активны.
- Узел `peskovp-hy2-sync`: `timer` активен, последний service run завершился `status=0/SUCCESS`.
- Узел `systemd-networkd-wait-online`: в текущем boot цикле `skipped` по condition, новых timeout-инцидентов не выявлено.
- SSH-noise метрики за 24 часа собраны: `SSH_ERR_TOTAL=22`, `SSH_KEX_COUNT=19`, `SSH_PROTOCOL_MISMATCH_COUNT=1`, `SSH_CONN_RESET_COUNT=1` (операционный шум, без отказа сервиса SSH).
- Локальные прикладные узлы подтверждены: `pytest` (`9 passed`) и `compileall` для `services/ai-module` + `integrations/vpn`.
- Docker runtime ограничение на текущем хосте зафиксировано как user-approved waiver и не блокирует закрытие Phase 13.
## Phase 14 Progress
- Актуализирован docs hub:
  - `docs/README.md` приведён к текущему фазовому состоянию (после Phase 13).
- Создана базовая структура документации для поддержки эксплуатации и разработки:
  - `docs/architecture/overview.md`
  - `docs/api/ai-module.md`
  - `docs/api/vpn-readonly.md`
  - `docs/runbooks/node-by-node-debugging.md`
  - `docs/operations/docker-runtime-waiver.md`
- Зафиксирована трассируемость документации к отчётам и gate:
  - `README.md`
  - `reports/05_implementation_log.md`
  - `reports/07_test_matrix.md`
- Docker runtime ограничение на текущем хосте задокументировано как operational waiver (без блокировки движения по фазам).
- Phase 14 закрыта (documentation deliverables подготовлены и синхронизированы).
## Phase 15 Progress
- Финальный отчёт `reports/09_final_report.md` обновлён до full-cycle формата (Phase 00-15).
- В отчёте зафиксированы:
  - выполненные этапы и ключевые артефакты;
  - текущие ограничения/waivers;
  - блок рисков и следующие профессиональные шаги.
- Phase 15 закрыта: финальная документация согласована, PR открыт и помечен ready for review.

## Phase 6 Preflight (ready)
- Input baseline fixed: Phase 0-5 closed and validated.
- Mandatory references: `reports/04_architecture_decision_record.md`, `reports/06_security_review.md`, `reports/07_test_matrix.md`, `reports/09_final_report.md`.
- Start objective for Phase 6: scaffold project structure and implementation tracks without production-destructive actions.
