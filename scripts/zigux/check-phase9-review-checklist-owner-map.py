#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()

REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
LANE_SEQUENCING_PATH = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"

CHECKLIST_OWNER_MAP_PATH_MARKER = (
    "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`"
)
CHECKLIST_OWNER_MAP_WORDING_MARKER = "dedicated owner-map split recorded in"
CHECKLIST_SHARED_REMINDER_MARKER = (
    "the docs-root, scripts-root, and tests-root shared reminders keep pointing back to "
    "that owner map instead of trying to restate the split from scratch"
)

LANE_NOTE_CHECKLIST_MARKER = (
    "- `Documentation/zigux/review-checklist.md` for the reviewer-facing Phase 9 prompt"
)
LANE_NOTE_SHARED_FOLLOW_THROUGH_MARKER = (
    "the docs root, scripts root, and tests root should keep pointing back here instead "
    "of duplicating those pilot-local reminders."
)
LANE_NOTE_CURRENT_STATE_MARKER = (
    "- `Documentation/zigux/review-checklist.md` now keeps the shared-loader split visible"
)


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / REVIEW_CHECKLIST_PATH).exists() and (candidate / LANE_SEQUENCING_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def ensure_contains(failures: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            failures.append(f"{label}:{marker}")


def ensure_exact_count(failures: list[str], label: str, text: str, marker: str, expected_count: int) -> None:
    actual_count = text.count(marker)
    if actual_count != expected_count:
        failures.append(
            f"{label}_exact_count:{marker}:expected={expected_count}:actual={actual_count}"
        )


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in [REVIEW_CHECKLIST_PATH, LANE_SEQUENCING_PATH]:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    checklist = read_text(root, REVIEW_CHECKLIST_PATH)
    lane_note = read_text(root, LANE_SEQUENCING_PATH)

    ensure_contains(
        failures,
        "review_checklist",
        checklist,
        [
            CHECKLIST_OWNER_MAP_PATH_MARKER,
            CHECKLIST_OWNER_MAP_WORDING_MARKER,
            CHECKLIST_SHARED_REMINDER_MARKER,
        ],
    )
    ensure_exact_count(
        failures,
        "review_checklist",
        checklist,
        CHECKLIST_OWNER_MAP_PATH_MARKER,
        1,
    )
    ensure_exact_count(
        failures,
        "review_checklist",
        checklist,
        CHECKLIST_OWNER_MAP_WORDING_MARKER,
        1,
    )
    ensure_exact_count(
        failures,
        "review_checklist",
        checklist,
        CHECKLIST_SHARED_REMINDER_MARKER,
        1,
    )

    ensure_contains(
        failures,
        "lane_note",
        lane_note,
        [
            LANE_NOTE_CHECKLIST_MARKER,
            LANE_NOTE_SHARED_FOLLOW_THROUGH_MARKER,
            LANE_NOTE_CURRENT_STATE_MARKER,
        ],
    )
    ensure_exact_count(
        failures,
        "lane_note",
        lane_note,
        LANE_NOTE_CHECKLIST_MARKER,
        1,
    )
    ensure_exact_count(
        failures,
        "lane_note",
        lane_note,
        LANE_NOTE_SHARED_FOLLOW_THROUGH_MARKER,
        1,
    )
    return failures


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)

    write_text(
        root / REVIEW_CHECKLIST_PATH,
        "\n".join(
            [
                "# Zigux Review Checklist",
                CHECKLIST_OWNER_MAP_WORDING_MARKER,
                CHECKLIST_OWNER_MAP_PATH_MARKER,
                CHECKLIST_SHARED_REMINDER_MARKER,
                "",
            ]
        ),
    )
    write_text(
        root / LANE_SEQUENCING_PATH,
        "\n".join(
            [
                "# Phase 9 Runtime Pilot Lane Sequencing",
                LANE_NOTE_CHECKLIST_MARKER,
                LANE_NOTE_SHARED_FOLLOW_THROUGH_MARKER,
                LANE_NOTE_CURRENT_STATE_MARKER,
                "",
            ]
        ),
    )


def expect_failure(root: Path, expected_failure: str, case_name: str) -> None:
    failures = validate(root)
    if expected_failure not in failures:
        raise SystemExit(
            f"self_test_case_failed:{case_name}:expected={expected_failure}:actual={failures}"
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase9_review_check_") as tmp_dir:
        root = Path(tmp_dir)

        write_fixture_tree(root)
        failures = validate(root)
        if failures:
            raise SystemExit(f"self_test_fixture_should_pass:{failures}")

        write_fixture_tree(root)
        checklist_path = root / REVIEW_CHECKLIST_PATH
        checklist = checklist_path.read_text(encoding="utf-8")
        checklist_path.write_text(
            checklist.replace(CHECKLIST_OWNER_MAP_PATH_MARKER, "", 1),
            encoding="utf-8",
        )
        expect_failure(
            root,
            f"review_checklist:{CHECKLIST_OWNER_MAP_PATH_MARKER}",
            "missing_checklist_owner_map_path",
        )

        write_fixture_tree(root)
        checklist_path = root / REVIEW_CHECKLIST_PATH
        checklist = checklist_path.read_text(encoding="utf-8")
        checklist_path.write_text(
            checklist + CHECKLIST_SHARED_REMINDER_MARKER + "\n",
            encoding="utf-8",
        )
        expect_failure(
            root,
            (
                "review_checklist_exact_count:"
                f"{CHECKLIST_SHARED_REMINDER_MARKER}:expected=1:actual=2"
            ),
            "duplicate_shared_reminder_marker",
        )

        write_fixture_tree(root)
        lane_note_path = root / LANE_SEQUENCING_PATH
        lane_note = lane_note_path.read_text(encoding="utf-8")
        lane_note_path.write_text(
            lane_note.replace(LANE_NOTE_SHARED_FOLLOW_THROUGH_MARKER, "", 1),
            encoding="utf-8",
        )
        expect_failure(
            root,
            f"lane_note:{LANE_NOTE_SHARED_FOLLOW_THROUGH_MARKER}",
            "missing_lane_note_follow_through_marker",
        )

        write_fixture_tree(root)
        checklist_path = root / REVIEW_CHECKLIST_PATH
        checklist = checklist_path.read_text(encoding="utf-8")
        checklist_path.write_text(
            checklist.replace(CHECKLIST_OWNER_MAP_WORDING_MARKER, "", 1),
            encoding="utf-8",
        )
        expect_failure(
            root,
            f"review_checklist:{CHECKLIST_OWNER_MAP_WORDING_MARKER}",
            "missing_checklist_owner_map_wording",
        )

    print("PHASE9_REVIEW_CHECKLIST_OWNER_MAP_SELF_TEST=pass")
    print("PHASE9_REVIEW_CHECKLIST_OWNER_MAP_SELF_TEST_CASE_COUNT=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the Phase 9 review-checklist owner-map wording against the "
            "shared lane-sequencing note."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate. Defaults to the inferred repository root.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the fixture-backed self-test.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        print("PHASE9_REVIEW_CHECKLIST_OWNER_MAP=fail")
        print("PHASE9_REVIEW_CHECKLIST_OWNER_MAP_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE9_REVIEW_CHECKLIST_OWNER_MAP_FAILURES_END")
        return 1

    print("PHASE9_REVIEW_CHECKLIST_OWNER_MAP=pass")
    print("PHASE9_REVIEW_CHECKLIST_OWNER_MAP_MARKER_COUNT=6")
    return 0


if __name__ == "__main__":
    sys.exit(main())
