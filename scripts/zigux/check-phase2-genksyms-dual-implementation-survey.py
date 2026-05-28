#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
SURVEY = ROOT / "Documentation" / "zigux" / "phase2-genksyms-dual-implementation-survey.md"

SURVEY_MARKERS = (
    "# Phase 2 genksyms dual-implementation survey",
    "Lane: `P2-L07`",
    "scripts/genksyms/genksyms.c",
    "scripts/zigux/genksyms.zig",
    "selected dual implementations",
    "wrapper-first",
    "scripts/zigux/genksyms_crc.zig",
    "scripts/zigux/check-genksyms-crc-diff.py",
    "scripts/zigux/check-genksyms-bridge.py",
    "wrapper bridge landed, deeper same-family dual-implementation evidence missing.",
    "restore the missing CRC-side tool-plus-checker evidence",
)

EXPECTED_SELF_TEST_CASE_COUNT = 4


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    survey_text = read_text(root / SURVEY.relative_to(ROOT))

    for marker in SURVEY_MARKERS:
        if marker not in survey_text:
            issues.append(("MISSING_SURVEY_MARKER", marker))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_GENKSYMS_SURVEY=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(root / SURVEY.relative_to(ROOT), "\n".join(SURVEY_MARKERS) + "\n")


def expect_issue(root: Path, expected: tuple[str, str]) -> None:
    issues = collect_issues(root)
    assert expected in issues, (expected, issues)


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_p2_genksyms_survey_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        survey_path = root / SURVEY.relative_to(ROOT)
        survey_path.write_text(
            survey_path.read_text(encoding="utf-8").replace(
                "wrapper bridge landed, deeper same-family dual-implementation evidence missing.\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_issue(root, ("MISSING_SURVEY_MARKER", "wrapper bridge landed, deeper same-family dual-implementation evidence missing."))
        checks_run += 1

        build_self_test_root(root)
        survey_path = root / SURVEY.relative_to(ROOT)
        survey_path.write_text(
            survey_path.read_text(encoding="utf-8").replace(
                "scripts/zigux/genksyms_crc.zig\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_issue(root, ("MISSING_SURVEY_MARKER", "scripts/zigux/genksyms_crc.zig"))
        checks_run += 1

        build_self_test_root(root)
        (root / SURVEY.relative_to(ROOT)).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
        else:
            raise AssertionError("missing survey did not abort")
        checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_GENKSYMS_SURVEY_SELF_TEST=pass")
    print(f"PHASE2_GENKSYMS_SURVEY_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the Phase 2 genksyms dual-implementation survey against live wrapper-first repo evidence.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_GENKSYMS_SURVEY=pass")
    print(f"PHASE2_GENKSYMS_SURVEY_MARKER_COUNT={len(SURVEY_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
