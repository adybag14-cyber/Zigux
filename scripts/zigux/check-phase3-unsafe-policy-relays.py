#!/usr/bin/env python3
"""Focused validator for Phase 3 unsafe_policy relay coverage."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


RELAY_GROUPS = {
    "scope decode relays": {
        "modeFromInteropPolicyBytes": "return scopeFromInteropPolicyBytes(scope, reserved);",
        "modeFromInteropPolicy": "return scopeFromInteropPolicy(policy);",
        "modeFromByte": "return scopeFromByte(scope);",
        "scopeFromInteropPolicyBytes": "return narrow.scopeFromInteropPolicyBytes(scope, reserved);",
        "scopeFromInteropPolicy": "return narrow.scopeFromInteropPolicy(policy);",
        "scopeFromByte": "return narrow.scopeFromByte(scope);",
    },
    "policy recognition relays": {
        "recognizesInteropPolicyBytes": "return narrow.recognizesInteropPolicyBytes(scope, reserved);",
        "recognizesInteropPolicy": "return narrow.recognizesInteropPolicy(policy);",
        "recognizesByte": "return narrow.recognizesByte(scope);",
        "allowsTypedOnlyAccess": "return narrow.allowsTypedOnlyAccess(scope);",
        "permitsNoUnsafe": "return narrow.permitsNoUnsafe(scope);",
        "permitsVolatileMmio": "return narrow.permitsVolatileMmio(scope);",
        "permitsRawPointerBridge": "return narrow.permitsRawPointerBridge(scope);",
        "allowsVolatileMmio": "return narrow.allowsVolatileMmio(scope);",
        "allowsRawPointerBridge": "return narrow.allowsRawPointerBridge(scope);",
    },
    "raw bridge pointer relays": {
        "pointerAtInteropPolicyBytes": "return narrow.pointerAtInteropPolicyBytes(T, address, byte_len, scope, reserved);",
        "pointerAtInteropPolicy": "return narrow.pointerAtInteropPolicy(T, address, byte_len, policy);",
        "pointerAtByte": "return narrow.pointerAtByte(T, address, byte_len, scope);",
        "constPointerAtInteropPolicyBytes": "return narrow.constPointerAtInteropPolicyBytes(T, address, scope, reserved);",
        "constPointerAtInteropPolicy": "return narrow.constPointerAtInteropPolicy(T, address, policy);",
        "constPointerAtByte": "return narrow.constPointerAtByte(T, address, scope);",
    },
    "raw bridge slice relays": {
        "sliceAtInteropPolicyBytes": "return narrow.sliceAtInteropPolicyBytes(T, address, len, scope, reserved);",
        "sliceAtInteropPolicy": "return narrow.sliceAtInteropPolicy(T, address, len, policy);",
        "sliceAtByte": "return narrow.sliceAtByte(T, address, len, scope);",
        "constSliceAtInteropPolicyBytes": "return narrow.constSliceAtInteropPolicyBytes(T, address, len, scope, reserved);",
        "constSliceAtInteropPolicy": "return narrow.constSliceAtInteropPolicy(T, address, len, policy);",
        "constSliceAtByte": "return narrow.constSliceAtByte(T, address, len, scope);",
    },
    "raw bridge write relays": {
        "writeValueAtInteropPolicyBytes": "return narrow.writeValueAtInteropPolicyBytes(T, address, value, scope, reserved);",
        "writeValueAtInteropPolicy": "return narrow.writeValueAtInteropPolicy(T, address, value, policy);",
        "writeValueAtByte": "return narrow.writeValueAtByte(T, address, value, scope);",
    },
}


def extract_function_body(source: str, func_name: str) -> str:
    match = re.search(rf"pub fn {re.escape(func_name)}\s*\(", source)
    if not match:
        raise KeyError(func_name)

    brace_index = source.find("{", match.end())
    if brace_index == -1:
        raise ValueError(f"{func_name}: missing opening brace")

    depth = 0
    for index in range(brace_index, len(source)):
        char = source[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[brace_index + 1 : index].strip()

    raise ValueError(f"{func_name}: missing closing brace")


def check_source(source: str) -> list[str]:
    errors: list[str] = []
    for group_name, functions in RELAY_GROUPS.items():
        for func_name, expected_line in functions.items():
            try:
                body = extract_function_body(source, func_name)
            except (KeyError, ValueError) as exc:
                errors.append(f"{group_name}: {exc}")
                continue

            normalized = " ".join(body.split())
            expected = " ".join(expected_line.split())
            if expected not in normalized:
                errors.append(
                    f"{group_name}: {func_name} does not contain expected relay `{expected_line}`"
                )
    return errors


def run_self_test() -> int:
    sample = """
const narrow = @import("narrow");

pub fn modeFromInteropPolicyBytes(scope: u8, reserved: u8) ?u8 {
    return scopeFromInteropPolicyBytes(scope, reserved);
}

pub fn modeFromInteropPolicy(policy: u8) ?u8 {
    return scopeFromInteropPolicy(policy);
}

