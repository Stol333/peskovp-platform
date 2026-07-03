# 07 Test Matrix

## Phase 0 Checks
- Local artifact creation: passed.
- Production server changes: none.

## Phase 1 Checks
- Read-only audit command bundle prepared: passed.
- Raw server snapshot collected: passed (`reports/01_server_audit_raw.txt`).
- Production server changes: none.

## Phase 2 Checks
- Official sources verification: passed (`reports/03_research_sources.md`).
- Architecture decisions documented: passed (`reports/04_architecture_decision_record.md`).
- Audit-to-decision traceability: passed (Phase 1 findings reflected in ADR).
- Production server changes: none.

## Phase 3 Checks
- Phase 3 script scaffold created: passed (`infra/scripts/phase3_backup_and_config_apply.ps1`).
- Backup/rollback runbook documents updated: passed.
- Manifest switched from pending to in-progress with executable commands: passed.
- `Prepare` mode execution: passed (`artifacts/phase3/20260703-140202`, `artifacts/phase3/20260703-140720`).
- `Apply` mode execution: blocked/interrupted (`artifacts/phase3/20260703-140234`).
- Script hardening after blocker: passed (non-interactive SSH options, targeted DB discovery, marker parsing).
- `Apply` mode execution (post-fixes): passed (`artifacts/phase3/20260703-151518`).
- Backup artifact integrity check: passed (system/network/services/packages/containers/app trees present).
- Production server changes in this step: backup execution completed; configuration-altering changes не выполнялись.

## Phase 4 Checks
- Phase 4 deployment script execution: passed (`artifacts/phase4/20260703-152642`).
- Safe upgrade strategy: passed (only non-excluded packages upgraded).
- VPN service continuity: passed (all critical services active before/after).
- Xray version invariance: passed (`26.2.6` before = `26.2.6` after).
- Nginx config validation: passed (`nginx -t` successful).
- Post-upgrade package state: passed (no remaining upgradable packages in run output).

## Phase 5 Checks
- Phase 5 final validation script execution: passed (`artifacts/phase5/20260703-153401`).
- Final result gate: passed (`PHASE5_RESULT=PASS`).
- Critical services state: passed (`active` + `enabled` for all target services).
- Systemd failed units check: passed (`0 loaded units listed`).
- Nginx syntax/config check: passed (`nginx -t` successful).
- Firewall baseline check: passed (`ufw active`, default deny incoming).
- Fail2ban baseline check: passed (`3x-ipl`, `sshd` jails active).
- Package drift check: passed (`apt list --upgradable` => only `Listing...`).
- VPN core continuity check: passed (`Xray 26.2.6`).

## Phase 6 Checks
- Scaffold directories creation: passed (`apps/`, `services/`, `integrations/`, `docker/`, `docs/`, `tests/`).
- Baseline templates creation: passed (`README.md`, `.gitignore`, `.env.example`, `infra/config/app.example.yaml`).
- Secrets hygiene check: passed (только placeholder значения, без реальных токенов/ключей).
- Production safety check: passed (локальный scaffold, без production-изменений).

## Phase 7 Checks
- AI module source scaffold: passed (`services/ai-module/src/*`).
- OpenAI Responses integration layer: passed (`src/openai_responses_client.py`).
- Guardrails implementation: passed (`src/guardrails.py`).
- Rate limiting implementation: passed (`src/rate_limiter.py`).
- History + usage logging implementation: passed (`src/history_store.py`, `src/usage_logger.py`).
- API endpoints presence: passed (`/health`, `/v1/ai/respond`, `/v1/ai/respond/stream`, `/v1/ai/respond/structured`, `/v1/ai/history/{session_id}`, `/v1/ai/tools/approval-check`).
- Secrets hygiene: passed (env placeholders only, no real keys in code/reports).
- Production safety: passed (изменения только в локальном коде и отчетах).
- Python compile check: passed (`python -m compileall services/ai-module/src`).
- Unit tests: passed (`3 passed` for `test_guardrails.py` + `test_rate_limiter.py`).

