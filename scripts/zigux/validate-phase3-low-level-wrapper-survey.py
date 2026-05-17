#!/usr/bin/env python3
"""Fail-close the current Phase 3 low-level wrapper survey packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


NOTE_PATH = Path("Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md")
ABI_SLICE_PATH = Path("Documentation/zigux/phase3-abi-slice.md")
ATOMIC_PATH = Path("zigux/helpers/atomic.zig")
BARRIER_PATH = Path("zigux/helpers/barrier.zig")
MMIO_PATH = Path("zigux/helpers/mmio.zig")
NARROW_PATH = Path("zigux/unsafe/narrow.zig")

REQUIRED_MARKERS = {
    NOTE_PATH: (
        "PHASE3_LOW_LEVEL_WRAPPER_SCOPE=the roadmap and bootstrap ledger still reserve a bounded Phase 3 low-level wrapper family for approved atomic, barrier, and MMIO wrappers, and current master now directly exposes one atomic helper shard, one barrier helper companion, one MMIO helper companion, one shared narrow-unsafe decoder, this dedicated survey note, and a dedicated survey validator, while the focused replay packet remains absent",
        "PHASE3_LOW_LEVEL_WRAPPER_GAP=direct current-head readback on 2026-05-17 reaches Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md, zigux/helpers/atomic.zig, zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/unsafe/narrow.zig, and scripts/zigux/validate-phase3-low-level-wrapper-survey.py, while repeated authenticated contents reads still return missing for zigux/tests/phase3_low_level_wrappers.zig and zigux/tests/phase3_low_level_wrappers_build.zig",
        "PHASE3_LOW_LEVEL_WRAPPER_NEXT_STEP=keep low-level wrapper follow-through in survey-and-gap-accounting mode with the dedicated survey validator keeping the current helper-trio packet fail-closed until current master materializes the focused replay companion beside zigux/helpers/atomic.zig, zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, and zigux/unsafe/narrow.zig",
        "`zigux/helpers/atomic.zig`",
        "`zigux/helpers/barrier.zig`",
        "`zigux/helpers/mmio.zig`",
        "`zigux/unsafe/narrow.zig`",
        "`scripts/zigux/validate-phase3-low-level-wrapper-survey.py`",
        "`zigux/tests/phase3_low_level_wrappers.zig`",
        "`zigux/tests/phase3_low_level_wrappers_build.zig`",
        "It now also exposes one directly readable MMIO helper companion through `zigux/helpers/mmio.zig`, which keeps volatile register reads, writes, exchange-style updates, and masked register writes reviewable before the focused replay route lands.",
        "Reviewers should treat the low-level wrapper family as materially but not fully materialized on current `master`: one atomic helper shard, one barrier helper companion, one MMIO helper companion, the shared narrow-unsafe decoder, and the dedicated survey validator are directly readable, while the focused replay companions remain current repo-reality gaps.",
    ),
    ABI_SLICE_PATH: (
        "one adjacent low-level-wrapper reminder surface built around the surviving atomic helper shard, one directly readable barrier helper companion, one directly readable MMIO helper companion, the shared unsafe-scope decoder, and the dedicated survey validator",
        "one adjacent low-level-wrapper reminder surface built around zigux/helpers/atomic.zig, zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/unsafe/narrow.zig, and scripts/zigux/validate-phase3-low-level-wrapper-survey.py, but it still lacks the broader shared Phase 3 ABI replay route, the focused low-level-wrapper replay route, the broader export/UAPI layout family, and the wider shared validator packet that earlier shared reminders described",
        "and it separately reaches one adjacent low-level-wrapper reminder surface through Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md, zigux/helpers/atomic.zig, zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/unsafe/narrow.zig, and scripts/zigux/validate-phase3-low-level-wrapper-survey.py, while representative broader Phase 3 paths still remain absent, including zigux/tests/phase3_low_level_wrappers.zig, zigux/tests/phase3_low_level_wrappers_build.zig, scripts/zigux/check-phase3-abi.py, scripts/zigux/validate-phase3.py, and zigux/tests/phase3_export_uapi_layout.zig",
        "`zigux/helpers/mmio.zig`",
        "Current `master` also separately exposes a bounded low-level-wrapper reminder surface through `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `zigux/helpers/atomic.zig`, `zigux/helpers/barrier.zig`, `zigux/helpers/mmio.zig`, `zigux/unsafe/narrow.zig`, and `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`.",
        "one directly readable MMIO helper companion",
        "the bounded low-level-wrapper reminder surface built around `zigux/helpers/atomic.zig`, `zigux/helpers/barrier.zig`, `zigux/helpers/mmio.zig`, `zigux/unsafe/narrow.zig`, the dedicated survey note, and the dedicated survey validator;",
    ),
    ATOMIC_PATH: (
        "pub fn compareExchangeFailureOrderAllowed(success: Ordering, failure: Ordering) bool {",
        'test "phase3 atomic helper keeps compare-exchange ordering rules explicit" {',
    ),
    BARRIER_PATH: (
        "pub fn compiler() void {",
        "pub fn acquire() void {",
        "pub fn release() void {",
        "pub fn full() void {",
        "pub fn acquireRelease() void {",
        "pub fn fullFence() void {",
        'test "phase3 barrier wrappers compile" {',
        'test "phase3 barrier wrappers keep non-mutating full fences reviewable" {',
    ),
    MMIO_PATH: (
        "pub fn read(comptime T: type, ptr: *volatile const T) T {",
        "pub fn write(comptime T: type, ptr: *volatile T, value: T) void {",
        "pub fn exchange(comptime T: type, ptr: *volatile T, value: T) T {",
        "pub fn writeMasked(comptime T: type, ptr: *volatile T, clear_mask: T, set_mask: T) T {",
        'test "phase3 mmio helper keeps volatile register reads and writes reviewable" {',
        'test "phase3 mmio helper keeps exchange-style register updates explicit" {',
        'test "phase3 mmio helper keeps masked register updates reviewable" {',
    ),
    NARROW_PATH: (
        "pub fn scopeFromInteropPolicyBytes(scope: u8, reserved: u8) ?abi.UnsafeScope {",
        'test "phase3 narrow unsafe surface keeps the capability split explicit" {',
    ),
}

SELF_TEST_CASES = (
    (NOTE_PATH, "It now also exposes one directly readable MMIO helper companion through `zigux/helpers/mmio.zig`, which keeps volatile register reads, writes, exchange-style updates, and masked register writes reviewable before the focused replay route lands."),
    (NOTE_PATH, "Reviewers should treat the low-level wrapper family as materially but not fully materialized on current `master`: one atomic helper shard, one barrier helper companion, one MMIO helper companion, the shared narrow-unsafe decoder, and the dedicated survey validator are directly readable, while the focused replay companions remain current repo-reality gaps."),
    (NOTE_PATH, "`zigux/helpers/barrier.zig`"),
    (NOTE_PATH, "`scripts/zigux/validate-phase3-low-level-wrapper-survey.py`"),
    (ABI_SLICE_PATH, "Current `master` also separately exposes a bounded low-level-wrapper reminder surface through `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `zigux/helpers/atomic.zig`, `zigux/helpers/barrier.zig`, `zigux/helpers/mmio.zig`, `zigux/unsafe/narrow.zig`, and `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`."),
    (ABI_SLICE_PATH, "the bounded low-level-wrapper reminder surface built around `zigux/helpers/atomic.zig`, `zigux/helpers/barrier.zig`, `zigux/helpers/mmio.zig`, `zigux/unsafe/narrow.zig`, the dedicated survey note, and the dedicated survey validator;"),
    (BARRIER_PATH, "pub fn acquire() void {"),
    (BARRIER_PATH, "pub fn fullFence() void {"),
    (BARRIER_PATH, 'test "phase3 barrier wrappers compile" {'),
    (BARRIER_PATH, 'test "phase3 barrier wrappers keep non-mutating full fences reviewable" {'),
    (MMIO_PATH, "pub fn read(comptime T: type, ptr: *volatile const T) T {"),
    (MMIO_PATH, "pub fn exchange(comptime T: type, ptr: *volatile T, value: T) T {"),
    (MMIO_PATH, "pub fn writeMasked(comptime T: type, ptr: *volatile T, clear_mask: T, set_mask: T) T {"),
    (MMIO_PATH, 'test "phase3 mmio helper keeps volatile register reads and writes reviewable" {'),
    (MMIO_PATH, 'test "phase3 mmio helper keeps exchange-style register updates explicit" {'),
    (MMIO_PATH, 'test "phase3 mmio helper keeps masked register updates reviewable" {'),
    (NARROW_PATH, "pub fn scopeFromInteropPolicyBytes(scope: u8, reserved: u8) ?abi.UnsafeScope {"),
    (NARROW_PATH, 'test "phase3 narrow unsafe surface keeps the capability split explicit" {'),
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
    for relative_path, markers in REQUIRED_MARKERS.items():
        _write(root / relative_path, "\n".join(markers) + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_low_level_wrapper_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in SELF_TEST_CASES:
            _populate_repo(root)
            path = root / relative_path
            path.write_text(_read(path).replace(marker, "", 1), encoding="utf-8")
            issues = validate_repo(root)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

    print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass")
    print(f"PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES) + 1}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 low-level wrapper survey packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 low-level wrapper survey packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / NOTE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())