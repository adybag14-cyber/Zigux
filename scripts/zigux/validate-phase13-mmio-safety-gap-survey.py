#!/usr/bin/env python3
"""Validate the current Phase 13 iomap/MMIO safety gap survey."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

NOTE_PATH = Path("Documentation/zigux/phase13-iomap-mmio-safety-gap-survey.md")
MMIO_PATH = Path("zigux/helpers/mmio.zig")
UNSAFE_POLICY_PATH = Path("zigux/helpers/unsafe_policy.zig")
NARROW_PATH = Path("zigux/unsafe/narrow.zig")
WRAPPER_REPLAY_PATH = Path("zigux/tests/phase3_low_level_wrappers.zig")
LOW_LEVEL_SURVEY_PATH = Path("Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md")
PHASE3_VALIDATOR_PATH = Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py")

REQUIRED_MARKERS = {
    NOTE_PATH: (
        "P13_L01_SCOPE=this lane stays inside the iomap/mmio safety surface survey and compares the current Zigux MMIO helper against the roadmap rule that approved MMIO wrappers must keep the unsafe surface narrow, reviewable, and validation-backed",
        "P13_L01_REPO_EVIDENCE=direct current-head readback reaches zigux/helpers/mmio.zig, zigux/helpers/unsafe_policy.zig, zigux/unsafe/narrow.zig, zigux/tests/phase3_low_level_wrappers.zig, Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md, and scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
        "P13_L01_ROADMAP_RULE=the roadmap keeps MMIO inside the approved atomic/barrier/MMIO wrapper family and requires wrapper-first handling plus a narrow unsafe surface rather than open-ended raw access",
        "P13_L01_FINDING_RANGE_IS_DESCRIPTIVE_ONLY=MmioRange is currently a descriptive blessed-window record, not an active access boundary, because later MMIO reads and writes do not consume the range object when they touch registers",
        "P13_L01_FINDING_NO_RANGE_BACKED_ACCESSORS=zigux/helpers/mmio.zig currently exposes range constructors and width-specific base-plus-offset helpers, but it does not yet expose range-backed read, write, exchange, or masked-update entry points that enforce length and stride at access time",
        "P13_L01_FINDING_WIDTH_HELPERS_BYPASS_WINDOW_REVIEW=the width-specific helpers validate alignment and interop policy, but they still operate on a raw base address plus offset, so they bypass any previously blessed MmioRange length or stride review surface",
        "P13_L01_FINDING_SURVEY_PACKET_OVERSTATES_CLOSURE=the existing low-level-wrapper survey truthfully lists the landed MMIO helper surface, but it does not keep these remaining range-enforcement gaps explicit, which makes the MMIO packet read closer to closed than the safety boundary actually is",
        "P13_L01_CONCLUSION=current master has landed the roadmap-approved MMIO wrapper leafs, but it has not yet closed the narrower safety gap where a blessed MMIO window should remain the object that later accessors validate against",
        "P13_L01_NEXT_STEP=add range-backed MMIO accessors that consume MmioRange at read/write time, reject out-of-range or stride-breaking offsets, and extend the focused low-level-wrapper replay so the survey can be tightened from gap-reporting to landed safety proof",
    ),
    MMIO_PATH: (
        "pub const MmioRange = extern struct {",
        "pub fn rangeScoped(base_addr: usize, length: u32, stride: u32, scope: abi.UnsafeScope) PolicyError!MmioRange {",
        "pub fn rangeInteropPolicy(base_addr: usize, length: u32, stride: u32, policy: abi.InteropPolicy) PolicyError!MmioRange {",
        "pub fn rangeInteropPolicyBytes(base_addr: usize, length: u32, stride: u32, unsafe_scope: u8, reserved: u8) PolicyError!MmioRange {",
        "pub fn rangeInteropPolicyByte(base_addr: usize, length: u32, stride: u32, unsafe_scope: u8) PolicyError!MmioRange {",
        "pub fn read8InteropPolicyBytes(base_addr: usize, byte_offset: usize, unsafe_scope: u8, reserved: u8) PolicyError!u8 {",
        "pub fn write8InteropPolicyBytes(base_addr: usize, byte_offset: usize, value: u8, unsafe_scope: u8, reserved: u8) PolicyError!void {",
        "pub fn read16InteropPolicyBytes(base_addr: usize, byte_offset: usize, unsafe_scope: u8, reserved: u8) PolicyError!u16 {",
        "pub fn write16InteropPolicyBytes(base_addr: usize, byte_offset: usize, value: u16, unsafe_scope: u8, reserved: u8) PolicyError!void {",
        "pub fn read32InteropPolicyByte(base_addr: usize, byte_offset: usize, unsafe_scope: u8) PolicyError!u32 {",
        "pub fn write32InteropPolicyByte(base_addr: usize, byte_offset: usize, value: u32, unsafe_scope: u8) PolicyError!void {",
        "pub fn read64InteropPolicyBytes(base_addr: usize, byte_offset: usize, unsafe_scope: u8, reserved: u8) PolicyError!u64 {",
        "pub fn write64InteropPolicyBytes(base_addr: usize, byte_offset: usize, value: u64, unsafe_scope: u8, reserved: u8) PolicyError!void {",
    ),
    UNSAFE_POLICY_PATH: (
        "pub fn permitsVolatileMmio(scope: abi.UnsafeScope) bool {",
        "pub fn permitsVolatileMmioInteropPolicy(policy: abi.InteropPolicy) bool {",
        "pub fn allowsVolatileMmioInteropPolicy(policy: abi.InteropPolicy) bool {",
    ),
    NARROW_PATH: (
        "pub const AccessBoundary = enum {",
        ".volatile_mmio_window",
        "pub fn permitsVolatileMmio(scope: UnsafeScopeTag) bool {",
    ),
    WRAPPER_REPLAY_PATH: (
        'test "phase3 low-level wrappers keep MMIO range helpers and width aliases explicit beside raw bridge gates" {',
        "const scoped_range = try mmio.rangeScoped(base_addr, 16, 4, .volatile_mmio);",
        "try mmio.write64InteropPolicyBytes(base_addr, 8, 0x0123_4567_89AB_CDEF, mmio_scope, 0);",
    ),
    LOW_LEVEL_SURVEY_PATH: (
        "Current `master` also keeps `MmioRange`, `rangeScoped()`, `rangeInteropPolicy()`, `rangeInteropPolicyBytes()`, `rangeInteropPolicyByte()`, and the width-specific `read8InteropPolicyBytes()`/`write8InteropPolicyBytes()`/`read16InteropPolicyBytes()`/`write16InteropPolicyBytes()`/`read32InteropPolicyByte()`/`write32InteropPolicyByte()`/`read64InteropPolicyBytes()`/`write64InteropPolicyBytes()` entrypoints directly readable in `zigux/helpers/mmio.zig`, so the bounded low-level-wrapper survey should treat those MMIO range and width-specific wrappers as landed helper-local evidence rather than collapsing MMIO coverage to the generic typed accessors alone.",
    ),
    PHASE3_VALIDATOR_PATH: (
        'MMIO_PATH: (',
        '"pub const MmioRange = extern struct {",',
        '"pub fn rangeInteropPolicyByte(base_addr: usize, length: u32, stride: u32, unsafe_scope: u8) PolicyError!MmioRange {",',
        '"pub fn write64InteropPolicyBytes(base_addr: usize, byte_offset: usize, value: u64, unsafe_scope: u8, reserved: u8) PolicyError!void {",',
    ),
}

SELF_TEST_MARKERS = tuple(
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
    with tempfile.TemporaryDirectory(prefix="zigux_phase13_mmio_survey_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE13_MMIO_SAFETY_SURVEY_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in SELF_TEST_MARKERS:
            _populate_repo(root)
            path = root / relative_path
            path.write_text(_read(path).replace(marker, ""), encoding="utf-8")
            issues = validate_repo(root)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE13_MMIO_SAFETY_SURVEY_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

    print("PHASE13_MMIO_SAFETY_SURVEY_SELF_TEST=pass")
    print(f"PHASE13_MMIO_SAFETY_SURVEY_SELF_TEST_CASE_COUNT={len(SELF_TEST_MARKERS)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 13 iomap/MMIO safety gap survey."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 13 survey note",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE13_MMIO_SAFETY_SURVEY=fail")
        print("\n".join(issues))
        return 1

    print(f"validated {NOTE_PATH.as_posix()}")
    print(f"validated {MMIO_PATH.as_posix()}")
    print(f"validated {UNSAFE_POLICY_PATH.as_posix()}")
    print(f"validated {NARROW_PATH.as_posix()}")
    print(f"validated {WRAPPER_REPLAY_PATH.as_posix()}")
    print(f"validated {LOW_LEVEL_SURVEY_PATH.as_posix()}")
    print(f"validated {PHASE3_VALIDATOR_PATH.as_posix()}")
    print("PHASE13_MMIO_SAFETY_SURVEY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
