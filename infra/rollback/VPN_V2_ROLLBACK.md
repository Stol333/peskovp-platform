# VPN V2 Rollback Runbook
## Scope
Rollback для V2 rollout/canary изменений на MAIN и RF.

## Trigger conditions
- Потеря доступности `panel.peskovp.com` или `sub.peskovp.com`.
- Регрессия legacy subscription.
- Рост ошибок V2 canary выше порога.
- Ошибка после конфиг-применения (`xray -test`/`nginx -t`/service crashloop).

## Backup prerequisites
- MAIN snapshot path:
  - `/root/backups/peskovp-platform-prechange-20260706-121952`
- RF snapshot path:
  - `/root/backups/peskovp-platform-prechange-20260706-122147`
- Локальные артефакты:
  - `artifacts/phase3_v6_main/20260706-121946/server_backup`
  - `artifacts/phase3_v6_rf/20260706-122143/server_backup`

## MAIN rollback sequence
1. Восстановить конфиги из snapshot:
   - `/etc/nginx`
   - `/etc/systemd/system`
   - связанные app/config файлы (`x-ui`, `peskovp-sub`, HY2 unit/env при изменениях).
2. Выполнить:
   - `systemctl daemon-reload`
   - `nginx -t`
   - `systemctl restart nginx x-ui peskovp-sub peskovp-hy2 peskovp-hy2-obfs peskovp-hy2-advanced`
3. Проверить:
   - `systemctl is-active ...` (все критичные сервисы),
   - `ss -tulpen` (ожидаемый ownership портов),
   - `ufw status verbose`.

## RF rollback sequence
1. Остановить V2 canary services (если были запущены).
2. Восстановить snapshot-конфиги из `BACKUP_BASE_PATH`.
3. Выполнить:
   - `systemctl daemon-reload`
   - `systemctl restart ssh docker containerd`
   - restart только тех VPN-сервисов, что были добавлены в V2.
4. Закрыть canary firewall ports (если открывались).
5. Проверить:
   - `systemctl is-active ssh docker containerd`,
   - `ss -tulpen`,
   - `ufw status verbose` / `iptables -S`.

## DNS rollback (if needed)
- Если V2 домены вызывают регрессию:
  - временно вернуть `ru.peskovp.com` и `relay-ru.peskovp.com` на стабильную точку маршрутизации,
  - уменьшить TTL до аварийного значения до стабилизации.

## Validation after rollback
- `panel.peskovp.com` доступен.
- `sub.peskovp.com` выдаёт ожидаемый ответ.
- Legacy клиенты могут подключаться.
- Нет новых critical ошибок в `journalctl -p 3`.

## Hard rule
Rollback имеет приоритет над продолжением rollout. Следующий шаг rollout разрешён только после подтверждения стабильности по всем пунктам проверки.

