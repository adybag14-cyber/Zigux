#!/usr/bin/env python3
"""Fail-close the bounded Phase 3 MMIO range-window packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


NOTE_PATH = Path("Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md")
MMIO_PATH = Path("zigux/helpers/mmio.zig")
WRAPPER_REPLAY_PATH = Path("zigux/tests/phase3_low_level_wrappers.zig")
WRAPPER_BUILD_PATH = Path("zigux/tests/phase3_low_level_wrappers_build.zig")

REQUIRED_MARKERS = {
    NOTE_PATH: (
        "Current `master` also keeps `MmioRange`, `rangeScoped()`, `rangeInteropPolicy()`, `rangeInteropPolicyBytes()`, `rangeInteropPolicyByte()`",
        "the bounded low-level-wrapper survey should treat those MMIO range and width-specific wrappers as landed helper-local evidence",
    ),
    MMIO_PATH: (
        "pub const MmioRange = extern struct {",
        "fn validateRangeWindow(base_addr: usize, length: u32) PolicyError!void {",
        "pub fn rangeScoped(base_addr: usize, length: u32, stride: u32, scope: abi.UnsafeScope) PolicyError!MmioRange {",
        "pub fn rangeInteropPolicy(base_addr: usize, length: u32, stride: u32, policy: abi.InteropPolicy) PolicyError!MmioRange {",
        "pub fn rangeInteropPolicyBytes(base_addr: usize, length: u32, stride: u32, unsafe_scope: u8, reserved: u8) PolicyError!MmioRange {",
        "pub fn rangeInteropPolicyByte(base_addr: usize, length: u32, stride: u32, unsafe_scope: u8) PolicyError!MmioRange {",
        "pub fn read8InteropPolicyBytes(base_addr: usize, byte_offset: usize, unsafe_scope: u8, reserved: u8) PolicyError!u8 {",
        "pub fn write16InteropPolicyBytes(base_addr: usize, byte_offset: usize, value: u16, unsafe_scope: u8, reserved: u8) PolicyError!void {",
        "pub fn read32InteropPolicyByte(base_addr: usize, byte_offset: usize, unsafe_scope: u8) PolicyError!u32 {",
        "pub fn write64InteropPolicyBytes(base_addr: usize, byte_offset: usize, value: u64, unsafe_scope: u8, reserved: u8) PolicyError!void {",
        'test "phase3 mmio helper keeps helper-local ranges and width aliases explicit" {',
        'test "phase3 mmio helper rejects overflowing range windows before blessing unsafe access" {',
    ),
    WRAPPER_REPLAY_PATH: (
        'test "phase3 low-level wrappers keep MMIO range helpers and width aliases explicit beside raw bridge gates" {',
        "const scoped_range = try mmio.rangeScoped(base_addr, 16, 4, .volatile_mmio);",
        "const policy_range = try mmio.rangeInteropPolicy(base_addr, 16, 4, mmio_policy);",
        "const bytes_range = try mmio.rangeInteropPolicyBytes(base_addr, 16, 4, mmio_scope, 0);",
        "const byte_range = try mmio.rangeInteropPolicyByte(base_addr, 16, 4, mmio_scope);",
        "try mmio.write64InteropPolicyBytes(base_addr, 8, 0x0123_4567_89AB_CDEF, mmio_scope, 0);",
        "try std.testing.expectError(error.UnsafeScopeDenied, narrow.constPointerAtByte(u32, base_addr + 4, mmio_scope));",
    ),
    WRAPPER_BUILD_PATH: (
        '.root_source_file = b.path("../helpers/mmio.zig"),',
        '.root_source_file = b.path("phase3_low_level_wrappers.zig"),',
        '"phase3-low-level-wrappers-test"',
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
    for relative_path, markers in REQUIRED_MARKERS.items():
        _write(root / relative_path, "\n".join(markers) + "\n")


def run_self_test() -> int:
    cases = tuple(
        (relative_path, marker)
        for relative_path, markers in REQUIRED_MARKERS.items()
        for marker in markers
    )

    with tempfile.TemporaryDirectory(prefix="zigux_phase3_mmio_range_window_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_MMIO_RANGE_WINDOW_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in cases:
            _populate_repo(root)
            path = root / relative_path
            path.write_text(_read(path).replace(marker, "", 1), encoding="utf-8")
            issues = validate_repo(root)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_MMIO_RANGE_WINDOW_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

        _populate_repo(root)
        (root / MMIO_PATH).unlink()
        issues = validate_repo(root)
        expected = f"missing repo file: {MMIO_PATH.as_posix()}"
        if expected not in issues:
            print("PHASE3_MMIO_RANGE_WINDOW_SELF_TEST=fail")
            print("expected missing mmio helper file was not reported")
            return 1

    print("PHASE3_MMIO_RANGE_WINDOW_SELF_TEST=pass")
    print(f"PHASE3_MMIO_RANGE_WINDOW_SELF_TEST_CASE_COUNT={len(cases) + 1}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 MMIO range-window packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the bounded Phase 3 MMIO range-window packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_MMIO_RANGE_WINDOW=fail")
        print("\n".join(issues))
        return 1

    print(f"validated {NOTE_PATH.as_posix()}")
    print(f"validated {MMIO_PATH.as_posix()}")
    print(f"validated {WRAPPER_REPLAY_PATH.as_posix()}")
    print(f"validated {WRAPPER_BUILD_PATH.as_posix()}")
    print("PHASE3_MMIO_RANGE_WINDOW=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
