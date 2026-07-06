# PRODUCTION DEPLOY (PHASE 15/16 baseline)
## Цель
Поднять production app stack без конфликта с host nginx и legacy VPN: без public `80/443`, без public PostgreSQL/Redis, с loopback publish только для application endpoints.
## Ключевые артефакты
- `docker/docker-compose.prod.yml`
- `docker/env/prod.env.example`
- `docker/scripts/postgres_backup.sh`
- `docker/scripts/postgres_restore.sh`
- `docker/scripts/redis_backup.sh`
- `docker/scripts/redis_restore.sh`
- `infra/scripts/phase16_prepare_env.py`
- `infra/scripts/phase16_validate_env.py`
## Port/collision check перед запуском
Проверить, что выбранный app bind порт (`3100` по умолчанию) свободен:
- Linux: `ss -ltnp | grep -E ':3000|:3100'`
- Windows (PowerShell): `netstat -ano | Select-String -Pattern ':3000\\s',':3100\\s'`
Если `3100` занят, изменить `APP_BIND_PORT` на свободный (`3000` или другой loopback-only порт).
## Обязательные правила безопасности
- Не запускать app stack с publish `80:80`/`443:443`.
- Host nginx остаётся владельцем публичных `80/443`.
- PostgreSQL и Redis работают только во внутренней Docker-сети (`expose`, без `ports`).
- Все секреты задаются только через server-side env file (не в git).
## Подготовка env на сервере
1. Скопировать шаблон:
   - `cp docker/env/prod.env.example /etc/peskovp/.env.production`
2. Заполнить секреты в `/etc/peskovp/.env.production`:
   - `POSTGRES_PASSWORD`
   - `OPENAI_API_KEY`
   - `AI_API_AUTH_TOKEN`
   - `VPN_API_TOKEN` (если используется)
3. Проверить, что файл не попадает в git.
## PHASE 16: server-only env generation
Для генерации внутренних секретов (`AUTH_SECRET`, `NEXTAUTH_SECRET`, `AI_API_AUTH_TOKEN`, `VPN_V2_CANARY_SALT`) использовать:
`python infra/scripts/phase16_prepare_env.py --template docker/env/prod.env.example --output /etc/peskovp/.env.production`
Важно:
- команда не печатает секретные значения в stdout;
- external provider secrets (`OPENAI_API_KEY`, `TELEGRAM_BOT_TOKEN`, payment secrets) заполнить вручную из secret manager.
## PHASE 16: env validation
Проверка структуры шаблона:
`python infra/scripts/phase16_validate_env.py --env-file docker/env/prod.env.example --mode template`
Проверка server env:
`python infra/scripts/phase16_validate_env.py --env-file /etc/peskovp/.env.production --mode production`
Критерии production validation:
- обязательные переменные присутствуют;
- internal routing: `DATABASE_URL` указывает на `postgres`, `REDIS_URL` на `redis`;
- для core secrets отсутствуют placeholder значения.
## Валидация compose (обязательный gate)
Перед любым `up`:
`docker compose -f docker/docker-compose.prod.yml --env-file /etc/peskovp/.env.production config`
Критерии:
- команда проходит без ошибок;
- в итоговом конфиге нет publish `80/443`;
- PostgreSQL/Redis не имеют `ports`.
## Запуск
`docker compose -f docker/docker-compose.prod.yml --env-file /etc/peskovp/.env.production up -d`
## Smoke/health checks
- `docker compose -f docker/docker-compose.prod.yml --env-file /etc/peskovp/.env.production ps`
- `docker compose -f docker/docker-compose.prod.yml --env-file /etc/peskovp/.env.production logs --tail=100`
- Проверить локальные endpoints:
  - `http://127.0.0.1:${APP_BIND_PORT}/api/health`
  - `http://127.0.0.1:${API_BIND_PORT}/health`
  - `http://127.0.0.1:${AI_BIND_PORT}/health`
## Backup/restore runbook (data services)
PostgreSQL:
- backup: `docker/scripts/postgres_backup.sh`
- restore: `docker/scripts/postgres_restore.sh /path/to/backup.sql.gz`
Redis:
- backup: `docker/scripts/redis_backup.sh`
- restore: `docker/scripts/redis_restore.sh /path/to/dump.rdb`
## Log rotation
Для всех сервисов включена JSON log rotation:
- `max-size=${LOG_MAX_SIZE:-10m}`
- `max-file=${LOG_MAX_FILES:-5}`
## Rollback note
При критическом сбое:
1. Остановить только новый app stack (`docker compose ... down`).
2. Не трогать host nginx/legacy VPN.
3. Восстановить data из последних backup-артефактов.
4. Следовать `infra/rollback/V6_ROLLBACK.md`.
