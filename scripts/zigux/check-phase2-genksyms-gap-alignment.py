#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
CLOSURE = Path("Documentation/zigux/phase2-closure.md")
SURVEY = Path("Documentation/zigux/phase2-genksyms-dual-implementation-survey.md")

CLOSURE_MARKERS = (
    "## Next Step",
    "If the `genksyms` lane resumes substantive implementation instead of closure upkeep, start with one smallest same-family step around the still-missing CRC-side evidence recorded in the survey rather than widening this shared note again.",
)

SURVEY_MARKERS = (
    "# Phase 2 genksyms dual-implementation survey",
    "Authenticated current-`master` reads for `scripts/zigux/genksyms_crc.zig` and `scripts/zigux/check-genksyms-crc-diff.py` return missing.",
    "wrapper bridge landed, deeper same-family dual-implementation evidence missing.",
    "If the lane next does reminder-surface upkeep instead of CRC restoration, wire the dedicated survey checker into the shared `phase2-genksyms` replay surfaces so the current wrapper-first packet and the dual-implementation gap statement cannot silently drift apart.",
)

EXPECTED_SELF_TEST_CASE_COUNT = 5


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_root(root: Path) -> None:
    closure_text = """# Phase 2 Closure

## Next Step

Keep the shared Phase 2 closure packet parked unless one shared reminder surface drifts again. If the kconfig bridge lane resumes substantive implementation instead of closure upkeep, start with one smallest same-family step that preserves the live split between request-plan overrides, the non-empty sentinel packet, and helper-local explicit-override coverage, then add a direct `conf.c` / `confdata.c` provenance anchor once those C sources are readable in-tree again on current `master`. If the `genksyms` lane resumes substantive implementation instead of closure upkeep, start with one smallest same-family step around the still-missing CRC-side evidence recorded in the survey rather than widening this shared note again.
"""
    survey_text = """# Phase 2 genksyms dual-implementation survey

- Authenticated current-`master` reads for `scripts/zigux/genksyms_crc.zig` and `scripts/zigux/check-genksyms-crc-diff.py` return missing.
- The truthful current state for lane `P2-L07` is therefore: wrapper bridge landed, deeper same-family dual-implementation evidence missing.
- If the lane next does reminder-surface upkeep instead of CRC restoration, wire the dedicated survey checker into the shared `phase2-genksyms` replay surfaces so the current wrapper-first packet and the dual-implementation gap statement cannot silently drift apart.
"""
    write_text(root / CLOSURE, closure_text)
    write_text(root / SURVEY, survey_text)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    closure_text = read_text(root / CLOSURE)
    survey_text = read_text(root / SURVEY)

    for marker in CLOSURE_MARKERS:
        if marker not in closure_text:
            issues.append(("MISSING_CLOSURE_MARKER", marker))

    for marker in SURVEY_MARKERS:
        if marker not in survey_text:
            issues.append(("MISSING_SURVEY_MARKER", marker))

    if CLOSURE_MARKERS[1] in closure_text and SURVEY_MARKERS[1] not in survey_text:
        issues.append(("MISSING_SHARED_CRC_GAP_ALIGNMENT", SURVEY_MARKERS[1]))

    if CLOSURE_MARKERS[1] in closure_text and SURVEY_MARKERS[2] not in survey_text:
        issues.append(("MISSING_SHARED_GAP_STATE_ALIGNMENT", SURVEY_MARKERS[2]))

    if CLOSURE_MARKERS[1] in closure_text and SURVEY_MARKERS[3] not in survey_text:
        issues.append(("MISSING_SHARED_NEXT_STEP_ALIGNMENT", SURVEY_MARKERS[3]))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_GENKSYMS_GAP_ALIGNMENT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_p2_genksyms_gap_alignment_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_sample_root(root)
        write_text(root / CLOSURE, read_text(root / CLOSURE).replace("still-missing CRC-side evidence recorded in the survey", "missing survey note", 1))
        assert ("MISSING_CLOSURE_MARKER", CLOSURE_MARKERS[1]) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        write_text(root / SURVEY, read_text(root / SURVEY).replace(SURVEY_MARKERS[1] + "\n", "", 1))
        issues = collect_issues(root)
        assert ("MISSING_SURVEY_MARKER", SURVEY_MARKERS[1]) in issues
        assert ("MISSING_SHARED_CRC_GAP_ALIGNMENT", SURVEY_MARKERS[1]) in issues
        checks_run += 1

        build_sample_root(root)
        write_text(root / SURVEY, read_text(root / SURVEY).replace(SURVEY_MARKERS[2] + "\n", "", 1))
        issues = collect_issues(root)
        assert ("MISSING_SURVEY_MARKER", SURVEY_MARKERS[2]) in issues
        assert ("MISSING_SHARED_GAP_STATE_ALIGNMENT", SURVEY_MARKERS[2]) in issues
        checks_run += 1

        build_sample_root(root)
        (root / SURVEY).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
        else:
            raise AssertionError("missing survey did not abort")
        checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_GENKSYMS_GAP_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_GENKSYMS_GAP_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Lane 22 Phase 2 closure note against the dedicated genksyms dual-implementation survey."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a compact passing sample root for validation and exit",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_GENKSYMS_GAP_ALIGNMENT_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_GENKSYMS_GAP_ALIGNMENT=pass")
    print(f"PHASE2_GENKSYMS_GAP_ALIGNMENT_CLOSURE_MARKER_COUNT={len(CLOSURE_MARKERS)}")
    print(f"PHASE2_GENKSYMS_GAP_ALIGNMENT_SURVEY_MARKER_COUNT={len(SURVEY_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
