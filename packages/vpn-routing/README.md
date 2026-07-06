# VPN Routing Package (`packages/vpn-routing`)
## Назначение
Пакет реализует базовую логику V2 маршрутизации:
- реестр нод;
- policy engine (`direct/proxy/block`);
- health scoring и ранжирование нод;
- canary rollout decision;
- генерацию profile preset для подписки.

## Ограничения
- Без секретов и реальных production credential.
- Без сетевых side-effect операций.
- Чистая business-логика для интеграции в API/control-plane.

## Быстрый обзор модулей
- `node_registry.py` — чтение/валидация нод.
- `policy_engine.py` — классификация трафика в policy lane.
- `health_scoring.py` — скоринг и ranking нод.
- `canary_rollout.py` — стабильное процентное распределение canary cohort.
- `subscription_profiles.py` — mapping decision -> набор профилей.

