#!/usr/bin/env python3
"""Fail-close the current Phase 3 shared reminder surfaces."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


GAP_NOTE_PATH = Path("Documentation/zigux/phase3-shared-reminder-gap.md")
VALIDATOR_NOTE_PATH = Path("Documentation/zigux/phase3-validator-support-surface.md")
DOCS_ROOT_PATH = Path("Documentation/zigux/README.md")
TESTS_ROOT_PATH = Path("zigux/tests/README.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")

REQUIRED_MARKERS = {
    GAP_NOTE_PATH: (
        "focused err_ptr/xarray, xarray slot, and policy slices explicit",
        "Documentation/zigux/phase3-xarray-slot-slice.md",
        "Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, and zigux/tests/README.md now all state that bounded four-slice posture directly",
        "There is no active shared-reminder sentence cleanup left in this packet today.",
    ),
    VALIDATOR_NOTE_PATH: (
        "## Focused xarray-slot slice present on `master`",
        "Documentation/zigux/phase3-xarray-slot-slice.md",
        "`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md` now all reflect that bounded four-slice posture",
    ),
    DOCS_ROOT_PATH: (
        "`Documentation/zigux/phase3-xarray-slot-slice.md`",
        "`zigux/helpers/xarray_slot_view.zig`",
        "`scripts/zigux/check-phase3-xarray-slot.py`",
        "one focused helper-local `xarray slot` slice",
    ),
    TESTS_ROOT_PATH: (
        "`Documentation/zigux/phase3-xarray-slot-slice.md`",
        "`zigux/helpers/xarray_slot_view.zig`",
        "`scripts/zigux/check-phase3-xarray-slot.py`",
        "the focused helper-local `xarray slot` slice",
    ),
    REVIEW_CHECKLIST_PATH: (
        "shared Phase 3 reminder packet",
        "`Documentation/zigux/phase3-xarray-slot-slice.md`",
        "`Documentation/zigux/phase3-validator-support-surface.md`",
        "bounded four-slice posture",
    ),
}

SELF_TEST_TEXT = {
    GAP_NOTE_PATH: """
# Phase 3 Shared Reminder Gap
focused err_ptr/xarray, xarray slot, and policy slices explicit
Documentation/zigux/phase3-xarray-slot-slice.md
Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, and zigux/tests/README.md now all state that bounded four-slice posture directly
There is no active shared-reminder sentence cleanup left in this packet today.
""".strip()
    + "\n",
    VALIDATOR_NOTE_PATH: """
# Phase 3 Validator Support Surface
## Focused xarray-slot slice present on `master`
Documentation/zigux/phase3-xarray-slot-slice.md
`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md` now all reflect that bounded four-slice posture
""".strip()
    + "\n",
    DOCS_ROOT_PATH: """
# Zigux Documentation
Phase 3 notes
- `Documentation/zigux/phase3-xarray-slot-slice.md`
- `zigux/helpers/xarray_slot_view.zig`
- `scripts/zigux/check-phase3-xarray-slot.py`
now keep the current Phase 3 reminder surface anchored to one bounded `dev_t` starter packet, one focused helper-local `err_ptr` / `xarray` slice, one focused helper-local `xarray slot` slice, and one focused helper-local policy slice.
""".strip()
    + "\n",
    TESTS_ROOT_PATH: """
# zigux/tests
Phase 3 review packet
  * `Documentation/zigux/phase3-xarray-slot-slice.md`
  * `zigux/helpers/xarray_slot_view.zig`
  * `scripts/zigux/check-phase3-xarray-slot.py`
  * keep the current shared Phase 3 reminder anchored to the bounded `dev_t` starter packet, the helper-local `err_ptr` / `xarray` slice, the focused helper-local `xarray slot` slice, and the focused policy slice.
""".strip()
    + "\n",
    REVIEW_CHECKLIST_PATH: """
# Zigux Review Checklist
  * if the change touches the shared Phase 3 reminder packet, do `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md` still agree with `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-errptr-xarray-slice.md`, `Documentation/zigux/phase3-xarray-slot-slice.md`, `Documentation/zigux/phase3-policy-slice.md`, and `Documentation/zigux/phase3-validator-support-surface.md` on the bounded four-slice posture?
""".strip()
    + "\n",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    for relative_path, markers in REQUIRED_MARKERS.items():
        path = repo_root / relative_path
        try:
            text = _read(path)
        except FileNotFoundError:
            issues.append(f"missing repo file: {relative_path.as_posix()}")
            continue
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {relative_path.as_posix()} marker: {marker}")
    return issues


def _populate_repo(root: Path) -> None:
    for relative_path, text in SELF_TEST_TEXT.items():
        _write(root / relative_path, text)


SELF_TEST_CASES = (
    (GAP_NOTE_PATH, "There is no active shared-reminder sentence cleanup left in this packet today."),
    (VALIDATOR_NOTE_PATH, "## Focused xarray-slot slice present on `master`"),
    (DOCS_ROOT_PATH, "`scripts/zigux/check-phase3-xarray-slot.py`"),
    (TESTS_ROOT_PATH, "`zigux/helpers/xarray_slot_view.zig`"),
    (REVIEW_CHECKLIST_PATH, "bounded four-slice posture"),
)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_shared_reminder_gap_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_SHARED_REMINDER_GAP_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in SELF_TEST_CASES:
            _populate_repo(root)
            path = root / relative_path
            path.write_text(_read(path).replace(marker, "", 1), encoding="utf-8")
            issues = validate_repo(root)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_SHARED_REMINDER_GAP_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

    print("PHASE3_SHARED_REMINDER_GAP_SELF_TEST=pass")
    print(f"PHASE3_SHARED_REMINDER_GAP_SELF_TEST_CASES={len(SELF_TEST_CASES)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 shared reminder surfaces."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 shared reminder surfaces",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_SHARED_REMINDER_GAP=fail")
        for issue in issues:
            print(issue)
        return 1

    for relative_path in REQUIRED_MARKERS:
        print(f"validated {args.repo_root / relative_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
