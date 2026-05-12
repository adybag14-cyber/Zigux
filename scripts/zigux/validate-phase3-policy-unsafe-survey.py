#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
SURVEY_REL = "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md"
MAKEFILE_REL = "zigux/Makefile"
LAYOUT_ASSERT_REL = "zigux/helpers/layout_assert.zig"
PANIC_POLICY_REL = "zigux/helpers/panic_policy.zig"
ALLOCATOR_POLICY_REL = "zigux/helpers/allocator_policy.zig"
MMIO_REL = "zigux/helpers/mmio.zig"
UNSAFE_NARROW_REL = "zigux/unsafe/narrow.zig"
POLICY_BYTE_GUARD_REL = "scripts/zigux/check-phase3-policy-byte-guards.py"
ABI_TEST_REL = "zigux/tests/phase3_abi.zig"
ABI_DUMP_REL = "zigux/tests/phase3_abi_dump.zig"
ABI_EXPECTED_REL = "zigux/tests/fixtures/phase3_abi/expected.json"
ABI_MANIFEST_REL = "zigux/tests/fixtures/phase3_abi_manifest.json"
ABI_SLICE_DOC_REL = "Documentation/zigux/phase3-abi-slice.md"

PATH_MARKERS = {
    "PHASE3_LAYOUT_ASSERT_PATH": LAYOUT_ASSERT_REL,
    "PHASE3_PANIC_POLICY_PATH": PANIC_POLICY_REL,
    "PHASE3_ALLOCATOR_POLICY_PATH": ALLOCATOR_POLICY_REL,
    "PHASE3_MMIO_PATH": MMIO_REL,
    "PHASE3_UNSAFE_PATH": UNSAFE_NARROW_REL,
    "PHASE3_ABI_TEST_PATH": ABI_TEST_REL,
    "PHASE3_ABI_DUMP_PATH": ABI_DUMP_REL,
}

STATIC_MARKERS = (
    "PHASE3_LAYOUT_ASSERT_SCOPE=generic-layout-helper-plus-canonical-abi-byte-and-field-asserts-consumed-by-shared-abi-replays",
    "PHASE3_PANIC_POLICY=explicit-modes-only",
    "PHASE3_ALLOCATOR_POLICY=explicit-modes-only",
    "PHASE3_UNSAFE_SCOPE=narrow-mmio-and-raw-pointer-bridge",
    "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py --slug abi",
    "PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug abi",
    "PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig",
    "PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig",
    "PHASE3_POLICY_BYTE_GUARD=python3 scripts/zigux/check-phase3-policy-byte-guards.py",
    "PHASE3_BOUNDARY_GAP=no-dedicated-policy-unsafe-subslice-beyond-the-shared-abi-packet",
    "PHASE3_NEXT_BOUNDED_STEP=keep-this-survey-aligned-with-the-live-helper-roles-and-shared-abi-markers-until-a-real-policy-or-unsafe-helper-expansion-lands",
)

BLOB_MARKERS = {
    "PHASE3_LAYOUT_ASSERT_BLOB_SHA": LAYOUT_ASSERT_REL,
    "PHASE3_PANIC_POLICY_BLOB_SHA": PANIC_POLICY_REL,
    "PHASE3_ALLOCATOR_POLICY_BLOB_SHA": ALLOCATOR_POLICY_REL,
    "PHASE3_MMIO_BLOB_SHA": MMIO_REL,
    "PHASE3_UNSAFE_BLOB_SHA": UNSAFE_NARROW_REL,
    "PHASE3_ABI_TEST_BLOB_SHA": ABI_TEST_REL,
    "PHASE3_ABI_DUMP_BLOB_SHA": ABI_DUMP_REL,
    "PHASE3_ABI_MANIFEST_BLOB_SHA": ABI_MANIFEST_REL,
    "PHASE3_ABI_SLICE_DOC_BLOB_SHA": ABI_SLICE_DOC_REL,
}

MAKEFILE_REQUIRED_LINES = (
    "phase3-validate:",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-policy-unsafe-survey.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "phase3-abi:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-test --build-file zigux/tests/build.zig",
    "phase3-interop:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-dump --build-file zigux/tests/build.zig",
)

