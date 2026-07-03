# PESKOVP Platform
## Назначение
Этот репозиторий содержит инфраструктурные артефакты и кодовую базу платформы PESKOVP.
Текущий этап: `Phase 12 — Testing (in progress)`.

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
- Инфраструктурный compose smoke-check остаётся ограничен текущим окружением до доступного Docker runtime.
- Фактические результаты зафиксированы в `reports/07_test_matrix.md` и `reports/05_implementation_log.md`.

## Следующий этап
`Phase 13 — Node-by-node debugging` (после завершения Phase 12).
