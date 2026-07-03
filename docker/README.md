# Docker Compose Infrastructure (Phase 9)
## Назначение
Каталог содержит compose-инфраструктуру для безопасного локального/стендового запуска реализованных сервисов PESKOVP.

## Сервисы
- `ai-module` — FastAPI AI service (Phase 7).
- `vpn-readonly` — read-only snapshot runner (Phase 8, запускается через профиль `vpn-readonly`).

## Файлы
- `docker-compose.yml` — базовый compose-манифест.
- `docker-compose.override.yml` — локальные dev-переопределения.
- `env/*.env.example` — шаблоны окружения без секретов.
- `healthchecks/ai_module_healthcheck.py` — readiness check для `ai-module`.

## Быстрый запуск
1. Проверить compose-конфигурацию:
   - `docker compose -f docker/docker-compose.yml -f docker/docker-compose.override.yml config`
2. Поднять основной сервис:
   - `docker compose -f docker/docker-compose.yml -f docker/docker-compose.override.yml up -d ai-module`
3. Запустить read-only VPN snapshot по профилю:
   - `docker compose -f docker/docker-compose.yml -f docker/docker-compose.override.yml --profile vpn-readonly run --rm vpn-readonly`
4. Остановить сервисы:
   - `docker compose -f docker/docker-compose.yml -f docker/docker-compose.override.yml down`

## Безопасность
- Секреты не хранятся в репозитории.
- Для `vpn-readonly` разрешены только read-only API вызовы (GET allowlist).
- Production-деструктивные операции в этом каталоге не реализуются.
