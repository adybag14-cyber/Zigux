#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SURVEY_REL = "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md"
PANIC_POLICY_REL = "zigux/helpers/panic_policy.zig"
ALLOCATOR_POLICY_REL = "zigux/helpers/allocator_policy.zig"
UNSAFE_NARROW_REL = "zigux/unsafe/narrow.zig"
LOW_LEVEL_WRAPPER_TEST_REL = "zigux/tests/phase3_low_level_wrappers.zig"

REQUIRED_SURVEY_MARKERS = (
    "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py --slug abi",
    "PHASE3_POLICY_BYTE_GUARD=python3 scripts/zigux/check-phase3-policy-byte-guards.py",
    "PHASE3_POLICY_UNSAFE_SURVEY_VALIDATOR_PATH=scripts/zigux/validate-phase3-policy-unsafe-survey.py",
)

REQUIRED_SURVEY_EXACT_LINES = (
    "PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig",
    "`zigux/helpers/panic_policy.zig` now keeps panic action explicit both through the typed enum path and through `modeFromInteropPolicyBytes`, `actionForInteropPolicyBytes`, and `canReturnInteropPolicyBytes` so unknown panic modes and nonzero reserved bytes fail closed before raw-byte callers infer behavior elsewhere in the packet.",
    "`zigux/helpers/allocator_policy.zig` now keeps caller-provided ownership and global-fallback policy explicit both through the typed predicates and through `modeFromInteropPolicyBytes`, `requiresExplicitCallerPolicyBytes`, `requiresExplicitCallerInteropPolicy`, `requiresExplicitCallerByte`, `permitsGlobalFallbackPolicyBytes`, `permitsGlobalFallbackInteropPolicy`, and `permitsGlobalFallbackByte` so unknown allocator modes and nonzero reserved bytes fail closed before raw-byte or typed shared callers infer behavior elsewhere in the packet.",
    "`zigux/unsafe/narrow.zig` still keeps the raw-pointer bridge deliberately small, but it now also decodes `InteropPolicy` unsafe-scope bytes explicitly through `scopeFromInteropPolicyBytes`, `recognizesInteropPolicyBytes`, `permitsVolatileMmioPolicyBytes`, and `permitsRawPointerBridgePolicyBytes` so unknown scopes and reserved-byte drift do not have to be inferred elsewhere in the packet.",
    "`zigux/unsafe/narrow.zig` now also mirrors the panic and allocator helper style with both typed and byte-scoped raw-pointer-bridge entry points, including `scopeFromInteropPolicy`, `recognizesInteropPolicy`, `permitsNoUnsafeInteropPolicy`, `permitsVolatileMmioInteropPolicy`, `permitsRawPointerBridgeInteropPolicy`, the new `requireRawPointerBridgeByte` gate, and matching `pointerAt*`, `constSliceAt*`, `constPointerAt*`, and `writeValueAt*` relay families so shared callers do not have to split unsafe-scope bytes out by hand before checking or using the bounded unsafe contract.",
)

