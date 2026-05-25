#!/usr/bin/env python3
"""Fail-close the current Phase 3 unsafe-policy raw-pointer relay surface."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


UNSAFE_POLICY_PATH = Path("zigux/helpers/unsafe_policy.zig")
NARROW_PATH = Path("zigux/unsafe/narrow.zig")

REQUIRED_MARKERS = {
    UNSAFE_POLICY_PATH: (
        "pub fn permitsRawPointerBridge(scope: abi.UnsafeScope) bool {",
        "pub fn permitsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {",
        "pub fn allowsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {",
        "pub fn requireRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {",
        "pub fn allowsRawPointerBridgePolicyBytes(scope: u8, reserved: u8) bool {",
        "pub fn requireRawPointerBridgePolicyBytes(scope: u8, reserved: u8) UnsafeScopeError!void {",
        "pub fn permitsRawPointerBridgeByte(scope: u8) bool {",
        "pub fn allowsRawPointerBridgeByte(scope: u8) bool {",
        "pub fn requireRawPointerBridgeByte(scope: u8) UnsafeScopeError!void {",
        "pub fn pointerAtInteropPolicyBytes(",
        "pub fn pointerAtInteropPolicy(",
        "pub fn pointerAtByte(",
        "pub fn constPointerAtInteropPolicyBytes(",
        "pub fn constPointerAtInteropPolicy(",
        "pub fn constPointerAtByte(",
        "pub fn sliceAtInteropPolicyBytes(",
        "pub fn sliceAtInteropPolicy(",
        "pub fn sliceAtByte(",
        "pub fn constSliceAtInteropPolicyBytes(",
        "pub fn constSliceAtInteropPolicy(",
        "pub fn constSliceAtByte(",
        "pub fn writeValueAtInteropPolicyBytes(",
        "pub fn writeValueAtInteropPolicy(",
        "pub fn writeValueAtByte(",
        'test "phase3 unsafe policy keeps raw-pointer bridge relays helper-local" {',
    ),
    NARROW_PATH: (
        "pub fn permitsRawPointerBridge(scope: UnsafeScopeTag) bool {",
        "pub fn permitsRawPointerBridgePolicyBytes(unsafe_scope: u8, reserved: u8) bool {",
        "pub fn permitsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {",
        "pub fn requireRawPointerBridgePolicyBytes(unsafe_scope: u8, reserved: u8) UnsafeScopeError!void {",
        "pub fn requireRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {",
        "pub fn pointerAtInteropPolicyBytes(comptime T: type, address: usize, byte_len: usize, unsafe_scope: u8, reserved: u8) RawPointerBridgeError!*align(1) T {",
        "pub fn pointerAtInteropPolicy(comptime T: type, address: usize, byte_len: usize, policy: abi.InteropPolicy) RawPointerBridgeError!*align(1) T {",
        "pub fn pointerAtByte(comptime T: type, address: usize, byte_len: usize, scope: u8) RawPointerBridgeError!*align(1) T {",
        "pub fn constPointerAtInteropPolicyBytes(comptime T: type, address: usize, unsafe_scope: u8, reserved: u8) RawPointerBridgeError!*align(1) const T {",
        "pub fn constPointerAtInteropPolicy(comptime T: type, address: usize, policy: abi.InteropPolicy) RawPointerBridgeError!*align(1) const T {",
        "pub fn constPointerAtByte(comptime T: type, address: usize, scope: u8) RawPointerBridgeError!*align(1) const T {",
        "pub fn sliceAtInteropPolicyBytes(comptime T: type, address: usize, len: usize, unsafe_scope: u8, reserved: u8) RawPointerBridgeError![]align(1) T {",
        "pub fn sliceAtInteropPolicy(comptime T: type, address: usize, len: usize, policy: abi.InteropPolicy) RawPointerBridgeError![]align(1) T {",
        "pub fn sliceAtByte(comptime T: type, address: usize, len: usize, scope: u8) RawPointerBridgeError![]align(1) T {",
        "pub fn constSliceAtInteropPolicyBytes(comptime T: type, address: usize, len: usize, unsafe_scope: u8, reserved: u8) RawPointerBridgeError![]align(1) const T {",
        "pub fn constSliceAtInteropPolicy(comptime T: type, address: usize, len: usize, policy: abi.InteropPolicy) RawPointerBridgeError![]align(1) const T {",
        "pub fn constSliceAtByte(comptime T: type, address: usize, len: usize, scope: u8) RawPointerBridgeError![]align(1) const T {",
        "pub fn writeValueAtInteropPolicyBytes(comptime T: type, address: usize, value: T, unsafe_scope: u8, reserved: u8) RawPointerBridgeError!void {",
        "pub fn writeValueAtInteropPolicy(comptime T: type, address: usize, value: T, policy: abi.InteropPolicy) RawPointerBridgeError!void {",
        "pub fn writeValueAtByte(comptime T: type, address: usize, value: T, scope: u8) RawPointerBridgeError!void {",
    ),
}

SELF_TEST_CASES = tuple(
    (relative_path, marker)
    for relative_path, markers in REQUIRED_MARKERS.items()
    for marker in markers
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
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_unsafe_policy_raw_bridge_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_UNSAFE_POLICY_RAW_BRIDGE_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in SELF_TEST_CASES:
            _populate_repo(root)
            path = root / relative_path
            path.write_text(_read(path).replace(marker, ""), encoding="utf-8")
            issues = validate_repo(root)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_UNSAFE_POLICY_RAW_BRIDGE_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

    print("PHASE3_UNSAFE_POLICY_RAW_BRIDGE_SELF_TEST=pass")
    print(f"PHASE3_UNSAFE_POLICY_RAW_BRIDGE_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 unsafe-policy raw-pointer bridge relay surface."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 unsafe-policy relay files",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_UNSAFE_POLICY_RAW_BRIDGE=fail")
        print("\n".join(issues))
        return 1

    print(f"validated {UNSAFE_POLICY_PATH.as_posix()}")
    print(f"validated {NARROW_PATH.as_posix()}")
    print("PHASE3_UNSAFE_POLICY_RAW_BRIDGE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
