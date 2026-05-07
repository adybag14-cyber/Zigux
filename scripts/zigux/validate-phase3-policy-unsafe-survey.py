#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SURVEY_REL = "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md"
MAKEFILE_REL = "zigux/Makefile"
ALLOCATOR_POLICY_REL = "zigux/helpers/allocator_policy.zig"
PANIC_POLICY_REL = "zigux/helpers/panic_policy.zig"
UNSAFE_NARROW_REL = "zigux/unsafe/narrow.zig"
ABI_TEST_REL = "zigux/tests/phase3_abi.zig"
ABI_DUMP_REL = "zigux/tests/phase3_abi_dump.zig"
ABI_EXPECTED_REL = "zigux/tests/fixtures/phase3_abi/expected.json"

PATH_MARKERS = {
    "PHASE3_LAYOUT_ASSERT_PATH": "zigux/helpers/layout_assert.zig",
    "PHASE3_PANIC_POLICY_PATH": "zigux/helpers/panic_policy.zig",
    "PHASE3_ALLOCATOR_POLICY_PATH": "zigux/helpers/allocator_policy.zig",
    "PHASE3_MMIO_PATH": "zigux/helpers/mmio.zig",
    "PHASE3_UNSAFE_PATH": "zigux/unsafe/narrow.zig",
    "PHASE3_ABI_TEST_PATH": "zigux/tests/phase3_abi.zig",
    "PHASE3_ABI_DUMP_PATH": "zigux/tests/phase3_abi_dump.zig",
}

STATIC_MARKERS = (
    "PHASE3_LAYOUT_ASSERT_SCOPE=canonical-bindings-plus-mmio-and-rbtree-views",
    "PHASE3_PANIC_POLICY=explicit-modes-only",
    "PHASE3_ALLOCATOR_POLICY=explicit-modes-only",
    "PHASE3_UNSAFE_SCOPE=narrow-mmio-and-raw-pointer-bridge",
    "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py --slug abi",
    "PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug abi",
    "PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig",
    "PHASE3_BOUNDARY_GAP=no-dedicated-policy-unsafe-subslice-beyond-the-shared-abi-packet",
    "PHASE3_NEXT_BOUNDED_STEP=keep-this-note-aligned-with-the-shared-abi-packet-until-a-real-policy-or-unsafe-helper-expansion-lands",
)

BLOB_MARKERS = {
    "PHASE3_LAYOUT_ASSERT_BLOB_SHA": "zigux/helpers/layout_assert.zig",
    "PHASE3_PANIC_POLICY_BLOB_SHA": "zigux/helpers/panic_policy.zig",
    "PHASE3_ALLOCATOR_POLICY_BLOB_SHA": "zigux/helpers/allocator_policy.zig",
    "PHASE3_MMIO_BLOB_SHA": "zigux/helpers/mmio.zig",
    "PHASE3_UNSAFE_BLOB_SHA": "zigux/unsafe/narrow.zig",
    "PHASE3_ABI_TEST_BLOB_SHA": "zigux/tests/phase3_abi.zig",
    "PHASE3_ABI_DUMP_BLOB_SHA": "zigux/tests/phase3_abi_dump.zig",
    "PHASE3_ABI_MANIFEST_BLOB_SHA": "zigux/tests/fixtures/phase3_abi_manifest.json",
    "PHASE3_ABI_SLICE_DOC_BLOB_SHA": "Documentation/zigux/phase3-abi-slice.md",
}

MAKEFILE_REQUIRED_LINES = (
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-policy-unsafe-survey.py --self-test",
)

