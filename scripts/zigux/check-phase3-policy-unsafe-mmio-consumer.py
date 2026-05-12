#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
SURVEY_REL = "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md"
LOW_LEVEL_SURVEY_REL = "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md"
MMIO_REL = "zigux/helpers/mmio.zig"
LOW_LEVEL_TEST_REL = "zigux/tests/phase3_low_level_wrappers.zig"

REQUIRED_SURVEY_MARKERS = (
    "PHASE3_MMIO_PATH=zigux/helpers/mmio.zig",
    "PHASE3_POLICY_BYTE_GUARD=python3 scripts/zigux/check-phase3-policy-byte-guards.py",
    "PHASE3_BOUNDARY_GAP=no-dedicated-policy-unsafe-subslice-beyond-the-shared-abi-packet",
)

REQUIRED_LOW_LEVEL_SURVEY_MARKERS = (
    "PHASE3_MMIO_PATH=zigux/helpers/mmio.zig",
    "PHASE3_MMIO_SCOPE=range-read-write-8-16-32-64-plus-interop-policy-and-policy-byte-entrypoints",
    "PHASE3_LOW_LEVEL_TEST_PATH=zigux/tests/phase3_low_level_wrappers.zig",
    "PHASE3_LOW_LEVEL_GATE=zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
)

REQUIRED_SURVEY_SNIPPETS = (
    "`zigux/helpers/mmio.zig` consumes that same narrow layer for direct `range()`, `read8()`, `write8()`, `read16()`, `write16()`, `read32()`, `write32()`, `read64()`, and `write64()` access while also routing policy-aware MMIO through `allowsInteropPolicy*`, `requireInteropPolicy*`, `rangeInteropPolicy*`, `read*InteropPolicy*`, and `write*InteropPolicy*` relays so volatile-MMIO callers stay inside the bounded unsafe contract.",
    "`scripts/zigux/check-phase3-policy-byte-guards.py` gives the shared policy-and-unsafe survey validator a dedicated reserved-byte and typed-wrapper guard across the policy helpers, this survey note, and the explicit shared dump gate, so the existing `phase3-validate` path can fail closed on policy-byte drift instead of leaving that contract implicit.",
)

REQUIRED_LOW_LEVEL_SURVEY_SNIPPETS = (
    "`zigux/helpers/mmio.zig` keeps the approved MMIO packet explicit through direct 8-, 16-, 32-, and 64-bit reads and writes plus the interop-policy and policy-byte entrypoints that the focused replay exercises.",
    "`zigux/tests/phase3_low_level_wrappers.zig` is the current exact replay for this packet, including the MMIO interop-policy gate",
)

REQUIRED_MMIO_SNIPPETS = (
    "pub fn allowsInteropPolicyBytes(unsafe_scope: u8, reserved: u8) bool {",
    "pub fn allowsInteropPolicy(policy: abi.InteropPolicy) bool {",
    "pub fn requireInteropPolicy(policy: abi.InteropPolicy) MmioError!void {",
    "pub fn rangeInteropPolicy(base_addr: usize, length: u32, stride: u32, policy: abi.InteropPolicy) MmioError!Range {",
    "pub fn rangeInteropPolicyBytes(base_addr: usize, length: u32, stride: u32, unsafe_scope: u8, reserved: u8) MmioError!Range {",
    "pub fn read8InteropPolicy(base_addr: usize, offset: usize, policy: abi.InteropPolicy) MmioError!u8 {",
    "pub fn read16InteropPolicy(base_addr: usize, offset: usize, policy: abi.InteropPolicy) MmioError!u16 {",
    "pub fn read32InteropPolicy(base_addr: usize, offset: usize, policy: abi.InteropPolicy) MmioError!u32 {",
    "pub fn read64InteropPolicy(base_addr: usize, offset: usize, policy: abi.InteropPolicy) MmioError!u64 {",
    "pub fn write8InteropPolicy(base_addr: usize, offset: usize, value: u8, policy: abi.InteropPolicy) MmioError!void {",
    "pub fn write16InteropPolicy(base_addr: usize, offset: usize, value: u16, policy: abi.InteropPolicy) MmioError!void {",
    "pub fn write32InteropPolicy(base_addr: usize, offset: usize, value: u32, policy: abi.InteropPolicy) MmioError!void {",
    "pub fn write64InteropPolicy(base_addr: usize, offset: usize, value: u64, policy: abi.InteropPolicy) MmioError!void {",
    'test "phase3 mmio wrappers keep volatile-mmio policy gates reviewable" {',
)

REQUIRED_LOW_LEVEL_TEST_SNIPPETS = (
    'test "phase3 low-level wrappers keep mmio interop policy gates reviewable" {',
    "try std.testing.expect(mmio.allowsInteropPolicy(mmio_policy));",
    "const scoped_desc = try mmio.rangeInteropPolicy(base, 16, 4, mmio_policy);",
    "const byte_scoped_desc = try mmio.rangeInteropPolicyByte(base, 12, 2, @intFromEnum(abi.UnsafeScope.volatile_mmio));",
    "const bytes_scoped_desc = try mmio.rangeInteropPolicyBytes(",
    "try mmio.write8InteropPolicy(base, 0, 0x33, mmio_policy);",
    "try mmio.write16InteropPolicy(base, 2, 0x1234, mmio_policy);",
    "try mmio.write32InteropPolicy(base, 4, 0xfeed_beef, mmio_policy);",
    "try mmio.write64InteropPolicy(base, 8, 0x0123_4567_89ab_cdef, mmio_policy);",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.read32InteropPolicy(base, 4, no_unsafe_policy));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.write16InteropPolicy(base, 2, 0x7777, raw_pointer_policy));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.read8InteropPolicyBytes(base, 1, 1, 1));",
)


