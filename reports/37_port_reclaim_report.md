# 37 Port Reclaim Report
## Scope
Отчёт по освобождению legacy-портов после V2 подготовки.

## Текущий статус
- Reclaim execution: `DEFERRED`.
- Причина:
  - production V2 traffic ещё не запущен в массовом режиме;
  - сначала требуется admin/test canary telemetry window.

## Baseline ownership (зафиксирован)
- MAIN:
  - `22/tcp` SSH,
  - `80/443 tcp` nginx,
  - `8443 tcp` x-ui/xray,
  - `443/2443/3443 udp` HY2.
- RF:
  - `22/tcp` SSH,
  - V2 data-plane ports доступны для controlled onboarding.

## Reclaim policy
- Освобождение портов только после:
  - стабильного canary success rate,
  - подтверждённого rollback drill,
  - отсутствия регрессии `panel/sub/legacy`.
- Шаг reclaim:
  - один legacy exposure за итерацию,
  - окно наблюдения между шагами,
  - немедленный rollback при деградации.

## Decision
- На момент отчёта legacy порты не освобождались намеренно.
- Текущий статус соответствует safe migration strategy.

