#!/usr/bin/env python3

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
README = ROOT / "README.md"

REQUIRED_HELPER_LINES = (
    "* `check-kconfig-bridge.py`",
    "* `check-phase2-kconfig-selftest-alignment.py`",
)

REQUIRED_PHASE2_LINES = (
    "* `check-phase2-kconfig-selftest-alignment.py --self-test` and `check-phase2-kconfig-selftest-alignment.py` keep `check-kconfig-bridge.py`, `scripts/zigux/validate-phase2.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` aligned around the shipped kconfig self-test hooks before the bridge and Zig replays run, so the shared Phase 2 validator, the Linux-style `phase2-kconfig` route, and the workflow-backed replay surface stay on the same bounded packet.",
    "* `check-kconfig-bridge.py` covers the bounded `kconfig/conf_bridge.zig` and `kconfig/confdata_bridge.zig` bridge lanes.",
)

EXPECTED_SELF_TEST_CASE_COUNT = 6


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_issues(readme_text: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for marker in REQUIRED_HELPER_LINES:
        count = count_exact_lines(readme_text, marker)
        if count != 1:
            issues.append(("HELPER_LINE_COUNT_MISMATCH", f"{marker}:actual={count}:expected=1"))

    for marker in REQUIRED_PHASE2_LINES:
        count = count_exact_lines(readme_text, marker)
        if count != 1:
            issues.append(("PHASE2_LINE_COUNT_MISMATCH", f"{marker}:actual={count}:expected=1"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> None:
    print("PHASE2_KCONFIG_README_ALIGNMENT=fail")
    for code, detail in issues:
        print(f"{code}={detail}")


def run_self_test() -> int:
    checks_run = 0
    base_lines = [
        "# scripts/zigux",
        "",
        "Current bootstrap helpers",
        *REQUIRED_HELPER_LINES,
        "",
        "Phase 2 flow",
        *REQUIRED_PHASE2_LINES,
        "",
    ]
    base_text = "\n".join(base_lines)

    assert collect_issues(base_text) == []
    checks_run += 1

    missing_helper = base_text.replace(REQUIRED_HELPER_LINES[1] + "\n", "", 1)
    issues = collect_issues(missing_helper)
    assert ("HELPER_LINE_COUNT_MISMATCH", f"{REQUIRED_HELPER_LINES[1]}:actual=0:expected=1") in issues
    checks_run += 1

    duplicate_helper = base_text + REQUIRED_HELPER_LINES[0] + "\n"
    issues = collect_issues(duplicate_helper)
    assert ("HELPER_LINE_COUNT_MISMATCH", f"{REQUIRED_HELPER_LINES[0]}:actual=2:expected=1") in issues
    checks_run += 1

    missing_phase2 = base_text.replace(REQUIRED_PHASE2_LINES[1] + "\n", "", 1)
    issues = collect_issues(missing_phase2)
    assert ("PHASE2_LINE_COUNT_MISMATCH", f"{REQUIRED_PHASE2_LINES[1]}:actual=0:expected=1") in issues
    checks_run += 1

    duplicate_phase2 = base_text + REQUIRED_PHASE2_LINES[0] + "\n"
    issues = collect_issues(duplicate_phase2)
    assert ("PHASE2_LINE_COUNT_MISMATCH", f"{REQUIRED_PHASE2_LINES[0]}:actual=2:expected=1") in issues
    checks_run += 1

    with tempfile.TemporaryDirectory(prefix="zigux_phase2_kconfig_readme_alignment_") as tmp_dir_str:
        readme_path = Path(tmp_dir_str) / "README.md"
        readme_path.write_text(base_text, encoding="utf-8")
        issues = collect_issues(read_text(readme_path))
        assert issues == []
        checks_run += 1

    if checks_run != EXPECTED_SELF_TEST_CASE_COUNT:
        print("PHASE2_KCONFIG_README_ALIGNMENT_SELF_TEST=fail")
        print(f"PHASE2_KCONFIG_README_ALIGNMENT_SELF_TEST_CASE_COUNT_ACTUAL={checks_run}")
        print(f"PHASE2_KCONFIG_README_ALIGNMENT_SELF_TEST_CASE_COUNT_EXPECTED={EXPECTED_SELF_TEST_CASE_COUNT}")
        return 1

    print("PHASE2_KCONFIG_README_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_KCONFIG_README_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the Phase 2 kconfig scripts README packet stays aligned.")
    parser.add_argument("--readme", type=Path, default=README, help="Override README path")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage without repo files")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(read_text(args.readme))
    if issues:
        emit_issues(issues)
        return 1

    print("PHASE2_KCONFIG_README_ALIGNMENT=pass")
    print(f"README={args.readme}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
