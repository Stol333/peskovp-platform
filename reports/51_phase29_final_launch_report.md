# PHASE 29.14 — Final launch report
## Goal
Закрыть PHASE 29+ честным итоговым отчётом с полным статусом production launch.
## Read
- `PESKOVP_PHASE29_PRODUCTION_LAUNCH_PLAN_V7.md` (секция PHASE 29.14).
- `reports/40_phase29_handoff_reconciliation.md` … `reports/50_phase29_port_reclaim_decision.md`.
- `TODO_PLAN_V6_EXECUTION.md`.
- `reports/34_v6_implementation_log.md`.
## Plan
- Свести результаты PHASE 29.0–29.13 в финальный запускной отчёт.
- Явно разделить выполненное/невыполненное и остаточные owner decisions.
- Зафиксировать итоговый production readiness статус без приукрашивания.
## Risk check
- Риск ложного `READY` при нерешённом foreign-exit ограничении для premium multi-route.
- Риск завышения готовности при отсутствии reclaim execution.
- Риск потери управляемости без явной owner action list.
## Backup / rollback check
- Backup refresh: `PHASE 29.3 PASSED`.
- Operational runbooks/scripts: `PHASE 29.11 PASSED`.
- Rollback path: `infra/rollback/PHASE29_PRODUCTION_ROLLBACK.md`.
## Final launch report (A–P)
### A. Что было сделано
- Закрыты PHASE `29.0 … 29.13` с evidence-отчётами `reports/40 … reports/50`.
- Подтверждены runtime/security/flow проверки:
  - RF runtime и routing policy;
  - subscription V2 + legacy compatibility;
  - web/API/admin RBAC fail-closed;
  - Telegram/payment/webhook fail-closed;
  - E2E сценарии A/B/C/D.
- Подготовлен operability-контур:
  - runbooks (`docs/OPERATIONS_PHASE29.md`, `docs/BACKUP_RESTORE_PHASE29.md`, `docs/INCIDENT_RESPONSE_PHASE29.md`);
  - scripts (`infra/scripts/phase29_healthcheck.sh`, `phase29_backup.sh`, `phase29_rollback.sh`, `phase29_e2e_smoke.sh`).
### B. Что не было сделано
- Не выполнен массовый rollout выше `5%` (решение `LIMITED_CANARY_5_HOLD`).
- Не выполнен фактический port reclaim (`NO_RECLAIM_YET`).
- Не добавлен dedicated foreign-exit узел (блокер для premium multi-route).
### C. Что запущено на MAIN
- Активный production edge/control contour:
  - `nginx`, `x-ui`, `peskovp-sub`, `peskovp-hy2*`, `docker`;
  - web/api в loopback publish;
  - DB/Redis без публичного exposure.
### D. Что запущено на RF
- Активный routing gateway:
  - `xray active`;
  - `xray -test = Configuration OK`;
  - firewall profile для `443/2087/2084`.
### E. Какие домены активны
- `app.peskovp.com`
- `admin.peskovp.com`
- `api.peskovp.com`
- `panel.peskovp.com` (legacy hidden-path behavior сохранён)
- `sub.peskovp.com` (legacy hidden-path behavior сохранён)
### F. Какие порты используются
- MAIN:
  - public: `22/tcp`, `80/tcp`, `443/tcp`, `8443/tcp`, `443/2443/3443 udp`.
- RF:
  - `22/tcp`, `443/tcp`, `2087/tcp`, `2084/tcp`.
- Ограничение:
  - host nginx остаётся владельцем `80/443`; Docker не публикует `80/443`.
### G. Как работает VPN routing
- Policy lanes:
  - `direct` (локальные/RU-направления),
  - `proxy` (дефолт),
  - `block` (например, bittorrent).
- Canary model:
  - regular baseline — `legacy`;
  - admin/test cohorts — `v2_canary`;
  - fallback — legacy/tiered path.
- Health posture:
  - `main-control`, `rf-primary-tcp`, `rf-secondary-grpc` в активном routing inventory.
### H. Какие competitor patterns адаптированы
- split DNS/route policy model;
- direct/proxy/block lane логика;
- tiered health scoring;
- transport diversity model (`TCP 443`, `XHTTP`, `gRPC fallback`).
### I. Что явно не копировалось из competitor-файла
- Не использовались чужие IP/UUID/password/publicKey/shortId/path/serverName.
- Применялись только абстрактные архитектурные паттерны.
### J. Как работает payment-to-subscription
- `create payment` поддерживает idempotency (`new/replay`).
- invalid webhook secret/signature -> `401`.
- `succeeded` webhook активирует подписку.
- `failed` webhook не активирует подписку.
- renewal сценарий корректно активирует/продлевает подписку.
### K. Как работает Telegram Mini App
- Entry routes доступны: `/telegram-miniapp-v2.html`, `/tg`.
- Backend валидирует `initData`; invalid payload fail-closed (`400`).
- Связка Telegram -> payment -> activation подтверждена в production checks.
### L. Как проверять health
- `bash infra/scripts/phase29_healthcheck.sh`
- `bash infra/scripts/phase29_e2e_smoke.sh`
- Дополнительно:
  - `GET /api/health`, `GET /api/ready`;
  - `/api/admin/metrics` RBAC matrix (`401/403/200`).
### M. Как откатиться
- Основной документ:
  - `infra/rollback/PHASE29_PRODUCTION_ROLLBACK.md`
- Wrapper:
  - `bash infra/scripts/phase29_rollback.sh --target all`
- Backup/restore:
  - `docs/BACKUP_RESTORE_PHASE29.md`
### N. Какие риски остались
- Отсутствует dedicated foreign-exit input для premium multi-route.
- Массовый rollout не подтверждён (текущий шаг фиксирован на `5%`).
- Port reclaim остаётся нерешённым operational шагом (осознанно не выполнялся).
### O. Что требует решения owner
- Когда и при каких условиях повышать rollout выше `5%`.
- Когда запускать отдельный проект по dedicated foreign-exit node.
- Когда запускать controlled reclaim-step (после отдельного safety approval).
### P. Следующий roadmap
- 1) Расширить telemetry window и подготовить owner-review для шага `10%`.
- 2) Подготовить foreign-exit deployment plan (separate node, backup/firewall/test gates).
- 3) После этого решить вопрос controlled port reclaim одним low-risk шагом.
## Record
- Created:
  - `reports/51_phase29_final_launch_report.md`
  - `artifacts/phase29_14/20260710-144759/phase29_14_summary.json`
## Gate
- `PHASE 29.14 = PASSED`.
- Final production status: `PARTIAL_READY`.
- Next gate: `PHASE_29_PASSED_FINAL_OWNER_SUMMARY_COMPLETE`.
