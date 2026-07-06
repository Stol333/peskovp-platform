# 33 VPN V2 Architecture Report
## Итог архитектурного решения
- Принята модель `MAIN control-plane + RF data-plane`.
- Введён модуль `packages/vpn-routing` как единая точка принятия routing/canary решений.
- Массовый switch legacy клиентов запрещён до прохождения canary-гейтов.

## Архитектурные блоки
- Policy engine:
  - deterministic rule matching (`direct`, `proxy`, `block`).
- Health scoring:
  - скоринг нод по latency/error/uptime/load.
- Canary rollout:
  - percentage-based assignment с cohort стабилизацией.
- Subscription presets:
  - `legacy`, `v2_auto`, `lte_safe`, `ru_direct`, `rf_gateway`, `canary`.

## Почему это безопасно
- MAIN порты не перехватываются новым compose runtime.
- RF добавляется как изолированный data-plane без вмешательства в panel/sub MAIN.
- Каждый rollout шаг обратим через отдельный rollback runbook.

## Dependency gates
- Backup gate: пройден (`reports/33_ru_gateway_backup.md`).
- Port ownership baseline: зафиксирован (`reports/32_port_ownership_and_migration_plan.md`).
- Competitor redacted patterns: учтены (`reports/30_competitor_pattern_analysis.md`).

## Следующий технический шаг
- Выполнить dry-run тесты routing модуля и API-контуров.
- После стабильной метрики canary users переходить к port reclaim по одному порту за итерацию.

