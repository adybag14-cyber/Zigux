#!/usr/bin/env python3
"""Validate the current Phase 3 policy-and-unsafe route packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


POLICY_DUMP_PATH = Path("zigux/tests/phase3_policy_dump.zig")
POLICY_DUMP_BUILD_PATH = Path("zigux/tests/phase3_policy_dump_build.zig")
LOW_LEVEL_WRAPPERS_PATH = Path("zigux/tests/phase3_low_level_wrappers.zig")
LOW_LEVEL_WRAPPERS_BUILD_PATH = Path("zigux/tests/phase3_low_level_wrappers_build.zig")
UNSAFE_POLICY_PATH = Path("zigux/helpers/unsafe_policy.zig")
MMIO_PATH = Path("zigux/helpers/mmio.zig")
NARROW_PATH = Path("zigux/unsafe/narrow.zig")

REQUIRED_MARKERS = {
    POLICY_DUMP_PATH: (
        "fn rawBridgeReplay(policy: abi.InteropPolicy) RawBridgeReplay {",
        '"safe-default"',
        '"mmio-bug"',
        '"raw-bridge-warn"',
        '"reserved-invalid"',
        '"bridge_read_ok={any}"',
        '"bridge_write_ok={any}"',
        'const narrow_surface = @import("narrow_surface");',
    ),
    POLICY_DUMP_BUILD_PATH: (
        '.root_source_file = b.path("../bindings/abi.zig"),',
        '.root_source_file = b.path("../helpers/panic_policy.zig"),',
        '.root_source_file = b.path("../helpers/allocator_policy.zig"),',
        '.root_source_file = b.path("../helpers/unsafe_policy.zig"),',
        '.root_source_file = b.path("../unsafe/narrow.zig"),',
        '.root_source_file = b.path("phase3_policy_dump.zig"),',
        '"phase3-policy-dump"',
        '"Dump the focused Phase 3 policy and unsafe substrate replay surface"',
    ),
    LOW_LEVEL_WRAPPERS_PATH: (
        'test "phase3 low-level wrappers keep MMIO unsafe-scope gates explicit across shared handoff" {',
        'test "phase3 low-level wrappers keep MMIO byte-policy shorthand aligned with reserved-byte gates" {',
        'test "phase3 low-level wrappers keep direct MMIO scope gates explicit" {',
        'test "phase3 low-level wrappers keep raw-pointer bridge scope gates explicit beside MMIO policy gates" {',
        'test "phase3 low-level wrappers keep raw-pointer bridge byte coverage explicit" {',
        'test "phase3 low-level wrappers keep raw-pointer bridge interop-policy helpers explicit" {',
    ),
    LOW_LEVEL_WRAPPERS_BUILD_PATH: (
        '.root_source_file = b.path("../helpers/atomic.zig"),',
        '.root_source_file = b.path("../helpers/barrier.zig"),',
        '.root_source_file = b.path("../helpers/mmio.zig"),',
        '.root_source_file = b.path("../helpers/unsafe_policy.zig"),',
        '.root_source_file = b.path("../unsafe/narrow.zig"),',
        '.root_source_file = b.path("phase3_low_level_wrappers.zig"),',
        '"phase3-low-level-wrappers-test"',
    ),
    UNSAFE_POLICY_PATH: (
        "pub fn requiresVolatileMmioAccessInteropPolicy(policy: abi.InteropPolicy) bool {",
        "pub fn requiresRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {",
        "pub fn allowsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {",
        "pub fn requiresDedicatedAuditInteropPolicy(policy: abi.InteropPolicy) bool {",
    ),
    MMIO_PATH: (
        "pub fn readInteropPolicy(comptime T: type, policy: abi.InteropPolicy, ptr: *const volatile T) PolicyError!T {",
        "pub fn writeInteropPolicy(comptime T: type, policy: abi.InteropPolicy, ptr: *volatile T, value: T) PolicyError!void {",
        "pub fn exchangeInteropPolicy(comptime T: type, policy: abi.InteropPolicy, ptr: *volatile T, value: T) PolicyError!T {",
        "pub fn writeMaskedInteropPolicy(",
        "pub fn readInteropPolicyBytes(",
        "pub fn exchangeInteropPolicyBytes(",
    ),
    NARROW_PATH: (
        "pub const Surface = enum {",
        "pub fn accessBoundaryFromInteropPolicy(policy: abi.InteropPolicy) ?AccessBoundary {",
        "pub fn requireRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {",
        "pub fn constSliceAtInteropPolicy(comptime T: type, address: usize, len: usize, policy: abi.InteropPolicy) RawPointerBridgeError![]align(1) const T {",
        "pub fn writeValueAtInteropPolicy(comptime T: type, address: usize, value: T, policy: abi.InteropPolicy) RawPointerBridgeError!void {",
    ),
}

SELF_TEST_CASES = (
    (POLICY_DUMP_PATH, '"bridge_write_ok={any}"'),
    (POLICY_DUMP_BUILD_PATH, '"phase3-policy-dump"'),
    (LOW_LEVEL_WRAPPERS_PATH, 'test "phase3 low-level wrappers keep raw-pointer bridge byte coverage explicit" {'),
    (LOW_LEVEL_WRAPPERS_BUILD_PATH, '"phase3-low-level-wrappers-test"'),
    (UNSAFE_POLICY_PATH, "pub fn requiresRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {"),
    (MMIO_PATH, "pub fn exchangeInteropPolicyBytes("),
    (NARROW_PATH, "pub fn constSliceAtInteropPolicy(comptime T: type, address: usize, len: usize, policy: abi.InteropPolicy) RawPointerBridgeError![]align(1) const T {"),
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


def populate_sample_repo(root: Path) -> None:
    for relative_path, markers in REQUIRED_MARKERS.items():
        _write(root / relative_path, "\n".join(markers) + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_policy_unsafe_routes_") as temp_dir:
        repo_root = Path(temp_dir)
        populate_sample_repo(repo_root)

        issues = validate_repo(repo_root)
        if issues:
            print("PHASE3_POLICY_UNSAFE_ROUTES_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in SELF_TEST_CASES:
            populate_sample_repo(repo_root)
            path = repo_root / relative_path
            _write(path, _read(path).replace(marker, "", 1))
            issues = validate_repo(repo_root)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_POLICY_UNSAFE_ROUTES_SELF_TEST=fail")
                print(f"expected issue not reported: {expected}")
                return 1

    print("PHASE3_POLICY_UNSAFE_ROUTES_SELF_TEST=pass")
    print(f"PHASE3_POLICY_UNSAFE_ROUTES_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES) + 1}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 policy-and-unsafe route packet."
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_POLICY_UNSAFE_ROUTES=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE3_POLICY_UNSAFE_ROUTES=pass")
    print(f"validated {args.repo_root / POLICY_DUMP_PATH}")
    print(f"validated {args.repo_root / LOW_LEVEL_WRAPPERS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
