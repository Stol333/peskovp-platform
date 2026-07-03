# Nginx / SSL / Domain Integration (Phase 10)
## Назначение
Каталог содержит шаблоны edge-конфигурации Nginx для HTTPS-доменов PESKOVP и reverse proxy к `ai-module`.

## Файлы
- `templates/peskovp.conf.template` — основной шаблон virtual hosts.
- `includes/ssl-params.conf` — TLS и security headers.

## Порядок применения
1. Заполнить `docker/env/nginx.env.example` актуальными доменами (`APP_DOMAIN`, `AI_DOMAIN`) и email.
2. Выпустить сертификат через compose-профиль `certbot` (порт `80` должен быть свободен).
3. Запустить `nginx-gateway` в compose.
4. Проверить:
   - HTTP redirect на HTTPS;
   - доступность `https://<AI_DOMAIN>/health`;
   - endpoint `https://<AI_DOMAIN>/nginx-health`.

## Ограничения текущего scope
- `apps/web` ещё не реализован, поэтому `APP_DOMAIN` временно редиректится на `AI_DOMAIN`.
- Конфиг ориентирован на безопасный baseline и может быть расширен в Phase 11 (hardening).
