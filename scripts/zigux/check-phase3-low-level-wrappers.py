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
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
ATOMIC_HELPER_PATH = Path("zigux/helpers/atomic.zig")
BARRIER_HELPER_PATH = Path("zigux/helpers/barrier.zig")
LAYOUT_ASSERT_HELPER_PATH = Path("zigux/helpers/layout_assert.zig")
MMIO_HELPER_PATH = Path("zigux/helpers/mmio.zig")
UNSAFE_POLICY_HELPER_PATH = Path("zigux/helpers/unsafe_policy.zig")
NARROW_HELPER_PATH = Path("zigux/unsafe/narrow.zig")

REQUIRED_MARKERS = {
    REPLAY_PATH: (
        'const atomic = @import("atomic");',
        'const barrier = @import("barrier");',
        'const layout_assert = @import("layout_assert");',
        'const mmio = @import("mmio");',
        'const unsafe_policy = @import("unsafe_policy");',
        'const narrow = @import("narrow");',
        'test "phase3 low-level wrappers keep helper-local MMIO layout assertions explicit" {',
        "try layout_assert.assertMmioRangeLayout();",
        'test "phase3 low-level wrappers keep MMIO unsafe-scope gates explicit across shared handoff" {',
        'test "phase3 low-level wrappers keep raw-pointer bridge scope gates explicit beside MMIO policy gates" {',
        'test "phase3 low-level wrappers keep raw-pointer bridge interop-policy helpers explicit" {',
        'test "phase3 low-level wrappers keep MMIO range helpers and width aliases explicit beside raw bridge gates" {',
        "const direct_ptr = try narrow.pointerAtInteropPolicyBytes(",
        "const scoped_range = try mmio.rangeScoped(base_addr, 16, 4, .volatile_mmio);",
        "try std.testing.expect(unsafe_policy.permitsRawPointerBridgeByte(raw_scope));",
        "try mmio.write64InteropPolicyBytes(base_addr, 8, 0x0123_4567_89AB_CDEF, mmio_scope, 0);",
        'test "phase3 low-level wrappers keep atomic order-gate failures explicit before MMIO publish" {',
    ),
    FOCUSED_BUILD_PATH: (
        '.root_source_file = b.path("../helpers/atomic.zig"),',
        '.root_source_file = b.path("../helpers/barrier.zig"),',
        '.root_source_file = b.path("../helpers/layout_assert.zig"),',
        '.root_source_file = b.path("../helpers/mmio.zig"),',
        '.root_source_file = b.path("../helpers/unsafe_policy.zig"),',
        '.root_source_file = b.path("../unsafe/narrow.zig"),',
        'layout_assert.addImport("abi_bindings", abi_bindings);',
        'narrow.addImport("abi_bindings", abi_bindings);',
        'unsafe_policy.addImport("narrow", narrow);',
        'mmio.addImport("unsafe_policy", unsafe_policy);',
        'root_module.addImport("layout_assert", layout_assert);',
        'root_module.addImport("unsafe_policy", unsafe_policy);',
        'root_module.addImport("narrow", narrow);',
        '"phase3-low-level-wrappers-test"',
    ),
    SHARED_BUILD_PATH: (
        "fn addPhase3LowLevelWrappers(",
        '"phase3-low-level-wrappers"',
        '"phase3-test"',
        "phase3_low_level_wrapper_step.dependOn(&phase3_low_level_wrappers.step);",
        "phase3_test_step.dependOn(&phase3_low_level_wrappers.step);",
    ),
    MAKEFILE_PATH: (
        'phase3-low-level-wrappers:',
        'phase3-low-level-wrappers-test:',
        '$(ZIG) build phase3-low-level-wrappers --build-file zigux/tests/build.zig',
        '$(ZIG) build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig',
        'phase3: phase3-validate phase3-export-uapi-layout phase3-export-shim-test phase3-low-level-wrappers phase3-policy-unsafe-test phase3-test phase3-policy-dump phase3-dump',
    ),
    WORKFLOW_PATH: (
        'python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test',
        'python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py',
        'zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig',
        'make -C zigux phase3-low-level-wrappers',
        'make -C zigux phase3-low-level-wrappers-test',
        'zig build phase3-test --build-file zigux/tests/build.zig',
    ),
    ATOMIC_HELPER_PATH: (
        'pub fn validateCompareExchangeOrders(',
        'pub fn load(comptime T: type, ptr: *const T, comptime order: Ordering) LoadError!T {',
        'pub fn strongestAllowedFailureOrder(success: Ordering) ?Ordering {',
        'pub fn weakestAllowedFailureOrder(success: Ordering) ?Ordering {',
        'pub fn fetchMax(',
    ),
    BARRIER_HELPER_PATH: (
        'pub fn fence(comptime order: Ordering) FenceError!void {',
        'pub fn validateFenceOrder(comptime order: Ordering) FenceError!void {',
        'pub fn acquireAfterControlDependency() void {',
        'pub fn storeLoad() void {',
        'pub fn afterAtomic() void {',
        'test "phase3 barrier wrappers keep seq-cst aliases aligned" {',
        'test "phase3 barrier wrappers keep acquire-after-control-dependency handoffs reviewable" {',
        'test "phase3 barrier wrappers keep post-atomic full barriers explicit" {',
    ),
    LAYOUT_ASSERT_HELPER_PATH: (
        'pub const MmioRange = extern struct {',
        'pub fn assertMmioRangeLayout() LayoutError!void {',
    ),
    MMIO_HELPER_PATH: (
        'pub fn allowsInteropPolicy(policy: abi.InteropPolicy) bool {',
        'pub fn requireInteropPolicy(policy: abi.InteropPolicy) PolicyError!void {',
        'pub fn rangeScoped(base_addr: usize, length: u32, stride: u32, scope: abi.UnsafeScope) PolicyError!MmioRange {',
        'pub fn rangeInteropPolicy(base_addr: usize, length: u32, stride: u32, policy: abi.InteropPolicy) PolicyError!MmioRange {',
        'pub fn rangeInteropPolicyBytes(base_addr: usize, length: u32, stride: u32, unsafe_scope: u8, reserved: u8) PolicyError!MmioRange {',
        'pub fn rangeInteropPolicyByte(base_addr: usize, length: u32, stride: u32, unsafe_scope: u8) PolicyError!MmioRange {',
        'pub fn readInteropPolicy(comptime T: type, policy: abi.InteropPolicy, ptr: *const volatile T) PolicyError!T {',
        'pub fn exchangeInteropPolicyBytes(',
        'pub fn read64InteropPolicyBytes(base_addr: usize, byte_offset: usize, unsafe_scope: u8, reserved: u8) PolicyError!u64 {',
        'pub fn constPointerAt(comptime T: type, range: MmioRange, byte_offset: usize) PolicyError!*const volatile T {',
        'pub fn pointerAt(comptime T: type, range: MmioRange, byte_offset: usize) PolicyError!*volatile T {',
        'pub fn readAt(comptime T: type, range: MmioRange, byte_offset: usize) PolicyError!T {',
        'pub fn writeAt(comptime T: type, range: MmioRange, byte_offset: usize, value: T) PolicyError!void {',
        'pub fn exchangeAt(comptime T: type, range: MmioRange, byte_offset: usize, value: T) PolicyError!T {',
        'pub fn writeMaskedAt(',
        'test "phase3 mmio helper keeps range-bound accessors inside the blessed MMIO window" {',
        'test "phase3 mmio helper rejects overflowing range windows before blessing unsafe access" {',
    ),
    UNSAFE_POLICY_HELPER_PATH: (
        'pub fn scopeFromInteropPolicyBytes(scope: u8, reserved: u8) ?abi.UnsafeScope {',
        'pub fn scopeFromInteropPolicy(policy: abi.InteropPolicy) ?abi.UnsafeScope {',
        'pub fn permitsVolatileMmioInteropPolicy(policy: abi.InteropPolicy) bool {',
        'pub fn requireVolatileMmioInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {',
        'pub fn permitsRawPointerBridgeByte(scope: u8) bool {',
        'pub fn requireRawPointerBridgeByte(scope: u8) UnsafeScopeError!void {',
    ),
    NARROW_HELPER_PATH: (
        'pub fn scopeFromInteropPolicyBytes(unsafe_scope: u8, reserved: u8) ?UnsafeScopeTag {',
        'pub fn permitsRawPointerBridgePolicyBytes(unsafe_scope: u8, reserved: u8) bool {',
        'pub fn pointerAtInteropPolicyBytes(comptime T: type, address: usize, byte_len: usize, unsafe_scope: u8, reserved: u8) RawPointerBridgeError!*align(1) T {',
        'pub fn pointerAtInteropPolicy(comptime T: type, address: usize, byte_len: usize, policy: abi.InteropPolicy) RawPointerBridgeError!*align(1) T {',
        'pub fn constPointerAtInteropPolicyBytes(comptime T: type, address: usize, unsafe_scope: u8, reserved: u8) RawPointerBridgeError!*align(1) const T {',
        'pub fn sliceAtInteropPolicy(comptime T: type, address: usize, len: usize, policy: abi.InteropPolicy) RawPointerBridgeError![]align(1) T {',
        'pub fn writeValueAtInteropPolicyBytes(comptime T: type, address: usize, value: T, unsafe_scope: u8, reserved: u8) RawPointerBridgeError!void {',
        'pub fn exchangeValueAtInteropPolicy(comptime T: type, address: usize, byte_len: usize, value: T, policy: abi.InteropPolicy) RawPointerBridgeError!T {',
        'pub fn exchangeValueAtByte(comptime T: type, address: usize, byte_len: usize, value: T, scope: u8) RawPointerBridgeError!T {',
    ),
}

