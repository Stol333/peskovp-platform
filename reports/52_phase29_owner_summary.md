# PHASE 29 — Owner Summary
Production status: `PARTIAL_READY`
Public URLs:
- `https://app.peskovp.com`
- `https://admin.peskovp.com`
- `https://api.peskovp.com`
- `https://app.peskovp.com/telegram-miniapp-v2.html`
- `https://app.peskovp.com/tg`
Telegram status:
- `PASS` для entry routes и backend fail-closed initData validation.
Payment status:
- `PASS` для create/idempotency/webhook security/activation semantics.
VPN status:
- `PASS` для RF runtime health (`xray active`, config test ok, required ports listening).
Routing status:
- `LIMITED_CANARY_5_HOLD` (legacy fallback активен; массовый rollout не запускался).
Rollback location:
- `infra/rollback/PHASE29_PRODUCTION_ROLLBACK.md`
- `infra/scripts/phase29_rollback.sh`
Monitoring location:
- `docs/OPERATIONS_PHASE29.md`
- `infra/scripts/phase29_healthcheck.sh`
- `infra/scripts/phase29_e2e_smoke.sh`
Known risks:
- Нет dedicated foreign-exit узла (блокер premium multi-route).
- Rollout выше `5%` не подтверждён в текущем gate.
- Port reclaim не выполнялся (`NO_RECLAIM_YET`).
Next owner actions:
- Подтвердить/отложить следующий rollout step (`10%`) после расширенного стабильного окна.
- Принять решение по отдельному foreign-exit node deployment.
- Вернуться к controlled reclaim только после отдельного safety approval.
