# PESKOVP Platform
## Назначение
Этот репозиторий содержит инфраструктурные артефакты и кодовую базу платформы PESKOVP.
Текущий этап: `Phase 11 — Security hardening (completed)`.

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

## Следующий этап
`Phase 12 — Testing`.
