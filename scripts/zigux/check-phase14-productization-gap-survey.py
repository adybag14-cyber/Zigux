#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=productization_gap_survey

Fail-closed checker for the current Phase 14 productization-gap reminder.

This guard keeps the productization note aligned with current repo reality:
the shared Makefile now ships `phase14-validate`, while the broader
`phase14-smoke`, `phase14-test`, and `phase14` wrappers remain absent.
"""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


MARKER = "PHASE14_CHECK_PACKET=productization_gap_survey"
SURVEY_PATH = Path("Documentation/zigux/phase14-productization-gap-survey.md")

REQUIRED_MARKERS = [
    "- `zigux/Makefile` is readable again on current `master`, and its live body currently exposes the Phase 2 toolchain and kbuild routes together with the bounded Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 routes plus `phase14-validate`, but no `phase14-smoke`, `phase14-test`, or `phase14` targets",
    "The remaining drift is the split between the directly readable shared-smoke documentation surfaces, the directly readable validator body, the directly readable release-boundary exact-count guard, the readable non-owner Makefile body with shipped Phase 2, Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 routes plus `phase14-validate` but no `phase14-smoke`, `phase14-test`, or `phase14` targets, the directly readable workqueue reviewability shard, and the still-unrecovered executable survey, manifest, and skbuff-side bridge layer beneath them.",
    "the directly readable validator surface, the directly readable release-boundary exact-count guard, the directly readable workqueue reviewability shard, and the current Makefile posture instead of repeating the older story that the broader shared smoke packet is simply unreadable or that the Makefile still ships none of the Phase 14 routes.",
    "the directly readable release-boundary exact-count guard, the directly readable workqueue reviewability shard, and the readable non-owner Makefile posture with shipped Phase 2, Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 routes plus `phase14-validate` but no `phase14-smoke`, `phase14-test`, or `phase14` aligned, or if the missing executable packet members above return through exact current-`master` readback.",
]

FORBIDDEN_MARKERS = [
    "but no `phase14-validate`, `phase14-smoke`, `phase14-test`, or `phase14` targets",
    "the Makefile still ships the old `phase14-*` routes",
]


def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def write_text(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_markers(errors: list[str], rel: Path, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"missing_marker:{rel.as_posix()}:{marker}")


def require_absent(errors: list[str], rel: Path, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker in text:
            errors.append(f"forbidden_marker:{rel.as_posix()}:{marker}")


def check(root: Path) -> list[str]:
    errors: list[str] = []
    if MARKER not in Path(__file__).read_text(encoding="utf-8"):
        errors.append("missing_checker_marker:self")

    if not (root / SURVEY_PATH).exists():
        errors.append(f"missing_file:{SURVEY_PATH.as_posix()}")
        return errors

    survey = read_text(root, SURVEY_PATH)
    require_markers(errors, SURVEY_PATH, survey, REQUIRED_MARKERS)
    require_absent(errors, SURVEY_PATH, survey, FORBIDDEN_MARKERS)
    return errors


def fixture_survey() -> str:
    return "\n".join(
        [
            "# Phase 14 Productization Gap Survey",
            "",
            "## Current Direct-Readback Evidence",
            REQUIRED_MARKERS[0],
            "",
            "## Current Readback Gaps",
            REQUIRED_MARKERS[1],
            "",
            "## Product Judgment",
            REQUIRED_MARKERS[2],
            "",
            "## Recommended Next Bounded Step",
            REQUIRED_MARKERS[3],
            "",
        ]
    )


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    write_text(root, SURVEY_PATH, fixture_survey())


def remove_line(root: Path, rel: Path, marker: str) -> None:
    text = read_text(root, rel)
    updated = text.replace(marker + "\n", "", 1)
    if updated == text:
        updated = text.replace(marker, "", 1)
    write_text(root, rel, updated)


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase14-productization-gap-"))
    try:
        write_fixture_tree(base)
        errors = check(base)
        if errors:
            print("PHASE14_PRODUCTIZATION_GAP_SURVEY_SELF_TEST=fail")
            for error in errors:
                print(error)
            return 1

        write_fixture_tree(base)
        remove_line(base, SURVEY_PATH, REQUIRED_MARKERS[0])
        if not any(REQUIRED_MARKERS[0] in error for error in check(base)):
            print("PHASE14_PRODUCTIZATION_GAP_SURVEY_SELF_TEST=fail")
            print("expected missing phase14-validate marker failure")
            return 1

        write_fixture_tree(base)
        write_text(base, SURVEY_PATH, fixture_survey() + FORBIDDEN_MARKERS[0] + "\n")
        if not any(FORBIDDEN_MARKERS[0] in error for error in check(base)):
            print("PHASE14_PRODUCTIZATION_GAP_SURVEY_SELF_TEST=fail")
            print("expected stale no-phase14-validate wording failure")
            return 1

        print("PHASE14_PRODUCTIZATION_GAP_SURVEY_SELF_TEST=pass")
        print("PHASE14_PRODUCTIZATION_GAP_SURVEY_SELF_TEST_CASE_COUNT=2")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = check(args.root)
    if errors:
        print("PHASE14_PRODUCTIZATION_GAP_SURVEY=fail")
        print("PHASE14_PRODUCTIZATION_GAP_SURVEY_ISSUES_START")
        for error in errors:
            print(error)
        print("PHASE14_PRODUCTIZATION_GAP_SURVEY_ISSUES_END")
        return 1

    print("PHASE14_PRODUCTIZATION_GAP_SURVEY=pass")
    print(f"PHASE14_PRODUCTIZATION_GAP_SURVEY_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print(f"PHASE14_PRODUCTIZATION_GAP_SURVEY_FORBIDDEN_MARKER_COUNT={len(FORBIDDEN_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
