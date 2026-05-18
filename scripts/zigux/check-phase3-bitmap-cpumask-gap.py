#!/usr/bin/env python3
"""Fail-close the Lane 27 bitmap/cpumask reminder gap note."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


GAP_NOTE_PATH = Path("Documentation/zigux/phase3-bitmap-cpumask-gap.md")

REQUIRED_MARKERS = (
    "PHASE3_BITMAP_CPUMASK_GAP=current master still lacks the bounded bitmap/cpumask helper-local slice",
    "PHASE3_BITMAP_CPUMASK_GAP_DETAIL=direct current-head readback still returns missing for Documentation/zigux/phase3-bitmap-cpumask-slice.md",
    "PHASE3_BITMAP_CPUMASK_NEXT_STEP=land or replay the bounded helper-local bitmap/cpumask packet",
    "`include/zigux/bitmap_cpumask.h`",
    "`zigux/helpers/bitmap_view.zig`",
    "`zigux/helpers/cpumask_view.zig`",
    "`scripts/zigux/check-phase3-bitmap-cpumask.py`",
    "`zig build phase3-bitmap-cpumask --build-file zigux/tests/build.zig`",
    "Do not use the adjacent low-level-wrapper reminder packet or focused export/UAPI layout replay pair as evidence that the bitmap/cpumask slice already landed.",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    path = repo_root / GAP_NOTE_PATH
    try:
        text = read_text(path)
    except FileNotFoundError:
        return [f"missing repo file: {GAP_NOTE_PATH.as_posix()}"]

    for marker in REQUIRED_MARKERS:
        if marker not in text:
            issues.append(f"missing {GAP_NOTE_PATH.as_posix()} marker: {marker}")
    return issues


SELF_TEST_SOURCE = """# Phase 3 Bitmap Cpumask Gap

This note records the current bounded Lane 27 gap on `master`.

## Current Status

- `PHASE3_BITMAP_CPUMASK_GAP=current master still lacks the bounded bitmap/cpumask helper-local slice while the adjacent dev_t, err_ptr/xarray, policy, low-level-wrapper, and focused export/UAPI reminder surfaces already ship`
- `PHASE3_BITMAP_CPUMASK_GAP_DETAIL=direct current-head readback still returns missing for Documentation/zigux/phase3-bitmap-cpumask-slice.md, include/zigux/bitmap_cpumask.h, zigux/uapi/bitmap_cpumask.zig, zigux/bindings/bitmap_cpumask.zig, zigux/helpers/bitmap_view.zig, zigux/helpers/cpumask_view.zig, zigux/tests/phase3_bitmap_cpumask_starter_packet.zig, zigux/tests/phase3_bitmap_cpumask_dump.zig, scripts/zigux/check-phase3-bitmap-cpumask.py, and the combined zig build phase3-bitmap-cpumask --build-file zigux/tests/build.zig route, so current reminder surfaces should keep that packet framed as an unlanded same-lane slice rather than folding it into the shipped helper-local or shared-route inventory`
- `PHASE3_BITMAP_CPUMASK_NEXT_STEP=land or replay the bounded helper-local bitmap/cpumask packet, then refresh the shared reminder surfaces so they promote this slice from tracked gap to shipped Phase 3 evidence`

## Sampled Missing Lane 27 Members

- `Documentation/zigux/phase3-bitmap-cpumask-slice.md`
- `include/zigux/bitmap_cpumask.h`
- `zigux/uapi/bitmap_cpumask.zig`
- `zigux/bindings/bitmap_cpumask.zig`
- `zigux/helpers/bitmap_view.zig`
- `zigux/helpers/cpumask_view.zig`
- `zigux/tests/phase3_bitmap_cpumask_starter_packet.zig`
- `zigux/tests/phase3_bitmap_cpumask_dump.zig`
- `scripts/zigux/check-phase3-bitmap-cpumask.py`
- `zig build phase3-bitmap-cpumask --build-file zigux/tests/build.zig`

## Shared Reminder Boundary

- Keep the current docs-root, tests-root, validator-support, and scripts-root Phase 3 reminder surfaces explicit about the shipped `dev_t`, `err_ptr` / `xarray`, policy, low-level-wrapper, and focused export/UAPI layout packet.
- Keep the bitmap/cpumask slice separate from that shipped packet until direct current-`master` readback returns the helper-local, UAPI, binding, dump, and route surfaces above.
- Do not use the adjacent low-level-wrapper reminder packet or focused export/UAPI layout replay pair as evidence that the bitmap/cpumask slice already landed.
"""


SELF_TEST_CASES = (
    "PHASE3_BITMAP_CPUMASK_GAP=current master still lacks the bounded bitmap/cpumask helper-local slice",
    "`include/zigux/bitmap_cpumask.h`",
    "`scripts/zigux/check-phase3-bitmap-cpumask.py`",
    "`zig build phase3-bitmap-cpumask --build-file zigux/tests/build.zig`",
)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_bitmap_cpumask_gap_") as temp_dir:
        root = Path(temp_dir)
        write_text(root / GAP_NOTE_PATH, SELF_TEST_SOURCE)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_BITMAP_CPUMASK_GAP_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for marker in SELF_TEST_CASES:
            write_text(root / GAP_NOTE_PATH, SELF_TEST_SOURCE.replace(marker, "", 1))
            issues = validate_repo(root)
            expected = f"missing {GAP_NOTE_PATH.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_BITMAP_CPUMASK_GAP_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1
            write_text(root / GAP_NOTE_PATH, SELF_TEST_SOURCE)

    print("PHASE3_BITMAP_CPUMASK_GAP_SELF_TEST=pass")
    print(f"PHASE3_BITMAP_CPUMASK_GAP_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Lane 27 bitmap/cpumask reminder gap note."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the gap note",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_BITMAP_CPUMASK_GAP=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / GAP_NOTE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())