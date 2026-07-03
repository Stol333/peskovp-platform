# Tests
Каталог тестирования для Phase 12 (Testing).
## Области проверки
- unit/regression тесты `services/ai-module`;
- unit/regression тесты `integrations/vpn`;
- инфраструктурные smoke-checks compose/edge (при доступном Docker runtime);
- контроль инвариантов безопасности после Phase 11 hardening.
## Базовый прогон
- `python -m pytest services/ai-module/tests`
- `python -m pytest integrations/vpn/tests`
- `python -m compileall services/ai-module/src integrations/vpn/src/vpn_readonly`
- при доступном Docker runtime: `docker compose -f docker/docker-compose.yml config` и профильные smoke-checks.
## Артефакты фазы
- Результаты прогонов фиксировать в `reports/07_test_matrix.md`.
- Ход выполнения и отклонения фиксировать в `reports/05_implementation_log.md`.
