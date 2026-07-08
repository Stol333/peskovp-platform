# 38 Web / Telegram / Payments Report
## PHASE 08 — Feature Map
## Product scope split
### Core (must-have before rollout)
- Public web: landing, pricing, features, status, legal, auth entry.
- Client dashboard: subscription status, QR/link, plan/renewal, payment history, support.
- Admin: users/orders/payments/subscriptions, VPN nodes/policies/canary, audit logs.
- Telegram Mini App: auth, plan selection, payment start, subscription retrieval.
- Payments: create order, webhook processing, idempotency, activation on verified success.
- AI support: server-side assistant for profile selection and troubleshooting.
### Canary / optional
- Advanced transport toggles (xHTTP/Trojan optional).
- Experimental policy bundles and adaptive scoring UI widgets.
- Extended premium profile variants.
## Public web feature map
- Pages:
  - `/`
  - `/pricing`
  - `/features`
  - `/status`
  - `/login`
  - `/register`
  - `/legal/privacy`
  - `/legal/terms`
- UX requirements:
  - mobile-first
  - clear CTA to Telegram Mini App and dashboard
  - loading/error/empty states
## Client dashboard feature map
- Routes:
  - `/dashboard`
  - `/dashboard/subscription`
  - `/dashboard/devices`
  - `/dashboard/payments`
  - `/dashboard/support`
  - `/dashboard/ai`
  - `/dashboard/settings`
- Core widgets:
  - active plan + expiry
  - profile selector (`legacy`, `v2_auto`, `v2_mobile_lte`, `v2_ru_whitelist`, `v2_rf_gateway`, `v2_premium`, `v2_canary`)
  - QR and copy link
## Admin feature map
- Routes:
  - `/admin`
  - `/admin/users`
  - `/admin/orders`
  - `/admin/payments`
  - `/admin/subscriptions`
  - `/admin/provisioning`
  - `/admin/vpn`
  - `/admin/ai`
  - `/admin/audit`
  - `/admin/settings`
- VPN sub-screens:
  - nodes
  - port ownership
  - routing policies
  - subscription profiles
  - canary rollout controls
## Telegram Mini App feature map
- Routes:
  - `/tg`
  - `/tg/plans`
  - `/tg/pay`
  - `/tg/subscription`
  - `/tg/support`
- Flow:
  1. validate Telegram initData on backend
  2. choose plan/profile
  3. payment intent/invoice
  4. webhook confirmation
  5. subscription link + QR
## Payments feature map
- Providers:
  - `manual` (baseline)
  - `telegram_stars` (optional integration stage)
  - `yookassa`/`cloudpayments` (when credentials available)
- Required controls:
  - idempotency key
  - event deduplication
  - state machine (`created/pending/succeeded/canceled/refunded/failed`)
## API map (core)
- `/api/health`
- `/api/ready`
- `/api/auth/*`
- `/api/telegram/*`
- `/api/payments/*`
- `/api/subscriptions/*`
- `/api/vpn/*`
- `/api/ai/chat`
- `/api/admin/*`
## Risks and constraints
- Current compose is not production-safe for MAIN due `80/443` publication; must be replaced in PHASE 15.
- Competitor source re-validation is `BLOCKED`; only prior redacted patterns are allowed.
- Legacy VPN/`panel/sub` invariants remain non-negotiable.
## PHASE 09 implementation snapshot
- Реализован `apps/web` Next.js scaffold:
  - `package.json`, `tsconfig.json`, `next.config.mjs`, `tailwind.config.ts`, `postcss.config.mjs`
  - `app/layout.tsx`, `app/globals.css`
- Добавлены обязательные страницы:
  - public: `/`, `/pricing`, `/features`, `/status`, `/login`, `/register`, `/legal/privacy`, `/legal/terms`
  - dashboard: `/dashboard/*`
  - admin: `/admin/*` + VPN sub-screens
  - telegram: `/tg/*`
- Добавлены обязательные API handlers:
  - `/api/health`, `/api/ready`, `/api/auth/session`
  - `/api/telegram/validate-init-data`, `/api/telegram/webhook`
  - `/api/payments/create`, `/api/payments/webhook/telegram`, `/api/payments/webhook/yookassa`
  - `/api/subscriptions/current`, `/api/subscriptions/provision`
  - `/api/vpn/health`, `/api/vpn/subscription-link`
  - `/api/ai/chat`, `/api/admin/metrics`
