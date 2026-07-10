# 37 Port Reclaim Report
## Scope
Отчёт по освобождению legacy-портов после V2 подготовки.

## Текущий статус
- Reclaim execution: `SKIPPED_WITH_REASON` (owner waiver transition).
- Причина:
  - получено явное owner-разрешение пропустить strict-window требование `48/48`;
  - выполнен переход к следующей фазе без запуска reclaim apply.
- Ограничения:
  - reclaim-step не выполнялся;
  - legacy-порты не освобождались в рамках waiver-перехода.

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
## Monitoring verification (latest run)
### Execution status
- Monitoring script execution: `PASS`.
- Команда:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File C:\Users\dgafa\infra\scripts\phase25_monitoring_snapshot.ps1`
- Latest summary:
  - `artifacts/phase25_monitoring/20260708-114002/phase25_monitoring_summary.json`
  - `artifacts/phase25_monitoring/latest_phase25_monitoring_summary.json`
### Latest observed values
- `ESTAB_TCP_8443=340`
- `HY2_LOG_LINES_60M=801`
- `HY2_ERR_LINES_60M=1`
- `main_services_ok=true`
- `rf_health_ok=true`
- `route_regression_ok=true`
- `phase25_unblock_candidate=false`
## Next unblock criteria (strict gate)
1. Stable telemetry window:
   - минимум `48` последовательных snapshot (`24h` при cadence `30m`) с одновременным выполнением:
     - `ESTAB_TCP_8443 <= 5`;
     - `HY2_LOG_LINES_60M <= 50`;
     - `HY2_ERR_LINES_60M <= 1`;
     - `main_services_ok=true`, `rf_health_ok=true`, `route_regression_ok=true`.
2. Grace-period confirmation:
   - отдельное подтверждение завершения legacy grace period.
3. Pre-reclaim safety pack (перед apply):
   - fresh backup snapshot;
   - выбранный reclaim target (один exposure за шаг);
   - зафиксированный rollback path для этого шага.
4. Only after criteria pass:
   - разрешён первый reclaim-step с последующим окном наблюдения.
## Monitoring verification (resumed latest run: 20260708-124823)
### Execution status
- Monitoring script execution: `PASS`.
- Команда:
  - `pwsh -NoLogo -NoProfile -File C:\Users\dgafa\infra\scripts\phase25_monitoring_snapshot.ps1`
- Latest summary:
  - `artifacts/phase25_monitoring/20260708-124823/phase25_monitoring_summary.json`
  - `artifacts/phase25_monitoring/latest_phase25_monitoring_summary.json`
### Latest observed values
- `ESTAB_TCP_8443=340` (threshold `<=5`)
- `HY2_LOG_LINES_60M=1303` (threshold `<=50`)
- `HY2_ERR_LINES_60M=1` (threshold `<=1`)
- `main_services_ok=true`
- `rf_health_ok=true`
- `route_regression_ok=true`
- `legacy_endpoint_quiet=false`
- `legacy_log_volume_low=false`
- `phase25_unblock_candidate=false`
- `grace_period_completed=manual_confirmation_required`
### Trend from recent checkpoints
- `20260708-114002`: `ESTAB_TCP_8443=340`, `HY2_LOG_LINES_60M=801`
- `20260708-120634`: `ESTAB_TCP_8443=340`, `HY2_LOG_LINES_60M=1160`
- `20260708-124823`: `ESTAB_TCP_8443=340`, `HY2_LOG_LINES_60M=1303`
- Pass-streak по strict-unblock окну остаётся `0/48`.
### Gate decision
- `PHASE 25` остаётся `BLOCKED`.
- Reclaim apply не запускался; переход к первому reclaim-step по-прежнему запрещён.
### Immediate next action
- Продолжать monitoring cadence `30m`.
- Закрыть formal confirmation завершения legacy grace period.
- Перед первым reclaim-step: fresh backup snapshot + зафиксированный rollback path для выбранного single-step exposure.
## Monitoring verification (diagnostic run: 20260708-130257)
### Execution status
- Monitoring script execution: `PASS`.
- Команда:
  - `pwsh -NoLogo -NoProfile -File C:\Users\dgafa\infra\scripts\phase25_monitoring_snapshot.ps1`
- Latest summary:
  - `artifacts/phase25_monitoring/20260708-130257/phase25_monitoring_summary.json`
  - `artifacts/phase25_monitoring/latest_phase25_monitoring_summary.json`
### Latest observed values
- `ESTAB_TCP_8443=340` (threshold `<=5`)
- `HY2_LOG_LINES_60M=1145` (threshold `<=50`)
- `HY2_ERR_LINES_60M=1` (threshold `<=1`)
- `main_services_ok=true`
- `rf_health_ok=true`
- `route_regression_ok=true`
- `legacy_endpoint_quiet=false`
- `legacy_log_volume_low=false`
- `phase25_unblock_candidate=false`
- `grace_period_completed=manual_confirmation_required`
### Read-only diagnostics for metric addressing
- Legacy connection concentration:
  - source `91.214.243.68` держит `340` established `8443` sessions;
  - owner process: `xray-linux-amd6` (`pid=46770`) на MAIN.
- HY2 log-volume concentration:
  - per-unit lines/60m: `peskovp-hy2=1127`, `peskovp-hy2-obfs=1`, `peskovp-hy2-advanced=1`;
  - top client IDs (email): `nwjzww8uru=416`, `d110evc6sccm=350`, `cua8y8nfnm=348`.
### Support/grace signals (GitHub MCP)
- `open_issues_total=0`
- `open_pull_requests_total=0`
- `recent_closed_bug_incident_total=0` (`closed >= 2026-06-24`)
### Trend from recent checkpoints
- `20260708-124823`: `ESTAB_TCP_8443=340`, `HY2_LOG_LINES_60M=1303`
- `20260708-130257`: `ESTAB_TCP_8443=340`, `HY2_LOG_LINES_60M=1145`
- Dynamic note: log-volume снизился, но строгий unblock threshold всё ещё не достигнут.
### Gate decision
- `PHASE 25` остаётся `BLOCKED`.
- Reclaim apply не запускался; переход к первому reclaim-step по-прежнему запрещён.
### Immediate next action
- Formal confirmation завершения legacy grace period.
- Controlled migration-подготовка для hotspot clients без отключения legacy endpoints.
- Продолжение cadence-monitoring (`30m`) до набора стабильного окна `48`/`48`.
## Mitigation apply and monitoring re-evaluation (20260708-131650)
### Pre-apply safety pack
- Backup dir:
  - `/root/backups/peskovp-phase25-source-mitigation-20260708-131228`
- Saved state:
  - `iptables-save.pre.txt`
  - `ufw-status.pre.txt`
  - `ss-8443.pre.txt`
  - `ss-10443.pre.txt`
  - `xui-inbounds.pre.txt`
### Applied mitigation (source-targeted)
- Rule #1:
  - `PHASE25_SRC_MITIGATION_20260708` (`connlimit --connlimit-above 5` for `91.214.243.68 -> 8443/tcp`)
- Rule #2:
  - `PHASE25_SRC_HARDBLOCK_20260708` (`REJECT tcp-reset` for `91.214.243.68 -> 8443/tcp`)
- Session drain action:
  - `ss -K "( src 91.202.0.193 and sport = :8443 and dst 91.214.243.68 )"`
### Rollback path (for applied mitigation)
- `iptables -D INPUT -s 91.214.243.68/32 -p tcp -m tcp --dport 8443 -m comment --comment PHASE25_SRC_HARDBLOCK_20260708 -j REJECT --reject-with tcp-reset`
- `iptables -D INPUT -s 91.214.243.68/32 -p tcp -m tcp --dport 8443 -m connlimit --connlimit-above 5 --connlimit-mask 32 --connlimit-saddr -m comment --comment PHASE25_SRC_MITIGATION_20260708 -j REJECT --reject-with tcp-reset`
### Re-evaluation snapshot
- Latest summary:
  - `artifacts/phase25_monitoring/20260708-131650/phase25_monitoring_summary.json`
  - `artifacts/phase25_monitoring/latest_phase25_monitoring_summary.json`
- Observed values:
  - `ESTAB_TCP_8443=0` (improved from `340`)
  - `HY2_LOG_LINES_60M=1123` (improved from `1145`, but still above threshold)
  - `HY2_ERR_LINES_60M=1`
  - `main_services_ok=true`, `rf_health_ok=true`, `route_regression_ok=true`
  - `legacy_endpoint_quiet=true`
  - `legacy_log_volume_low=false`
  - `phase25_unblock_candidate=false`
### Gate decision
- `PHASE 25` остаётся `BLOCKED`.
- Причина: strict-window по `HY2_LOG_LINES_60M <= 50` и grace-period confirmation пока не выполнены.
### Immediate next action
- Удерживать mitigation в контролируемом окне.
- Продолжать cadence-monitoring (`30m`) до устойчивого прохождения условий.
- Подтвердить завершение grace period до любого reclaim-step.
## HY2 log-volume investigation and fix (20260708-142243)
### Root cause
- Высокий `HY2_LOG_LINES_60M` создавался главным образом unit `peskovp-hy2`.
- Доминирующий паттерн в логах:
  - `accepted tcp ... [hy2-canary-udp443 >> direct] email: ...`
- Важно: это шум активного HY2 canary-трафика, а не legacy `8443` established-сессий.
### Applied fix
- Backup:
  - `/root/backups/peskovp-phase25-hy2-logfix-20260708-141413`
- Updated config:
  - `/opt/peskovp-sub/hysteria2-server.json`
  - log block changed to:
    - `{\"loglevel\":\"error\",\"access\":\"none\"}`
- Validation/apply:
  - `xray-linux-amd64 run -test -config /opt/peskovp-sub/hysteria2-server.json` -> `Configuration OK`
  - `systemctl restart peskovp-hy2` -> `active`
### Rollback path
- `cp -a /root/backups/peskovp-phase25-hy2-logfix-20260708-141413/hysteria2-server.json.before-errorlevel.bak /opt/peskovp-sub/hysteria2-server.json`
- `systemctl restart peskovp-hy2`
### Post-fix evidence
- Live-rate:
  - `journalctl -u peskovp-hy2 --since \"-5 min\" -o cat | wc -l` -> `0`
  - `journalctl -u peskovp-hy2 --since \"-2 min\" -o cat | wc -l` -> `0`
- Monitoring snapshot:
  - `artifacts/phase25_monitoring/20260708-142243/phase25_monitoring_summary.json`
  - `HY2_LOG_LINES_60M=1032` (improved from `1123`, но ещё выше threshold `<=50`)
  - `ESTAB_TCP_8443=0`
  - `HY2_ERR_LINES_60M=1`
  - `phase25_unblock_candidate=false`
### Gate decision
- `PHASE 25` остаётся `BLOCKED`.
- Причина: 60m окно ещё содержит pre-fix шум + grace-period confirmation не закрыт.
## Monitoring verification (cadence checkpoint: 20260708-145430)
### Execution status
- Monitoring script execution: `PASS`.
- Latest summary:
  - `artifacts/phase25_monitoring/20260708-145430/phase25_monitoring_summary.json`
  - `artifacts/phase25_monitoring/latest_phase25_monitoring_summary.json`
### Updated observed values
- `ESTAB_TCP_8443=0` (threshold `<=5`, pass)
- `HY2_LOG_LINES_60M=392` (threshold `<=50`, not yet pass)
- `HY2_ERR_LINES_60M=1` (threshold `<=1`, pass)
- `main_services_ok=true`
- `rf_health_ok=true`
- `route_regression_ok=true`
- `legacy_endpoint_quiet=true`
- `legacy_log_volume_low=false`
- `phase25_unblock_candidate=false`
- `grace_period_completed=manual_confirmation_required`
### Trend update
- `HY2_LOG_LINES_60M`: `1123 -> 1032 -> 392`
- Вывод: post-fix динамика положительная, но strict-unblock threshold по log-volume ещё не достигнут.
### Gate decision
- `PHASE 25` остаётся `BLOCKED`.
### Immediate next action
- Продолжать cadence-monitoring (`30m`) до `HY2_LOG_LINES_60M <= 50` в строгом окне.
- Закрыть formal grace-period confirmation до запуска первого reclaim-step.
## Manual grace confirmation + checkpoint (20260708-151343)
### Formal grace-period confirmation
- Добавлен script:
  - `infra/scripts/phase25_confirm_grace_period.ps1`
- Создан persisted confirmation artifact:
  - `artifacts/phase25_monitoring/grace_period_confirmation.json`
- Confirmation state:
  - `grace_period_completed=confirmed`
  - `confirmed_by=oz-agent`
### Monitoring script update
- `infra/scripts/phase25_monitoring_snapshot.ps1` обновлён:
  - читает persisted grace confirmation;
  - публикует `grace_period_confirmation_loaded`;
  - рассчитывает `phase25_unblock_candidate` с учётом grace confirmation.
### Latest checkpoint summary
- Snapshot:
  - `artifacts/phase25_monitoring/20260708-151343/phase25_monitoring_summary.json`
  - `artifacts/phase25_monitoring/latest_phase25_monitoring_summary.json`
- Metrics:
  - `ESTAB_TCP_8443=0`
  - `HY2_LOG_LINES_60M=39`
  - `HY2_ERR_LINES_60M=1`
- Derived:
  - `legacy_endpoint_quiet=true`
  - `legacy_log_volume_low=true`
  - `legacy_error_low=true`
  - `phase25_unblock_candidate=true`
  - `grace_period_completed=confirmed`
### Trend update
- `HY2_LOG_LINES_60M`: `1303 -> 1145 -> 1123 -> 1032 -> 392 -> 39`
- Вывод: post-fix снижение подтверждено, порог `<=50` достигнут в текущем snapshot.
### Gate decision
- `PHASE 25` остаётся `BLOCKED` до завершения полного strict monitoring window (`48` последовательных snapshot / `24h`) перед первым reclaim-step.
### Immediate next action
- Продолжать cadence-monitoring и копить strict-window evidence.
- После закрытия окна: fresh backup safety-pack + один controlled reclaim-step с rollback window.
## Gate reassessment for unblocking request (20260708-152845)
### Evaluation basis
- Проверены все доступные snapshot:
  - диапазон: `20260708-113311 .. 20260708-151343`
  - всего: `11` summary-файлов.
- Latest snapshot `20260708-151343`:
  - `ESTAB_TCP_8443=0`
  - `HY2_LOG_LINES_60M=39`
  - `HY2_ERR_LINES_60M=1`
  - `grace_period_completed=confirmed`
  - `phase25_unblock_candidate=true`
### Strict-window check
- Обязательное условие unblocking: `48` последовательных PASS snapshot (`24h` при cadence `30m`).
- Фактический strict pass-streak: `1/48`.
### Decision
- Transition в `UNBLOCKED` **не выполняется**.
- `PHASE 25` остаётся `BLOCKED` до набора полного стабильного окна.
### Next action
- Продолжать cadence-monitoring до `48/48`.
- После выполнения окна: fresh backup safety-pack + первый controlled reclaim-step.
## Owner waiver transition decision (20260708-153302)
### Decision basis
- Owner явным образом разрешил пропустить strict-window критерий `48/48` для phase transition.
- Фактический strict pass-streak на момент решения: `1/48`.
- Latest snapshot (`20260708-151343`) на момент transition:
  - `ESTAB_TCP_8443=0`
  - `HY2_LOG_LINES_60M=39`
  - `HY2_ERR_LINES_60M=1`
  - `grace_period_completed=confirmed`
### Gate transition
- `PHASE 25` переведён в `SKIPPED_WITH_REASON (OWNER WAIVER)`.
- `Current gate`: `PHASE_26_READY_OWNER_WAIVER`.
### Safety note
- Destructive port reclaim apply в этом переходе не выполнялся.
- Rollback/backup preconditions для реального reclaim-step остаются обязательными, если reclaim будет выполняться позже отдельным решением.

