# AI Module API Contract
Актуально для `services/ai-module` после Phase 13.
## Базовые принципы
- API выполняется server-side.
- Секреты (`OPENAI_API_KEY`) только через env.
- Опасные intent-ы проходят через guardrails и approval flow.
## Endpoints
- `GET /health`
  - Назначение: liveness/readiness проверка.
- `POST /v1/ai/respond`
  - Назначение: обычный non-stream ответ.
- `POST /v1/ai/respond/stream`
  - Назначение: stream ответ.
- `POST /v1/ai/respond/structured`
  - Назначение: структурированный JSON output по схеме.
- `GET /v1/ai/history/{session_id}`
  - Назначение: получить in-memory историю сессии.
- `POST /v1/ai/tools/approval-check`
  - Назначение: проверка необходимости human approval для destructive action.
## Эксплуатационные замечания
- Файловая запись usage логов выполняется в JSONL.
- Rate limit применяется по `user_id`.
- История и лимиты в текущей реализации in-memory.
## Валидация
- Unit/regression: `python -m pytest services/ai-module/tests`.
- Compile sanity: `python -m compileall services/ai-module/src`.