pub fn modeFromByte(scope: u8) ?u8 {
    return scopeFromByte(scope);
}

pub fn scopeFromInteropPolicyBytes(scope: u8, reserved: u8) ?u8 {
    return narrow.scopeFromInteropPolicyBytes(scope, reserved);
}

pub fn scopeFromInteropPolicy(policy: u8) ?u8 {
    return narrow.scopeFromInteropPolicy(policy);
}

pub fn scopeFromByte(scope: u8) ?u8 {
    return narrow.scopeFromByte(scope);
}

pub fn recognizesInteropPolicyBytes(scope: u8, reserved: u8) bool {
    return narrow.recognizesInteropPolicyBytes(scope, reserved);
}

pub fn recognizesInteropPolicy(policy: u8) bool {
    return narrow.recognizesInteropPolicy(policy);
}

pub fn recognizesByte(scope: u8) bool {
    return narrow.recognizesByte(scope);
}

pub fn allowsTypedOnlyAccess(scope: u8) bool {
    return narrow.allowsTypedOnlyAccess(scope);
}

pub fn permitsNoUnsafe(scope: u8) bool {
    return narrow.permitsNoUnsafe(scope);
}

pub fn permitsVolatileMmio(scope: u8) bool {
    return narrow.permitsVolatileMmio(scope);
}

pub fn permitsRawPointerBridge(scope: u8) bool {
    return narrow.permitsRawPointerBridge(scope);
}

pub fn allowsVolatileMmio(scope: u8) bool {
    return narrow.allowsVolatileMmio(scope);
}

pub fn allowsRawPointerBridge(scope: u8) bool {
    return narrow.allowsRawPointerBridge(scope);
}

pub fn pointerAtInteropPolicyBytes(comptime T: type, address: usize, byte_len: usize, scope: u8, reserved: u8) !*align(1) T {
    return narrow.pointerAtInteropPolicyBytes(T, address, byte_len, scope, reserved);
}

pub fn pointerAtInteropPolicy(comptime T: type, address: usize, byte_len: usize, policy: u8) !*align(1) T {
    return narrow.pointerAtInteropPolicy(T, address, byte_len, policy);
}

pub fn pointerAtByte(comptime T: type, address: usize, byte_len: usize, scope: u8) !*align(1) T {
    return narrow.pointerAtByte(T, address, byte_len, scope);
}

pub fn constPointerAtInteropPolicyBytes(comptime T: type, address: usize, scope: u8, reserved: u8) !*align(1) const T {
    return narrow.constPointerAtInteropPolicyBytes(T, address, scope, reserved);
}

pub fn constPointerAtInteropPolicy(comptime T: type, address: usize, policy: u8) !*align(1) const T {
    return narrow.constPointerAtInteropPolicy(T, address, policy);
}

pub fn constPointerAtByte(comptime T: type, address: usize, scope: u8) !*align(1) const T {
    return narrow.constPointerAtByte(T, address, scope);
}

pub fn sliceAtInteropPolicyBytes(comptime T: type, address: usize, len: usize, scope: u8, reserved: u8) ![]align(1) T {
    return narrow.sliceAtInteropPolicyBytes(T, address, len, scope, reserved);
}

pub fn sliceAtInteropPolicy(comptime T: type, address: usize, len: usize, policy: u8) ![]align(1) T {
    return narrow.sliceAtInteropPolicy(T, address, len, policy);
}

pub fn sliceAtByte(comptime T: type, address: usize, len: usize, scope: u8) ![]align(1) T {
    return narrow.sliceAtByte(T, address, len, scope);
}

pub fn constSliceAtInteropPolicyBytes(comptime T: type, address: usize, len: usize, scope: u8, reserved: u8) ![]align(1) const T {
    return narrow.constSliceAtInteropPolicyBytes(T, address, len, scope, reserved);
}

pub fn constSliceAtInteropPolicy(comptime T: type, address: usize, len: usize, policy: u8) ![]align(1) const T {
    return narrow.constSliceAtInteropPolicy(T, address, len, policy);
}

pub fn constSliceAtByte(comptime T: type, address: usize, len: usize, scope: u8) ![]align(1) const T {
    return narrow.constSliceAtByte(T, address, len, scope);
}

pub fn writeValueAtInteropPolicyBytes(comptime T: type, address: usize, value: T, scope: u8, reserved: u8) !void {
    return narrow.writeValueAtInteropPolicyBytes(T, address, value, scope, reserved);
}

pub fn writeValueAtInteropPolicy(comptime T: type, address: usize, value: T, policy: u8) !void {
    return narrow.writeValueAtInteropPolicy(T, address, value, policy);
}

pub fn writeValueAtByte(comptime T: type, address: usize, value: T, scope: u8) !void {
    return narrow.writeValueAtByte(T, address, value, scope);
}
"""
    errors = check_source(sample)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.path is None:
        parser.error("path is required unless --self-test is used")

    source = args.path.read_text(encoding="utf-8")
    errors = check_source(source)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print(f"unsafe_policy relay surface looks consistent in {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
