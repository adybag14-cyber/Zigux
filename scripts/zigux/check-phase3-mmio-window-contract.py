#!/usr/bin/env python3
"""Validate the bounded Phase 3 MMIO window contract surface."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


CONTRACT_PATH = Path("zigux/tests/fixtures/phase3_mmio_window_contract.json")
SELF_TEST_CONTRACT = {
    "phase": "Phase 3",
    "lane": "abi-runtime",
    "slice": "mmio-window-contract",
    "scope": "bounded MMIO range helpers, policy gates, and width-specific wrapper replay evidence",
    "files": {
        "zigux/helpers/mmio.zig": [
            "pub const MmioRange = extern struct {",
            "pub fn allowsInteropPolicy(policy: abi.InteropPolicy) bool {",
            "pub fn requireVolatileMmioScope(scope: abi.UnsafeScope) PolicyError!void {",
            "pub fn rangeScoped(base_addr: usize, length: u32, stride: u32, scope: abi.UnsafeScope) PolicyError!MmioRange {",
            "pub fn rangeInteropPolicy(base_addr: usize, length: u32, stride: u32, policy: abi.InteropPolicy) PolicyError!MmioRange {",
            "pub fn rangeInteropPolicyBytes(base_addr: usize, length: u32, stride: u32, unsafe_scope: u8, reserved: u8) PolicyError!MmioRange {",
            "pub fn rangeInteropPolicyByte(base_addr: usize, length: u32, stride: u32, unsafe_scope: u8) PolicyError!MmioRange {",
            "pub fn read8InteropPolicyBytes(base_addr: usize, byte_offset: usize, unsafe_scope: u8, reserved: u8) PolicyError!u8 {",
            "pub fn write8InteropPolicyBytes(base_addr: usize, byte_offset: usize, value: u8, unsafe_scope: u8, reserved: u8) PolicyError!void {",
            "pub fn read32InteropPolicyByte(base_addr: usize, byte_offset: usize, unsafe_scope: u8) PolicyError!u32 {",
            "pub fn write32InteropPolicyByte(base_addr: usize, byte_offset: usize, value: u32, unsafe_scope: u8) PolicyError!void {",
            "pub fn read64InteropPolicyBytes(base_addr: usize, byte_offset: usize, unsafe_scope: u8, reserved: u8) PolicyError!u64 {",
            "pub fn write64InteropPolicyBytes(base_addr: usize, byte_offset: usize, value: u64, unsafe_scope: u8, reserved: u8) PolicyError!void {",
            "test \"phase3 mmio helper keeps helper-local ranges and width aliases explicit\" {",
        ],
        "zigux/tests/phase3_low_level_wrappers.zig": [
            "test \"phase3 low-level wrappers keep MMIO range helpers and width aliases explicit beside raw bridge gates\" {",
            "const scoped_range = try mmio.rangeScoped(base_addr, 16, 4, .volatile_mmio);",
            "try std.testing.expectError(error.UnsafeScopeDenied, mmio.rangeInteropPolicy(base_addr, 16, 4, raw_policy));",
            "const policy_range = try mmio.rangeInteropPolicy(base_addr, 16, 4, mmio_policy);",
            "const byte_range = try mmio.rangeInteropPolicyByte(base_addr, 16, 4, mmio_scope);",
            "try mmio.write8InteropPolicyBytes(base_addr, 1, 0x44, mmio_scope, 0);",
            "try std.testing.expectEqual(@as(u8, 0x44), try mmio.read8InteropPolicyBytes(base_addr, 1, mmio_scope, 0));",
            "try mmio.write32InteropPolicyByte(base_addr, 4, 0xCAFE_BABE, mmio_scope);",
            "try std.testing.expectEqual(@as(u32, 0xCAFE_BABE), try mmio.read32InteropPolicyByte(base_addr, 4, mmio_scope));",
            "try mmio.write64InteropPolicyBytes(base_addr, 8, 0x0123_4567_89AB_CDEF, mmio_scope, 0);",
            "try narrow.readValueAtInteropPolicyBytes(u64, base_addr + 8, @sizeOf(u64), raw_scope, 0),",
            "try std.testing.expectError(error.UnsafeScopeDenied, narrow.constPointerAtByte(u32, base_addr + 4, mmio_scope));",
        ],
    },
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_contract(repo_root: Path) -> dict[str, object]:
    return json.loads(_read(repo_root / CONTRACT_PATH))


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    try:
        contract = load_contract(repo_root)
    except FileNotFoundError:
        return [f"missing repo file: {CONTRACT_PATH.as_posix()}"]
    except json.JSONDecodeError as exc:
        return [f"invalid JSON in {CONTRACT_PATH.as_posix()}: {exc}"]

    files = contract.get("files")
    if not isinstance(files, dict):
        return [f"{CONTRACT_PATH.as_posix()} field 'files' is not an object"]

    for relative_path, markers in files.items():
        if not isinstance(relative_path, str):
            issues.append(f"contract file key is not a string: {relative_path!r}")
            continue
        if not isinstance(markers, list) or not all(isinstance(marker, str) for marker in markers):
            issues.append(f"contract markers for {relative_path} are not a string list")
            continue

        path = repo_root / relative_path
        try:
            text = _read(path)
        except FileNotFoundError:
            issues.append(f"missing repo file: {relative_path}")
            continue

        for marker in markers:
            if marker not in text:
                issues.append(f"missing {relative_path} marker: {marker}")

    return issues


def _populate_repo(root: Path) -> tuple[dict[str, object], list[tuple[str, str]]]:
    contract = json.loads(json.dumps(SELF_TEST_CONTRACT))
    _write(root / CONTRACT_PATH, json.dumps(contract, indent=2) + "\n")

    cases: list[tuple[str, str]] = []
    files = contract["files"]
    for relative_path, markers in files.items():
        text = "\n".join(markers) + "\n"
        _write(root / relative_path, text)
        for marker in markers:
            cases.append((relative_path, marker))

    return contract, cases


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_mmio_window_") as temp_dir:
        root = Path(temp_dir)
        contract, cases = _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_MMIO_WINDOW_CONTRACT_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in cases:
            _populate_repo(root)
            path = root / relative_path
            path.write_text(_read(path).replace(marker, "", 1), encoding="utf-8")
            issues = validate_repo(root)
            expected = f"missing {relative_path} marker: {marker}"
            if expected not in issues:
                print("PHASE3_MMIO_WINDOW_CONTRACT_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

        _populate_repo(root)
        contract_path = root / CONTRACT_PATH
        broken = contract
        broken["files"]["zigux/helpers/mmio.zig"] = "not-a-list"
        _write(contract_path, json.dumps(broken, indent=2) + "\n")
        issues = validate_repo(root)
        expected = "contract markers for zigux/helpers/mmio.zig are not a string list"
        if expected not in issues:
            print("PHASE3_MMIO_WINDOW_CONTRACT_SELF_TEST=fail")
            print("expected malformed marker-list error was not reported")
            return 1

    print("PHASE3_MMIO_WINDOW_CONTRACT_SELF_TEST=pass")
    print(f"PHASE3_MMIO_WINDOW_CONTRACT_SELF_TEST_CASE_COUNT={len(cases) + 1}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the bounded Phase 3 MMIO window contract surface."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 MMIO window contract files",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_MMIO_WINDOW_CONTRACT=fail")
        print("\n".join(issues))
        return 1

    print(f"validated {CONTRACT_PATH.as_posix()}")
    print("validated zigux/helpers/mmio.zig")
    print("validated zigux/tests/phase3_low_level_wrappers.zig")
    print("PHASE3_MMIO_WINDOW_CONTRACT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
