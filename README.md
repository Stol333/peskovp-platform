# PESKOVP Platform
## Назначение
Этот репозиторий содержит инфраструктурные артефакты и кодовую базу платформы PESKOVP.
Текущий этап: `V6 PHASE 17 — TEST BEFORE DEPLOY (BLOCKED: отсутствует node/npm/pnpm)`.

## Базовая структура
- `apps/api` — backend API (Phase 7+).
- `apps/web` — frontend/admin UI (Phase 7+).
- `services/ai-module` — AI-модуль (Phase 7).
- `integrations/vpn` — read-only интеграции с VPN-контуром (Phase 8).
- `docker` — Compose + edge-инфраструктура (Phase 9-10).
- `infra/config` — шаблоны конфигураций.
- `infra/services` — сервисные unit/runbook-заготовки.
- `tests` — матрица и автоматизация проверок (Phase 12).
- `docs` — продуктовая и техническая документация (Phase 14).
- `reports` — фазовые отчёты исполнения.

## Правила безопасности
- Никаких секретов в репозитории.
- Все секреты только через env/secret manager.
- Production-изменения только после backup/rollback и validation.
## Документация
- Главный индекс документации: `docs/README.md`
- Гайд по обновлению документации: `docs/CONTRIBUTING.md`
- Фазовые технические отчёты: `reports/*.md`
## Статус Phase 12 (Testing)
- Выполнены локальные regression/unit прогоны:
  - `services/ai-module/tests` — `3 passed`;
  - `integrations/vpn/tests` — `6 passed`;
  - compile check `services/ai-module/src` и `integrations/vpn/src/vpn_readonly` — успешно.
- Выполнены server-side security regression проверки (read-only): активность `ssh/nginx/fail2ban`, наличие hardening-конфигов, `sshd -t`, `nginx -t`, `ufw` SSH `LIMIT`, `fail2ban sshd` jail.
- Блокер `docker compose` снят: установлены `Docker.DockerCompose` и `Docker.DockerDesktop`, `docker compose version` и `docker compose ... config` проходят успешно.
- Runtime запуск edge-сервисов (`docker compose ... up -d ai-module nginx-gateway`) на текущем хосте падает с `Docker Desktop is unable to start` (desktop status: `stopped`).
- По решению пользователя Docker runtime smoke-check на этом хосте пропущен (waiver), без остановки этапа.
- Фактические результаты зафиксированы в `reports/07_test_matrix.md` и `reports/05_implementation_log.md`.
- Фаза 12 закрыта с документированным waiver по локальному Docker runtime.
## Статус Phase 13 (Node-by-node debugging)
- Выполнена read-only узловая диагностика production-контура:
  - critical services `nginx/x-ui/peskovp-sub/peskovp-hy2/peskovp-hy2-obfs/peskovp-hy2-advanced/fail2ban/ssh` — `active`;
  - `systemctl --failed` — пусто;
  - `peskovp-hy2-sync.timer` — `active`, последний запуск `peskovp-hy2-sync.service` завершился `status=0/SUCCESS`.
- Проверены operational узлы:
  - `systemd-networkd-wait-online.service` в текущем boot цикле `skipped` по condition (без активного timeout-инцидента);
  - SSH preauth noise за последние 24 часа: `SSH_ERR_TOTAL=22`, `SSH_KEX_COUNT=19`, `SSH_PROTOCOL_MISMATCH_COUNT=1`, `SSH_CONN_RESET_COUNT=1`.
- Локальные прикладные узлы подтверждены:
  - `python -m pytest services/ai-module/tests integrations/vpn/tests` — `9 passed`;
  - `python -m compileall services/ai-module/src integrations/vpn/src/vpn_readonly` — успешно.
- Docker runtime на текущем хосте остаётся non-operational (`docker compose up` -> `Docker Desktop is unable to start`; desktop logs указывают на precondition `Virtual Machine Platform not enabled`), и по решению пользователя этот runtime-блок оставлен в waiver без блокировки Phase 13.
- Phase 13 закрыта, результаты зафиксированы в `reports/07_test_matrix.md` и `reports/05_implementation_log.md`.
## Статус Phase 14 (Documentation)
- Обновлён документационный хаб `docs/README.md` с актуальной структурой и статусом проекта.
- Добавлены целевые документы:
  - `docs/architecture/overview.md`
  - `docs/api/ai-module.md`
  - `docs/api/vpn-readonly.md`
  - `docs/runbooks/node-by-node-debugging.md`
  - `docs/operations/docker-runtime-waiver.md`
- Документация синхронизируется с фазовой отчётностью (`reports/05_implementation_log.md`, `reports/07_test_matrix.md`) и текущим gate в `TODO_PLAN.md`.
- Runtime ограничение Docker на текущем хосте явно задокументировано как operational waiver.
- Phase 14 закрыта: документационный набор переведён из scaffold в рабочий вид.
## Статус Phase 15 (Final report)
- Финальный отчёт переведён в актуальный формат полного цикла (Phase 00-15) в `reports/09_final_report.md`.
- В отчёт включены:
  - итоги по безопасному выполнению фаз;
  - подтверждённые результаты тестирования и node-by-node debugging;
  - зафиксированный Docker runtime waiver на текущем хосте;
  - набор рекомендаций для post-phase развития.
- Phase 15 завершена: итоговый отчёт сформирован и статусы фаз синхронизированы.

## V6 Controlled VPN Re-Architecture (execution update)
- Выполнены baseline + backup + architecture + implementation артефакты V6:
  - `reports/30_*` ... `reports/38_*`,
  - `docs/VPN_V2_ARCHITECTURE.md`,
  - `infra/rollback/VPN_V2_ROLLBACK.md`,
  - `packages/vpn-routing`,
  - `apps/api` V2 contour,
  - `apps/web` Telegram/admin scaffold.
- Backup gate подтверждён для MAIN и RF.
- Mass switch legacy подписки не выполнялся (только controlled canary readiness).
- Port reclaim отложен до live canary telemetry.

## Дорожная карта (обновление после PHASE 17 BLOCKED)
1. Разблокировать зависимости toolchain:
   - установить Node.js LTS;
   - активировать `pnpm@9.12.3` через Corepack;
   - подтвердить `node/npm/pnpm` версии.
2. Повторно выполнить обязательный predeploy-цикл PHASE 17:
   - `pnpm install`, `lint`, `prettier --check`, `typecheck`, `build`, `@peskovp/db build`;
   - контрольные Python test/compile и `docker compose config`.
3. Закрыть PHASE 17 статусом `PASSED` и только после этого перейти к PHASE 18.
4. После PHASE 18 продолжить canary-ветку PHASE 19-20 (RF gateway + V2 subscription canary) с rollback-ready контролем.
