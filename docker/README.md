# Docker Compose Infrastructure (Phase 10)
## Назначение
Каталог содержит compose-инфраструктуру PESKOVP с reverse-proxy слоем Nginx, TLS-терминацией и доменной маршрутизацией для `ai-module`.

## Сервисы
- `ai-module` — backend AI API (internal only, порт наружу только в override-файле).
- `vpn-readonly` — read-only snapshot runner (профиль `vpn-readonly`).
- `nginx-gateway` — edge reverse proxy с HTTPS и доменными virtual host.
- `certbot` — one-shot выпуск/обновление сертификата (профиль `certbot`).

## Файлы
- `docker-compose.yml` — базовый compose-манифест.
- `docker-compose.override.yml` — dev-переопределения.
- `env/ai-module.env.example` — шаблон env для AI сервиса.
- `env/vpn-readonly.env.example` — шаблон env для VPN read-only сервиса.
- `env/nginx.env.example` — шаблон domain/SSL параметров Nginx+Certbot.
- `healthchecks/ai_module_healthcheck.py` — readiness check для `ai-module`.

## Быстрый запуск
1. Подготовить DNS и env:
   - заполнить `docker/env/nginx.env.example` реальными доменами/email (без коммита секретов);
   - убедиться, что `APP_DOMAIN` и `AI_DOMAIN` резолвятся на хост.
2. Выпустить TLS сертификат:
   - `docker compose -f docker/docker-compose.yml --profile certbot run --rm certbot`
   - важно: на момент запуска certbot порт `80` должен быть свободен (остановить `nginx-gateway`, если он уже запущен).
3. Проверить compose-конфигурацию:
   - `docker compose -f docker/docker-compose.yml -f docker/docker-compose.override.yml config`
4. Поднять сервисы:
   - `docker compose -f docker/docker-compose.yml -f docker/docker-compose.override.yml up -d ai-module nginx-gateway`
5. Опционально запустить VPN snapshot:
   - `docker compose -f docker/docker-compose.yml -f docker/docker-compose.override.yml --profile vpn-readonly run --rm vpn-readonly`
6. Остановить сервисы:
   - `docker compose -f docker/docker-compose.yml -f docker/docker-compose.override.yml down`

## Безопасность
- Секреты не хранятся в git; в репозитории только `*.env.example`.
- `ai-module` в базовом compose не публикует порт наружу.
- Для `vpn-readonly` сохраняется строгий read-only контракт.
- Nginx конфиг использует только TLSv1.2/TLSv1.3 и базовые hardening headers.
