#!/usr/bin/env python3
"""Fail-close the current Phase 3 shared reminder gap note."""

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
        "PHASE3_SHARED_REMINDER_GAP=current master now keeps the bounded dev_t starter packet plus the focused err_ptr/xarray and policy slices explicit",
        "There is no active shared-reminder sentence cleanup left in this packet today.",
        "broader scripts-root inventory truthfulness work should remain a separate same-lane step.",
    ),
    VALIDATOR_NOTE_PATH: (
        "## Focused policy slice present on `master`",
        "`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md` now all reflect that bounded three-slice posture",
        "`Documentation/zigux/phase3-shared-reminder-gap.md` now records that the earlier shared-reminder sentence drift is closed on current `master`.",
    ),
    DOCS_ROOT_PATH: (
        "Phase 3 notes",
        "`Documentation/zigux/phase3-shared-reminder-gap.md`",
        "keep `Documentation/zigux/phase3-shared-reminder-gap.md` explicit as the tracker for any remaining docs-root or tests-root reminder drift",
    ),
    TESTS_ROOT_PATH: (
        "Phase 3 review packet",
        "keep `Documentation/zigux/phase3-shared-reminder-gap.md` limited to tracking any future shared-surface drift or separate scripts-root inventory follow-through",
        "`Documentation/zigux/README.md` and `Documentation/zigux/review-checklist.md` already carry the bounded three-slice posture",
    ),
    REVIEW_CHECKLIST_PATH: (
        "if the change touches the shared Phase 12 release-planning packet",
        "if the change touches the shared Phase 2 toolchain packet",
        "if the change touches the shared Phase 15 freeze-posture packet",
    ),
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


SAMPLE_FILES = {
    path: "\n".join(markers) + "\n"
    for path, markers in REQUIRED_MARKERS.items()
}

SELF_TEST_CASES = (
    (
        GAP_NOTE_PATH,
        "There is no active shared-reminder sentence cleanup left in this packet today.",
    ),
    (
        VALIDATOR_NOTE_PATH,
        "`Documentation/zigux/phase3-shared-reminder-gap.md` now records that the earlier shared-reminder sentence drift is closed on current `master`.",
    ),
    (
        DOCS_ROOT_PATH,
        "keep `Documentation/zigux/phase3-shared-reminder-gap.md` explicit as the tracker for any remaining docs-root or tests-root reminder drift",
    ),
    (
        TESTS_ROOT_PATH,
        "keep `Documentation/zigux/phase3-shared-reminder-gap.md` limited to tracking any future shared-surface drift or separate scripts-root inventory follow-through",
    ),
    (
        REVIEW_CHECKLIST_PATH,
        "if the change touches the shared Phase 15 freeze-posture packet",
    ),
)


def _populate_repo(root: Path) -> None:
    for relative_path, text in SAMPLE_FILES.items():
        _write(root / relative_path, text)


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
        description="Validate the current Phase 3 shared reminder gap note."
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

    print(f"validated {args.repo_root / GAP_NOTE_PATH}")
    print(f"validated {args.repo_root / VALIDATOR_NOTE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
