# Tests
Каталог тестирования для Phase 12 (Testing).
## Области проверки
- unit/regression тесты `services/ai-module`;
- unit/regression тесты `integrations/vpn`;
- инфраструктурные smoke-checks compose/edge (при доступном Docker runtime);
- контроль инвариантов безопасности после Phase 11 hardening.
## PHASE 23 integration smoke (CI)
- Скрипт: `tests/integration/phase23_payment_subscription_smoke.py`.
- Покрывает цепочку `create intent -> idempotency replay -> webhook success/fail -> invalid secret -> renew -> subscription link`.
- Артефакты запросов/ответов сохраняются в `artifacts/phase23_ci`.
- Локальный запуск (при поднятом `web-app` на `127.0.0.1:3100`):
  - `python tests/integration/phase23_payment_subscription_smoke.py --base-url http://127.0.0.1:3100 --webhook-secret ci-phase23-telegram-secret --artifacts-dir artifacts/phase23_ci`
## Базовый прогон
- `python -m pytest services/ai-module/tests`
- `python -m pytest integrations/vpn/tests`
- `python -m compileall services/ai-module/src integrations/vpn/src/vpn_readonly`
- при доступном Docker runtime: `docker compose -f docker/docker-compose.yml config` и профильные smoke-checks.
## Артефакты фазы
- Результаты прогонов фиксировать в `reports/07_test_matrix.md`.
- Ход выполнения и отклонения фиксировать в `reports/05_implementation_log.md`.
