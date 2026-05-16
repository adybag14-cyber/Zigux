#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GAP_NOTE = "Documentation/zigux/phase15-review-checklist-review-process-gap.md"
REVIEW_CHECKLIST = "Documentation/zigux/review-checklist.md"

EXPECTED_GAP_MARKERS = [
    "PHASE15_GAP=review_checklist_review_process_packet",
    "PHASE15_GAP_STATE=open_on_current_master",
    "current `master` already carries the dedicated Architecture Council review-process packet",
    "still lacks the three dedicated shared Phase 15 review-process bullets below",
    "automatic return-to-blocked trigger",
    "trigger-specific refreshed evidence by path",
    "retire or rewrite this gap note instead of leaving it open",
]

REVIEW_PROCESS_BULLETS = [
    "if the change touches the shared Phase 15 Architecture Council review-process packet, are the current roadmap phase and written rationale explicit",
    "if the change touches the shared Phase 15 Architecture Council review-process packet, does the packet name the automatic return-to-blocked trigger",
    "if the change touches the shared Phase 15 Architecture Council review-process packet, are the retained discussion state, the indefinite-C policy link or explicit non-applicability note, and the reopen triggers explicit",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [
        rel_path for rel_path in (GAP_NOTE, REVIEW_CHECKLIST) if not (root / rel_path).exists()
    ]
    if missing_files:
        return missing_files, []

    gap_note = read_text(root, GAP_NOTE)
    review_checklist = read_text(root, REVIEW_CHECKLIST)

    missing_markers = [
        f"gap_note::{marker}" for marker in EXPECTED_GAP_MARKERS if marker not in gap_note
    ]

    missing_bullets = [marker for marker in REVIEW_PROCESS_BULLETS if marker not in review_checklist]
    if missing_bullets:
        if len(missing_bullets) != len(REVIEW_PROCESS_BULLETS):
            missing_markers.append(
                "review_checklist::partial_phase15_review_process_packet_sync"
            )
        if "PHASE15_GAP_STATE=open_on_current_master" not in gap_note:
            missing_markers.append("gap_note::open_gap_state_marker")
    else:
        missing_markers.append(
            "review_checklist::phase15_review_process_gap_already_closed_retire_note"
        )

    return [], missing_markers


def write_file(root: Path, rel_path: str, text: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_self_test() -> int:
    cases_run = 0

    with tempfile.TemporaryDirectory(prefix="phase15-review-checklist-gap-") as tmp:
        root = Path(tmp)

        good_gap = """# Gap

- PHASE15_GAP=review_checklist_review_process_packet
- PHASE15_GAP_STATE=open_on_current_master
- current `master` already carries the dedicated Architecture Council review-process packet
- still lacks the three dedicated shared Phase 15 review-process bullets below
- automatic return-to-blocked trigger
- trigger-specific refreshed evidence by path
- retire or rewrite this gap note instead of leaving it open
"""

        missing_all_checklist = """# Review

- phase 14 packet only
"""

        write_file(root, GAP_NOTE, good_gap)
        write_file(root, REVIEW_CHECKLIST, missing_all_checklist)
        missing_files, missing_markers = validate(root)
        cases_run += 1
        if missing_files or missing_markers:
            print("PHASE15_REVIEW_CHECKLIST_GAP_SELF_TEST=fail")
            print("SELF_TEST_CASE=missing_all_should_pass")
            return 1

        partial_checklist = f"""# Review

- {REVIEW_PROCESS_BULLETS[0]}
"""
        write_file(root, REVIEW_CHECKLIST, partial_checklist)
        _, missing_markers = validate(root)
        cases_run += 1
        if "review_checklist::partial_phase15_review_process_packet_sync" not in missing_markers:
            print("PHASE15_REVIEW_CHECKLIST_GAP_SELF_TEST=fail")
            print("SELF_TEST_CASE=partial_should_fail")
            return 1

        full_checklist = "\n".join(f"- {marker}" for marker in REVIEW_PROCESS_BULLETS) + "\n"
        write_file(root, REVIEW_CHECKLIST, full_checklist)
        _, missing_markers = validate(root)
        cases_run += 1
        if (
            "review_checklist::phase15_review_process_gap_already_closed_retire_note"
            not in missing_markers
        ):
            print("PHASE15_REVIEW_CHECKLIST_GAP_SELF_TEST=fail")
            print("SELF_TEST_CASE=closed_gap_should_fail")
            return 1

    print("PHASE15_REVIEW_CHECKLIST_GAP_SELF_TEST=pass")
    print(f"PHASE15_REVIEW_CHECKLIST_GAP_SELF_TEST_CASES={cases_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 15 review-checklist Architecture Council gap note."
    )
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers = validate(args.repo_root)
    if missing_files:
        print("PHASE15_REVIEW_CHECKLIST_GAP=fail")
        print("MISSING_FILES_START")
        for rel_path in missing_files:
            print(rel_path)
        print("MISSING_FILES_END")
        return 1

    if missing_markers:
        print("PHASE15_REVIEW_CHECKLIST_GAP=fail")
        print("MISSING_MARKERS_START")
        for marker in missing_markers:
            print(marker)
        print("MISSING_MARKERS_END")
        return 1

    print("PHASE15_REVIEW_CHECKLIST_GAP=pass")
    print(f"PHASE15_REVIEW_CHECKLIST_REQUIRED_MARKER_COUNT={len(EXPECTED_GAP_MARKERS)}")
    print(f"PHASE15_REVIEW_CHECKLIST_EXPECTED_BULLET_COUNT={len(REVIEW_PROCESS_BULLETS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
