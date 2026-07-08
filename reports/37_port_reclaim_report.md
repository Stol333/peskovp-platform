# 37 Port Reclaim Report
## Scope
Отчёт по освобождению legacy-портов после V2 подготовки.

## Текущий статус
- Reclaim execution: `BLOCKED` (PHASE 25 precheck).
- Причина:
  - legacy grace period не завершён (система в режиме `LIMITED_CANARY_5`);
  - на legacy endpoint зафиксирована активность (`ESTAB_TCP_8443=340`);
  - отключение legacy transport на этом шаге создаёт риск пользовательской деградации.

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
## PHASE 25 precheck (post LIMITED_CANARY_5)
### Read-only evidence
- MAIN snapshot:
  - `VPN_V2_CANARY_PERCENT=5`
  - `VPN_WRITE_ENABLED=false`
  - `VPN_PROVISIONING_DRY_RUN=true`
  - `ESTAB_TCP_8443=340`
  - `ESTAB_TCP_443=26`
  - `UDP_LISTEN_443_2443_3443=3`
  - `HY2_LOG_LINES_60M=1637`
- RF snapshot:
  - `xray active`
  - `xray -test` = `Configuration OK`
  - ports/firewall baseline unchanged
### Gate decision
- `PHASE 25`: `BLOCKED`.
- Port reclaim apply не выполнялся (no-op по destructive шагам).
### Unblock criteria
- Подтверждённое завершение legacy grace period.
- Снижение/отсутствие активных клиентов на legacy endpoint.
- Fresh backup непосредственно перед первым reclaim-step.
- Поэтапный reclaim одного legacy exposure за итерацию с rollback window.
## PHASE 25 monitoring kickoff (blocked phase)
### Monitoring process
- Добавлен read-only script: `infra/scripts/phase25_monitoring_snapshot.ps1`.
- Назначение:
  - сбор MAIN/RF метрик по legacy активности;
  - контроль service/route стабильности;
  - фиксация derived readiness flags для PHASE 25.
- Путь артефактов: `artifacts/phase25_monitoring`.
### Baseline snapshot
- Snapshot ID: `20260708-113418`.
- Артефакты:
  - `artifacts/phase25_monitoring/20260708-113418/phase25_monitoring_summary.json`
  - `artifacts/phase25_monitoring/20260708-113418/main_snapshot_raw.txt`
  - `artifacts/phase25_monitoring/20260708-113418/rf_snapshot_raw.txt`
- MAIN baseline:
  - `VPN_V2_CANARY_PERCENT=5`;
  - `ESTAB_TCP_8443=340`;
  - `HY2_LOG_LINES_60M=1009`;
  - `HY2_ERR_LINES_60M=1`;
  - route checks: `app=200`, `admin=200`, `api/health=200`, `panel=404`, `sub=404`, `www=403`.
- RF baseline:
  - `XRAY_ACTIVE=active`;
  - `XRAY_CONFIG_TEST=ok`;
  - listen ports `443/2087/2084` присутствуют.
### Support burden (GitHub MCP)
- Snapshot:
  - `artifacts/phase25_monitoring/20260708-113418/github_support_snapshot.json`
  - `artifacts/phase25_monitoring/latest_github_support_snapshot.json`
- Значения:
  - `open_issues_total=0`;
  - `open_pull_requests_total=0`;
  - `recent_closed_bug_incident_total=0`.
### Monitoring policy (unblock gate)
- Cadence: каждые `30` минут.
- Required stable window: минимум `24` часа.
- Unblock thresholds:
  - `ESTAB_TCP_8443 <= 5` на всём стабильном окне;
  - `HY2_LOG_LINES_60M <= 50` и `HY2_ERR_LINES_60M <= 1`;
  - без route/service регрессий;
  - отдельное подтверждение завершения legacy grace period.
### Current decision
- `PHASE 25` остаётся `BLOCKED`.
- Port reclaim apply по-прежнему `not started` до выполнения всех условий.

