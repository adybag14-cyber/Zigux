#!/usr/bin/env python3
"""Fail-close the remaining shared Phase 3 Lane 30 reminder gap contract."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


REMINDER_GAP_PATH = Path("Documentation/zigux/phase3-shared-reminder-gap.md")
VALIDATOR_NOTE_PATH = Path("Documentation/zigux/phase3-validator-support-surface.md")
STARTER_CHECKER_PATH = Path("scripts/zigux/check-phase3-xarray-slot-starter-packet.py")

REQUIRED_MARKERS = {
    REMINDER_GAP_PATH: (
        "the remaining shared Phase 3 reminder drift is the four-slice truthfulness pass across Documentation/zigux/README.md, zigux/tests/README.md, and Documentation/zigux/review-checklist.md",
        "`Documentation/zigux/README.md` still needs the same four-slice narrowing pass.",
        "`zigux/tests/README.md` still needs the same four-slice narrowing pass.",
        "`Documentation/zigux/review-checklist.md` still needs the same four-slice narrowing pass.",
        "PHASE3_SHARED_REMINDER_GAP_CHECKER=python3 scripts/zigux/check-phase3-shared-reminder-gap.py --self-test",
    ),
    VALIDATOR_NOTE_PATH: (
        "`Documentation/zigux/README.md`, `zigux/tests/README.md`, and `Documentation/zigux/review-checklist.md` still need one narrow truthfulness pass",
        "`Documentation/zigux/phase3-shared-reminder-gap.md` remains the direct-readback tracker for that docs-root, tests-root, and review-checklist four-slice cleanup.",
        "`python3 scripts/zigux/check-phase3-shared-reminder-gap.py --self-test` now fail-closes on this note",
    ),
    STARTER_CHECKER_PATH: (
        "the remaining shared Phase 3 reminder drift is the four-slice truthfulness pass across Documentation/zigux/README.md, zigux/tests/README.md, and Documentation/zigux/review-checklist.md",
        "`Documentation/zigux/README.md`, `zigux/tests/README.md`, and `Documentation/zigux/review-checklist.md` still need one narrow truthfulness pass",
        "Keep the remaining follow-up focused on those three shared reminder surfaces so they stop parking the policy slice and the xarray-slot slice as broader missing routes",
    ),
}

SAMPLE_FILES = {
    path: "\n".join(markers) + "\n"
    for path, markers in REQUIRED_MARKERS.items()
}

SELF_TEST_CASES = (
    (
        REMINDER_GAP_PATH,
        "`Documentation/zigux/README.md` still needs the same four-slice narrowing pass.",
    ),
    (
        REMINDER_GAP_PATH,
        "PHASE3_SHARED_REMINDER_GAP_CHECKER=python3 scripts/zigux/check-phase3-shared-reminder-gap.py --self-test",
    ),
    (
        VALIDATOR_NOTE_PATH,
        "`Documentation/zigux/phase3-shared-reminder-gap.md` remains the direct-readback tracker for that docs-root, tests-root, and review-checklist four-slice cleanup.",
    ),
    (
        VALIDATOR_NOTE_PATH,
        "`python3 scripts/zigux/check-phase3-shared-reminder-gap.py --self-test` now fail-closes on this note",
    ),
    (
        STARTER_CHECKER_PATH,
        "the remaining shared Phase 3 reminder drift is the four-slice truthfulness pass across Documentation/zigux/README.md, zigux/tests/README.md, and Documentation/zigux/review-checklist.md",
    ),
    (
        STARTER_CHECKER_PATH,
        "Keep the remaining follow-up focused on those three shared reminder surfaces so they stop parking the policy slice and the xarray-slot slice as broader missing routes",
    ),
)


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
        description="Validate the remaining shared Phase 3 Lane 30 reminder gap contract."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the shared Phase 3 reminder gap files",
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

    print(f"validated {args.repo_root / REMINDER_GAP_PATH}")
    print(f"validated {args.repo_root / VALIDATOR_NOTE_PATH}")
    print(f"validated {args.repo_root / STARTER_CHECKER_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())