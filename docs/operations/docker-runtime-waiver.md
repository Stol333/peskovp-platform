# Docker Runtime Waiver (Current Host)
Фиксирует operational ограничение локального Docker runtime на текущем хосте.
## Симптомы
- `docker compose ... config` проходит успешно.
- `docker compose ... up -d ai-module nginx-gateway` завершается ошибкой:
  - `Docker Desktop is unable to start`.
- `docker desktop status` показывает:
  - `stopped`.
## Диагностический вывод
- В логах Docker Desktop присутствует precondition issue:
  - `Virtual Machine Platform not enabled`
  - `no virtualization found`.
## Влияние
- Невозможно выполнить локальный runtime smoke-check контейнеров на данном хосте.
- Это влияет на локальные edge/runtime проверки, но не отменяет результаты unit/regression и server-side read-only validation.
## Решение на текущем этапе
- Ограничение принято как user-approved waiver.
- Waiver не блокирует закрытие Phase 12/13 и переход к следующей фазе.
## Критерий снятия waiver
- Docker Desktop runtime стабильно запускается (`docker desktop status` != `stopped`).
- Команда `docker compose ... up -d ai-module nginx-gateway` выполняется успешно.
- Выполнены runtime smoke-checks и результаты зафиксированы в `reports/07_test_matrix.md`.
