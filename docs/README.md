# PESKOVP Documentation Hub
Центральный индекс технической документации проекта.
## Текущий статус
- Phase 13 завершена (node-by-node debugging).
- Phase 14 завершена: документация переведена из scaffold в рабочий набор.
- Phase 15 завершена: финальный отчёт консолидирован и статус проекта закрыт по плановому циклу.
- V6 execution update: подготовлены controlled VPN re-architecture артефакты (baseline, backup, rollback, architecture, canary evidence).
## Структура документации
- `architecture/overview.md` — актуальная архитектурная карта и границы ответственности компонентов.
- `api/ai-module.md` — контракт AI module API и эксплуатационные ограничения.
- `api/vpn-readonly.md` — контракт read-only VPN integration.
- `runbooks/node-by-node-debugging.md` — runbook выполнения и интерпретации Phase 13 диагностики.
- `operations/docker-runtime-waiver.md` — operational waiver и диагностика Docker runtime на текущем хосте.
- `VPN_V2_ARCHITECTURE.md` — целевая архитектура V2 controlled rollout (MAIN/RF, routing policy, canary gates).
- `CONTRIBUTING.md` — правила и workflow обновления документации.
## Трассируемость
- План и фазовые статусы: `TODO_PLAN.md`.
- Ход выполнения: `reports/05_implementation_log.md`.
- Матрица проверок: `reports/07_test_matrix.md`.
- Сводка проекта: `README.md`.
## Правила качества документации
- Описывать только подтверждённые факты и реально существующие артефакты.
- Не публиковать секреты, токены, приватные ключи и скрытые служебные пути.
- Для каждого operational ограничения указывать:
  - симптомы;
  - влияние;
  - временный workaround/waiver;
  - критерий снятия ограничения.
