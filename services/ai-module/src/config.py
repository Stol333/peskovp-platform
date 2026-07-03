from pydantic_settings import BaseSettings, SettingsConfigDict


class AISettings(BaseSettings):
    app_env: str = "development"
    ai_provider: str = "openai"
    ai_model: str = "gpt-5"
    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"

    ai_rate_limit_rpm: int = 20
    ai_max_prompt_chars: int = 6000
    ai_history_limit: int = 50
    ai_usage_log_path: str = "services/ai-module/logs/usage.jsonl"
    ai_prompt_dir: str = "services/ai-module/prompts"
    ai_default_template: str = "support_assistant"
    ai_streaming_enabled: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
