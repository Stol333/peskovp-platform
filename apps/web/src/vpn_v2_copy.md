# VPN V2 UI Copy Draft
## Rollout panel
- Заголовок: `VPN V2 Controlled Rollout`.
- Подзаголовок: `Изменения применяются поэтапно и обратимы через rollback runbook`.
- Тултип canary: `Изменение затрагивает только cohort в пределах заданного процента`.

## Subscription preview
- Блок `Recommended profiles`:
  - `V2 Canary`
  - `V2 Auto`
  - `LTE Safe`
  - `RU Direct + Proxy Mix`
  - `Legacy Stable (fallback)`
- Warning:
  - `Legacy route остаётся доступным до завершения миграции`.

## Telegram Mini App
- CTA:
  - `Открыть Mini App`
  - `Получить V2 профиль`
- Diagnostics text:
  - `Если подключение нестабильно, переключитесь на Legacy Stable`.