REQUIRED_SURVEY_SNIPPETS = (
    "`zigux/helpers/allocator_policy.zig` now keeps caller-provided ownership and global-fallback policy explicit both through the typed predicates and through `modeFromInteropPolicyBytes`, `requiresExplicitCallerPolicyBytes`, and `permitsGlobalFallbackPolicyBytes` so unknown allocator modes and nonzero reserved bytes fail closed before raw-byte callers infer behavior elsewhere in the packet.",
    "`zigux/unsafe/narrow.zig` still keeps the raw-pointer bridge deliberately small, but it now also decodes `InteropPolicy` unsafe-scope bytes explicitly through `scopeFromInteropPolicyBytes`, `recognizesInteropPolicyBytes`, `permitsVolatileMmioPolicyBytes`, and `permitsRawPointerBridgePolicyBytes` so unknown scopes and reserved-byte drift do not have to be inferred elsewhere in the packet.",
    "`zigux/helpers/mmio.zig` still consumes that same narrow layer for `range()`, `read8()`, `write8()`, `read16()`, `write16()`, `read32()`, and `write32()` rather than widening into a larger policy substrate.",
)

REQUIRED_ALLOCATOR_POLICY_SNIPPETS = (
    "pub fn requiresExplicitCaller(mode: abi.AllocatorMode) bool {",
    "return mode == .caller_provided;",
    "pub fn permitsGlobalFallback(mode: abi.AllocatorMode) bool {",
    ".caller_provided => false,",
    ".kernel_heap, .arena => true,",
    'test "phase3 allocator policy stays explicit" {',
    "try std.testing.expect(requiresExplicitCaller(.caller_provided));",
    "try std.testing.expect(!permitsGlobalFallback(.caller_provided));",
)

REQUIRED_PANIC_POLICY_SNIPPETS = (
    "pub const Action = enum {",
    "abort_now,",
    "bug_check,",
    "warn_and_return,",
    "pub fn actionFor(mode: abi.PanicMode) Action {",
    ".abort => .abort_now,",
    ".bug => .bug_check,",
    ".warn => .warn_and_return,",
    "pub fn canReturn(mode: abi.PanicMode) bool {",
    "return actionFor(mode) == .warn_and_return;",
    'test "phase3 panic policy stays explicit" {',
    "try std.testing.expect(canReturn(.warn));",
)

REQUIRED_NARROW_UNSAFE_SNIPPETS = (
    "pub fn addressOf(ptr: anytype) usize {",
    "pub fn byteOffset(base: usize, offset: usize) usize {",
    'return std.math.add(usize, base, offset) catch @panic("phase3 narrow unsafe byte offset overflow");',
    "pub fn pointerAt(comptime T: type, base: usize, offset: usize) *align(1) volatile T {",
    "pub fn constSliceAt(comptime T: type, base: usize, len: usize) []const T {",
    "pub fn constPointerAt(comptime T: type, addr: usize) *const T {",
    "pub fn writeValueAt(comptime T: type, addr: usize, value: T) void {",
    "pub fn scopeFromInteropPolicyBytes(unsafe_scope: u8, reserved: u8) ?UnsafeScopeTag {",
    "pub fn recognizesInteropPolicyBytes(unsafe_scope: u8, reserved: u8) bool {",
    "pub fn permitsVolatileMmioPolicyBytes(unsafe_scope: u8, reserved: u8) bool {",
    "pub fn permitsRawPointerBridgePolicyBytes(unsafe_scope: u8, reserved: u8) bool {",
    'test "phase3 narrow unsafe wrappers stay bounded" {',
    'test "phase3 narrow unsafe scope bytes stay explicit" {',
    "try std.testing.expectEqual(@as(usize, 12), byteOffset(9, 3));",
    "const ptr = pointerAt(u32, base, 0);",
    "const slice = constSliceAt(u32, base, 1);",
    "const const_ptr = constPointerAt(u32, base);",
    "writeValueAt(u32, base, 19);",
    "try std.testing.expectEqual(@as(?UnsafeScopeTag, .volatile_mmio), scopeFromInteropPolicyBytes(1, 0));",
    "try std.testing.expect(!recognizesInteropPolicyBytes(1, 1));",
    "try std.testing.expect(permitsVolatileMmioPolicyBytes(1, 0));",
    "try std.testing.expect(permitsRawPointerBridgePolicyBytes(2, 0));",
)

