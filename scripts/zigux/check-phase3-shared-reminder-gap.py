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
        "Documentation/zigux/phase3-policy-slice.md",
        "include/zigux/abi.h",
        "zigux/bindings/abi.zig",
        "Documentation/zigux/README.md, zigux/tests/README.md, and Documentation/zigux/review-checklist.md",
        "one narrow reminder-surface cleanup pass",
    ),
    VALIDATOR_NOTE_PATH: (
        "## Focused policy slice present on `master`",
        "Documentation/zigux/README.md`, `zigux/tests/README.md`, and `Documentation/zigux/review-checklist.md` still lag",
        "bounded three-slice posture on current `master`",
    ),
    DOCS_ROOT_PATH: (
        "Phase 3 notes - `Documentation/zigux/phase3-abi-slice.md`",
        "`Documentation/zigux/phase3-errptr-xarray-slice.md`",
        "`include/zigux/abi.h`",
        "`zigux/bindings/abi.zig`",
    ),
    TESTS_ROOT_PATH: (
        "Phase 3 review packet",
        "`Documentation/zigux/phase3-abi-slice.md`",
        "`Documentation/zigux/phase3-errptr-xarray-slice.md`",
        "`include/zigux/abi.h`",
        "`zigux/bindings/abi.zig`",
    ),
    REVIEW_CHECKLIST_PATH: (
        "if the change touches the shared Phase 3 ABI packet or a broad reminder surface",
        "`Documentation/zigux/phase3-errptr-xarray-slice.md`",
        "`Documentation/zigux/README.md` and `zigux/tests/README.md` stay framed as the remaining broader shared reminder surfaces",
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
    (GAP_NOTE_PATH, "one narrow reminder-surface cleanup pass"),
    (VALIDATOR_NOTE_PATH, "## Focused policy slice present on `master`"),
    (DOCS_ROOT_PATH, "`include/zigux/abi.h`"),
    (TESTS_ROOT_PATH, "`zigux/bindings/abi.zig`"),
    (
        REVIEW_CHECKLIST_PATH,
        "`Documentation/zigux/README.md` and `zigux/tests/README.md` stay framed as the remaining broader shared reminder surfaces",
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