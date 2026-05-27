#!/usr/bin/env python3
"""Fail-close the current Phase 3 low-level-wrapper compile-route packet."""

from __future__ import annotations

import argparse
import os
import subprocess
import tempfile
from pathlib import Path

REPLAY_PATH = Path("zigux/tests/phase3_low_level_wrappers.zig")
FOCUSED_BUILD_PATH = Path("zigux/tests/phase3_low_level_wrappers_build.zig")
SHARED_BUILD_PATH = Path("zigux/tests/build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
ATOMIC_HELPER_PATH = Path("zigux/helpers/atomic.zig")
BARRIER_HELPER_PATH = Path("zigux/helpers/barrier.zig")
MMIO_HELPER_PATH = Path("zigux/helpers/mmio.zig")

REQUIRED_MARKERS = {
    REPLAY_PATH: (
        'const atomic = @import("atomic");',
        'const barrier = @import("barrier");',
        'const mmio = @import("mmio");',
        'test "phase3 low-level wrappers keep MMIO range helpers and width aliases explicit beside raw bridge gates" {',
        'test "phase3 low-level wrappers keep atomic order-gate failures explicit before MMIO publish" {',
    ),
    FOCUSED_BUILD_PATH: (
        '.root_source_file = b.path("phase3_low_level_wrappers.zig"),',
        'root_module.addImport("atomic", atomic);',
        'root_module.addImport("barrier", barrier);',
        'root_module.addImport("mmio", mmio);',
        '"phase3-low-level-wrappers-test"',
    ),
    SHARED_BUILD_PATH: (
        "const phase3_low_level_wrappers = addPhase3LowLevelWrappers(b, target, optimize);",
        '"phase3-low-level-wrappers"',
        "phase3_test_step.dependOn(&phase3_low_level_wrappers.step);",
    ),
    MAKEFILE_PATH: (
        "phase3-low-level-wrappers:",
        "phase3-low-level-wrappers-test:",
        "$(ZIG) build phase3-low-level-wrappers --build-file zigux/tests/build.zig",
        "$(ZIG) build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    ),
    ATOMIC_HELPER_PATH: (
        "pub fn validateCompareExchangeOrders(",
        "pub fn load(comptime T: type, ptr: *const T, comptime order: Ordering) LoadError!T {",
        "pub fn fetchMax(",
    ),
    BARRIER_HELPER_PATH: (
        "pub fn fence(comptime order: Ordering) FenceError!void {",
        "pub fn storeLoad() void {",
        'test "phase3 barrier wrappers keep seq-cst aliases aligned" {',
    ),
    MMIO_HELPER_PATH: (
        "pub fn rangeScoped(base_addr: usize, length: u32, stride: u32, scope: abi.UnsafeScope) PolicyError!MmioRange {",
        "pub fn constPointerAt(comptime T: type, range: MmioRange, byte_offset: usize) PolicyError!*const volatile T {",
        "pub fn pointerAt(comptime T: type, range: MmioRange, byte_offset: usize) PolicyError!*volatile T {",
        "pub fn readAt(comptime T: type, range: MmioRange, byte_offset: usize) PolicyError!T {",
        "pub fn writeAt(comptime T: type, range: MmioRange, byte_offset: usize, value: T) PolicyError!void {",
        "pub fn exchangeAt(comptime T: type, range: MmioRange, byte_offset: usize, value: T) PolicyError!T {",
        "pub fn writeMaskedAt(",
        'test "phase3 mmio helper keeps range-bound accessors inside the blessed MMIO window" {',
        'test "phase3 mmio helper rejects overflowing range windows before blessing unsafe access" {',
    ),
}

SELF_TEST_CASES = (
    (REPLAY_PATH, 'const mmio = @import("mmio");'),
    (FOCUSED_BUILD_PATH, '"phase3-low-level-wrappers-test"'),
    (SHARED_BUILD_PATH, "phase3_test_step.dependOn(&phase3_low_level_wrappers.step);"),
    (MAKEFILE_PATH, "phase3-low-level-wrappers-test:"),
    (ATOMIC_HELPER_PATH, "pub fn fetchMax("),
    (BARRIER_HELPER_PATH, "pub fn storeLoad() void {"),
    (MMIO_HELPER_PATH, "pub fn readAt(comptime T: type, range: MmioRange, byte_offset: usize) PolicyError!T {"),
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _resolve_tool(explicit: str | None, env_name: str, default: str) -> str:
    if explicit:
        return explicit
    return os.environ.get(env_name, default)


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def validate_repo(repo_root: Path, zig: str, *, skip_exec: bool = False) -> list[str]:
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

    if issues or skip_exec:
        return issues

    focused = _run(
        [
            zig,
            "build",
            "phase3-low-level-wrappers-test",
            "--build-file",
            str(repo_root / FOCUSED_BUILD_PATH),
        ],
        cwd=repo_root,
    )
    if focused.returncode != 0:
        issues.append(
            "focused low-level-wrapper build failed:\n"
            f"stdout:\n{focused.stdout}\n"
            f"stderr:\n{focused.stderr}"
        )

    shared = _run(
        [
            zig,
            "build",
            "phase3-low-level-wrappers",
            "--build-file",
            str(repo_root / SHARED_BUILD_PATH),
        ],
        cwd=repo_root,
    )
    if shared.returncode != 0:
        issues.append(
            "shared low-level-wrapper build failed:\n"
            f"stdout:\n{shared.stdout}\n"
            f"stderr:\n{shared.stderr}"
        )

    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_low_level_wrappers_") as tmp_dir:
        root = Path(tmp_dir)
        for relative_path, markers in REQUIRED_MARKERS.items():
            _write(root / relative_path, "\n".join(markers) + "\n")

        issues = validate_repo(root, zig="zig", skip_exec=True)
        if issues:
            print("PHASE3_LOW_LEVEL_WRAPPERS_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in SELF_TEST_CASES:
            path = root / relative_path
            original = _read(path)
            _write(path, original.replace(marker, "", 1))
            try:
                issues = validate_repo(root, zig="zig", skip_exec=True)
                expected = f"missing {relative_path.as_posix()} marker: {marker}"
                if expected not in issues:
                    print("PHASE3_LOW_LEVEL_WRAPPERS_SELF_TEST=fail")
                    print(f"expected missing marker was not reported: {expected}")
                    return 1
            finally:
                _write(path, original)

    print("PHASE3_LOW_LEVEL_WRAPPERS_SELF_TEST=pass")
    print(f"PHASE3_LOW_LEVEL_WRAPPERS_SELF_TEST_CASES={len(SELF_TEST_CASES)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 low-level-wrapper compile-route packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 low-level-wrapper packet",
    )
    parser.add_argument("--zig", help="path to zig executable")
    parser.add_argument("--skip-exec", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    zig = _resolve_tool(args.zig, "ZIG", "zig")
    issues = validate_repo(args.repo_root, zig, skip_exec=args.skip_exec)
    if issues:
        print("PHASE3_LOW_LEVEL_WRAPPERS=fail")
        print("\n".join(issues))
        return 1

    print(f"validated {args.repo_root / REPLAY_PATH}")
    print(f"validated {args.repo_root / FOCUSED_BUILD_PATH}")
    print(f"validated {args.repo_root / SHARED_BUILD_PATH}")
    print(f"validated {args.repo_root / MAKEFILE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
