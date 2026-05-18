#!/usr/bin/env python3
"""Fail-close the current Phase 3 shared reminder gap note."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


GAP_NOTE_PATH = Path("Documentation/zigux/phase3-shared-reminder-gap.md")
VALIDATOR_NOTE_PATH = Path("Documentation/zigux/phase3-validator-support-surface.md")

GAP_NOTE_MARKERS = (
    "PHASE3_SHARED_REMINDER_GAP=current master now ships the bounded xarray-slot helper-local slice plus its shared starter and dump routes",
    "zigux/helpers/xarray_slot_view.zig",
    "zigux/tests/phase3_xarray_slot_starter_packet.zig",
    "zigux/tests/phase3_xarray_slot_dump.zig",
    "zigux/tests/fixtures/phase3_xarray_slot_manifest.json",
    "scripts/zigux/check-phase3-xarray-slot.py",
    "zig build phase3-xarray-slot-starter-packet --build-file zigux/tests/build.zig",
    "zig build phase3-xarray-slot-dump --build-file zigux/tests/build.zig",
    "Documentation/zigux/README.md",
    "zigux/tests/README.md",
    "Documentation/zigux/review-checklist.md",
)

VALIDATOR_NOTE_MARKERS = (
    "one bounded `xarray_slot` helper-local slice with shared starter and dump routes",
    "zigux/helpers/xarray_slot_view.zig",
    "zigux/tests/phase3_xarray_slot_starter_packet.zig",
    "zigux/tests/phase3_xarray_slot_dump.zig",
    "zigux/tests/fixtures/phase3_xarray_slot_manifest.json",
    "scripts/zigux/check-phase3-xarray-slot.py",
    "Documentation/zigux/phase3-shared-reminder-gap.md",
    "Documentation/zigux/README.md`, `zigux/tests/README.md`, and `Documentation/zigux/review-checklist.md`",
)

REQUIRED_FILES = (
    GAP_NOTE_PATH,
    VALIDATOR_NOTE_PATH,
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []

    for rel_path in REQUIRED_FILES:
        if not (repo_root / rel_path).is_file():
            issues.append(f"missing repo file: {rel_path.as_posix()}")

    if issues:
        return issues

    gap_text = _read(repo_root / GAP_NOTE_PATH)
    for marker in GAP_NOTE_MARKERS:
        if marker not in gap_text:
            issues.append(f"missing {GAP_NOTE_PATH.as_posix()} marker: {marker}")

    validator_text = _read(repo_root / VALIDATOR_NOTE_PATH)
    for marker in VALIDATOR_NOTE_MARKERS:
        if marker not in validator_text:
            issues.append(f"missing {VALIDATOR_NOTE_PATH.as_posix()} marker: {marker}")

    return issues


def _populate_repo(root: Path) -> None:
    gap_text = "\n".join(GAP_NOTE_MARKERS) + "\n"
    validator_text = "\n".join(VALIDATOR_NOTE_MARKERS) + "\n"
    _write(root / GAP_NOTE_PATH, gap_text)
    _write(root / VALIDATOR_NOTE_PATH, validator_text)


SELF_TEST_CASES = (
    (GAP_NOTE_PATH, GAP_NOTE_MARKERS[0]),
    (GAP_NOTE_PATH, GAP_NOTE_MARKERS[6]),
    (GAP_NOTE_PATH, GAP_NOTE_MARKERS[10]),
    (VALIDATOR_NOTE_PATH, VALIDATOR_NOTE_MARKERS[0]),
    (VALIDATOR_NOTE_PATH, VALIDATOR_NOTE_MARKERS[5]),
    (VALIDATOR_NOTE_PATH, VALIDATOR_NOTE_MARKERS[7]),
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
        description="Validate the current Phase 3 shared reminder gap note."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 shared reminder note",
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
