#!/usr/bin/env python3
"""Check that the Phase 2 fixdep parity runner keeps deterministic replay guards."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

FIXDEP_DIFF_REL = Path("scripts/zigux/check-fixdep-diff.py")

REQUIRED_EXACT_LINES = (
    "compare_returncode(f\"{case['name']} Zig\", expected_exit_code, zig_result.returncode)",
    "compare_returncode(f\"{case['name']} Zig repeat\", zig_result.returncode, zig_repeat_result.returncode)",
    "diff_text(expected_stdout, zig_actual)",
    "diff_text(expected_stdout, zig_repeat)",
    "diff_text(zig_actual, zig_repeat)",
    "diff_text(expected_stderr_path, zig_actual_stderr)",
    "diff_text(expected_stderr_path, zig_repeat_stderr)",
    "diff_text(zig_actual_stderr, zig_repeat_stderr)",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    fixdep_diff = read_text(root / FIXDEP_DIFF_REL)
    issues: list[tuple[str, str]] = []
    for marker in REQUIRED_EXACT_LINES:
        count = count_exact_lines(fixdep_diff, marker)
        if count == 0:
            issues.append(("MISSING_FIXDEP_DETERMINISM_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_FIXDEP_DETERMINISM_LINE", f"{marker}:count={count}"))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_FIXDEP_DETERMINISM_CONTRACT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_minimal_packet(root: Path) -> None:
    path = root / FIXDEP_DIFF_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(REQUIRED_EXACT_LINES) + "\n", encoding="utf-8")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_fixdep_determinism_contract_") as tmp_dir:
        root = Path(tmp_dir)

        write_minimal_packet(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in REQUIRED_EXACT_LINES:
            write_minimal_packet(root)
            path = root / FIXDEP_DIFF_REL
            path.write_text(read_text(path).replace(marker + "\n", "", 1), encoding="utf-8")
            assert ("MISSING_FIXDEP_DETERMINISM_LINE", marker) in collect_issues(root)
            checks_run += 1

        write_minimal_packet(root)
        duplicate_marker = REQUIRED_EXACT_LINES[0]
        path = root / FIXDEP_DIFF_REL
        path.write_text(read_text(path) + duplicate_marker + "\n", encoding="utf-8")
        assert (
            "DUPLICATE_FIXDEP_DETERMINISM_LINE",
            f"{duplicate_marker}:count=2",
        ) in collect_issues(root)
        checks_run += 1

    print("PHASE2_FIXDEP_DETERMINISM_CONTRACT_SELF_TEST=pass")
    print(f"PHASE2_FIXDEP_DETERMINISM_CONTRACT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the fixdep parity runner keeps deterministic replay contracts."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_FIXDEP_DETERMINISM_CONTRACT=pass")
    print(f"PHASE2_FIXDEP_DETERMINISM_CONTRACT_REQUIRED_LINE_COUNT={len(REQUIRED_EXACT_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
