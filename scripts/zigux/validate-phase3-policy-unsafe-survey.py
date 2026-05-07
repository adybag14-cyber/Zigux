#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SURVEY_REL = "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md"
MAKEFILE_REL = "zigux/Makefile"
LAYOUT_ASSERT_REL = "zigux/helpers/layout_assert.zig"
PANIC_POLICY_REL = "zigux/helpers/panic_policy.zig"
ALLOCATOR_POLICY_REL = "zigux/helpers/allocator_policy.zig"
MMIO_REL = "zigux/helpers/mmio.zig"
UNSAFE_NARROW_REL = "zigux/unsafe/narrow.zig"
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
    "PHASE3_LAYOUT_ASSERT_SCOPE=canonical-bindings-plus-mmio-and-rbtree-views",
    "PHASE3_PANIC_POLICY=explicit-modes-only",
    "PHASE3_ALLOCATOR_POLICY=explicit-modes-only",
    "PHASE3_UNSAFE_SCOPE=narrow-mmio-and-raw-pointer-bridge",
    "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py --slug abi",
    "PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug abi",
    "PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig",
    "PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig",
    "PHASE3_BOUNDARY_GAP=no-dedicated-policy-unsafe-subslice-beyond-the-shared-abi-packet",
    "PHASE3_NEXT_BOUNDED_STEP=keep-this-note-aligned-with-the-shared-abi-packet-until-a-real-policy-or-unsafe-helper-expansion-lands",
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
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-policy-unsafe-survey.py --self-test",
)

REQUIRED_SURVEY_SNIPPETS = (
    "`zigux/helpers/layout_assert.zig` keeps compile-time size, alignment, field-type, and offset checks for the canonical ABI root while also covering the shipped `MmioRange` and `RbtreeRootView` layouts that now sit inside the same bounded packet.",
    "`zigux/helpers/panic_policy.zig` now keeps panic action explicit both through the typed enum path and through `modeFromInteropPolicyBytes`, `actionForInteropPolicyBytes`, and `canReturnInteropPolicyBytes` so unknown panic modes and nonzero reserved bytes fail closed before raw-byte callers infer behavior elsewhere in the packet.",
    "`zigux/helpers/allocator_policy.zig` now keeps caller-provided ownership and global-fallback policy explicit both through the typed predicates and through `modeFromInteropPolicyBytes`, `requiresExplicitCallerPolicyBytes`, and `permitsGlobalFallbackPolicyBytes` so unknown allocator modes and nonzero reserved bytes fail closed before raw-byte callers infer behavior elsewhere in the packet.",
    "`zigux/unsafe/narrow.zig` still keeps the raw-pointer bridge deliberately small, but it now also decodes `InteropPolicy` unsafe-scope bytes explicitly through `scopeFromInteropPolicyBytes`, `recognizesInteropPolicyBytes`, `permitsVolatileMmioPolicyBytes`, and `permitsRawPointerBridgePolicyBytes` so unknown scopes and reserved-byte drift do not have to be inferred elsewhere in the packet.",
    "`zigux/helpers/mmio.zig` still consumes that same narrow layer for `range()`, `read8()`, `write8()`, `read16()`, `write16()`, `read32()`, and `write32()` rather than widening into a larger policy substrate.",
)

REQUIRED_LAYOUT_ASSERT_SNIPPETS = (
    "fn assertInteropPolicyModeValues() void {",
    "assertInteropPolicyByteValue(\"panic_mode.abort\", @intFromEnum(abi.PanicMode.abort), 0);",
    "assertInteropPolicyByteValue(\"allocator_mode.caller_provided\", @intFromEnum(abi.AllocatorMode.caller_provided), 0);",
    "assertInteropPolicyByteValue(\"unsafe_scope.raw_pointer_bridge\", @intFromEnum(abi.UnsafeScope.raw_pointer_bridge), 2);",
    "pub fn assertMmioRangeLayout() void {",
    "pub fn assertRbtreeRootViewLayout() void {",
    'test "phase3 layout assertions cover canonical bindings" {',
)

REQUIRED_PANIC_POLICY_SNIPPETS = (
    "pub fn modeFromInteropPolicyBytes(mode: u8, reserved: u8) ?abi.PanicMode {",
    "if (reserved != 0) return null;",
    "pub fn actionForInteropPolicyBytes(mode: u8, reserved: u8) ?Action {",
    "return actionFor(modeFromInteropPolicyBytes(mode, reserved) orelse return null);",
    "pub fn canReturnInteropPolicyBytes(mode: u8, reserved: u8) bool {",
    "return actionForInteropPolicyBytes(mode, reserved) == .warn_and_return;",
    "try std.testing.expectEqual(@as(?abi.PanicMode, null), modeFromInteropPolicyBytes(2, 1));",
    "try std.testing.expectEqual(@as(?Action, null), actionForInteropPolicyBytes(2, 1));",
    "try std.testing.expect(!canReturnInteropPolicyBytes(2, 1));",
)