REQUIRED_PANIC_SNIPPETS = (
    "pub fn modeFromInteropPolicyBytes(mode: u8, reserved: u8) ?abi.PanicMode {",
    "if (reserved != 0) return null;",
    "pub fn recognizesInteropPolicy(policy: abi.InteropPolicy) bool {",
    "return modeFromInteropPolicy(policy) != null;",
    "pub fn recognizesByte(mode: u8) bool {",
    "return recognizesInteropPolicyBytes(mode, 0);",
    "pub fn actionForInteropPolicyBytes(mode: u8, reserved: u8) ?Action {",
    "return actionFor(modeFromInteropPolicyBytes(mode, reserved) orelse return null);",
    "pub fn actionForInteropPolicy(policy: abi.InteropPolicy) ?Action {",
    "pub fn actionForByte(mode: u8) ?Action {",
    "pub fn canReturnInteropPolicyBytes(mode: u8, reserved: u8) bool {",
    "return actionForInteropPolicyBytes(mode, reserved) == .warn_and_return;",
    "pub fn canReturnInteropPolicy(policy: abi.InteropPolicy) bool {",
    "pub fn canReturnByte(mode: u8) bool {",
    "try std.testing.expect(recognizesByte(0));",
    "try std.testing.expect(!recognizesByte(9));",
    "try std.testing.expectEqual(@as(?abi.PanicMode, null), modeFromInteropPolicyBytes(2, 1));",
    "try std.testing.expect(recognizesInteropPolicy(abort_policy));",
    "try std.testing.expect(!recognizesInteropPolicy(unknown_policy));",
    "try std.testing.expect(!recognizesInteropPolicy(reserved_policy));",
    "try std.testing.expectEqual(@as(?abi.PanicMode, null), modeFromInteropPolicy(unknown_policy));",
    "try std.testing.expectEqual(@as(?Action, null), actionForInteropPolicyBytes(2, 1));",
    "try std.testing.expectEqual(@as(?Action, .abort_now), actionForInteropPolicy(abort_policy));",
    "try std.testing.expectEqual(@as(?Action, .warn_and_return), actionForInteropPolicy(warn_policy));",
    "try std.testing.expectEqual(@as(?Action, null), actionForInteropPolicy(unknown_policy));",
    "try std.testing.expectEqual(@as(?Action, null), actionForInteropPolicy(reserved_policy));",
    "try std.testing.expect(!canReturnByte(0));",
    "try std.testing.expect(canReturnByte(2));",
    "try std.testing.expect(!canReturnByte(9));",
    "try std.testing.expect(!canReturnInteropPolicyBytes(2, 1));",
    "try std.testing.expect(!canReturnInteropPolicy(abort_policy));",
    "try std.testing.expect(canReturnInteropPolicy(warn_policy));",
    "try std.testing.expect(!canReturnInteropPolicy(unknown_policy));",
    "try std.testing.expect(!canReturnInteropPolicy(reserved_policy));",
)

REQUIRED_ALLOCATOR_SNIPPETS = (
    "pub fn modeFromInteropPolicyBytes(mode: u8, reserved: u8) ?abi.AllocatorMode {",
    "if (reserved != 0) return null;",
    "pub fn recognizesInteropPolicy(policy: abi.InteropPolicy) bool {",
    "return modeFromInteropPolicy(policy) != null;",
    "pub fn recognizesByte(mode: u8) bool {",
    "return recognizesInteropPolicyBytes(mode, 0);",
    "pub fn requiresExplicitCallerPolicyBytes(mode: u8, reserved: u8) bool {",
    "return modeFromInteropPolicyBytes(mode, reserved) == .caller_provided;",
    "pub fn permitsGlobalFallbackPolicyBytes(mode: u8, reserved: u8) bool {",
    "return switch (modeFromInteropPolicyBytes(mode, reserved) orelse return false) {",
    "try std.testing.expect(recognizesByte(0));",
    "try std.testing.expect(!recognizesByte(9));",
    "try std.testing.expectEqual(@as(?abi.AllocatorMode, null), modeFromInteropPolicyBytes(2, 1));",
    "try std.testing.expect(recognizesInteropPolicy(caller_policy));",
    "try std.testing.expect(!recognizesInteropPolicy(unknown_policy));",
    "try std.testing.expect(!recognizesInteropPolicy(reserved_policy));",
    "try std.testing.expect(!requiresExplicitCallerPolicyBytes(2, 1));",
    "try std.testing.expect(!permitsGlobalFallbackPolicyBytes(2, 1));",
)

REQUIRED_UNSAFE_SNIPPETS = (
    "const abi = @import(\"abi_bindings\");",
    "pub fn scopeFromInteropPolicy(policy: abi.InteropPolicy) ?UnsafeScopeTag {",
    "pub fn recognizesInteropPolicy(policy: abi.InteropPolicy) bool {",
    "pub fn recognizesByte(unsafe_scope: u8) bool {",
    "return recognizesInteropPolicyBytes(unsafe_scope, 0);",
    "pub fn permitsNoUnsafeInteropPolicy(policy: abi.InteropPolicy) bool {",
    "pub fn permitsVolatileMmioInteropPolicy(policy: abi.InteropPolicy) bool {",
    "pub fn permitsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {",
    "pub fn requireRawPointerBridgeByte(unsafe_scope: u8) UnsafeScopeError!void {",
    "if (reserved != 0) return null;",
    "try std.testing.expect(recognizesByte(0));",
    "try std.testing.expect(!recognizesByte(9));",
    "try std.testing.expect(!recognizesInteropPolicyBytes(1, 1));",
    "try std.testing.expectEqual(@as(?UnsafeScopeTag, .raw_pointer_bridge), scopeFromInteropPolicy(raw_policy));",
    "try std.testing.expect(recognizesInteropPolicy(raw_policy));",
    "try std.testing.expect(!recognizesInteropPolicy(reserved_policy));",
    "try std.testing.expect(permitsNoUnsafeInteropPolicy(none_policy));",
    "try std.testing.expect(permitsVolatileMmioInteropPolicy(mmio_policy));",
    "try std.testing.expect(!permitsRawPointerBridgeInteropPolicy(reserved_policy));",
    "try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridgeByte(0));",
    "try requireRawPointerBridgeByte(2);",
)