SELF_TEST_CASES = (
    (REPLAY_PATH, 'const layout_assert = @import("layout_assert");'),
    (REPLAY_PATH, 'const narrow = @import("narrow");'),
    (REPLAY_PATH, 'test "phase3 low-level wrappers keep MMIO range helpers and width aliases explicit beside raw bridge gates" {'),
    (FOCUSED_BUILD_PATH, 'root_module.addImport("layout_assert", layout_assert);'),
    (FOCUSED_BUILD_PATH, 'root_module.addImport("unsafe_policy", unsafe_policy);'),
    (FOCUSED_BUILD_PATH, 'root_module.addImport("narrow", narrow);'),
    (SHARED_BUILD_PATH, 'phase3_low_level_wrapper_step.dependOn(&phase3_low_level_wrappers.step);'),
    (MAKEFILE_PATH, 'phase3: phase3-validate phase3-export-uapi-layout phase3-export-shim-test phase3-low-level-wrappers phase3-policy-unsafe-test phase3-test phase3-policy-dump phase3-dump'),
    (WORKFLOW_PATH, 'python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test'),
    (BARRIER_HELPER_PATH, 'pub fn afterAtomic() void {'),
    (BARRIER_HELPER_PATH, 'test "phase3 barrier wrappers keep post-atomic full barriers explicit" {'),
    (LAYOUT_ASSERT_HELPER_PATH, 'pub fn assertMmioRangeLayout() LayoutError!void {'),
    (MMIO_HELPER_PATH, 'pub fn readAt(comptime T: type, range: MmioRange, byte_offset: usize) PolicyError!T {'),
    (UNSAFE_POLICY_HELPER_PATH, 'pub fn permitsRawPointerBridgeByte(scope: u8) bool {'),
    (NARROW_HELPER_PATH, 'pub fn pointerAtInteropPolicyBytes(comptime T: type, address: usize, byte_len: usize, unsafe_scope: u8, reserved: u8) RawPointerBridgeError!*align(1) T {'),
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
            'build',
            'phase3-low-level-wrappers-test',
            '--build-file',
            str(repo_root / FOCUSED_BUILD_PATH),
        ],
        cwd=repo_root,
    )
    if focused.returncode != 0:
        issues.append(
            'focused low-level-wrapper build failed:\n'
            f'stdout:\n{focused.stdout}\n'
            f'stderr:\n{focused.stderr}'
        )

    shared = _run(
        [
            zig,
            'build',
            'phase3-low-level-wrappers',
            '--build-file',
            str(repo_root / SHARED_BUILD_PATH),
        ],
        cwd=repo_root,
    )
    if shared.returncode != 0:
        issues.append(
            'shared low-level-wrapper build failed:\n'
            f'stdout:\n{shared.stdout}\n'
            f'stderr:\n{shared.stderr}'
        )

    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix='zigux_phase3_low_level_wrappers_') as tmp_dir:
        root = Path(tmp_dir)
        for relative_path, markers in REQUIRED_MARKERS.items():
            _write(root / relative_path, '\n'.join(markers) + '\n')

        issues = validate_repo(root, zig='zig', skip_exec=True)
        if issues:
            print('PHASE3_LOW_LEVEL_WRAPPERS_SELF_TEST=fail')
            print('\n'.join(issues))
            return 1

        for relative_path, marker in SELF_TEST_CASES:
            path = root / relative_path
            original = _read(path)
            _write(path, original.replace(marker, '', 1))
            try:
                issues = validate_repo(root, zig='zig', skip_exec=True)
                expected = f'missing {relative_path.as_posix()} marker: {marker}'
                if expected not in issues:
                    print('PHASE3_LOW_LEVEL_WRAPPERS_SELF_TEST=fail')
                    print(f'expected missing marker was not reported: {expected}')
                    return 1
            finally:
                _write(path, original)

    print('PHASE3_LOW_LEVEL_WRAPPERS_SELF_TEST=pass')
    print(f'PHASE3_LOW_LEVEL_WRAPPERS_SELF_TEST_CASES={len(SELF_TEST_CASES)}')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Validate the current Phase 3 low-level-wrapper compile-route packet.'
    )
    parser.add_argument(
        '--repo-root',
        type=Path,
        default=Path('.'),
        help='repository root that contains the Phase 3 low-level-wrapper packet',
    )
    parser.add_argument('--zig', help='path to zig executable')
    parser.add_argument('--skip-exec', action='store_true')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    zig = _resolve_tool(args.zig, 'ZIG', 'zig')
    issues = validate_repo(args.repo_root, zig, skip_exec=args.skip_exec)
    if issues:
        print('PHASE3_LOW_LEVEL_WRAPPERS=fail')
        print('\n'.join(issues))
        return 1

    print(f'validated {args.repo_root / REPLAY_PATH}')
    print(f'validated {args.repo_root / FOCUSED_BUILD_PATH}')
    print(f'validated {args.repo_root / SHARED_BUILD_PATH}')
    print(f'validated {args.repo_root / MAKEFILE_PATH}')
    print(f'validated {args.repo_root / WORKFLOW_PATH}')
    print(f'validated {args.repo_root / ATOMIC_HELPER_PATH}')
    print(f'validated {args.repo_root / BARRIER_HELPER_PATH}')
    print(f'validated {args.repo_root / LAYOUT_ASSERT_HELPER_PATH}')
    print(f'validated {args.repo_root / MMIO_HELPER_PATH}')
    print(f'validated {args.repo_root / UNSAFE_POLICY_HELPER_PATH}')
    print(f'validated {args.repo_root / NARROW_HELPER_PATH}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
