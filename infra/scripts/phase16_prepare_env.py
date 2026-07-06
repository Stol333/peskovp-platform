from __future__ import annotations

import argparse
import secrets
from pathlib import Path

AUTO_GENERATED_SECRET_KEYS = (
    "POSTGRES_PASSWORD",
    "AUTH_SECRET",
    "NEXTAUTH_SECRET",
    "AI_API_AUTH_TOKEN",
    "VPN_V2_CANARY_SALT",
)

PLACEHOLDER_MARKERS = (
    "REPLACE_IN_SECRET_MANAGER",
    "REPLACE_WITH_SECURE_RANDOM",
    "CHANGE_ME",
)


def read_env_file(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def parse_key_value(line: str) -> tuple[str, str] | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or "=" not in stripped:
        return None
    key, value = stripped.split("=", 1)
    return key.strip(), value.strip()


def should_generate(value: str) -> bool:
    if not value:
        return True
    upper = value.upper()
    return any(marker in upper for marker in PLACEHOLDER_MARKERS)


def generate_secret(length_bytes: int = 48) -> str:
    return secrets.token_urlsafe(length_bytes)


def prepare_env(template: Path, output: Path) -> tuple[int, int]:
    lines = read_env_file(template)
    updated_lines: list[str] = []
    generated_count = 0
    present_count = 0
    generated_values: dict[str, str] = {}

    for line in lines:
        parsed = parse_key_value(line)
        if parsed is None:
            updated_lines.append(line)
            continue

        key, value = parsed
        if key in AUTO_GENERATED_SECRET_KEYS:
            present_count += 1
            if should_generate(value):
                new_value = generate_secret()
                updated_lines.append(f"{key}={new_value}")
                generated_values[key] = new_value
                generated_count += 1
            else:
                generated_values[key] = value
                updated_lines.append(line)
            continue

        if key == "DATABASE_URL" and should_generate(value):
            pg_password = generated_values.get("POSTGRES_PASSWORD")
            if pg_password:
                updated_lines.append(
                    f"DATABASE_URL=postgresql://peskovp:{pg_password}@postgres:5432/peskovp"
                )
                continue

        updated_lines.append(line)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")
    return present_count, generated_count


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare server-only .env.production from template without printing secret values."
    )
    parser.add_argument(
        "--template",
        type=Path,
        default=Path("docker/env/prod.env.example"),
        help="Path to env template",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Target env file path (server-only)",
    )
    args = parser.parse_args()

    if not args.template.exists():
        raise FileNotFoundError(f"Template file not found: {args.template}")

    present_count, generated_count = prepare_env(args.template, args.output)
    print(
        f"Prepared env file: {args.output} "
        f"(auto-secret keys found: {present_count}, generated: {generated_count})."
    )
    print("Note: Fill external provider secrets manually from secret manager.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
