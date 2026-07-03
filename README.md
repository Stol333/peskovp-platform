# PESKOVP Platform
## Назначение
Этот репозиторий содержит инфраструктурные артефакты и кодовую базу платформы PESKOVP.
Текущий этап: `Phase 7 — AI module (completed)`.

## Базовая структура
- `apps/api` — backend API (Phase 7+).
- `apps/web` — frontend/admin UI (Phase 7+).
- `services/ai-module` — AI-модуль (Phase 7).
- `integrations/vpn` — read-only интеграции с VPN-контуром (Phase 8).
- `docker` — подготовка к Compose-инфраструктуре (Phase 9).
- `infra/config` — шаблоны конфигураций.
- `infra/services` — сервисные unit/runbook-заготовки.
- `tests` — матрица и автоматизация проверок (Phase 12).
- `docs` — продуктовая и техническая документация (Phase 14).
- `reports` — фазовые отчёты исполнения.

## Правила безопасности
- Никаких секретов в репозитории.
- Все секреты только через env/secret manager.
- Production-изменения только после backup/rollback и validation.

## Следующий этап
`Phase 8 — Read-only VPN integration`.
