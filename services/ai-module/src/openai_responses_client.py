from __future__ import annotations

import json
from collections.abc import Iterator
from typing import Any


class OpenAIResponsesClient:
    def __init__(self, *, api_key: str | None, base_url: str, default_model: str) -> None:
        self._default_model = default_model
        self._ready = False
        self._client: Any = None
        self._init_error: str | None = None

        if not api_key:
            self._init_error = "OPENAI_API_KEY не задан."
            return

        try:
            from openai import OpenAI

            self._client = OpenAI(api_key=api_key, base_url=base_url)
            self._ready = True
        except Exception as exc:  # pragma: no cover - defensive
            self._init_error = f"OpenAI client init failed: {exc}"

    @property
    def is_ready(self) -> bool:
        return self._ready

    @property
    def init_error(self) -> str | None:
        return self._init_error

    def create_response(self, *, messages: list[dict[str, str]], model: str | None = None) -> tuple[str, dict[str, Any]]:
        self._ensure_ready()
        response = self._client.responses.create(
            model=model or self._default_model,
            input=messages,
        )
        text = self._extract_text(response)
        usage = self._extract_usage(response)
        return text, usage

    def create_structured_response(
        self,
        *,
        messages: list[dict[str, str]],
        schema: dict[str, Any],
        model: str | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        self._ensure_ready()
        response = self._client.responses.create(
            model=model or self._default_model,
            input=messages,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "peskovp_ai_structured_output",
                    "schema": schema,
                    "strict": True,
                }
            },
        )
        raw_text = self._extract_text(response)
        usage = self._extract_usage(response)
        data = json.loads(raw_text) if raw_text else {}
        if not isinstance(data, dict):
            raise ValueError("Structured output должен быть JSON-объектом.")
        return data, usage

    def stream_response(self, *, messages: list[dict[str, str]], model: str | None = None) -> Iterator[str]:
        self._ensure_ready()
        chosen_model = model or self._default_model

        try:
            with self._client.responses.stream(model=chosen_model, input=messages) as stream:
                yielded = False
                for event in stream:
                    event_type = getattr(event, "type", "")
                    if event_type in {"response.output_text.delta", "response.refusal.delta"}:
                        delta = getattr(event, "delta", None)
                        if isinstance(delta, str) and delta:
                            yielded = True
                            yield delta

                if not yielded:
                    final_response = stream.get_final_response()
                    fallback_text = self._extract_text(final_response)
                    for chunk in self._chunk_text(fallback_text):
                        yield chunk
        except Exception:
            text, _ = self.create_response(messages=messages, model=chosen_model)
            for chunk in self._chunk_text(text):
                yield chunk

    def _ensure_ready(self) -> None:
        if not self._ready:
            raise RuntimeError(self._init_error or "OpenAI client не готов.")

    @staticmethod
    def _extract_text(response: Any) -> str:
        output_text = getattr(response, "output_text", None)
        if isinstance(output_text, str) and output_text.strip():
            return output_text.strip()

        parts: list[str] = []
        output = getattr(response, "output", None) or []
        for item in output:
            content = getattr(item, "content", None) or []
            for block in content:
                text = getattr(block, "text", None)
                if isinstance(text, str) and text:
                    parts.append(text)
        return "\n".join(parts).strip()

    @staticmethod
    def _extract_usage(response: Any) -> dict[str, Any]:
        usage = getattr(response, "usage", None)
        if not usage:
            return {}
        return {
            "input_tokens": getattr(usage, "input_tokens", None),
            "output_tokens": getattr(usage, "output_tokens", None),
            "total_tokens": getattr(usage, "total_tokens", None),
        }

    @staticmethod
    def _chunk_text(text: str, size: int = 160) -> Iterator[str]:
        if not text:
            return
        start = 0
        while start < len(text):
            yield text[start : start + size]
            start += size