def _read_text(root: Path, rel: str, issues: list[str]) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(f"missing_file:{rel}")
        return ""


def _check_snippets(text: str, snippets: tuple[str, ...], prefix: str, issues: list[str]) -> None:
    for snippet in snippets:
        if snippet not in text:
            issues.append(f"{prefix}:{snippet}")


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    survey = _read_text(root, SURVEY_REL, issues)
    low_level_survey = _read_text(root, LOW_LEVEL_SURVEY_REL, issues)
    mmio = _read_text(root, MMIO_REL, issues)
    low_level_test = _read_text(root, LOW_LEVEL_TEST_REL, issues)

    if survey:
        _check_snippets(survey, REQUIRED_SURVEY_MARKERS, "missing_survey_marker", issues)
        _check_snippets(survey, REQUIRED_SURVEY_SNIPPETS, "missing_survey_snippet", issues)
    if low_level_survey:
        _check_snippets(
            low_level_survey,
            REQUIRED_LOW_LEVEL_SURVEY_MARKERS,
            "missing_low_level_survey_marker",
            issues,
        )
        _check_snippets(
            low_level_survey,
            REQUIRED_LOW_LEVEL_SURVEY_SNIPPETS,
            "missing_low_level_survey_snippet",
            issues,
        )
    if mmio:
        _check_snippets(mmio, REQUIRED_MMIO_SNIPPETS, "missing_mmio_snippet", issues)
    if low_level_test:
        _check_snippets(
            low_level_test,
            REQUIRED_LOW_LEVEL_TEST_SNIPPETS,
            "missing_low_level_test_snippet",
            issues,
        )
    return issues


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_policy_unsafe_mmio_consumer_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        _write(root, SURVEY_REL, "\n".join(REQUIRED_SURVEY_MARKERS + REQUIRED_SURVEY_SNIPPETS) + "\n")
        _write(
            root,
            LOW_LEVEL_SURVEY_REL,
            "\n".join(REQUIRED_LOW_LEVEL_SURVEY_MARKERS + REQUIRED_LOW_LEVEL_SURVEY_SNIPPETS) + "\n",
        )
        _write(root, MMIO_REL, "\n".join(REQUIRED_MMIO_SNIPPETS) + "\n")
        _write(root, LOW_LEVEL_TEST_REL, "\n".join(REQUIRED_LOW_LEVEL_TEST_SNIPPETS) + "\n")
        assert validate(root) == []

        _write(
            root,
            LOW_LEVEL_TEST_REL,
            "\n".join(
                snippet
                for snippet in REQUIRED_LOW_LEVEL_TEST_SNIPPETS
                if "write64InteropPolicy" not in snippet
            )
            + "\n",
        )
        issues = validate(root)
        assert (
            "missing_low_level_test_snippet:try mmio.write64InteropPolicy(base, 8, 0x0123_4567_89ab_cdef, mmio_policy);"
            in issues
        )

        _write(root, LOW_LEVEL_TEST_REL, "\n".join(REQUIRED_LOW_LEVEL_TEST_SNIPPETS) + "\n")
        _write(root, SURVEY_REL, "\n".join(REQUIRED_SURVEY_MARKERS + REQUIRED_SURVEY_SNIPPETS[:-1]) + "\n")
        issues = validate(root)
        assert f"missing_survey_snippet:{REQUIRED_SURVEY_SNIPPETS[-1]}" in issues

        _write(root, SURVEY_REL, "\n".join(REQUIRED_SURVEY_MARKERS + REQUIRED_SURVEY_SNIPPETS) + "\n")
        _write(
            root,
            LOW_LEVEL_SURVEY_REL,
            "\n".join(REQUIRED_LOW_LEVEL_SURVEY_MARKERS[:-1] + REQUIRED_LOW_LEVEL_SURVEY_SNIPPETS) + "\n",
        )
        issues = validate(root)
        assert f"missing_low_level_survey_marker:{REQUIRED_LOW_LEVEL_SURVEY_MARKERS[-1]}" in issues

        _write(
            root,
            LOW_LEVEL_SURVEY_REL,
            "\n".join(REQUIRED_LOW_LEVEL_SURVEY_MARKERS + REQUIRED_LOW_LEVEL_SURVEY_SNIPPETS) + "\n",
        )
        _write(
            root,
            MMIO_REL,
            "\n".join(
                snippet
                for snippet in REQUIRED_MMIO_SNIPPETS
                if snippet
                != "pub fn read64InteropPolicy(base_addr: usize, offset: usize, policy: abi.InteropPolicy) MmioError!u64 {"
            )
            + "\n",
        )
        issues = validate(root)
        assert (
            "missing_mmio_snippet:pub fn read64InteropPolicy(base_addr: usize, offset: usize, policy: abi.InteropPolicy) MmioError!u64 {"
            in issues
        )

    print("PHASE3_POLICY_UNSAFE_MMIO_CONSUMER_SELF_TEST=pass")
    print("PHASE3_POLICY_UNSAFE_MMIO_CONSUMER_SELF_TEST_CASE_COUNT=5")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate that the Phase 3 policy/unsafe packet still records and tests the live MMIO policy consumer surface."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated validator coverage.")
    parser.add_argument("root", nargs="?", help="Optional repo root override.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(Path(args.root).resolve() if args.root else ROOT)
    if issues:
        print("PHASE3_POLICY_UNSAFE_MMIO_CONSUMER=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE3_POLICY_UNSAFE_MMIO_CONSUMER=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
