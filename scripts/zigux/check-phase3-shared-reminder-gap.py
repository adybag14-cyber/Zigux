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
        "the earlier shared-reminder sentence drift is closed",
        "Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, and zigux/tests/README.md now all state that bounded three-slice posture directly",
        "there is no active shared-reminder sentence cleanup left in this packet today",
        "scripts/zigux/README.md` remains a separate scripts-root reminder surface",
    ),
    VALIDATOR_NOTE_PATH: (
        "one focused helper-local `err_ptr` / `xarray` interop slice with both starter-packet and fixture-backed parity coverage",
        "`Documentation/zigux/phase3-shared-reminder-gap.md` now records that the earlier shared-reminder sentence drift is closed on current `master`",
        "`scripts/zigux/README.md` remains a separate scripts-root reminder surface",
        "Keep any remaining follow-up focused on separate scripts-root inventory drift",
    ),
    DOCS_ROOT_PATH: (
        "one bounded `dev_t` starter packet with its directly readable export shim companion, one focused helper-local `err_ptr` / `xarray` slice, and one focused helper-local policy slice",
        "`zigux/kernel/export_shim.zig`",
        "`Documentation/zigux/phase3-errptr-xarray-slice.md`",
        "`include/zigux/abi.h`",
    ),
    TESTS_ROOT_PATH: (
        "keep the current shared Phase 3 reminder anchored to the bounded `dev_t` starter packet, the helper-local `err_ptr` / `xarray` slice, and the focused policy slice",
        "`Documentation/zigux/phase3-shared-reminder-gap.md` limited to tracking any future shared-surface drift or separate scripts-root inventory follow-through",
        "`zigux/kernel/export_shim.zig`",
        "`include/zigux/abi.h`",
    ),
    REVIEW_CHECKLIST_PATH: (
        "if the change touches the shared Phase 3 ABI packet or a broad reminder surface",
        "`Documentation/zigux/phase3-errptr-xarray-slice.md`",
        "`Documentation/zigux/phase3-policy-slice.md`",
        "keep `Documentation/zigux/phase3-shared-reminder-gap.md` explicit as the tracker for any remaining docs-root or tests-root reminder drift",
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


def _populate_repo(root: Path) -> None:
    for relative_path in (
        GAP_NOTE_PATH,
        VALIDATOR_NOTE_PATH,
        DOCS_ROOT_PATH,
        TESTS_ROOT_PATH,
        REVIEW_CHECKLIST_PATH,
    ):
        source = Path("/workspace/.scratch-l29-reminder-source") / relative_path
        _write(root / relative_path, _read(source))


SELF_TEST_CASES = (
    (
        GAP_NOTE_PATH,
        "there is no active shared-reminder sentence cleanup left in this packet today",
    ),
    (
        VALIDATOR_NOTE_PATH,
        "`Documentation/zigux/phase3-shared-reminder-gap.md` now records that the earlier shared-reminder sentence drift is closed on current `master`",
    ),
    (
        DOCS_ROOT_PATH,
        "one bounded `dev_t` starter packet with its directly readable export shim companion, one focused helper-local `err_ptr` / `xarray` slice, and one focused helper-local policy slice",
    ),
    (
        TESTS_ROOT_PATH,
        "`Documentation/zigux/phase3-shared-reminder-gap.md` limited to tracking any future shared-surface drift or separate scripts-root inventory follow-through",
    ),
    (
        REVIEW_CHECKLIST_PATH,
        "keep `Documentation/zigux/phase3-shared-reminder-gap.md` explicit as the tracker for any remaining docs-root or tests-root reminder drift",
    ),
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