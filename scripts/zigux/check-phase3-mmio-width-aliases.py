#!/usr/bin/env python3
"""Fail-close the Phase 3 MMIO width-specific alias surface."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


MMIO_PATH = Path("zigux/helpers/mmio.zig")

WIDTH_ALIAS_MARKERS = (
    "pub fn read8InteropPolicyBytes(base_addr: usize, byte_offset: usize, unsafe_scope: u8, reserved: u8) PolicyError!u8 {",
    "pub fn write8InteropPolicyBytes(base_addr: usize, byte_offset: usize, value: u8, unsafe_scope: u8, reserved: u8) PolicyError!void {",
    "pub fn read8InteropPolicyByte(base_addr: usize, byte_offset: usize, unsafe_scope: u8) PolicyError!u8 {",
    "pub fn write8InteropPolicyByte(base_addr: usize, byte_offset: usize, value: u8, unsafe_scope: u8) PolicyError!void {",
    "pub fn read16InteropPolicyBytes(base_addr: usize, byte_offset: usize, unsafe_scope: u8, reserved: u8) PolicyError!u16 {",
    "pub fn write16InteropPolicyBytes(base_addr: usize, byte_offset: usize, value: u16, unsafe_scope: u8, reserved: u8) PolicyError!void {",
    "pub fn read16InteropPolicyByte(base_addr: usize, byte_offset: usize, unsafe_scope: u8) PolicyError!u16 {",
    "pub fn write16InteropPolicyByte(base_addr: usize, byte_offset: usize, value: u16, unsafe_scope: u8) PolicyError!void {",
    "pub fn read32InteropPolicyBytes(base_addr: usize, byte_offset: usize, unsafe_scope: u8, reserved: u8) PolicyError!u32 {",
    "pub fn write32InteropPolicyBytes(base_addr: usize, byte_offset: usize, value: u32, unsafe_scope: u8, reserved: u8) PolicyError!void {",
    "pub fn read32InteropPolicyByte(base_addr: usize, byte_offset: usize, unsafe_scope: u8) PolicyError!u32 {",
    "pub fn write32InteropPolicyByte(base_addr: usize, byte_offset: usize, value: u32, unsafe_scope: u8) PolicyError!void {",
    "pub fn read64InteropPolicyBytes(base_addr: usize, byte_offset: usize, unsafe_scope: u8, reserved: u8) PolicyError!u64 {",
    "pub fn write64InteropPolicyBytes(base_addr: usize, byte_offset: usize, value: u64, unsafe_scope: u8, reserved: u8) PolicyError!void {",
    "pub fn read64InteropPolicyByte(base_addr: usize, byte_offset: usize, unsafe_scope: u8) PolicyError!u64 {",
    "pub fn write64InteropPolicyByte(base_addr: usize, byte_offset: usize, value: u64, unsafe_scope: u8) PolicyError!void {",
)


def validate_mmio(mmio_path: Path) -> list[str]:
    try:
        text = mmio_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return [f"missing repo file: {mmio_path.as_posix()}"]

    issues: list[str] = []
    for marker in WIDTH_ALIAS_MARKERS:
        if marker not in text:
            issues.append(f"missing MMIO width alias marker: {marker}")
    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_mmio_width_aliases_") as temp_dir:
        root = Path(temp_dir)
        mmio_path = root / MMIO_PATH
        mmio_path.parent.mkdir(parents=True)
        mmio_path.write_text("\n".join(WIDTH_ALIAS_MARKERS) + "\n", encoding="utf-8")

        issues = validate_mmio(mmio_path)
        if issues:
            print("PHASE3_MMIO_WIDTH_ALIASES_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for marker in WIDTH_ALIAS_MARKERS:
            mmio_path.write_text(
                ("\n".join(WIDTH_ALIAS_MARKERS) + "\n").replace(marker + "\n", ""),
                encoding="utf-8",
            )
            issues = validate_mmio(mmio_path)
            expected = f"missing MMIO width alias marker: {marker}"
            if expected not in issues:
                print("PHASE3_MMIO_WIDTH_ALIASES_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

    print("PHASE3_MMIO_WIDTH_ALIASES_SELF_TEST=pass")
    print(f"PHASE3_MMIO_WIDTH_ALIASES_SELF_TEST_CASE_COUNT={len(WIDTH_ALIAS_MARKERS)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 3 MMIO width-specific interop-policy aliases."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains zigux/helpers/mmio.zig",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_mmio(args.repo_root / MMIO_PATH)
    if issues:
        print("PHASE3_MMIO_WIDTH_ALIASES=fail")
        print("\n".join(issues))
        return 1

    print(f"validated {MMIO_PATH.as_posix()}")
    print("PHASE3_MMIO_WIDTH_ALIASES=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