## Phase 9 Checks (completed)
- Compose artifacts creation: passed (`docker/docker-compose.yml`, `docker/docker-compose.override.yml`, `docker/env/*.env.example`, `docker/healthchecks/ai_module_healthcheck.py`, Dockerfile-ы сервисов).
- Docker CLI availability check: environment constraint (`docker compose version` => `docker` command not found in current shell).
- AI module unit tests: passed (`3 passed`).
- VPN integration unit tests: passed (`6 passed`).
- Python compile check for healthcheck + service modules: passed.
- Phase completion decision: accepted for Phase 09 scope with documented runtime constraint on current host session.
- Production safety: passed (локальные инфраструктурные изменения, без production runtime-действий).

## Phase 10 Checks (completed)
- Nginx/SSL/domain compose artifacts: passed (Nginx templates, SSL params, compose gateway/certbot, env scaffold).
- Runtime edge validation (`docker compose config`, `nginx -t`, HTTPS handshake): blocked on current host (`docker` command not found).
- AI module regression tests: passed (`3 passed`).
- VPN integration regression tests: passed (`6 passed`).
- Secrets hygiene: passed (только шаблоны env, без секретов).
- Phase completion decision: accepted for Phase 10 scope with documented Docker runtime constraint.
- Production safety: passed (изменения только в локальных конфигурационных артефактах).

## Phase 11 Checks (completed)
- Server hardening script execution: passed (`infra/scripts/phase11_security_hardening.ps1`).
- Phase 11 remote apply result: passed (`PHASE11_RESULT=PASS`, run base `/root/backups/peskovp-phase11-hardening-20260703-181859`).
- SSH hardening validation: passed (`sshd` config test successful, service state `ssh=active`).
- Nginx hardening validation: passed (`nginx -t` successful, service state `nginx=active`).
- Fail2ban hardening validation: passed (`fail2ban=active`, `sshd` jail active).
- Firewall hardening validation: passed (`22/tcp LIMIT IN` for IPv4/IPv6 in UFW status).
- Backup-before-change policy: passed (pre-change snapshots saved in phase11 backup bundle).

## Phase 12 Preparation Checks
- Entry gate after Phase 11 completion: passed.
- Documentation sync for testing phase: passed (`README.md`, `TODO_PLAN.md`, `docs/README.md`, `tests/README.md`).
- Planned regression scope definition: passed (AI module + VPN readonly + security invariants).
- Planned infrastructure smoke scope definition: passed (compose/edge checks when Docker runtime is available).

## Phase 12 Checks (in progress)
- AI module regression tests: passed (`python -m pytest C:\\Users\\dgafa\\services\\ai-module\\tests` => `3 passed`).
- VPN readonly regression tests: passed (`python -m pytest C:\\Users\\dgafa\\integrations\\vpn\\tests` => `6 passed`).
- Compile checks: passed (`python -m compileall C:\\Users\\dgafa\\services\\ai-module\\src C:\\Users\\dgafa\\integrations\\vpn\\src\\vpn_readonly`).
- Docker runtime availability: blocked (`docker compose version` => `docker` command not found).
- Security regression — services active: passed (`ssh=active`, `nginx=active`, `fail2ban=active`).
- Security regression — hardening artifacts presence: passed (`/etc/ssh/sshd_config.d/99-peskovp-hardening.conf`, `/etc/fail2ban/jail.d/10-peskovp-sshd.local`, `/etc/nginx/conf.d/zz-peskovp-hardening.conf`).
- Security regression — config validation: passed (`sshd -t` => `SSHD_TEST=ok`; `nginx -t` => successful).
- Security regression — firewall/jail status: passed (`ufw` содержит `22/tcp LIMIT IN` и `22/tcp (v6) LIMIT IN`; `fail2ban-client status sshd` показывает активный jail).
- Phase status decision: in progress (compose/edge smoke-check требует доступного Docker runtime).

