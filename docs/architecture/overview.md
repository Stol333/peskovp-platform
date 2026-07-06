# Architecture Overview
Документ фиксирует текущую архитектуру PESKOVP после завершения Phase 13.
## Цели архитектуры
- Сохранять стабильность production VPN-контура.
- Развивать приложение и инфраструктуру рядом с production, не нарушая read-only/backup/safety gate.
- Обеспечить трассируемость решений между `TODO_PLAN.md`, `reports/*` и runtime-проверками.
## Компоненты
- `services/ai-module`:
  - FastAPI сервис;
  - server-side интеграция с OpenAI Responses API;
  - guardrails, rate-limit, usage logging, history.
- `integrations/vpn`:
  - read-only сбор snapshot данных VPN-контура;
  - allowlist endpoint-ов и запрет mutate-операций.
- `docker` + `infra/nginx`:
  - compose-инфраструктура для `ai-module`, `nginx-gateway`, `certbot`, `vpn-readonly`;
  - edge-маршрутизация и TLS baseline.
- Production security layer:
  - SSH hardening include;
  - fail2ban jail для SSH;
  - UFW SSH rate limit;
  - Nginx hardening include.
## Границы ответственности
- Код приложения: `services/ai-module`, `integrations/vpn`.
- Инфраструктура runtime: `docker/*`, `infra/nginx/*`.
- Эксплуатационные проверки и hardening evidence: `reports/*`, `artifacts/*`.
## Текущие ограничения
- На текущем локальном хосте Docker Desktop runtime не стартует.
- Ограничение зафиксировано как waiver и не блокирует фазовое движение.
- Условия снятия waiver описаны в `docs/operations/docker-runtime-waiver.md`.
## Следующий шаг
- Phase 14: закрытие документационных пробелов.
- Phase 15: финальный сводный отчёт и фиксация итогового статуса проекта.
