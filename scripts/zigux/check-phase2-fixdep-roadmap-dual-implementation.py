#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SURVEY_NOTE = ROOT / "Documentation" / "zigux" / "phase2-fixdep-roadmap-dual-implementation-survey.md"

SURVEY_NOTE_MARKERS = (
    "Lane: `P2-L01`",
    "Current `master` already satisfies the roadmap's selected dual-implementation expectation for the bounded `fixdep` lane.",
    "`scripts/zigux/fixdep.zig`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`zigux/tests/fixtures/fixdep/cases.json`",
    "`zig test scripts/zigux/fixdep.zig`",
    "Keep this lane parked unless a new fixdep-local or shared Phase 2 reminder drift reappears.",
)

EXPECTED_SELF_TEST_CASE_COUNT = (
    1
    + len(SURVEY_NOTE_MARKERS)
    + 1
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    survey_note_text = read_text(resolve_path(root, SURVEY_NOTE))
    issues.extend(
        collect_missing_markers(
            survey_note_text,
            SURVEY_NOTE_MARKERS,
            "MISSING_SURVEY_NOTE_MARKERS",
        )
    )
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_FIXDEP_ROADMAP_DUAL_IMPLEMENTATION=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, SURVEY_NOTE), "\n".join(SURVEY_NOTE_MARKERS) + "\n")


def replace_once(text: str, marker: str, replacement: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_p2_fixdep_roadmap_dual_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in SURVEY_NOTE_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, SURVEY_NOTE)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker, ""), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_SURVEY_NOTE_MARKERS", marker) in issues
            checks_run += 1

        build_self_test_root(root)
        resolve_path(root, SURVEY_NOTE).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError(f"missing file did not abort: {SURVEY_NOTE}")

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_FIXDEP_ROADMAP_DUAL_IMPLEMENTATION_SELF_TEST=pass")
    print(f"PHASE2_FIXDEP_ROADMAP_DUAL_IMPLEMENTATION_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the bounded Phase 2 fixdep roadmap dual-implementation survey stays aligned with the shipped reminder surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_FIXDEP_ROADMAP_DUAL_IMPLEMENTATION=pass")
    print(f"PHASE2_FIXDEP_ROADMAP_DUAL_IMPLEMENTATION_MARKER_COUNT={len(SURVEY_NOTE_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