REQUIRED_ABI_TEST_SNIPPETS = (
    'const panic_policy = @import("panic_policy");',
    'const allocator_policy = @import("allocator_policy");',
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
    issues: list[str] = []
    survey_path = root / SURVEY_REL
    makefile_path = root / MAKEFILE_REL
    allocator_policy_path = root / ALLOCATOR_POLICY_REL
    panic_policy_path = root / PANIC_POLICY_REL
    narrow_unsafe_path = root / UNSAFE_NARROW_REL
    abi_test_path = root / ABI_TEST_REL
    abi_dump_path = root / ABI_DUMP_REL
    abi_expected_path = root / ABI_EXPECTED_REL

    try:
        survey = survey_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return [f"missing_survey:{SURVEY_REL}"]
    survey_lines = normalized_marker_lines(survey)

    for marker, rel in PATH_MARKERS.items():
        expected = f"{marker}={rel}"
        require_exact_line_count(issues, survey, "marker", expected, normalized=True)
        if not (root / rel).exists():
            issues.append(f"missing_file:{rel}")

    for marker in STATIC_MARKERS:
        require_exact_line_count(issues, survey, "marker", marker, normalized=True)

    require_snippets(issues, survey, "survey", REQUIRED_SURVEY_SNIPPETS)

    for marker, rel in BLOB_MARKERS.items():
        path = root / rel
        if not path.exists():
            issues.append(f"missing_file:{rel}")
            continue
        prefix = f"{marker}="
        matching_lines = [line for line in survey_lines if line.startswith(prefix)]
        if not matching_lines:
            issues.append(f"missing_blob_marker:{marker}=<sha>")
            continue
        if len(matching_lines) != 1:
            issues.append(f"duplicate_blob_marker:{marker}=<sha>:{len(matching_lines)}")
            continue
        actual = matching_lines[0].split(prefix, 1)[1]
        expected = git_blob_sha(path)
        if actual != expected:
            issues.append(f"stale_blob_marker:{marker}:{actual}!={expected}")

    try:
        allocator_policy = allocator_policy_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(f"missing_file:{ALLOCATOR_POLICY_REL}")
    else:
        require_snippets(issues, allocator_policy, "allocator_policy", REQUIRED_ALLOCATOR_POLICY_SNIPPETS)

    try:
        panic_policy = panic_policy_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(f"missing_file:{PANIC_POLICY_REL}")
    else:
        require_snippets(issues, panic_policy, "panic_policy", REQUIRED_PANIC_POLICY_SNIPPETS)

    try:
        narrow_unsafe = narrow_unsafe_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(f"missing_file:{UNSAFE_NARROW_REL}")
    else:
        require_snippets(issues, narrow_unsafe, "narrow_unsafe", REQUIRED_NARROW_UNSAFE_SNIPPETS)

    try:
        abi_test = abi_test_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(f"missing_file:{ABI_TEST_REL}")
    else:
        require_snippets(issues, abi_test, "abi_test", REQUIRED_ABI_TEST_SNIPPETS)

    try:
        abi_dump = abi_dump_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(f"missing_file:{ABI_DUMP_REL}")
    else:
        require_snippets(issues, abi_dump, "abi_dump", REQUIRED_ABI_DUMP_SNIPPETS)

    try:
        abi_expected = abi_expected_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(f"missing_file:{ABI_EXPECTED_REL}")
    else:
        require_snippets(issues, abi_expected, "abi_expected", REQUIRED_ABI_EXPECTED_SNIPPETS)

    try:
        makefile = makefile_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(f"missing_makefile:{MAKEFILE_REL}")
        return issues

    for line in MAKEFILE_REQUIRED_LINES:
        require_exact_line_count(issues, makefile, "makefile_line", line)

    return issues


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def build_valid_workspace(root: Path) -> None:
    content_by_rel = {
        "zigux/helpers/layout_assert.zig": "// layout\n",
        PANIC_POLICY_REL: "\n".join(
            [
                'const std = @import("std");',
                'const abi = @import("abi_bindings");',
                "",
                "pub const Action = enum {",
                "    abort_now,",
                "    bug_check,",
                "    warn_and_return,",
                "};",
                "",
                "pub fn actionFor(mode: abi.PanicMode) Action {",
                "    return switch (mode) {",
                "        .abort => .abort_now,",
                "        .bug => .bug_check,",
                "        .warn => .warn_and_return,",
                "    };",
                "}",
                "",
                "pub fn canReturn(mode: abi.PanicMode) bool {",
                "    return actionFor(mode) == .warn_and_return;",
                "}",
                "",
                'test "phase3 panic policy stays explicit" {',
                "    try std.testing.expect(!canReturn(.abort));",
                "    try std.testing.expect(!canReturn(.bug));",
                "    try std.testing.expect(canReturn(.warn));",
                "}",
                "",
            ]
        ),
        ALLOCATOR_POLICY_REL: "\n".join(REQUIRED_ALLOCATOR_POLICY_SNIPPETS) + "\n",
        "zigux/helpers/mmio.zig": "// mmio\n",
        UNSAFE_NARROW_REL: "\n".join(REQUIRED_NARROW_UNSAFE_SNIPPETS) + "\n",
        ABI_TEST_REL: "\n".join(REQUIRED_ABI_TEST_SNIPPETS) + "\n",
        ABI_DUMP_REL: "\n".join(REQUIRED_ABI_DUMP_SNIPPETS) + "\n",
        ABI_EXPECTED_REL: "\n".join(REQUIRED_ABI_EXPECTED_SNIPPETS) + "\n",
        "zigux/tests/fixtures/phase3_abi_manifest.json": "{\n  \"phase\": \"Phase 3\"\n}\n",
        "Documentation/zigux/phase3-abi-slice.md": "# abi\n",
    }
    for rel, body in content_by_rel.items():
        write_file(root / rel, body)

    survey_lines = [
        "# Phase 3 Policy and Unsafe Boundary Survey",
        "",
    ]
    for marker, rel in PATH_MARKERS.items():
        survey_lines.append(f"- `{marker}={rel}`")
    for marker in STATIC_MARKERS:
        survey_lines.append(f"- `{marker}`")
    survey_lines.extend(f"- {snippet}" for snippet in REQUIRED_SURVEY_SNIPPETS)
    for marker, rel in BLOB_MARKERS.items():
        survey_lines.append(f"- `{marker}={git_blob_sha(root / rel)}`")
    write_file(root / SURVEY_REL, "\n".join(survey_lines) + "\n")

    write_file(
        root / MAKEFILE_REL,
        "\n".join(
            [
                "phase3-validate:",
                MAKEFILE_REQUIRED_LINES[0],
                MAKEFILE_REQUIRED_LINES[1],
                "",
            ]
        ),
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_policy_unsafe_validator_") as tmp_dir:
        root = Path(tmp_dir)
        build_valid_workspace(root)
        assert validate(root) == []

        broken_note = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            "PHASE3_MMIO_BLOB_SHA=",
            "PHASE3_MMIO_BLOB_SHA=stale-",
            1,
        )
        write_file(root / SURVEY_REL, broken_note)
        issues = validate(root)
        expected_mmio_blob_sha = git_blob_sha(root / "zigux/helpers/mmio.zig")
        assert (
            f"stale_blob_marker:PHASE3_MMIO_BLOB_SHA:stale-{expected_mmio_blob_sha}!={expected_mmio_blob_sha}"
            in issues
        )

        build_valid_workspace(root)
        missing_layout_scope = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            "- `PHASE3_LAYOUT_ASSERT_SCOPE=canonical-bindings-plus-mmio-and-rbtree-views`\n",
            "",
            1,
        )
        write_file(root / SURVEY_REL, missing_layout_scope)
        issues = validate(root)
        assert (
            "missing_marker:PHASE3_LAYOUT_ASSERT_SCOPE=canonical-bindings-plus-mmio-and-rbtree-views"
            in issues
        )

        build_valid_workspace(root)
        missing_boundary_gap = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            "- `PHASE3_BOUNDARY_GAP=no-dedicated-policy-unsafe-subslice-beyond-the-shared-abi-packet`\n",
            "",
            1,
        )
        write_file(root / SURVEY_REL, missing_boundary_gap)
        issues = validate(root)
        assert (
            "missing_marker:PHASE3_BOUNDARY_GAP=no-dedicated-policy-unsafe-subslice-beyond-the-shared-abi-packet"
            in issues
        )

        build_valid_workspace(root)
        missing_allocator_surface = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            "- `zigux/helpers/allocator_policy.zig` now keeps caller-provided ownership and global-fallback policy explicit both through the typed predicates and through `modeFromInteropPolicyBytes`, `requiresExplicitCallerPolicyBytes`, and `permitsGlobalFallbackPolicyBytes` so unknown allocator modes and nonzero reserved bytes fail closed before raw-byte callers infer behavior elsewhere in the packet.\n",
            "",
            1,
        )
        write_file(root / SURVEY_REL, missing_allocator_surface)
        issues = validate(root)
        assert (
            "missing_survey_snippet:`zigux/helpers/allocator_policy.zig` now keeps caller-provided ownership and global-fallback policy explicit both through the typed predicates and through `modeFromInteropPolicyBytes`, `requiresExplicitCallerPolicyBytes`, and `permitsGlobalFallbackPolicyBytes` so unknown allocator modes and nonzero reserved bytes fail closed before raw-byte callers infer behavior elsewhere in the packet."
            in issues
        )

        build_valid_workspace(root)
        missing_unsafe_surface = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            "- `zigux/unsafe/narrow.zig` still keeps the raw-pointer bridge deliberately small, but it now also decodes `InteropPolicy` unsafe-scope bytes explicitly through `scopeFromInteropPolicyBytes`, `recognizesInteropPolicyBytes`, `permitsVolatileMmioPolicyBytes`, and `permitsRawPointerBridgePolicyBytes` so unknown scopes and reserved-byte drift do not have to be inferred elsewhere in the packet.\n",
            "",
            1,
        )
        write_file(root / SURVEY_REL, missing_unsafe_surface)
        issues = validate(root)
        assert (
            "missing_survey_snippet:`zigux/unsafe/narrow.zig` still keeps the raw-pointer bridge deliberately small, but it now also decodes `InteropPolicy` unsafe-scope bytes explicitly through `scopeFromInteropPolicyBytes`, `recognizesInteropPolicyBytes`, `permitsVolatileMmioPolicyBytes`, and `permitsRawPointerBridgePolicyBytes` so unknown scopes and reserved-byte drift do not have to be inferred elsewhere in the packet."
            in issues
        )

        build_valid_workspace(root)
        missing_mmio_surface = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            "- `zigux/helpers/mmio.zig` still consumes that same narrow layer for `range()`, `read8()`, `write8()`, `read16()`, `write16()`, `read32()`, and `write32()` rather than widening into a larger policy substrate.\n",
            "",
            1,
        )
        write_file(root / SURVEY_REL, missing_mmio_surface)
        issues = validate(root)
        assert (
            "missing_survey_snippet:`zigux/helpers/mmio.zig` still consumes that same narrow layer for `range()`, `read8()`, `write8()`, `read16()`, `write16()`, `read32()`, and `write32()` rather than widening into a larger policy substrate."
            in issues
        )

        build_valid_workspace(root)
        duplicate_path = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            "- `PHASE3_MMIO_PATH=zigux/helpers/mmio.zig`\n",
            "- `PHASE3_MMIO_PATH=zigux/helpers/mmio.zig`\n- `PHASE3_MMIO_PATH=zigux/helpers/mmio.zig`\n",
            1,
        )
        write_file(root / SURVEY_REL, duplicate_path)
        issues = validate(root)
        assert "duplicate_marker:PHASE3_MMIO_PATH=zigux/helpers/mmio.zig:2" in issues

        build_valid_workspace(root)
        duplicate_boundary_gap = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            "- `PHASE3_BOUNDARY_GAP=no-dedicated-policy-unsafe-subslice-beyond-the-shared-abi-packet`\n",
            "- `PHASE3_BOUNDARY_GAP=no-dedicated-policy-unsafe-subslice-beyond-the-shared-abi-packet`\n- `PHASE3_BOUNDARY_GAP=no-dedicated-policy-unsafe-subslice-beyond-the-shared-abi-packet`\n",
            1,
        )
        write_file(root / SURVEY_REL, duplicate_boundary_gap)
        issues = validate(root)
        assert (
            "duplicate_marker:PHASE3_BOUNDARY_GAP=no-dedicated-policy-unsafe-subslice-beyond-the-shared-abi-packet:2"
            in issues
        )

        build_valid_workspace(root)
        missing_next_step = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            "- `PHASE3_NEXT_BOUNDED_STEP=keep-this-note-aligned-with-the-shared-abi-packet-until-a-real-policy-or-unsafe-helper-expansion-lands`\n",
            "",
            1,
        )
        write_file(root / SURVEY_REL, missing_next_step)
        issues = validate(root)
        assert (
            "missing_marker:PHASE3_NEXT_BOUNDED_STEP=keep-this-note-aligned-with-the-shared-abi-packet-until-a-real-policy-or-unsafe-helper-expansion-lands"
            in issues
        )

        build_valid_workspace(root)
        broken_allocator_policy = (root / ALLOCATOR_POLICY_REL).read_text(encoding="utf-8").replace(
            "try std.testing.expect(requiresExplicitCaller(.caller_provided));\n",
            "",
            1,
        )
        write_file(root / ALLOCATOR_POLICY_REL, broken_allocator_policy)
        issues = validate(root)
        assert (
            "missing_allocator_policy_snippet:try std.testing.expect(requiresExplicitCaller(.caller_provided));"
            in issues
        )

        build_valid_workspace(root)
        broken_panic_policy = (root / PANIC_POLICY_REL).read_text(encoding="utf-8").replace(
            "try std.testing.expect(canReturn(.warn));\n",
            "",
            1,
        )
        write_file(root / PANIC_POLICY_REL, broken_panic_policy)
        issues = validate(root)
        assert (
            "missing_panic_policy_snippet:try std.testing.expect(canReturn(.warn));"
            in issues
        )

        build_valid_workspace(root)
        broken_narrow_unsafe = (root / UNSAFE_NARROW_REL).read_text(encoding="utf-8").replace(
            "try std.testing.expect(permitsRawPointerBridgePolicyBytes(2, 0));\n",
            "",
            1,
        )
        write_file(root / UNSAFE_NARROW_REL, broken_narrow_unsafe)
        issues = validate(root)
        assert (
            "missing_narrow_unsafe_snippet:try std.testing.expect(permitsRawPointerBridgePolicyBytes(2, 0));"
            in issues
        )

        build_valid_workspace(root)
        broken_abi_test = (root / ABI_TEST_REL).read_text(encoding="utf-8").replace(
            'const narrow = @import("narrow_unsafe");\n',
            "",
            1,
        )
        write_file(root / ABI_TEST_REL, broken_abi_test)
        issues = validate(root)
        assert (
            'missing_abi_test_snippet:const narrow = @import("narrow_unsafe");'
            in issues
        )

        build_valid_workspace(root)
        broken_makefile = (root / MAKEFILE_REL).read_text(encoding="utf-8").replace(
            MAKEFILE_REQUIRED_LINES[1] + "\n",
            "",
            1,
        )
        write_file(root / MAKEFILE_REL, broken_makefile)
        issues = validate(root)
        assert (
            "missing_makefile_line:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-policy-unsafe-survey.py --self-test"
            in issues
        )

        build_valid_workspace(root)
        manifest_blob_sha = git_blob_sha(root / "zigux/tests/fixtures/phase3_abi_manifest.json")
        duplicate_blob_marker = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            f"- `PHASE3_ABI_MANIFEST_BLOB_SHA={manifest_blob_sha}`\n",
            f"- `PHASE3_ABI_MANIFEST_BLOB_SHA={manifest_blob_sha}`\n- `PHASE3_ABI_MANIFEST_BLOB_SHA={manifest_blob_sha}`\n",
            1,
        )
        write_file(root / SURVEY_REL, duplicate_blob_marker)
        issues = validate(root)
        assert "duplicate_blob_marker:PHASE3_ABI_MANIFEST_BLOB_SHA=<sha>:2" in issues

        build_valid_workspace(root)
        duplicate_makefile_line = (root / MAKEFILE_REL).read_text(encoding="utf-8").replace(
            MAKEFILE_REQUIRED_LINES[0] + "\n",
            MAKEFILE_REQUIRED_LINES[0] + "\n" + MAKEFILE_REQUIRED_LINES[0] + "\n",
            1,
        )
        write_file(root / MAKEFILE_REL, duplicate_makefile_line)
        issues = validate(root)
        assert (
            "duplicate_makefile_line:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-policy-unsafe-survey.py:2"
            in issues
        )

        build_valid_workspace(root)
        broken_abi_dump = (root / ABI_DUMP_REL).read_text(encoding="utf-8").replace(
            'try writeLayoutPrefix(writer, "zigux_mmio_range", @sizeOf(abi.MmioRange), @alignOf(abi.MmioRange));\n',
            "",
            1,
        )
        write_file(root / ABI_DUMP_REL, broken_abi_dump)
        issues = validate(root)
        assert (
            'missing_abi_dump_snippet:try writeLayoutPrefix(writer, "zigux_mmio_range", @sizeOf(abi.MmioRange), @alignOf(abi.MmioRange));'
            in issues
        )

        build_valid_workspace(root)
        broken_abi_dump_panic = (root / ABI_DUMP_REL).read_text(encoding="utf-8").replace(
            'try writer.writeAll(",\\\"panic_abort\\\":");\n',
            "",
            1,
        )
        write_file(root / ABI_DUMP_REL, broken_abi_dump_panic)
        issues = validate(root)
        assert (
            'missing_abi_dump_snippet:try writer.writeAll(",\\\"panic_abort\\\":");'
            in issues
        )

        build_valid_workspace(root)
        broken_abi_expected = (root / ABI_EXPECTED_REL).read_text(encoding="utf-8").replace(
            '"zigux_interop_policy":{"size":4,"align":1,"offsets":{"panic_mode":0,"allocator_mode":1,"unsafe_scope":2,"reserved":3}}\n',
            "",
            1,
        )
        write_file(root / ABI_EXPECTED_REL, broken_abi_expected)
        issues = validate(root)
        assert (
            'missing_abi_expected_snippet:"zigux_interop_policy":{"size":4,"align":1,"offsets":{"panic_mode":0,"allocator_mode":1,"unsafe_scope":2,"reserved":3}}'
            in issues
        )

        build_valid_workspace(root)
        broken_abi_expected_allocator = (root / ABI_EXPECTED_REL).read_text(encoding="utf-8").replace(
            '"allocator_caller_provided":0\n',
            "",
            1,
        )
        write_file(root / ABI_EXPECTED_REL, broken_abi_expected_allocator)
        issues = validate(root)
        assert (
            'missing_abi_expected_snippet:"allocator_caller_provided":0'
            in issues
        )

    print("PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=pass")
    print("PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST_CASE_COUNT=21")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Phase 3 policy and unsafe survey note against the current ABI packet.")
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
