from __future__ import annotations

import re


class GuardrailViolation(ValueError):
    pass


DESTRUCTIVE_PATTERNS = [
    re.compile(r"\brm\s+-rf\b", re.IGNORECASE),
    re.compile(r"\bdrop\s+database\b", re.IGNORECASE),
    re.compile(r"\bdelete\s+all\b", re.IGNORECASE),
    re.compile(r"\btruncate\b", re.IGNORECASE),
    re.compile(r"\bshutdown\b", re.IGNORECASE),
    re.compile(r"\bformat\s+disk\b", re.IGNORECASE),
]

SECRET_PATTERNS = [
    re.compile(r"OPENAI_API_KEY\s*=", re.IGNORECASE),
    re.compile(r"TELEGRAM_BOT_TOKEN\s*=", re.IGNORECASE),
    re.compile(r"YOOKASSA_SECRET_KEY\s*=", re.IGNORECASE),
    re.compile(r"CLOUDPAYMENTS_API_SECRET\s*=", re.IGNORECASE),
    re.compile(r"Bearer\s+[A-Za-z0-9._\-]{16,}", re.IGNORECASE),
    re.compile(r"sk-[A-Za-z0-9_\-]{20,}", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----", re.IGNORECASE),
]


def validate_user_message(
    message: str,
    *,
    max_chars: int,
    allow_destructive_tools: bool,
) -> None:
    content = message.strip()
    if not content:
        raise GuardrailViolation("Пустое сообщение не допускается.")

    if len(content) > max_chars:
        raise GuardrailViolation(f"Сообщение превышает лимит {max_chars} символов.")

    for pattern in SECRET_PATTERNS:
        if pattern.search(content):
            raise GuardrailViolation("В запросе обнаружен потенциальный секрет. Уберите секрет из текста.")

    if allow_destructive_tools:
        return

    for pattern in DESTRUCTIVE_PATTERNS:
        if pattern.search(content):
            raise GuardrailViolation(
                "Обнаружен destructive intent. Требуется отдельный human approval для таких операций."
            )