REQUIRED_LOW_LEVEL_WRAPPER_SNIPPETS = (
    "try std.testing.expect(narrow.permitsRawPointerBridgeInteropPolicy(raw_policy));",
    "try std.testing.expect(!narrow.permitsRawPointerBridgeInteropPolicy(mmio_policy));",
    "const third_addr = narrow.byteOffset(base, @sizeOf(u32) * 2);",
    "const scoped_ptr = try narrow.pointerAtInteropPolicy(u32, base, @sizeOf(u32), raw_policy);",
    "const scoped_slice = try narrow.constSliceAtInteropPolicy(u32, base, values.len, raw_policy);",
    "const scoped_const_ptr = try narrow.constPointerAtInteropPolicyBytes(u32, third_addr, 2, 0);",
    "try narrow.writeValueAtInteropPolicy(u32, base, 55, raw_policy);",
    "try narrow.writeValueAtInteropPolicyBytes(u32, third_addr, 66, 2, 0);",
    "try mmio.write8InteropPolicyBytes(base, 1, 0x44, @intFromEnum(abi.UnsafeScope.volatile_mmio), 0);",
    "try mmio.read8InteropPolicyBytes(base, 1, @intFromEnum(abi.UnsafeScope.volatile_mmio), 0),",
    "try mmio.write32InteropPolicyByte(base, 4, 0xc001_d00d, @intFromEnum(abi.UnsafeScope.volatile_mmio));",
    "try mmio.read32InteropPolicyByte(base, 4, @intFromEnum(abi.UnsafeScope.volatile_mmio)),",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.read8InteropPolicyBytes(base, 1, 1, 1));",
    "mmio.read32InteropPolicyByte(base, 4, @intFromEnum(abi.UnsafeScope.none)),",
    "mmio.write32InteropPolicyByte(base, 4, 0, @intFromEnum(abi.UnsafeScope.raw_pointer_bridge)),",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.write64InteropPolicyBytes(base, 8, 0, 0, 0));",
    "try std.testing.expectError(error.UnsafeScopeDenied, narrow.pointerAtInteropPolicy(u32, base, 0, mmio_policy));",
    "try std.testing.expectError(error.UnsafeScopeDenied, narrow.constSliceAtInteropPolicy(u32, base, values.len, no_unsafe_policy));",
    "try std.testing.expectError(error.UnsafeScopeDenied, narrow.constPointerAtInteropPolicyBytes(u32, third_addr, 2, 1));",
    "try std.testing.expectError(error.UnsafeScopeDenied, narrow.writeValueAtInteropPolicy(u32, base, 77, reserved_policy));",
)


def require_snippets(issues: list[str], text: str, prefix: str, snippets: tuple[str, ...]) -> None:
    for snippet in snippets:
        if snippet not in text:
            issues.append(f"missing_{prefix}_snippet:{snippet}")


def normalized_marker_lines(text: str) -> list[str]:
    lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("- "):
            line = line[2:].strip()
        if line.startswith("`") and line.endswith("`"):
            line = line[1:-1]
        lines.append(line)
    return lines