REQUIRED_ALLOCATOR_POLICY_SNIPPETS = (
    "pub fn modeFromInteropPolicyBytes(mode: u8, reserved: u8) ?abi.AllocatorMode {",
    "if (reserved != 0) return null;",
    "pub fn requiresExplicitCallerPolicyBytes(mode: u8, reserved: u8) bool {",
    "return modeFromInteropPolicyBytes(mode, reserved) == .caller_provided;",
    "pub fn permitsGlobalFallbackPolicyBytes(mode: u8, reserved: u8) bool {",
    "return switch (modeFromInteropPolicyBytes(mode, reserved) orelse return false) {",
    "try std.testing.expectEqual(@as(?abi.AllocatorMode, null), modeFromInteropPolicyBytes(2, 1));",
    "try std.testing.expect(!requiresExplicitCallerPolicyBytes(2, 1));",
    "try std.testing.expect(!permitsGlobalFallbackPolicyBytes(2, 1));",
)

REQUIRED_UNSAFE_SNIPPETS = (
    "pub fn addressOf(ptr: anytype) usize {",
    "pub fn byteOffset(base: usize, offset: usize) usize {",
    'return std.math.add(usize, base, offset) catch @panic("phase3 narrow unsafe byte offset overflow");',
    "pub fn pointerAt(comptime T: type, base: usize, offset: usize) *align(1) volatile T {",
    "pub fn scopeFromInteropPolicyBytes(unsafe_scope: u8, reserved: u8) ?UnsafeScopeTag {",
    "if (reserved != 0) return null;",
    "try std.testing.expect(!recognizesInteropPolicyBytes(1, 1));",
    "try std.testing.expect(!permitsRawPointerBridgePolicyBytes(2, 1));",
)

REQUIRED_ABI_TEST_SNIPPETS = (
    'const layout_assert = @import("layout_assert");',
    'const panic_policy = @import("panic_policy");',
    'const allocator_policy = @import("allocator_policy");',
    'const mmio = @import("mmio_helpers");',
    'const narrow = @import("narrow_unsafe");',
)

REQUIRED_ABI_DUMP_SNIPPETS = (
    'try writer.writeAll(",\\\"panic_abort\\\":");',
    'try writer.writeAll(",\\\"allocator_caller_provided\\\":");',
    'try writer.writeAll(",\\\"unsafe_scope_raw_pointer_bridge\\\":");',
    'try writeLayoutPrefix(writer, "zigux_mmio_range", @sizeOf(abi.MmioRange), @alignOf(abi.MmioRange));',
    'try writeLayoutPrefix(writer, "zigux_interop_policy", @sizeOf(abi.InteropPolicy), @alignOf(abi.InteropPolicy));',
)