REQUIRED_SURVEY_SNIPPETS = (
    "`zigux/helpers/layout_assert.zig` is still a small generic helper, but it now centralizes compile-time layout checks for `BoundaryHeader`, `ExportStatus`, and `InteropPolicy`",
    "`zigux/helpers/panic_policy.zig` keeps panic action explicit both through the typed enum path and through `modeFromInteropPolicyBytes`, `actionForInteropPolicyBytes`, and `canReturnInteropPolicyBytes`",
    "`zigux/helpers/allocator_policy.zig` keeps caller-provided ownership and global-fallback policy explicit both through the typed predicates and through `modeFromInteropPolicyBytes`, `requiresExplicitCallerPolicyBytes`, `requiresExplicitCallerInteropPolicy`, `requiresExplicitCallerByte`, `permitsGlobalFallbackPolicyBytes`, `permitsGlobalFallbackInteropPolicy`, and `permitsGlobalFallbackByte`",
    "`zigux/unsafe/narrow.zig` still keeps the raw-pointer bridge deliberately small, but it also decodes `InteropPolicy` unsafe-scope bytes explicitly through `scopeFromInteropPolicyBytes`, `recognizesInteropPolicyBytes`, `permitsVolatileMmioPolicyBytes`, and `permitsRawPointerBridgePolicyBytes`",
    "`zigux/helpers/mmio.zig` consumes that same narrow layer for direct `range()`, `read8()`, `write8()`, `read16()`, `write16()`, `read32()`, `write32()`, `read64()`, and `write64()` access while also routing policy-aware MMIO through `allowsInteropPolicy*`, `requireInteropPolicy*`, `rangeInteropPolicy*`, `read*InteropPolicy*`, and `write*InteropPolicy*` relays",
    "`scripts/zigux/check-phase3-policy-byte-guards.py` gives the shared policy-and-unsafe survey validator a dedicated reserved-byte and typed-wrapper guard",
    "`zigux/tests/phase3_abi.zig` is the live shared Zig proof packet for this family today, but it currently proves the `BoundaryHeader`, `ExportStatus`, and `InteropPolicy` layouts, exported constants, and `export_shim` compatibility rules directly against `abi_bindings` and `export_shim`",
    "`zigux/tests/phase3_abi_dump.zig` keeps the current shared dump path explicit by emitting ABI constants plus the `InteropPolicy` and chrdev budget-window struct layouts",
)

REQUIRED_LAYOUT_ASSERT_SNIPPETS = (
    "pub fn assertBoundaryHeaderLayout() !void {",
    "pub fn assertExportStatusLayout() !void {",
    "pub fn assertInteropPolicyLayout() !void {",
    "pub fn assertInteropPolicyModeValues() void {",
    'byteValue("unsafe_scope.raw_pointer_bridge", @intFromEnum(abi.UnsafeScope.raw_pointer_bridge), abi.UNSAFE_RAW_POINTER_BRIDGE);',
    'test "phase3 layout assertions cover canonical bindings" {',
)

REQUIRED_PANIC_POLICY_SNIPPETS = (
    "pub fn modeFromInteropPolicyBytes(mode: u8, reserved: u8) ?abi.PanicMode {",
    "pub fn actionForInteropPolicyBytes(mode: u8, reserved: u8) ?Action {",
    "pub fn canReturnInteropPolicyBytes(mode: u8, reserved: u8) bool {",
    'try std.testing.expectEqual(@as(?abi.PanicMode, null), modeFromInteropPolicyBytes(2, 1));',
    'try std.testing.expectEqual(@as(?Action, null), actionForInteropPolicyBytes(2, 1));',
    'try std.testing.expect(!canReturnInteropPolicyBytes(2, 1));',
)

REQUIRED_ALLOCATOR_POLICY_SNIPPETS = (
    "pub fn modeFromInteropPolicyBytes(mode: u8, reserved: u8) ?abi.AllocatorMode {",
    "pub fn requiresExplicitCallerPolicyBytes(mode: u8, reserved: u8) bool {",
    "pub fn permitsGlobalFallbackPolicyBytes(mode: u8, reserved: u8) bool {",
    'try std.testing.expectEqual(@as(?abi.AllocatorMode, null), modeFromInteropPolicyBytes(2, 1));',
    'try std.testing.expect(!requiresExplicitCallerPolicyBytes(2, 1));',
    'try std.testing.expect(!permitsGlobalFallbackPolicyBytes(2, 1));',
)