def require_exact_line_count(
    issues: list[str],
    text: str,
    prefix: str,
    line: str,
    *,
    normalized: bool = False,
    expected_count: int = 1,
) -> None:
    lines = normalized_marker_lines(text) if normalized else text.splitlines()
    count = lines.count(line)
    if count == expected_count:
        return
    if count == 0:
        issues.append(f"missing_{prefix}:{line}")
        return
    issues.append(f"duplicate_{prefix}:{line}:{count}")


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    survey = (root / SURVEY_REL).read_text(encoding="utf-8")
    panic = (root / PANIC_POLICY_REL).read_text(encoding="utf-8")
    allocator = (root / ALLOCATOR_POLICY_REL).read_text(encoding="utf-8")
    unsafe = (root / UNSAFE_NARROW_REL).read_text(encoding="utf-8")
    low_level_wrapper = (root / LOW_LEVEL_WRAPPER_TEST_REL).read_text(encoding="utf-8")

    for marker in REQUIRED_SURVEY_MARKERS:
        require_exact_line_count(issues, survey, "survey_marker", marker, normalized=True)
    for line in REQUIRED_SURVEY_EXACT_LINES:
        require_exact_line_count(issues, survey, "survey_line", line, normalized=True)

    require_snippets(issues, panic, "panic", REQUIRED_PANIC_SNIPPETS)
    require_snippets(issues, allocator, "allocator", REQUIRED_ALLOCATOR_SNIPPETS)
    require_snippets(issues, unsafe, "unsafe", REQUIRED_UNSAFE_SNIPPETS)
    require_snippets(issues, low_level_wrapper, "low_level_wrapper", REQUIRED_LOW_LEVEL_WRAPPER_SNIPPETS)
    return issues


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def build_valid_workspace(root: Path) -> None:
    survey_lines = ["# survey"]
    survey_lines.extend(f"`{marker}`" for marker in REQUIRED_SURVEY_MARKERS)
    survey_lines.extend(f"- `{line}`" if line.startswith("PHASE3_") else f"- {line}" for line in REQUIRED_SURVEY_EXACT_LINES)
    survey_lines.append("")
    write(root / SURVEY_REL, "\n".join(survey_lines))
    write(root / PANIC_POLICY_REL, "\n".join([*REQUIRED_PANIC_SNIPPETS, ""]))
    write(root / ALLOCATOR_POLICY_REL, "\n".join([*REQUIRED_ALLOCATOR_SNIPPETS, ""]))
    write(root / UNSAFE_NARROW_REL, "\n".join([*REQUIRED_UNSAFE_SNIPPETS, ""]))
    write(root / LOW_LEVEL_WRAPPER_TEST_REL, "\n".join([*REQUIRED_LOW_LEVEL_WRAPPER_SNIPPETS, ""]))


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_policy_byte_guard_") as tmp_dir:
        root = Path(tmp_dir)
        build_valid_workspace(root)
        assert validate(root) == []

        broken_validate_marker = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            "`PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py --slug abi`\n",
            "",
            1,
        )
        write(root / SURVEY_REL, broken_validate_marker)
        issues = validate(root)
        assert (
            "missing_survey_marker:PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py --slug abi"
            in issues
        )

        build_valid_workspace(root)
        duplicate_validate_marker = (root / SURVEY_REL).read_text(encoding="utf-8") + (
            "`PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py --slug abi`\n"
        )
        write(root / SURVEY_REL, duplicate_validate_marker)
        issues = validate(root)
        assert (
            "duplicate_survey_marker:PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py --slug abi:2"
            in issues
        )

        build_valid_workspace(root)
        broken_guard_marker = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            "`PHASE3_POLICY_BYTE_GUARD=python3 scripts/zigux/check-phase3-policy-byte-guards.py`\n",
            "",
            1,
        )
        write(root / SURVEY_REL, broken_guard_marker)
        issues = validate(root)
        assert (
            "missing_survey_marker:PHASE3_POLICY_BYTE_GUARD=python3 scripts/zigux/check-phase3-policy-byte-guards.py"
            in issues
        )

        build_valid_workspace(root)
        broken_validator_path_marker = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            "`PHASE3_POLICY_UNSAFE_SURVEY_VALIDATOR_PATH=scripts/zigux/validate-phase3-policy-unsafe-survey.py`\n",
            "",
            1,
        )
        write(root / SURVEY_REL, broken_validator_path_marker)
        issues = validate(root)
        assert (
            "missing_survey_marker:PHASE3_POLICY_UNSAFE_SURVEY_VALIDATOR_PATH=scripts/zigux/validate-phase3-policy-unsafe-survey.py"
            in issues
        )

        build_valid_workspace(root)
        broken_survey = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            "modeFromInteropPolicyBytes`, `actionForInteropPolicyBytes`, and `canReturnInteropPolicyBytes`",
            "modeFromByte`, `actionForByte`, and `canReturnByte`",
            1,
        )
        write(root / SURVEY_REL, broken_survey)
        issues = validate(root)
        assert any(issue.startswith("missing_survey_line:") for issue in issues)

        build_valid_workspace(root)
        broken_allocator_survey = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            REQUIRED_SURVEY_EXACT_LINES[2] + "\n",
            "",
            1,
        )
        write(root / SURVEY_REL, broken_allocator_survey)
        issues = validate(root)
        assert f"missing_survey_line:{REQUIRED_SURVEY_EXACT_LINES[2]}" in issues

        build_valid_workspace(root)
        duplicate_dump_gate = (root / SURVEY_REL).read_text(encoding="utf-8") + "- `PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig`\n"
        write(root / SURVEY_REL, duplicate_dump_gate)
        issues = validate(root)
        assert (
            "duplicate_survey_line:PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig:2"
            in issues
        )

        build_valid_workspace(root)
        broken_dump_gate = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            "- `PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig`\n",
            "",
            1,
        )
        write(root / SURVEY_REL, broken_dump_gate)
        issues = validate(root)
        assert (
            "missing_survey_line:PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig"
            in issues
        )

        build_valid_workspace(root)
        broken_panic = (root / PANIC_POLICY_REL).read_text(encoding="utf-8").replace(
            "try std.testing.expect(recognizesInteropPolicy(abort_policy));\n",
            "",
            1,
        )
        write(root / PANIC_POLICY_REL, broken_panic)
        issues = validate(root)
        assert "missing_panic_snippet:try std.testing.expect(recognizesInteropPolicy(abort_policy));" in issues

        build_valid_workspace(root)
        broken_panic_typed_wrapper = (root / PANIC_POLICY_REL).read_text(encoding="utf-8").replace(
            "try std.testing.expect(canReturnInteropPolicy(warn_policy));\n",
            "",
            1,
        )
        write(root / PANIC_POLICY_REL, broken_panic_typed_wrapper)
        issues = validate(root)
        assert "missing_panic_snippet:try std.testing.expect(canReturnInteropPolicy(warn_policy));" in issues

        build_valid_workspace(root)
        broken_panic_unknown_policy = (root / PANIC_POLICY_REL).read_text(encoding="utf-8").replace(
            "try std.testing.expectEqual(@as(?Action, null), actionForInteropPolicy(unknown_policy));\n",
            "",
            1,
        )
        write(root / PANIC_POLICY_REL, broken_panic_unknown_policy)
        issues = validate(root)
        assert "missing_panic_snippet:try std.testing.expectEqual(@as(?Action, null), actionForInteropPolicy(unknown_policy));" in issues

        build_valid_workspace(root)
        broken_allocator = (root / ALLOCATOR_POLICY_REL).read_text(encoding="utf-8").replace(
            "try std.testing.expect(!recognizesInteropPolicy(unknown_policy));\n",
            "",
            1,
        )
        write(root / ALLOCATOR_POLICY_REL, broken_allocator)
        issues = validate(root)
        assert (
            "missing_allocator_snippet:try std.testing.expect(!recognizesInteropPolicy(unknown_policy));"
            in issues
        )

        build_valid_workspace(root)
        broken_unsafe = (root / UNSAFE_NARROW_REL).read_text(encoding="utf-8").replace(
            "try std.testing.expect(!recognizesInteropPolicyBytes(1, 1));\n",
            "",
            1,
        )
        write(root / UNSAFE_NARROW_REL, broken_unsafe)
        issues = validate(root)
        assert "missing_unsafe_snippet:try std.testing.expect(!recognizesInteropPolicyBytes(1, 1));" in issues

        build_valid_workspace(root)
        broken_typed_unsafe = (root / UNSAFE_NARROW_REL).read_text(encoding="utf-8").replace(
            "pub fn permitsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {\n",
            "",
            1,
        )
        write(root / UNSAFE_NARROW_REL, broken_typed_unsafe)
        issues = validate(root)
        assert "missing_unsafe_snippet:pub fn permitsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {" in issues

        build_valid_workspace(root)
        broken_unsafe_require_byte = (root / UNSAFE_NARROW_REL).read_text(encoding="utf-8").replace(
            "pub fn requireRawPointerBridgeByte(unsafe_scope: u8) UnsafeScopeError!void {\n",
            "",
            1,
        )
        write(root / UNSAFE_NARROW_REL, broken_unsafe_require_byte)
        issues = validate(root)
        assert "missing_unsafe_snippet:pub fn requireRawPointerBridgeByte(unsafe_scope: u8) UnsafeScopeError!void {" in issues

        build_valid_workspace(root)
        broken_unsafe_require_byte_replay = (root / UNSAFE_NARROW_REL).read_text(encoding="utf-8").replace(
            "try requireRawPointerBridgeByte(2);\n",
            "",
            1,
        )
        write(root / UNSAFE_NARROW_REL, broken_unsafe_require_byte_replay)
        issues = validate(root)
        assert "missing_unsafe_snippet:try requireRawPointerBridgeByte(2);" in issues

        build_valid_workspace(root)
        broken_unsafe_recognizes_byte = (root / UNSAFE_NARROW_REL).read_text(encoding="utf-8").replace(
            "pub fn recognizesByte(unsafe_scope: u8) bool {\n",
            "",
            1,
        )
        write(root / UNSAFE_NARROW_REL, broken_unsafe_recognizes_byte)
        issues = validate(root)
        assert "missing_unsafe_snippet:pub fn recognizesByte(unsafe_scope: u8) bool {" in issues

        build_valid_workspace(root)
        broken_low_level_wrapper = (root / LOW_LEVEL_WRAPPER_TEST_REL).read_text(encoding="utf-8").replace(
            "const scoped_slice = try narrow.constSliceAtInteropPolicy(u32, base, values.len, raw_policy);\n",
            "",
            1,
        )
        write(root / LOW_LEVEL_WRAPPER_TEST_REL, broken_low_level_wrapper)
        issues = validate(root)
        assert (
            "missing_low_level_wrapper_snippet:const scoped_slice = try narrow.constSliceAtInteropPolicy(u32, base, values.len, raw_policy);"
            in issues
        )

        build_valid_workspace(root)
        broken_low_level_mmio_positive = (root / LOW_LEVEL_WRAPPER_TEST_REL).read_text(encoding="utf-8").replace(
            "try mmio.write32InteropPolicyByte(base, 4, 0xc001_d00d, @intFromEnum(abi.UnsafeScope.volatile_mmio));\n",
            "",
            1,
        )
        write(root / LOW_LEVEL_WRAPPER_TEST_REL, broken_low_level_mmio_positive)
        issues = validate(root)
        assert (
            "missing_low_level_wrapper_snippet:try mmio.write32InteropPolicyByte(base, 4, 0xc001_d00d, @intFromEnum(abi.UnsafeScope.volatile_mmio));"
            in issues
        )

        build_valid_workspace(root)
        broken_low_level_mmio_denial = (root / LOW_LEVEL_WRAPPER_TEST_REL).read_text(encoding="utf-8").replace(
            "try std.testing.expectError(error.UnsafeScopeDenied, mmio.write64InteropPolicyBytes(base, 8, 0, 0, 0));\n",
            "",
            1,
        )
        write(root / LOW_LEVEL_WRAPPER_TEST_REL, broken_low_level_mmio_denial)
        issues = validate(root)
        assert (
            "missing_low_level_wrapper_snippet:try std.testing.expectError(error.UnsafeScopeDenied, mmio.write64InteropPolicyBytes(base, 8, 0, 0, 0));"
            in issues
        )

    print("PHASE3_POLICY_BYTE_GUARDS_SELF_TEST=pass")
    print("PHASE3_POLICY_BYTE_GUARDS_SELF_TEST_CASE_COUNT=19")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 3 policy helpers and survey still guard InteropPolicy reserved bytes."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated checker coverage.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(ROOT)
    if issues:
        print("PHASE3_POLICY_BYTE_GUARDS=fail")
        print("PHASE3_POLICY_BYTE_GUARDS_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE3_POLICY_BYTE_GUARDS_ISSUES_END")
        return 1

    print("PHASE3_POLICY_BYTE_GUARDS=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
