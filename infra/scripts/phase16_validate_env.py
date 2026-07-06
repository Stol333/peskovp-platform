from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import urlparse

REQUIRED_KEYS = (
    "APP_ENV",
    "POSTGRES_USER",
    "POSTGRES_DB",
    "POSTGRES_PASSWORD",
    "DATABASE_URL",
    "REDIS_URL",
    "OPENAI_API_KEY",
    "AI_API_AUTH_TOKEN",
    "AUTH_SECRET",
    "NEXTAUTH_SECRET",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_WEBHOOK_SECRET",
    "PAYMENT_PROVIDER",
)

CORE_SECRET_KEYS = (
    "AUTH_SECRET",
    "NEXTAUTH_SECRET",
    "AI_API_AUTH_TOKEN",
    "POSTGRES_PASSWORD",
)

PLACEHOLDER_MARKERS = (
    "REPLACE_IN_SECRET_MANAGER",
    "REPLACE_WITH_SECURE_RANDOM",
    "CHANGE_ME",
    "YOUR_",
    "TODO",
)


def load_env(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
    return data


def is_placeholder(value: str) -> bool:
    if not value:
        return True
    upper = value.upper()
    return any(marker in upper for marker in PLACEHOLDER_MARKERS)


def validate_internal_urls(env: dict[str, str]) -> list[str]:
    errors: list[str] = []

    db_url = env.get("DATABASE_URL", "")
    redis_url = env.get("REDIS_URL", "")

    db_host = urlparse(db_url).hostname
    redis_host = urlparse(redis_url).hostname

    if db_host != "postgres":
        errors.append("DATABASE_URL должен указывать на internal host 'postgres'.")
    if redis_host != "redis":
        errors.append("REDIS_URL должен указывать на internal host 'redis'.")

    return errors


def validate(path: Path, mode: str) -> tuple[list[str], list[str]]:
    env = load_env(path)
    errors: list[str] = []
    warnings: list[str] = []

    for key in REQUIRED_KEYS:
        if key not in env:
            errors.append(f"Missing required key: {key}")

    if errors:
        return errors, warnings

    errors.extend(validate_internal_urls(env))

    if mode == "production":
        for key in CORE_SECRET_KEYS:
            value = env.get(key, "")
            if is_placeholder(value):
                errors.append(f"Core secret key has placeholder value: {key}")
    else:
        placeholder_count = sum(
            1
            for key, value in env.items()
            if key in CORE_SECRET_KEYS and is_placeholder(value)
        )
        if placeholder_count > 0:
            warnings.append(
                f"Template mode: detected {placeholder_count} core secret placeholder value(s)."
            )

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate PHASE 16 env file.")
    parser.add_argument(
        "--env-file",
        type=Path,
        required=True,
        help="Path to env file",
    )
    parser.add_argument(
        "--mode",
        choices=("template", "production"),
        default="template",
        help="Validation strictness",
    )
    args = parser.parse_args()

    if not args.env_file.exists():
        raise FileNotFoundError(f"Env file not found: {args.env_file}")

    errors, warnings = validate(args.env_file, args.mode)
    for item in warnings:
        print(f"WARNING: {item}")
    if errors:
        for item in errors:
            print(f"ERROR: {item}")
        return 1

    print(f"OK: env validation passed ({args.mode}) for {args.env_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
