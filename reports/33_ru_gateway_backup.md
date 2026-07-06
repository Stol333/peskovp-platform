# 33 RU Gateway Backup Report
## Цель
Подтвердить backup/restore readiness для V2 rollout на MAIN и RF до любых canary-изменений.

## Запущенные команды
- MAIN:
  - `pwsh -NoProfile -File C:\Users\dgafa\infra\scripts\phase3_backup_and_config_apply.ps1 -Mode Apply -RemoteHost 91.202.0.193 -RemoteUser root -SshKeyPath C:\Users\dgafa\.ssh\spain_new -LocalArtifactsDir C:\Users\dgafa\artifacts\phase3_v6_main`
- RF:
  - `pwsh -NoProfile -File C:\Users\dgafa\infra\scripts\phase3_backup_and_config_apply.ps1 -Mode Apply -RemoteHost 138.16.181.33 -RemoteUser root -SshKeyPath C:\Users\dgafa\.ssh\id_ed25519_138_16_181_33_ru -LocalArtifactsDir C:\Users\dgafa\artifacts\phase3_v6_rf`

## Результат
### MAIN backup
- Status: `Apply mode completed successfully`.
- Remote backup path:
  - `/root/backups/peskovp-platform-prechange-20260706-121952`
- Local artifacts:
  - `artifacts/phase3_v6_main/20260706-121946/server_backup`
  - `artifacts/phase3_v6_main/20260706-121946/manifests/phase3_apply_summary.json`
- Подтверждённые файлы:
  - `BACKUP_BASE_PATH.txt`,
  - `app/_etc_x-ui_x-ui.db.bak`,
  - `network/ufw-status.txt`,
  - `containers/docker-ps-a.txt`,
  - `services/*.unit.txt`.

### RF backup
- Status: `Apply mode completed successfully`.
- Remote backup path:
  - `/root/backups/peskovp-platform-prechange-20260706-122147`
- Local artifacts:
  - `artifacts/phase3_v6_rf/20260706-122143/server_backup`
  - `artifacts/phase3_v6_rf/20260706-122143/manifests/phase3_apply_summary.json`
- Подтверждённые файлы:
  - `BACKUP_BASE_PATH.txt`,
  - `network/ufw-status.txt`,
  - `containers/docker-ps-a.txt`,
  - `services/*.unit.txt`.

## Backup quality checks
- Snapshot collected с обеих нод: `PASS`.
- Local download завершён: `PASS`.
- x-ui DB snapshot на MAIN присутствует: `PASS`.
- Manifest paths согласованы с логами запуска: `PASS`.

## Вывод
- Backup gate пройден для MAIN и RF.
- Можно переходить к controlled canary фазе при соблюдении rollback runbook.