REQUIRED_ABI_EXPECTED_SNIPPETS = (
    '"panic_abort":0',
    '"allocator_caller_provided":0',
    '"unsafe_scope_raw_pointer_bridge":2',
    '"zigux_mmio_range":{"size":16,"align":8,"offsets":{"base_addr":0,"length":8,"stride":12}}',
    '"zigux_interop_policy":{"size":4,"align":1,"offsets":{"panic_mode":0,"allocator_mode":1,"unsafe_scope":2,"reserved":3}}',
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

    require_snippets(issues, survey, "survey", REQUIRED_SURVEY_SNIPPETS)
    require_snippets(issues, layout_assert, "layout_assert", REQUIRED_LAYOUT_ASSERT_SNIPPETS)
    require_snippets(issues, panic_policy, "panic_policy", REQUIRED_PANIC_POLICY_SNIPPETS)
    require_snippets(issues, allocator_policy, "allocator_policy", REQUIRED_ALLOCATOR_POLICY_SNIPPETS)
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
        MMIO_REL: "pub fn range() void {}\npub fn write32() void {}\n",
        UNSAFE_NARROW_REL: "\n".join(REQUIRED_UNSAFE_SNIPPETS) + "\n",
        ABI_TEST_REL: "\n".join(REQUIRED_ABI_TEST_SNIPPETS) + "\n",
        ABI_DUMP_REL: "\n".join(REQUIRED_ABI_DUMP_SNIPPETS) + "\n",
        ABI_EXPECTED_REL: "\n".join(REQUIRED_ABI_EXPECTED_SNIPPETS) + "\n",
        ABI_MANIFEST_REL: '{"phase":"Phase 3"}\n',
        ABI_SLICE_DOC_REL: "# Phase 3 ABI Substrate Slice\n",
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

    write_file(root / MAKEFILE_REL, "phase3-validate:\n" + "\n".join(MAKEFILE_REQUIRED_LINES) + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_policy_unsafe_validator_") as tmp_dir:
        root = Path(tmp_dir)
        build_valid_workspace(root)
        assert validate(root) == []

        stale_note = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            "PHASE3_PANIC_POLICY_BLOB_SHA=",
            "PHASE3_PANIC_POLICY_BLOB_SHA=stale-",
            1,
        )
        write_file(root / SURVEY_REL, stale_note)
        issues = validate(root)
        expected = git_blob_sha(root / PANIC_POLICY_REL)
        assert f"stale_blob_marker:PHASE3_PANIC_POLICY_BLOB_SHA:stale-{expected}!={expected}" in issues

        build_valid_workspace(root)
        missing_boundary_gap = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            "- `PHASE3_BOUNDARY_GAP=no-dedicated-policy-unsafe-subslice-beyond-the-shared-abi-packet`\n",
            "",
            1,
        )
        write_file(root / SURVEY_REL, missing_boundary_gap)
        issues = validate(root)
        assert "missing_marker:PHASE3_BOUNDARY_GAP=no-dedicated-policy-unsafe-subslice-beyond-the-shared-abi-packet" in issues

        build_valid_workspace(root)
        missing_dump_gate = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            "- `PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig`\n",
            "",
            1,
        )
        write_file(root / SURVEY_REL, missing_dump_gate)
        issues = validate(root)
        assert "missing_marker:PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig" in issues

        build_valid_workspace(root)
        missing_panic_survey_snippet = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            REQUIRED_SURVEY_SNIPPETS[1] + "\n",
            "",
            1,
        )
        write_file(root / SURVEY_REL, missing_panic_survey_snippet)
        issues = validate(root)
        assert f"missing_survey_snippet:{REQUIRED_SURVEY_SNIPPETS[1]}" in issues

        build_valid_workspace(root)
        missing_allocator_survey_snippet = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            REQUIRED_SURVEY_SNIPPETS[2] + "\n",
            "",
            1,
        )
        write_file(root / SURVEY_REL, missing_allocator_survey_snippet)
        issues = validate(root)
        assert f"missing_survey_snippet:{REQUIRED_SURVEY_SNIPPETS[2]}" in issues

        build_valid_workspace(root)
        broken_layout = (root / LAYOUT_ASSERT_REL).read_text(encoding="utf-8").replace(
            REQUIRED_LAYOUT_ASSERT_SNIPPETS[5] + "\n",
            "",
            1,
        )
        write_file(root / LAYOUT_ASSERT_REL, broken_layout)
        issues = validate(root)
        assert f"missing_layout_assert_snippet:{REQUIRED_LAYOUT_ASSERT_SNIPPETS[5]}" in issues

        build_valid_workspace(root)
        broken_panic = (root / PANIC_POLICY_REL).read_text(encoding="utf-8").replace(
            REQUIRED_PANIC_POLICY_SNIPPETS[8] + "\n",
            "",
            1,
        )
        write_file(root / PANIC_POLICY_REL, broken_panic)
        issues = validate(root)
        assert f"missing_panic_policy_snippet:{REQUIRED_PANIC_POLICY_SNIPPETS[8]}" in issues

        build_valid_workspace(root)
        broken_allocator = (root / ALLOCATOR_POLICY_REL).read_text(encoding="utf-8").replace(
            REQUIRED_ALLOCATOR_POLICY_SNIPPETS[8] + "\n",
            "",
            1,
        )
        write_file(root / ALLOCATOR_POLICY_REL, broken_allocator)
        issues = validate(root)
        assert f"missing_allocator_policy_snippet:{REQUIRED_ALLOCATOR_POLICY_SNIPPETS[8]}" in issues

        build_valid_workspace(root)
        broken_unsafe = (root / UNSAFE_NARROW_REL).read_text(encoding="utf-8").replace(
            REQUIRED_UNSAFE_SNIPPETS[3] + "\n",
            "",
            1,
        )
        write_file(root / UNSAFE_NARROW_REL, broken_unsafe)
        issues = validate(root)
        assert f"missing_unsafe_snippet:{REQUIRED_UNSAFE_SNIPPETS[3]}" in issues

        build_valid_workspace(root)
        broken_dump = (root / ABI_DUMP_REL).read_text(encoding="utf-8").replace(
            REQUIRED_ABI_DUMP_SNIPPETS[4] + "\n",
            "",
            1,
        )
        write_file(root / ABI_DUMP_REL, broken_dump)
        issues = validate(root)
        assert f"missing_abi_dump_snippet:{REQUIRED_ABI_DUMP_SNIPPETS[4]}" in issues

        build_valid_workspace(root)
        broken_makefile = (root / MAKEFILE_REL).read_text(encoding="utf-8").replace(
            MAKEFILE_REQUIRED_LINES[1] + "\n",
            "",
            1,
        )
        write_file(root / MAKEFILE_REL, broken_makefile)
        issues = validate(root)
        assert f"missing_makefile_line:{MAKEFILE_REQUIRED_LINES[1]}" in issues

    print("PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=pass")
    print("PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST_CASE_COUNT=10")
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