REQUIRED_MMIO_SNIPPETS = (
    "pub fn range(base_addr: usize, length: u32, stride: u32) Range {",
    "pub fn allowsInteropPolicy(policy: abi.InteropPolicy) bool {",
    "pub fn requireInteropPolicy(policy: abi.InteropPolicy) MmioError!void {",
    "pub fn rangeInteropPolicy(base_addr: usize, length: u32, stride: u32, policy: abi.InteropPolicy) MmioError!Range {",
    "pub fn read32InteropPolicy(base_addr: usize, offset: usize, policy: abi.InteropPolicy) MmioError!u32 {",
    "pub fn write32InteropPolicy(base_addr: usize, offset: usize, value: u32, policy: abi.InteropPolicy) MmioError!void {",
    'test "phase3 mmio wrappers keep volatile-mmio policy gates reviewable" {',
)

REQUIRED_UNSAFE_SNIPPETS = (
    "pub fn scopeFromInteropPolicyBytes(unsafe_scope: u8, reserved: u8) ?UnsafeScopeTag {",
    "pub fn scopeFromInteropPolicy(policy: abi.InteropPolicy) ?UnsafeScopeTag {",
    "pub fn recognizesInteropPolicy(policy: abi.InteropPolicy) bool {",
    "pub fn permitsVolatileMmioInteropPolicy(policy: abi.InteropPolicy) bool {",
    "pub fn permitsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {",
    "pub fn constSliceAt(comptime T: type, base: usize, len: usize) []const T {",
    "pub fn constPointerAt(comptime T: type, addr: usize) *const T {",
    "pub fn writeValueAt(comptime T: type, addr: usize, value: T) void {",
    'test "phase3 narrow unsafe scope bytes stay explicit" {',
)

REQUIRED_ABI_TEST_SNIPPETS = (
    'const abi = @import("abi_bindings");',
    'const export_shim = @import("export_shim");',
    'test "phase3 abi keeps starter header and status layouts explicit" {',
    'try std.testing.expectEqual(@as(usize, 4), @sizeOf(abi.InteropPolicy));',
    'test "phase3 abi keeps exported status helpers and compatibility rules reviewable" {',
    'test "phase3 abi keeps exported constants and family markers present" {',
)

REQUIRED_ABI_DUMP_SNIPPETS = (
    'try writer.writeAll(",\\\"constants\\\":{");',
    '\\"panic_abort\\\":{d},\\"panic_bug\\\":{d},\\"panic_warn\\\":{d}',
    'try writeStruct(writer, "interop_policy", abi.InteropPolicy);',
    'try writeStruct(',
    '"chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary",',
)

REQUIRED_ABI_EXPECTED_SNIPPETS = (
    '"panic_abort": 0',
    '"allocator_caller_provided": 0',
    '"unsafe_scope_raw_pointer_bridge": 2',
    '"interop_policy": {',
    '"chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary": {',
)


def git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    header = f"blob {len(payload)}\0".encode("utf-8")
    return hashlib.sha1(header + payload).hexdigest()


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


def require_snippets(issues: list[str], text: str, prefix: str, snippets: tuple[str, ...]) -> None:
    for snippet in snippets:
        if snippet not in text:
            issues.append(f"missing_{prefix}_snippet:{snippet}")


