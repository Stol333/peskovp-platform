# Runbook: Node-by-node Debugging
Документирует практику диагностики, применённую в Phase 13.
## Цель
Подтвердить стабильность ключевых узлов и выявить operational шум без destructive действий.
## Минимальный чеклист
- Проверка критичных сервисов:
  - `nginx`, `x-ui`, `peskovp-sub`, `peskovp-hy2*`, `fail2ban`, `ssh`.
- Проверка failed units:
  - `systemctl --failed --no-legend`.
- Проверка sync узла:
  - `peskovp-hy2-sync.service`
  - `peskovp-hy2-sync.timer`.
- Проверка edge/security:
  - `nginx -t`
  - `ufw status verbose`
  - `fail2ban-client status sshd`.
- Проверка локальных прикладных узлов:
  - `pytest` для `services/ai-module` и `integrations/vpn`
  - `compileall` по целевым модулям.
## Интерпретация результатов
- `systemctl --failed` пусто и critical services `active` → базовая узловая стабильность подтверждена.
- `wait-online` в `skipped` по condition при отсутствии деградации сервисов → informational сигнал.
- SSH preauth noise считать operational noise, если SSH service stable и fail2ban jail активен.
## Эскалация
- Если `systemctl --failed` не пусто или critical service не `active`, фиксировать инцидент в `reports/05_implementation_log.md` и запускать отдельный remediation track.