- Валидация build/typecheck заблокирована: в текущем окружении отсутствуют `pnpm`, `node`, `npm`.
## Gate
- `PHASE 08`: `PASSED`.
- `PHASE 09`: `BLOCKED` (runtime verify невозможен без `pnpm/node/npm` в текущем окружении).
## PHASE 11 implementation snapshot
- Добавлен runtime scaffold Telegram bot:
  - `apps/bot/package.json`
  - `apps/bot/tsconfig.json`
  - `apps/bot/src/config.ts`
  - `apps/bot/src/logger.ts`
  - `apps/bot/src/commands.ts`
  - `apps/bot/src/main.ts`
- Добавлен security package Telegram:
  - `packages/telegram/src/init-data.ts` (HMAC verification + `auth_date` freshness)
  - `packages/telegram/src/redaction.ts` (safe log redaction)
  - `packages/telegram/src/rate-limit.ts` (in-memory limiter)
  - `packages/telegram/src/webhook.ts` (secret token verify)
- Усилены backend маршруты:
  - `/api/telegram/validate-init-data` — только backend verify, no trust to client payload.
  - `/api/telegram/webhook` — secret check + rate limiting + safe logging.
- Создана документация: `docs/TELEGRAM_MINI_APP.md`.
## PHASE 12 implementation snapshot
- Добавлен payment domain package:
  - `packages/payments/src/types.ts`
  - `packages/payments/src/idempotency.ts`
  - `packages/payments/src/state-machine.ts`
  - `packages/payments/src/security.ts`
  - `packages/payments/src/service.ts`
  - `packages/payments/src/manual-provider.ts`
- Добавлен web singleton runtime: `apps/web/src/lib/payment-service.ts`.
- Обновлены payment endpoints:
  - `/api/payments/create` — required `x-idempotency-key`, provider abstraction.
  - `/api/payments/webhook/telegram` — secret verify + idempotent processing.
  - `/api/payments/webhook/yookassa` — secret/HMAC verify + idempotent processing.
- Обновлён `apps/web/src/lib/api-response.ts` для HTTP ошибок `401/409/429/503`.
- Добавлена документация: `docs/PAYMENTS.md`.
## Updated gate status
- `PHASE 11`: `BLOCKED` (runtime smoke test невозможен без `pnpm/node/npm`).
- `PHASE 12`: `BLOCKED` (runtime payment flow verify невозможен без `pnpm/node/npm`).
- Next gate: `PHASE_13_IN_PROGRESS`.
## PHASE 22 — Payment to subscription smoke (closure run)
### Runtime context
- MAIN runtime stack поднят в loopback режиме:
  - `web-app` -> `127.0.0.1:3100`
  - `api` -> `127.0.0.1:18081`
  - `postgres`/`redis` -> healthy.
- Host routes `app/api/admin` переключены с PHASE21 static responses на live backend proxy.
### Smoke results
- Public routes:
  - `https://app.peskovp.com` -> `200`
  - `https://admin.peskovp.com` -> `200`
  - `https://api.peskovp.com` -> `200`
  - `https://api.peskovp.com/api/health` -> `200`
- Payment flow:
  - create intent (`telegram_stars`) -> `created`.
  - repeated create same idempotency key -> `replay` (same payment id).
  - webhook `succeeded` -> subscription activation `true`.
  - repeated webhook same idempotency key -> `replay` (no duplication).
  - webhook `failed` -> activation отсутствует.
  - invalid webhook secret -> HTTP `401`.
- Renewal/expiry check (practical smoke):
  - renew simulated via second successful payment for same user/plan -> activation confirmed;
  - negative/expire-like branch validated via failed payment (no activation).
- Subscription output:
  - `/api/vpn/subscription-link` -> `ok`, `qrAvailable=true`, masked link returned.
- Audit:
  - `payments.audit` events (`intent_created`, `webhook_processed`) присутствуют в логах `web-app`.
### Regression safety
- `panel/sub/default route` поведение сохранено (`404/404/403`).
- MAIN VPN/infra services (`nginx/x-ui/peskovp-sub/peskovp-hy2*`) остаются `active`.
### Evidence
- `artifacts/phase22_v6/phase22_payment_subscription_smoke_evidence.txt`
### Gate decision
- `PHASE 22`: `PASSED`.