def validate(root: Path) -> list[str]:
    required_paths = {
        SURVEY_REL,
        MAKEFILE_REL,
        LAYOUT_ASSERT_REL,
        PANIC_POLICY_REL,
        ALLOCATOR_POLICY_REL,
        MMIO_REL,
        UNSAFE_NARROW_REL,
        POLICY_BYTE_GUARD_REL,
        ABI_TEST_REL,
        ABI_DUMP_REL,
        ABI_EXPECTED_REL,
        ABI_MANIFEST_REL,
        ABI_SLICE_DOC_REL,
    }
    missing = [rel for rel in sorted(required_paths) if not (root / rel).exists()]
    if missing:
        return [f"missing_file:{rel}" for rel in missing]

    issues: list[str] = []
    survey = (root / SURVEY_REL).read_text(encoding="utf-8")
    makefile = (root / MAKEFILE_REL).read_text(encoding="utf-8")
    layout_assert = (root / LAYOUT_ASSERT_REL).read_text(encoding="utf-8")
    panic_policy = (root / PANIC_POLICY_REL).read_text(encoding="utf-8")
    allocator_policy = (root / ALLOCATOR_POLICY_REL).read_text(encoding="utf-8")
    mmio = (root / MMIO_REL).read_text(encoding="utf-8")
    unsafe = (root / UNSAFE_NARROW_REL).read_text(encoding="utf-8")
    abi_test = (root / ABI_TEST_REL).read_text(encoding="utf-8")
    abi_dump = (root / ABI_DUMP_REL).read_text(encoding="utf-8")
    abi_expected = (root / ABI_EXPECTED_REL).read_text(encoding="utf-8")

    for marker, rel in PATH_MARKERS.items():
        require_exact_line_count(issues, survey, "marker", f"{marker}={rel}", normalized=True)

    for marker in STATIC_MARKERS:
        require_exact_line_count(issues, survey, "marker", marker, normalized=True)

    survey_lines = normalized_marker_lines(survey)
    for marker, rel in BLOB_MARKERS.items():
        prefix = f"{marker}="
        matches = [line for line in survey_lines if line.startswith(prefix)]
        if not matches:
            issues.append(f"missing_blob_marker:{marker}=<sha>")
            continue
        if len(matches) != 1:
            issues.append(f"duplicate_blob_marker:{marker}=<sha>:{len(matches)}")
            continue
        actual = matches[0].split(prefix, 1)[1]
        expected = git_blob_sha(root / rel)
        if actual != expected:
            issues.append(f"stale_blob_marker:{marker}:{actual}!={expected}")

    for line in MAKEFILE_REQUIRED_LINES:
        require_exact_line_count(issues, makefile, "makefile_line", line)

    checker = subprocess.run(
        [sys.executable, root / POLICY_BYTE_GUARD_REL],
        capture_output=True,
        text=True,
        check=False,
    )
    if checker.returncode != 0:
        issues.append(f"policy_byte_guard_exit:{checker.returncode}")
        for line in checker.stdout.splitlines():
            issues.append(f"policy_byte_guard_stdout:{line}")
        for line in checker.stderr.splitlines():
            issues.append(f"policy_byte_guard_stderr:{line}")

    require_snippets(issues, survey, "survey", REQUIRED_SURVEY_SNIPPETS)
    require_snippets(issues, layout_assert, "layout_assert", REQUIRED_LAYOUT_ASSERT_SNIPPETS)
    require_snippets(issues, panic_policy, "panic_policy", REQUIRED_PANIC_POLICY_SNIPPETS)
    require_snippets(issues, allocator_policy, "allocator_policy", REQUIRED_ALLOCATOR_POLICY_SNIPPETS)
    require_snippets(issues, mmio, "mmio", REQUIRED_MMIO_SNIPPETS)
    require_snippets(issues, unsafe, "unsafe", REQUIRED_UNSAFE_SNIPPETS)
    require_snippets(issues, abi_test, "abi_test", REQUIRED_ABI_TEST_SNIPPETS)
    require_snippets(issues, abi_dump, "abi_dump", REQUIRED_ABI_DUMP_SNIPPETS)
    require_snippets(issues, abi_expected, "abi_expected", REQUIRED_ABI_EXPECTED_SNIPPETS)
    return issues


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def build_valid_workspace(root: Path) -> None:
    minimal_files = {
        LAYOUT_ASSERT_REL: "\n".join(REQUIRED_LAYOUT_ASSERT_SNIPPETS) + "\n",
        PANIC_POLICY_REL: "\n".join(REQUIRED_PANIC_POLICY_SNIPPETS) + "\n",
        ALLOCATOR_POLICY_REL: "\n".join(REQUIRED_ALLOCATOR_POLICY_SNIPPETS) + "\n",
        MMIO_REL: "\n".join(REQUIRED_MMIO_SNIPPETS) + "\n",
        UNSAFE_NARROW_REL: "\n".join(REQUIRED_UNSAFE_SNIPPETS) + "\n",
        POLICY_BYTE_GUARD_REL: "#!/usr/bin/env python3\nprint(\"PHASE3_POLICY_BYTE_GUARDS=pass\")\n",
        ABI_TEST_REL: "\n".join(REQUIRED_ABI_TEST_SNIPPETS) + "\n",
        ABI_DUMP_REL: "\n".join(REQUIRED_ABI_DUMP_SNIPPETS) + "\n",
        ABI_EXPECTED_REL: "\n".join(REQUIRED_ABI_EXPECTED_SNIPPETS) + "\n",
        ABI_MANIFEST_REL: '{"phase":"Phase 3"}\n',
        ABI_SLICE_DOC_REL: "# Phase 3 ABI Slice\n",
    }
    for rel, content in minimal_files.items():
        write_file(root / rel, content)

    survey_lines = ["# Phase 3 Policy and Unsafe Boundary Survey", ""]
    for marker, rel in PATH_MARKERS.items():
        survey_lines.append(f"- `{marker}={rel}`")
    for marker in STATIC_MARKERS:
        survey_lines.append(f"- `{marker}`")
    for snippet in REQUIRED_SURVEY_SNIPPETS:
        survey_lines.append(f"- {snippet}")
    for marker, rel in BLOB_MARKERS.items():
        survey_lines.append(f"- `{marker}={git_blob_sha(root / rel)}`")
    write_file(root / SURVEY_REL, "\n".join(survey_lines) + "\n")

    write_file(root / MAKEFILE_REL, "\n".join(MAKEFILE_REQUIRED_LINES) + "\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_policy_unsafe_validator_") as tmp_dir:
        root = Path(tmp_dir)
        build_valid_workspace(root)
        assert validate(root) == []
        case_count += 1

        stale_note = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            "PHASE3_PANIC_POLICY_BLOB_SHA=",
            "PHASE3_PANIC_POLICY_BLOB_SHA=stale-",
            1,
        )
        write_file(root / SURVEY_REL, stale_note)
        issues = validate(root)
        expected = git_blob_sha(root / PANIC_POLICY_REL)
        assert f"stale_blob_marker:PHASE3_PANIC_POLICY_BLOB_SHA:stale-{expected}!={expected}" in issues
        case_count += 1

        build_valid_workspace(root)
        broken = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            "- `PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig`\n",
            "",
            1,
        )
        write_file(root / SURVEY_REL, broken)
        issues = validate(root)
        assert "missing_marker:PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig" in issues
        case_count += 1

        build_valid_workspace(root)
        broken = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            REQUIRED_SURVEY_SNIPPETS[-1] + "\n",
            "",
            1,
        )
        write_file(root / SURVEY_REL, broken)
        issues = validate(root)
        assert f"missing_survey_snippet:{REQUIRED_SURVEY_SNIPPETS[-1]}" in issues
        case_count += 1

        build_valid_workspace(root)
        write_file(root / LAYOUT_ASSERT_REL, "\n".join(REQUIRED_LAYOUT_ASSERT_SNIPPETS[:-1]) + "\n")
        issues = validate(root)
        assert f"missing_layout_assert_snippet:{REQUIRED_LAYOUT_ASSERT_SNIPPETS[-1]}" in issues
        case_count += 1

        build_valid_workspace(root)
        write_file(root / ABI_TEST_REL, "\n".join(REQUIRED_ABI_TEST_SNIPPETS[:-1]) + "\n")
        issues = validate(root)
        assert f"missing_abi_test_snippet:{REQUIRED_ABI_TEST_SNIPPETS[-1]}" in issues
        case_count += 1

        build_valid_workspace(root)
        write_file(root / ABI_DUMP_REL, "\n".join(REQUIRED_ABI_DUMP_SNIPPETS[:-1]) + "\n")
        issues = validate(root)
        assert f"missing_abi_dump_snippet:{REQUIRED_ABI_DUMP_SNIPPETS[-1]}" in issues
        case_count += 1

        build_valid_workspace(root)
        write_file(root / MAKEFILE_REL, "\n".join(MAKEFILE_REQUIRED_LINES[:-1]) + "\n")
        issues = validate(root)
        assert f"missing_makefile_line:{MAKEFILE_REQUIRED_LINES[-1]}" in issues
        case_count += 1

        build_valid_workspace(root)
        write_file(
            root / POLICY_BYTE_GUARD_REL,
            "#!/usr/bin/env python3\nimport sys\nprint(\"PHASE3_POLICY_BYTE_GUARDS=fail\")\nsys.exit(1)\n",
        )
        issues = validate(root)
        assert "policy_byte_guard_exit:1" in issues
        case_count += 1

    print("PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=pass")
    print(f"PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 3 policy and unsafe survey note against the current shared ABI packet."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated validator coverage in a temporary workspace.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(ROOT)
    if issues:
        print("PHASE3_POLICY_UNSAFE_SURVEY_VALIDATION=fail")
        print("PHASE3_POLICY_UNSAFE_SURVEY_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE3_POLICY_UNSAFE_SURVEY_ISSUES_END")
        return 1

    print("PHASE3_POLICY_UNSAFE_SURVEY_VALIDATION=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
