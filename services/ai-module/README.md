# AI Module (Phase 7)
## Назначение
Сервисный AI-модуль PESKOVP, работающий только server-side через OpenAI Responses API.

## Реализовано в Phase 7
- Responses API (non-stream + stream).
- Structured outputs (JSON schema).
- Prompt templates из `prompts/`.
- In-memory history по `session_id`.
- Rate limiting по `user_id`.
- Usage logging в JSONL.
- Guardrails (ограничение опасных/destructive запросов).
- Approval gate для destructive tools (без фактического выполнения системных действий).

## Быстрый старт
1. Перейти в каталог `services/ai-module`.
2. Установить зависимости:
   - `pip install -r requirements.txt`
3. Подготовить env:
   - скопировать `.env.example` в `.env`
   - задать `OPENAI_API_KEY`
4. Запуск:
   - `uvicorn src.main:app --host 127.0.0.1 --port 8787 --reload`

## Endpoint-ы
- `GET /health`
- `POST /v1/ai/respond`
- `POST /v1/ai/respond/stream`
- `POST /v1/ai/respond/structured`
- `GET /v1/ai/history/{session_id}`
- `POST /v1/ai/tools/approval-check`

## Безопасность
- Секреты только через env.
- Никаких shell/system действий модулем.
- Destructive intent требует human approval.
