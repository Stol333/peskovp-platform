import pytest

from guardrails import GuardrailViolation, validate_user_message


def test_guardrails_blocks_destructive_without_approval() -> None:
    with pytest.raises(GuardrailViolation):
        validate_user_message(
            "Please run rm -rf / and clean everything",
            max_chars=500,
            allow_destructive_tools=False,
        )


def test_guardrails_allows_normal_message() -> None:
    validate_user_message(
        "Покажи безопасный план диагностики проблемы с подключением.",
        max_chars=500,
        allow_destructive_tools=False,
    )
