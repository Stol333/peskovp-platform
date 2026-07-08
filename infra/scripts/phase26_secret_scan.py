from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

SKIP_PATH_PATTERNS = (
    re.compile(r"^\.git/"),
    re.compile(r"^\.next/"),
    re.compile(r"^node_modules/"),
    re.compile(r"^artifacts/"),
    re.compile(r"^\.tmp_phase23_ci_repro/"),
    re.compile(r"^\.tmp_phase23_ci_repro_exact/"),
)

BINARY_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".pdf",
    ".zip",
    ".gz",
    ".tar",
    ".tgz",
    ".7z",
    ".ico",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".mp3",
    ".mp4",
    ".mov",
    ".avi",
    ".dll",
    ".exe",
    ".bin",
}

PRIVATE_KEY_RE = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")
ASSIGNMENT_RE = re.compile(
    r"(?x)\b("
    r"[A-Z][A-Z0-9_]*(?:SECRET|TOKEN|PASSWORD|API_KEY|PRIVATE_KEY|WEBHOOK_SECRET)[A-Z0-9_]*"
    r")\b\s*[:=]\s*(.+)$"
)

ALLOWLIST_VALUE_RE = re.compile(
    r"(?i)^("
    r"replace(_in_secret_manager|_with_secure_random)?|"
    r"change_me|"
    r"ci[-_a-z0-9]*(secret|token|key|password)?|"
    r"example(\.com)?|"
    r"localhost|127\.0\.0\.1|"
    r"dummy|placeholder|unknown|"
    r"\*{3}redacted\*{3}"
    r")$"
)


def get_tracked_files() -> list[Path]:
    completed = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "-z"],
        check=True,
        capture_output=True,
    )
    raw_items = [item for item in completed.stdout.decode("utf-8", errors="ignore").split("\x00") if item]
    return [Path(item) for item in raw_items]


def should_skip(path: Path) -> bool:
    rel = path.as_posix()
    if path.suffix.lower() in BINARY_EXTENSIONS:
        return True
    for pattern in SKIP_PATH_PATTERNS:
        if pattern.search(rel):
            return True
    return False


def normalize_value(raw_value: str) -> str:
    value = raw_value.strip()
    if "#" in value:
        value = value.split("#", 1)[0].strip()
    value = value.rstrip(",;").strip()
    value = value.strip("\"'`").strip()
    value = value.rstrip(",;").strip()
    return value


def looks_like_real_secret(value: str) -> bool:
    if not value:
        return False
    if len(value) < 16:
        return False
    if ALLOWLIST_VALUE_RE.match(value):
        return False
    if any(ch in value for ch in (" ", "\t", "(", ")", "{", "}", "[", "]", ",", ";")):
        return False
    lowered = value.lower()
    if (
        "process.env" in lowered
        or "os.getenv" in lowered
        or "request.headers" in lowered
        or "settings." in lowered
        or "parsed." in lowered
        or lowered.startswith("http://")
        or lowered.startswith("https://")
    ):
        return False
    if value in {"true", "false", "None", "null"}:
        return False
    if value.endswith(")") and "(" in value:
        return False
    classes = 0
    classes += int(any(ch.islower() for ch in value))
    classes += int(any(ch.isupper() for ch in value))
    classes += int(any(ch.isdigit() for ch in value))
    classes += int(any(not ch.isalnum() for ch in value))
    if classes < 2:
        return False
    return True


def main() -> int:
    findings: list[str] = []

    try:
        tracked_files = get_tracked_files()
    except subprocess.CalledProcessError as exc:
        print(f"Secret scan failed to enumerate tracked files: {exc}", file=sys.stderr)
        return 2

    for rel_path in tracked_files:
        if should_skip(rel_path):
            continue

        absolute_path = ROOT / rel_path
        if not absolute_path.exists() or absolute_path.is_dir():
            continue

        try:
            lines = absolute_path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue

        for line_number, line in enumerate(lines, start=1):
            if PRIVATE_KEY_RE.search(line):
                findings.append(
                    f"{rel_path.as_posix()}:{line_number}: private_key_block"
                )
                continue

            assignment_match = ASSIGNMENT_RE.search(line)
            if assignment_match is None:
                continue

            raw_value = assignment_match.group(2)
            value = normalize_value(raw_value)
            if looks_like_real_secret(value):
                findings.append(
                    f"{rel_path.as_posix()}:{line_number}: potential_secret_assignment"
                )

    if findings:
        print("Secret scan: FAILED")
        for finding in findings:
            print(f" - {finding}")
        return 1

    print("Secret scan: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
