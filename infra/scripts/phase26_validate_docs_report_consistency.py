from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = (
    "TODO_PLAN_V6_EXECUTION.md",
    "reports/34_v6_implementation_log.md",
    "reports/35_vpn_v2_test_matrix.md",
    "reports/36_vpn_v2_canary_report.md",
    "reports/37_port_reclaim_report.md",
    "reports/38_final_v6_report.md",
    "reports/39_final_v6_execution_report.md",
)

MERGE_CONFLICT_MARKERS = ("<<<<<<<", "=======", ">>>>>>>")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    errors: list[str] = []

    for rel_path in REQUIRED_FILES:
        absolute_path = ROOT / rel_path
        if not absolute_path.exists():
            errors.append(f"[missing-file] {rel_path}")
            continue
        if absolute_path.stat().st_size == 0:
            errors.append(f"[empty-file] {rel_path}")

    todo_plan = ROOT / "TODO_PLAN_V6_EXECUTION.md"
    impl_log = ROOT / "reports/34_v6_implementation_log.md"
    reclaim_report = ROOT / "reports/37_port_reclaim_report.md"

    if todo_plan.exists():
        todo_text = read_text(todo_plan)

        gate_match = re.search(
            r"^## Current gate\s*\n([A-Z0-9_]+)\s*$",
            todo_text,
            flags=re.MULTILINE,
        )
        if gate_match is None:
            errors.append("[gate-format] Не удалось прочитать Current gate из TODO_PLAN_V6_EXECUTION.md")
            current_gate = ""
        else:
            current_gate = gate_match.group(1)

        report_refs = set(re.findall(r"`(reports/[^`]+\.md)`", todo_text))
        missing_report_refs = sorted(
            rel for rel in report_refs if not (ROOT / rel).exists()
        )
        if missing_report_refs:
            errors.append(
                "[missing-referenced-reports] "
                + ", ".join(missing_report_refs)
            )

        if current_gate and impl_log.exists() and reclaim_report.exists():
            impl_text = read_text(impl_log)
            reclaim_text = read_text(reclaim_report)
            if current_gate not in impl_text and current_gate not in reclaim_text:
                errors.append(
                    "[gate-sync] Current gate отсутствует в reports/34_v6_implementation_log.md "
                    "и reports/37_port_reclaim_report.md"
                )

    for rel_path in REQUIRED_FILES:
        absolute_path = ROOT / rel_path
        if not absolute_path.exists():
            continue
        text = read_text(absolute_path)
        for marker in MERGE_CONFLICT_MARKERS:
            if marker in text:
                errors.append(f"[merge-conflict-marker] {rel_path}: найдено '{marker}'")

    if errors:
        print("Docs/report consistency check: FAILED")
        for error in errors:
            print(f" - {error}")
        return 1

    print("Docs/report consistency check: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
