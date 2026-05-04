#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import subprocess
import tempfile


_HERE = Path(__file__).resolve()
ROOT = _HERE.parents[2] if len(_HERE.parents) > 2 else _HERE.parent
SURVEY_REL = "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md"
DOCS_README_REL = "Documentation/zigux/README.md"
SCRIPTS_README_REL = "scripts/zigux/README.md"
MAKEFILE_REL = "zigux/Makefile"
ABI_SLICE_REL = "Documentation/zigux/phase3-abi-slice.md"
MANIFEST_REL = "zigux/tests/fixtures/phase3_abi_manifest.json"
POLICY_UNSAFE_BUILD_REL = "zigux/tests/phase3_policy_unsafe_build.zig"
POLICY_UNSAFE_TEST_REL = "zigux/tests/phase3_policy_unsafe.zig"
LAYOUT_ASSERT_REL = "zigux/helpers/layout_assert.zig"
PANIC_POLICY_REL = "zigux/helpers/panic_policy.zig"
ALLOCATOR_POLICY_REL = "zigux/helpers/allocator_policy.zig"
INTEROP_POLICY_REL = "zigux/helpers/interop_policy.zig"
UNSAFE_NARROW_REL = "zigux/unsafe/narrow.zig"
MMIO_REL = "zigux/helpers/mmio.zig"
POLICY_UNSAFE_MMIO_CONSUMER_CHECK_REL = "scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py"

HEX40 = re.compile(r"^[0-9a-f]{40}$")
PLACEHOLDER_SHA = "0123456789abcdef0123456789abcdef01234567"
PLACEHOLDER_COMMIT = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

REQUIRED_SURVEY_MARKERS = (
    "PHASE3_LAYOUT_ASSERT_PATH=zigux/helpers/layout_assert.zig",
    "PHASE3_LAYOUT_ASSERT_SCOPE=canonical-bindings",
    "PHASE3_LAYOUT_ASSERT_STATUS=canonical-layout-assertions-landed",
    "PHASE3_PANIC_POLICY_PATH=zigux/helpers/panic_policy.zig",
    "PHASE3_PANIC_POLICY=explicit-modes-only",
    "PHASE3_PANIC_POLICY_STATUS=interop-byte-decode-landed",
    "PHASE3_ALLOCATOR_POLICY_PATH=zigux/helpers/allocator_policy.zig",
    "PHASE3_ALLOCATOR_POLICY=explicit-modes-only",
    "PHASE3_ALLOCATOR_POLICY_STATUS=interop-byte-decode-and-init-flow-landed",
    "PHASE3_INTEROP_POLICY_PATH=zigux/helpers/interop_policy.zig",
    "PHASE3_INTEROP_POLICY_SCOPE=whole-record-decode-explicit-mode-and-scope-validation",
    "PHASE3_UNSAFE_PATH=zigux/unsafe/narrow.zig",
    "PHASE3_UNSAFE_SCOPE=narrow-mmio-and-raw-pointer-bridge",
    "PHASE3_MMIO_PATH=zigux/helpers/mmio.zig",
    "PHASE3_MMIO_TYPED_POLICY_CONSUMER=zigux/helpers/mmio.zig",
    "PHASE3_POLICY_UNSAFE_GATE=zig build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig",
    "PHASE3_BOUNDARY_GAP=typed-policy-mmio-consumer-landed-no-third-boundary-helper-beyond-focused-replay",
    "PHASE3_NEXT_BOUNDED_STEP=keep-the-policy-and-unsafe-surface-narrow-until-one-roadmap-backed-helper-beyond-mmio-needs-a-typed-interop-policy-consumer",
)

REQUIRED_SURVEY_SNIPPETS = (
    "verified `master` head",
    "zigux/helpers/layout_assert.zig",
    "zigux/helpers/panic_policy.zig",
    "zigux/helpers/allocator_policy.zig",
    "zigux/helpers/interop_policy.zig",
    "zigux/unsafe/narrow.zig",
    "zigux/helpers/mmio.zig",
    "zigux/tests/phase3_policy_unsafe_build.zig",
    "zigux/tests/phase3_policy_unsafe.zig",
    "typed interop-policy",
    "`init`, `encode`, and round-trip replay helpers",
    "`action()`, `permitsVolatileMmio()`, and `permitsRawPointerBridge()` accessors",
    "readScopedWithPolicy",
    "`mmio.write32Policy()` and `mmio.read32Policy()`",
)

REQUIRED_SURVEY_PATHS = (
    LAYOUT_ASSERT_REL,
    PANIC_POLICY_REL,
    ALLOCATOR_POLICY_REL,
    INTEROP_POLICY_REL,
    UNSAFE_NARROW_REL,
    MMIO_REL,
    POLICY_UNSAFE_BUILD_REL,
    POLICY_UNSAFE_TEST_REL,
    POLICY_UNSAFE_MMIO_CONSUMER_CHECK_REL,
    MANIFEST_REL,
    ABI_SLICE_REL,
)

REQUIRED_DOCS_README_SNIPPETS = (
    "`Documentation/zigux/phase3-policy-unsafe-boundary-survey.md`",
    "`scripts/zigux/validate-phase3-policy-unsafe-survey.py`",
    "`make -C zigux phase3-validate`",
    "shared docs-index hook",
    "shared scripts-index hook",
)

REQUIRED_SCRIPTS_README_SNIPPETS = (
    "`validate-phase3-policy-unsafe-survey.py`",
    "`Documentation/zigux/phase3-policy-unsafe-boundary-survey.md`",
    "published docs-index and scripts-index hooks",
)

REQUIRED_MAKEFILE_SNIPPETS = (
    "scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "scripts/zigux/validate-phase3-policy-unsafe-survey.py --self-test",
    "$(ZIG) build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig",
)

REQUIRED_LAYOUT_ASSERT_SNIPPETS = (
    "pub fn assertInteropPolicyLayout() void {",
    "pub fn assertMmioRangeLayout() void {",
    "pub fn assertRbtreeRootViewLayout() void {",
    "assertRbtreeRootViewLayout();",
    'test "phase3 layout assertions cover canonical bindings"',
)

REQUIRED_PANIC_POLICY_SNIPPETS = (
    "pub fn modeFromInteropPolicyByte(panic_mode: u8) ?abi.PanicMode {",
    "pub fn recognizesInteropPolicyByte(panic_mode: u8) bool {",
    "pub fn canReturnPolicyByte(panic_mode: u8) bool {",
    'test "phase3 panic policy stays explicit"',
)

REQUIRED_ALLOCATOR_POLICY_SNIPPETS = (
    "pub fn modeFromInteropPolicyByte(allocator_mode: u8) ?abi.AllocatorMode {",
    "pub fn permitsGlobalFallbackPolicyByte(allocator_mode: u8) bool {",
    "pub fn initializesOwnedStatePolicyByte(allocator_mode: u8) bool {",
    "pub fn requiresResetOnInitPolicyByte(allocator_mode: u8) bool {",
    'test "phase3 allocator policy stays explicit"',
)

REQUIRED_INTEROP_POLICY_SNIPPETS = (
    "pub const DecodedInteropPolicy = struct {",
    "    pub fn action(self: DecodedInteropPolicy) panic_policy.Action {",
    "    pub fn permitsVolatileMmio(self: DecodedInteropPolicy) bool {",
    "    pub fn permitsRawPointerBridge(self: DecodedInteropPolicy) bool {",
    "pub fn init(panic_mode: abi.PanicMode, allocator_mode: abi.AllocatorMode, unsafe_scope: narrow.UnsafeScopeTag) DecodedInteropPolicy {",
    "pub fn encode(panic_mode: abi.PanicMode, allocator_mode: abi.AllocatorMode, unsafe_scope: narrow.UnsafeScopeTag) abi.InteropPolicy {",
    "pub fn decode(policy: abi.InteropPolicy) DecodeError!DecodedInteropPolicy {",
    "pub fn recognizes(policy: abi.InteropPolicy) bool {",
    'test "phase3 interop policy decoder keeps the boundary typed"',
    'test "phase3 interop policy decoder keeps the panic action explicit"',
    'test "phase3 interop policy decoder keeps allocator init requirements explicit"',
    'test "phase3 interop policy keeps canonical abi encoding explicit"',
    'test "phase3 interop policy encode helper preserves explicit policy behavior"',
    'test "phase3 interop policy decoder rejects invalid bytes and reserved bits"',
)

REQUIRED_UNSAFE_SNIPPETS = (
    "pub const UnsafeScopeTag = enum(u8) {",
    "pub fn scopeFromInteropPolicyBytes(unsafe_scope: u8, reserved: u8) ?UnsafeScopeTag {",
    "pub fn permitsVolatileMmioPolicyBytes(unsafe_scope: u8, reserved: u8) bool {",
    "pub fn permitsRawPointerBridgePolicyBytes(unsafe_scope: u8, reserved: u8) bool {",
    "pub fn recognizesInteropPolicyBytes(unsafe_scope: u8, reserved: u8) bool {",
    "pub fn scopedPointerAt(comptime T: type, scope: UnsafeScopeTag, base: usize, offset: usize) ScopeError!*volatile T {",
    "pub fn scopedConstSliceAt(comptime T: type, scope: UnsafeScopeTag, base: usize, len: usize) ScopeError![]const T {",
    "pub fn scopedConstPointerAt(comptime T: type, scope: UnsafeScopeTag, addr: usize) ScopeError!*const T {",
    "pub fn constValueAt(comptime T: type, scope: UnsafeScopeTag, addr: usize) ScopeError!T {",
    "pub fn scopedConstValueAt(comptime T: type, scope: UnsafeScopeTag, addr: usize) ScopeError!T {",
    'test "phase3 narrow unsafe wrappers stay bounded"',
    'test "phase3 narrow unsafe scope stays explicit"',
    'test "phase3 narrow unsafe scoped helpers reject misaligned addresses"',
    'test "phase3 narrow unsafe interop policy decoding stays explicit"',
    'test "phase3 scoped unsafe helpers require the declared scope"',
    'test "phase3 narrow unsafe scoped helpers reject overflowed address math"',
)

REQUIRED_MMIO_SNIPPETS = (
    "pub fn read16Scoped(scope: narrow.UnsafeScopeTag, base_addr: usize, offset: usize) narrow.ScopeError!u16 {",
    "pub fn write16Scoped(",
    "pub fn read32Scoped(scope: narrow.UnsafeScopeTag, base_addr: usize, offset: usize) narrow.ScopeError!u32 {",
    "pub fn write32Scoped(",
    "fn scopeFromPolicy(policy: interop_policy.DecodedInteropPolicy) narrow.ScopeError!narrow.UnsafeScopeTag {",
    "pub fn readScopedWithPolicy(",
    "pub fn writeScopedWithPolicy(",
    "pub fn read8Policy(policy: interop_policy.DecodedInteropPolicy, base_addr: usize, offset: usize) narrow.ScopeError!u8 {",
    "pub fn write8Policy(",
    "pub fn read16Policy(policy: interop_policy.DecodedInteropPolicy, base_addr: usize, offset: usize) narrow.ScopeError!u16 {",
    "pub fn write16Policy(",
    "pub fn read32Policy(policy: interop_policy.DecodedInteropPolicy, base_addr: usize, offset: usize) narrow.ScopeError!u32 {",
    "pub fn write32Policy(",
    "pub fn read64Policy(policy: interop_policy.DecodedInteropPolicy, base_addr: usize, offset: usize) narrow.ScopeError!u64 {",
    "pub fn write64Policy(",
    'test "phase3 mmio wrapper consumes decoded interop policy"',
    'test "phase3 mmio wrapper keeps declared scope explicit across widths"',
    'test "phase3 mmio wrapper rejects misaligned scoped accesses"',
)

REQUIRED_POLICY_UNSAFE_TEST_SNIPPETS = (
    'test "phase3 policy helpers stay ABI aligned"',
    'test "phase3 policy decoder validates the whole interop record"',
    'test "phase3 policy decoder keeps allocator init and reset requirements reviewable"',
    "allocator_policy.initializesOwnedStatePolicyByte(@intFromEnum(abi.AllocatorMode.kernel_heap))",
    "allocator_policy.requiresResetOnInitPolicyByte(@intFromEnum(abi.AllocatorMode.arena))",
    'test "phase3 policy decoder rejects partial or reserved policy bytes"',
    "try std.testing.expectError(error.InvalidPanicMode, interop_policy.decode(.{",
    "try std.testing.expectError(error.InvalidAllocatorMode, interop_policy.decode(.{",
    'test "phase3 policy encoder keeps a canonical interop record"',
    "const encoded = interop_policy.encode(.warn, .arena, .raw_pointer_bridge);",
    "const round_trip = try interop_policy.decode(encoded);",
    'test "phase3 policy init helper round trips through decode without widening scope"',
    "const decoded = interop_policy.init(.abort, .caller_provided, .none);",
    'test "phase3 policy gate reaches a second boundary helper through decoded policy"',
    "try mmio.write32Policy(mmio_policy, base32, @sizeOf(u32), 0xdecafbad);",
    "try std.testing.expectEqual(@as(u32, 0xdecafbad), try mmio.read32Policy(mmio_policy, base32, @sizeOf(u32)));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.write32Policy(raw_pointer_policy, base32, 0, 1));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.read32Policy(raw_pointer_policy, base32, 0));",
    'test "phase3 policy gate decodes interop-policy unsafe bytes explicitly"',
    'test "phase3 policy gate enforces the declared unsafe scope"',
    "try std.testing.expectError(error.UnsafeScopeDenied, narrow.constSliceAt(u32, .volatile_mmio, base, words.len));",
    "const words_slice = try narrow.constSliceAt(u32, .raw_pointer_bridge, base, words.len);",
    "try std.testing.expectError(error.UnsafeScopeDenied, narrow.constPointerAt(u32, .volatile_mmio, base + @sizeOf(u32)));",
    "const second_word = try narrow.constPointerAt(u32, .raw_pointer_bridge, base + @sizeOf(u32));",
    'test "phase3 policy gate rejects overflowed unsafe address math"',
    "try std.testing.expectError(error.AddressOverflow, narrow.checkedByteOffset(max, 1));",
    "try std.testing.expectError(error.AddressOverflow, narrow.scopedPointerAt(u32, .volatile_mmio, max, 1));",
)

REQUIRED_ABI_SLICE_SNIPPETS = (
    "focused replay gate: `zigux/tests/phase3_policy_unsafe.zig` now verifies both successful whole-record decoding and rejection of partial or reserved policy bytes",
    "focused replay gate: `zigux/tests/phase3_policy_unsafe.zig` now keeps `layout_assert`, panic, allocator, whole-record interop-policy decoding, unsafe-byte decoding, and declared-scope enforcement aligned on its own compile-and-test path",
)

REQUIRED_POLICY_UNSAFE_MMIO_CONSUMER_CHECK_SNIPPETS = (
    "PHASE3_MMIO_TYPED_POLICY_CONSUMER=zigux/helpers/mmio.zig",
    "PHASE3_BOUNDARY_GAP=typed-policy-mmio-consumer-landed-no-third-boundary-helper-beyond-focused-replay",
    "PHASE3_NEXT_BOUNDED_STEP=keep-the-policy-and-unsafe-surface-narrow-until-one-roadmap-backed-helper-beyond-mmio-needs-a-typed-interop-policy-consumer",
    "`zigux/helpers/mmio.zig` is now the shipped second boundary helper that consumes `DecodedInteropPolicy` directly outside the focused `phase3_policy_unsafe` test packet",
    "the current tree does not yet ship a third Phase 3 boundary helper that consumes `DecodedInteropPolicy` directly beyond the focused replay and the scoped MMIO helper",
    'test "phase3 mmio wrapper consumes decoded interop policy"',
)

REQUIRED_POLICY_BUILD_SNIPPETS = (
    "const rbtree_bindings_module = b.createModule(.{",
    '.root_source_file = b.path("../bindings/rbtree.zig"),',
    'layout_assert_module.addImport("abi_bindings", abi_bindings_module);',
    'layout_assert_module.addImport("rbtree_bindings", rbtree_bindings_module);',
    "const interop_policy_module = b.createModule(.{",
    'interop_policy_module.addImport("abi_bindings", abi_bindings_module);',
    'interop_policy_module.addImport("panic_policy", panic_policy_module);',
    'interop_policy_module.addImport("allocator_policy", allocator_policy_module);',
    'interop_policy_module.addImport("narrow_unsafe", narrow_unsafe_module);',
    "const mmio_module = b.createModule(.{",
    'mmio_module.addImport("abi_bindings", abi_bindings_module);',
    'mmio_module.addImport("interop_policy", interop_policy_module);',
    'mmio_module.addImport("narrow_unsafe", narrow_unsafe_module);',
    'root_module.addImport("interop_policy", interop_policy_module);',
    'root_module.addImport("layout_assert", layout_assert_module);',
    'root_module.addImport("mmio", mmio_module);',
    '"phase3-policy-unsafe-test",',
)

SURVEYED_PACKET_BLOB_MARKERS = {
    "PHASE3_LAYOUT_ASSERT_BLOB_SHA": LAYOUT_ASSERT_REL,
    "PHASE3_PANIC_POLICY_BLOB_SHA": PANIC_POLICY_REL,
    "PHASE3_ALLOCATOR_POLICY_BLOB_SHA": ALLOCATOR_POLICY_REL,
    "PHASE3_INTEROP_POLICY_BLOB_SHA": INTEROP_POLICY_REL,
    "PHASE3_UNSAFE_BLOB_SHA": UNSAFE_NARROW_REL,
    "PHASE3_MMIO_BLOB_SHA": MMIO_REL,
    "PHASE3_ABI_SLICE_DOC_BLOB_SHA": ABI_SLICE_REL,
    "PHASE3_POLICY_UNSAFE_BUILD_BLOB_SHA": POLICY_UNSAFE_BUILD_REL,
    "PHASE3_POLICY_UNSAFE_TEST_BLOB_SHA": POLICY_UNSAFE_TEST_REL,
    "PHASE3_ABI_MANIFEST_BLOB_SHA": MANIFEST_REL,
}

SURVEYED_PACKET_PATHS = tuple(SURVEYED_PACKET_BLOB_MARKERS.values())


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


def _marker_value_from_text(text: str, marker: str) -> str | None:
    prefix = f"{marker}="
    for line in text.splitlines():
        stripped = line.strip().strip("- ").strip("`")
        if stripped.startswith(prefix):
            return stripped[len(prefix) :]
    return None


def _surveyed_commit_from_text(text: str) -> str | None:
    return _marker_value_from_text(text, "PHASE3_SURVEYED_COMMIT")


def _has_local_commit(root: Path, commit: str) -> bool:
    if not (root / ".git").exists():
        return False
    result = subprocess.run(
        ["git", "cat-file", "-e", f"{commit}^{{commit}}"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def _packet_drift_since_commit(root: Path, commit: str) -> list[str]:
    if not (root / ".git").exists():
        return []
    if not _has_local_commit(root, commit):
        return [f"surveyed_commit_unavailable_locally:{commit}"]

    result = subprocess.run(
        ["git", "diff", "--name-only", commit, "HEAD", "--", *SURVEYED_PACKET_PATHS],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return [f"surveyed_commit_diff_error:{commit}"]
    return [f"surveyed_commit_packet_drift:{rel}" for rel in result.stdout.splitlines() if rel.strip()]


def _packet_drift_by_blob_sha(root: Path, survey: str) -> list[str]:
    if not (root / ".git").exists():
        return []

    issues: list[str] = []
    saw_blob_marker = False
    for marker, rel in SURVEYED_PACKET_BLOB_MARKERS.items():
        expected_blob = _marker_value_from_text(survey, marker)
        if expected_blob is None:
            continue
        saw_blob_marker = True

        path = root / rel
        if not path.exists():
            issues.append(f"current_blob_unavailable:{rel}")
            continue

        result = subprocess.run(
            ["git", "hash-object", "--no-filters", str(path)],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            issues.append(f"current_blob_unavailable:{rel}")
            continue

        current_blob = result.stdout.strip()
        if not HEX40.fullmatch(current_blob):
            issues.append(f"invalid_current_blob_sha:{rel}:{current_blob}")
        elif current_blob != expected_blob:
            issues.append(f"surveyed_blob_drift:{rel}")

    return issues if saw_blob_marker else []


def validate(root: Path) -> list[str]:
    issues: list[str] = []

    survey = _read_text(root, SURVEY_REL, issues)
    docs_readme = _read_text(root, DOCS_README_REL, issues)
    scripts_readme = _read_text(root, SCRIPTS_README_REL, issues)
    makefile = _read_text(root, MAKEFILE_REL, issues)
    layout_assert = _read_text(root, LAYOUT_ASSERT_REL, issues)
    panic_policy = _read_text(root, PANIC_POLICY_REL, issues)
    allocator_policy = _read_text(root, ALLOCATOR_POLICY_REL, issues)
    interop_policy = _read_text(root, INTEROP_POLICY_REL, issues)
    unsafe_narrow = _read_text(root, UNSAFE_NARROW_REL, issues)
    mmio = _read_text(root, MMIO_REL, issues)
    policy_unsafe_test = _read_text(root, POLICY_UNSAFE_TEST_REL, issues)
    policy_unsafe_mmio_consumer_check = _read_text(root, POLICY_UNSAFE_MMIO_CONSUMER_CHECK_REL, issues)
    abi_slice = _read_text(root, ABI_SLICE_REL, issues)
    policy_build = _read_text(root, POLICY_UNSAFE_BUILD_REL, issues)

    if survey:
        _check_snippets(survey, REQUIRED_SURVEY_MARKERS, "missing_survey_marker", issues)
        for marker in SURVEYED_PACKET_BLOB_MARKERS:
            value = _marker_value_from_text(survey, marker)
            if value is None:
                issues.append(f"missing_survey_marker:{marker}=")
            elif not HEX40.fullmatch(value):
                issues.append(f"invalid_survey_blob_sha:{marker}:{value}")

        _check_snippets(survey, REQUIRED_SURVEY_SNIPPETS, "missing_survey_snippet", issues)

        surveyed_commit = _surveyed_commit_from_text(survey)
        if surveyed_commit is None:
            issues.append("missing_surveyed_commit")
        elif not HEX40.fullmatch(surveyed_commit):
            issues.append(f"invalid_surveyed_commit:{surveyed_commit}")
        else:
            blob_issues = _packet_drift_by_blob_sha(root, survey)
            if blob_issues:
                issues.extend(blob_issues)
            elif not all(_marker_value_from_text(survey, marker) is not None for marker in SURVEYED_PACKET_BLOB_MARKERS):
                issues.extend(_packet_drift_since_commit(root, surveyed_commit))

    for rel in REQUIRED_SURVEY_PATHS:
        if not (root / rel).exists():
            issues.append(f"missing_repo_path:{rel}")

    if docs_readme:
        _check_snippets(docs_readme, REQUIRED_DOCS_README_SNIPPETS, "missing_docs_readme_snippet", issues)
    if scripts_readme:
        _check_snippets(scripts_readme, REQUIRED_SCRIPTS_README_SNIPPETS, "missing_scripts_readme_snippet", issues)
    if makefile:
        _check_snippets(makefile, REQUIRED_MAKEFILE_SNIPPETS, "missing_makefile_snippet", issues)
    if layout_assert:
        _check_snippets(layout_assert, REQUIRED_LAYOUT_ASSERT_SNIPPETS, "missing_layout_assert_snippet", issues)
    if panic_policy:
        _check_snippets(panic_policy, REQUIRED_PANIC_POLICY_SNIPPETS, "missing_panic_policy_snippet", issues)
    if allocator_policy:
        _check_snippets(allocator_policy, REQUIRED_ALLOCATOR_POLICY_SNIPPETS, "missing_allocator_policy_snippet", issues)
    if interop_policy:
        _check_snippets(interop_policy, REQUIRED_INTEROP_POLICY_SNIPPETS, "missing_interop_policy_snippet", issues)
    if unsafe_narrow:
        _check_snippets(unsafe_narrow, REQUIRED_UNSAFE_SNIPPETS, "missing_unsafe_snippet", issues)
    if mmio:
        _check_snippets(mmio, REQUIRED_MMIO_SNIPPETS, "missing_mmio_snippet", issues)
    if policy_unsafe_test:
        _check_snippets(policy_unsafe_test, REQUIRED_POLICY_UNSAFE_TEST_SNIPPETS, "missing_policy_unsafe_test_snippet", issues)
    if policy_unsafe_mmio_consumer_check:
        _check_snippets(
            policy_unsafe_mmio_consumer_check,
            REQUIRED_POLICY_UNSAFE_MMIO_CONSUMER_CHECK_SNIPPETS,
            "missing_policy_unsafe_mmio_consumer_check_snippet",
            issues,
        )
    if abi_slice:
        _check_snippets(abi_slice, REQUIRED_ABI_SLICE_SNIPPETS, "missing_abi_slice_snippet", issues)
    if policy_build:
        _check_snippets(policy_build, REQUIRED_POLICY_BUILD_SNIPPETS, "missing_policy_build_snippet", issues)

    return issues


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _blob_marker_lines() -> list[str]:
    return [f"- `{marker}={PLACEHOLDER_SHA}`" for marker in SURVEYED_PACKET_BLOB_MARKERS]


def _replace_blob_markers_with_head(root: Path, survey_path: Path) -> None:
    survey_text = survey_path.read_text(encoding="utf-8")
    for marker, rel in SURVEYED_PACKET_BLOB_MARKERS.items():
        blob_sha = subprocess.run(
            ["git", "hash-object", "--no-filters", str(root / rel)],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        survey_text = survey_text.replace(f"{marker}={PLACEHOLDER_SHA}", f"{marker}={blob_sha}")
    survey_path.write_text(survey_text, encoding="utf-8", newline="\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_policy_unsafe_survey_") as tmp_dir_str:
        root = Path(tmp_dir_str)

        _write(
            root,
            SURVEY_REL,
            "\n".join(
                [
                    "# Phase 3 Policy and Unsafe Boundary Survey",
                    "",
                    f"- `PHASE3_SURVEYED_COMMIT={PLACEHOLDER_COMMIT}`",
                    "- `PHASE3_LAYOUT_ASSERT_PATH=zigux/helpers/layout_assert.zig`",
                    "- `PHASE3_LAYOUT_ASSERT_SCOPE=canonical-bindings`",
                    "- `PHASE3_LAYOUT_ASSERT_STATUS=canonical-layout-assertions-landed`",
                    "- `PHASE3_PANIC_POLICY_PATH=zigux/helpers/panic_policy.zig`",
                    "- `PHASE3_PANIC_POLICY=explicit-modes-only`",
                    "- `PHASE3_PANIC_POLICY_STATUS=interop-byte-decode-landed`",
                    "- `PHASE3_ALLOCATOR_POLICY_PATH=zigux/helpers/allocator_policy.zig`",
                    "- `PHASE3_ALLOCATOR_POLICY=explicit-modes-only`",
                    "- `PHASE3_ALLOCATOR_POLICY_STATUS=interop-byte-decode-and-init-flow-landed`",
                    "- `PHASE3_INTEROP_POLICY_PATH=zigux/helpers/interop_policy.zig`",
                    "- `PHASE3_INTEROP_POLICY_SCOPE=whole-record-decode-explicit-mode-and-scope-validation`",
                    "- `PHASE3_UNSAFE_PATH=zigux/unsafe/narrow.zig`",
                    "- `PHASE3_UNSAFE_SCOPE=narrow-mmio-and-raw-pointer-bridge`",
                    "- `PHASE3_MMIO_PATH=zigux/helpers/mmio.zig`",
                    "- `PHASE3_MMIO_TYPED_POLICY_CONSUMER=zigux/helpers/mmio.zig`",
                    "- `PHASE3_POLICY_UNSAFE_GATE=zig build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig`",
                    "- `PHASE3_BOUNDARY_GAP=typed-policy-mmio-consumer-landed-no-third-boundary-helper-beyond-focused-replay`",
                    "- `PHASE3_NEXT_BOUNDED_STEP=keep-the-policy-and-unsafe-surface-narrow-until-one-roadmap-backed-helper-beyond-mmio-needs-a-typed-interop-policy-consumer`",
                    *_blob_marker_lines(),
                    "",
                    f"This survey is pinned to verified `master` head `{PLACEHOLDER_COMMIT}`.",
                    "The packet names zigux/helpers/layout_assert.zig, zigux/helpers/panic_policy.zig, zigux/helpers/allocator_policy.zig, zigux/helpers/interop_policy.zig, zigux/unsafe/narrow.zig, zigux/helpers/mmio.zig, zigux/tests/phase3_policy_unsafe_build.zig, and zigux/tests/phase3_policy_unsafe.zig.",
                    "The current bounded packet keeps typed interop-policy decoding explicit through `init`, `encode`, and round-trip replay helpers plus `action()`, `permitsVolatileMmio()`, and `permitsRawPointerBridge()` accessors.",
                    "The same packet keeps decoded-policy MMIO reviewable through readScopedWithPolicy and `mmio.write32Policy()` and `mmio.read32Policy()`.",
                    "",
                ]
            ),
        )
        _write(root, DOCS_README_REL, "\n".join(REQUIRED_DOCS_README_SNIPPETS) + "\n")
        _write(root, SCRIPTS_README_REL, "\n".join(REQUIRED_SCRIPTS_README_SNIPPETS) + "\n")
        _write(
            root,
            MAKEFILE_REL,
            "\n".join(REQUIRED_MAKEFILE_SNIPPETS) + "\n",
        )
        _write(
            root,
            LAYOUT_ASSERT_REL,
            "\n".join(
                [
                    "pub fn assertInteropPolicyLayout() void {}",
                    "pub fn assertMmioRangeLayout() void {}",
                    "pub fn assertRbtreeRootViewLayout() void {}",
                    'test "phase3 layout assertions cover canonical bindings" {',
                    "    assertRbtreeRootViewLayout();",
                    "}",
                    "",
                ]
            ),
        )
        _write(
            root,
            PANIC_POLICY_REL,
            "\n".join(REQUIRED_PANIC_POLICY_SNIPPETS) + "\n",
        )
        _write(
            root,
            ALLOCATOR_POLICY_REL,
            "\n".join(REQUIRED_ALLOCATOR_POLICY_SNIPPETS) + "\n",
        )
        _write(
            root,
            INTEROP_POLICY_REL,
            "\n".join(REQUIRED_INTEROP_POLICY_SNIPPETS) + "\n",
        )
        _write(
            root,
            UNSAFE_NARROW_REL,
            "\n".join(REQUIRED_UNSAFE_SNIPPETS) + "\n",
        )
        _write(
            root,
            MMIO_REL,
            "\n".join(REQUIRED_MMIO_SNIPPETS) + "\n",
        )
        _write(
            root,
            POLICY_UNSAFE_TEST_REL,
            "\n".join(REQUIRED_POLICY_UNSAFE_TEST_SNIPPETS) + "\n",
        )
        _write(
            root,
            ABI_SLICE_REL,
            "\n".join(REQUIRED_ABI_SLICE_SNIPPETS) + "\n",
        )
        _write(root, MANIFEST_REL, "{}\n")
        _write(
            root,
            POLICY_UNSAFE_MMIO_CONSUMER_CHECK_REL,
            "\n".join(REQUIRED_POLICY_UNSAFE_MMIO_CONSUMER_CHECK_SNIPPETS) + "\n",
        )
        _write(
            root,
            POLICY_UNSAFE_BUILD_REL,
            "\n".join(REQUIRED_POLICY_BUILD_SNIPPETS) + "\n",
        )

        assert validate(root) == []

        subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, text=True)
        subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True, text=True)
        env = {
            **os.environ,
            "GIT_AUTHOR_NAME": "Codex",
            "GIT_AUTHOR_EMAIL": "codex@example.com",
            "GIT_COMMITTER_NAME": "Codex",
            "GIT_COMMITTER_EMAIL": "codex@example.com",
        }
        subprocess.run(
            ["git", "commit", "-m", "self-test snapshot"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        survey_path = root / SURVEY_REL
        survey_path.write_text(
            survey_path.read_text(encoding="utf-8").replace(PLACEHOLDER_COMMIT, head),
            encoding="utf-8",
            newline="\n",
        )
        _replace_blob_markers_with_head(root, survey_path)
        assert validate(root) == []

        missing_repo_path = root / POLICY_UNSAFE_BUILD_REL
        missing_repo_path.unlink()
        issues = validate(root)
        assert f"missing_repo_path:{POLICY_UNSAFE_BUILD_REL}" in issues
        _write(root, POLICY_UNSAFE_BUILD_REL, "\n".join(REQUIRED_POLICY_BUILD_SNIPPETS) + "\n")

        current_survey = survey_path.read_text(encoding="utf-8")
        layout_assert_blob = _marker_value_from_text(current_survey, "PHASE3_LAYOUT_ASSERT_BLOB_SHA")
        assert layout_assert_blob is not None
        survey_path.write_text(
            current_survey.replace(
                f"PHASE3_LAYOUT_ASSERT_BLOB_SHA={layout_assert_blob}",
                "PHASE3_LAYOUT_ASSERT_BLOB_SHA=not-a-sha",
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert "invalid_survey_blob_sha:PHASE3_LAYOUT_ASSERT_BLOB_SHA:not-a-sha" in issues

        survey_path.write_text(
            current_survey,
            encoding="utf-8",
            newline="\n",
        )
        survey_path.write_text(
            survey_path.read_text(encoding="utf-8").replace(head, "not-a-sha"),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert "invalid_surveyed_commit:not-a-sha" in issues

        survey_path.write_text(
            current_survey,
            encoding="utf-8",
            newline="\n",
        )
        missing_commit = "fedcba9876543210fedcba9876543210fedcba98"
        survey_path.write_text(
            survey_path.read_text(encoding="utf-8").replace(head, missing_commit),
            encoding="utf-8",
            newline="\n",
        )
        assert validate(root) == []

        survey_path.write_text(
            survey_path.read_text(encoding="utf-8").replace(missing_commit, head),
            encoding="utf-8",
            newline="\n",
        )
        _write(root, MMIO_REL, (root / MMIO_REL).read_text(encoding="utf-8") + "// drift\n")
        issues = validate(root)
        assert f"surveyed_blob_drift:{MMIO_REL}" in issues

        _write(
            root,
            DOCS_README_REL,
            "\n".join(REQUIRED_DOCS_README_SNIPPETS[:-1]) + "\n",
        )
        issues = validate(root)
        assert "missing_docs_readme_snippet:shared scripts-index hook" in issues

        _write(
            root,
            DOCS_README_REL,
            "\n".join(REQUIRED_DOCS_README_SNIPPETS) + "\n",
        )
        _write(
            root,
            SCRIPTS_README_REL,
            "\n".join(REQUIRED_SCRIPTS_README_SNIPPETS[:-1]) + "\n",
        )
        issues = validate(root)
        assert "missing_scripts_readme_snippet:published docs-index and scripts-index hooks" in issues

        _write(
            root,
            SCRIPTS_README_REL,
            "\n".join(REQUIRED_SCRIPTS_README_SNIPPETS) + "\n",
        )
        _write(
            root,
            POLICY_UNSAFE_TEST_REL,
            "\n".join(
                [
                    'test "phase3 policy helpers stay ABI aligned" {}',
                    'test "phase3 policy decoder validates the whole interop record" {}',
                    'test "phase3 policy decoder rejects partial or reserved policy bytes" {}',
                    'test "phase3 policy gate decodes interop-policy unsafe bytes explicitly" {}',
                    'test "phase3 policy gate enforces the declared unsafe scope" {}',
                    "",
                ]
            ),
        )
        issues = validate(root)
        assert (
            'missing_policy_unsafe_test_snippet:test "phase3 policy decoder keeps allocator init and reset requirements reviewable"'
            in issues
        )
        assert (
            'missing_policy_unsafe_test_snippet:try std.testing.expectError(error.InvalidPanicMode, interop_policy.decode(.{'
            in issues
        )
        assert (
            'missing_policy_unsafe_test_snippet:test "phase3 policy encoder keeps a canonical interop record"'
            in issues
        )
        assert (
            'missing_policy_unsafe_test_snippet:test "phase3 policy init helper round trips through decode without widening scope"'
            in issues
        )
        assert (
            'missing_policy_unsafe_test_snippet:test "phase3 policy gate reaches a second boundary helper through decoded policy"'
            in issues
        )
        assert (
            'missing_policy_unsafe_test_snippet:try mmio.write32Policy(mmio_policy, base32, @sizeOf(u32), 0xdecafbad);'
            in issues
        )
        assert (
            'missing_policy_unsafe_test_snippet:try std.testing.expectEqual(@as(u32, 0xdecafbad), try mmio.read32Policy(mmio_policy, base32, @sizeOf(u32)));'
            in issues
        )
        assert (
            'missing_policy_unsafe_test_snippet:try std.testing.expectError(error.UnsafeScopeDenied, mmio.write32Policy(raw_pointer_policy, base32, 0, 1));'
            in issues
        )
        assert (
            'missing_policy_unsafe_test_snippet:try std.testing.expectError(error.UnsafeScopeDenied, mmio.read32Policy(raw_pointer_policy, base32, 0));'
            in issues
        )
        assert (
            'missing_policy_unsafe_test_snippet:try std.testing.expectError(error.UnsafeScopeDenied, narrow.constSliceAt(u32, .volatile_mmio, base, words.len));'
            in issues
        )
        assert (
            'missing_policy_unsafe_test_snippet:try std.testing.expectError(error.AddressOverflow, narrow.checkedByteOffset(max, 1));'
            in issues
        )
        assert (
            'missing_policy_unsafe_test_snippet:test "phase3 policy gate rejects overflowed unsafe address math"'
            in issues
        )

        _write(
            root,
            MAKEFILE_REL,
            "scripts/zigux/validate-phase3-policy-unsafe-survey.py\nscripts/zigux/validate-phase3-policy-unsafe-survey.py --self-test\n",
        )
        issues = validate(root)
        assert (
            "missing_makefile_snippet:$(ZIG) build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig"
            in issues
        )

        _write(
            root,
            INTEROP_POLICY_REL,
            "\n".join(
                [
                    "pub const DecodedInteropPolicy = struct {};",
                    "pub fn init(panic_mode: abi.PanicMode, allocator_mode: abi.AllocatorMode, unsafe_scope: narrow.UnsafeScopeTag) DecodedInteropPolicy { _ = panic_mode; _ = allocator_mode; _ = unsafe_scope; }",
                    "pub fn encode(panic_mode: abi.PanicMode, allocator_mode: abi.AllocatorMode, unsafe_scope: narrow.UnsafeScopeTag) abi.InteropPolicy { _ = panic_mode; _ = allocator_mode; _ = unsafe_scope; }",
                    "pub fn decode(policy: abi.InteropPolicy) DecodeError!DecodedInteropPolicy { _ = policy; }",
                    "pub fn recognizes(policy: abi.InteropPolicy) bool { _ = policy; }",
                    'test "phase3 interop policy decoder keeps the boundary typed" {}',
                    'test "phase3 interop policy decoder keeps allocator init requirements explicit" {}',
                    'test "phase3 interop policy decoder rejects invalid bytes and reserved bits" {}',
                    "",
                ]
            ),
        )
        issues = validate(root)
        assert (
            'missing_interop_policy_snippet:    pub fn action(self: DecodedInteropPolicy) panic_policy.Action {'
            in issues
        )
        assert (
            'missing_interop_policy_snippet:    pub fn permitsVolatileMmio(self: DecodedInteropPolicy) bool {'
            in issues
        )
        assert (
            'missing_interop_policy_snippet:    pub fn permitsRawPointerBridge(self: DecodedInteropPolicy) bool {'
            in issues
        )
        assert (
            'missing_interop_policy_snippet:test "phase3 interop policy decoder keeps the panic action explicit"'
            in issues
        )
        assert (
            'missing_interop_policy_snippet:test "phase3 interop policy keeps canonical abi encoding explicit"'
            in issues
        )
        assert (
            'missing_interop_policy_snippet:test "phase3 interop policy encode helper preserves explicit policy behavior"'
            in issues
        )

        _write(
            root,
            UNSAFE_NARROW_REL,
            "\n".join(
                [
                    "pub const UnsafeScopeTag = enum(u8) {",
                    "pub fn scopeFromInteropPolicyBytes(unsafe_scope: u8, reserved: u8) ?UnsafeScopeTag { _ = unsafe_scope; _ = reserved; }",
                    "pub fn scopedPointerAt(comptime T: type, scope: UnsafeScopeTag, base: usize, offset: usize) ScopeError!*volatile T { _ = T; _ = scope; _ = base; _ = offset; }",
                    "pub fn scopedConstSliceAt(comptime T: type, scope: UnsafeScopeTag, base: usize, len: usize) ScopeError![]const T { _ = T; _ = scope; _ = base; _ = len; }",
                    "pub fn scopedConstPointerAt(comptime T: type, scope: UnsafeScopeTag, addr: usize) ScopeError!*const T { _ = T; _ = scope; _ = addr; }",
                    'test "phase3 narrow unsafe interop policy decoding stays explicit" {}',
                    'test "phase3 scoped unsafe helpers require the declared scope" {}',
                    'test "phase3 narrow unsafe scoped helpers reject overflowed address math" {}',
                    "",
                ]
            ),
        )
        issues = validate(root)
        assert (
            "missing_unsafe_snippet:pub fn permitsVolatileMmioPolicyBytes(unsafe_scope: u8, reserved: u8) bool {"
            in issues
        )
        assert (
            "missing_unsafe_snippet:pub fn permitsRawPointerBridgePolicyBytes(unsafe_scope: u8, reserved: u8) bool {"
            in issues
        )
        assert (
            "missing_unsafe_snippet:pub fn recognizesInteropPolicyBytes(unsafe_scope: u8, reserved: u8) bool {"
            in issues
        )
        assert (
            "missing_unsafe_snippet:pub fn constValueAt(comptime T: type, scope: UnsafeScopeTag, addr: usize) ScopeError!T {"
            in issues
        )
        assert (
            "missing_unsafe_snippet:pub fn scopedConstValueAt(comptime T: type, scope: UnsafeScopeTag, addr: usize) ScopeError!T {"
            in issues
        )
        assert 'missing_unsafe_snippet:test "phase3 narrow unsafe wrappers stay bounded"' in issues
        assert 'missing_unsafe_snippet:test "phase3 narrow unsafe scope stays explicit"' in issues
        assert 'missing_unsafe_snippet:test "phase3 narrow unsafe scoped helpers reject misaligned addresses"' in issues

        _write(
            root,
            UNSAFE_NARROW_REL,
            "\n".join(REQUIRED_UNSAFE_SNIPPETS) + "\n",
        )
        _write(
            root,
            MMIO_REL,
            "\n".join(
                [
                    "pub fn read16Scoped(scope: narrow.UnsafeScopeTag, base_addr: usize, offset: usize) narrow.ScopeError!u16 { _ = scope; _ = base_addr; _ = offset; }",
                    "pub fn write16Scoped() void {}",
                    "pub fn read32Scoped(scope: narrow.UnsafeScopeTag, base_addr: usize, offset: usize) narrow.ScopeError!u32 { _ = scope; _ = base_addr; _ = offset; }",
                    "pub fn write32Scoped() void {}",
                    'test "phase3 mmio wrapper keeps declared scope explicit across widths" {}',
                    'test "phase3 mmio wrapper rejects misaligned scoped accesses" {}',
                    "",
                ]
            ),
        )
        issues = validate(root)
        assert (
            "missing_mmio_snippet:fn scopeFromPolicy(policy: interop_policy.DecodedInteropPolicy) narrow.ScopeError!narrow.UnsafeScopeTag {"
            in issues
        )
        assert "missing_mmio_snippet:pub fn readScopedWithPolicy(" in issues
        assert "missing_mmio_snippet:pub fn writeScopedWithPolicy(" in issues
        assert (
            "missing_mmio_snippet:pub fn read8Policy(policy: interop_policy.DecodedInteropPolicy, base_addr: usize, offset: usize) narrow.ScopeError!u8 {"
            in issues
        )
        assert "missing_mmio_snippet:pub fn write8Policy(" in issues
        assert (
            "missing_mmio_snippet:pub fn read16Policy(policy: interop_policy.DecodedInteropPolicy, base_addr: usize, offset: usize) narrow.ScopeError!u16 {"
            in issues
        )
        assert "missing_mmio_snippet:pub fn write16Policy(" in issues
        assert (
            "missing_mmio_snippet:pub fn read32Policy(policy: interop_policy.DecodedInteropPolicy, base_addr: usize, offset: usize) narrow.ScopeError!u32 {"
            in issues
        )
        assert "missing_mmio_snippet:pub fn write32Policy(" in issues
        assert (
            "missing_mmio_snippet:pub fn read64Policy(policy: interop_policy.DecodedInteropPolicy, base_addr: usize, offset: usize) narrow.ScopeError!u64 {"
            in issues
        )
        assert "missing_mmio_snippet:pub fn write64Policy(" in issues
        assert 'missing_mmio_snippet:test "phase3 mmio wrapper consumes decoded interop policy"' in issues

        _write(
            root,
            MMIO_REL,
            "\n".join(
                [
                    "fn scopeFromPolicy(policy: interop_policy.DecodedInteropPolicy) narrow.ScopeError!narrow.UnsafeScopeTag { _ = policy; }",
                    "pub fn readScopedWithPolicy(comptime T: type, policy: interop_policy.DecodedInteropPolicy, base_addr: usize, offset: usize) narrow.ScopeError!T { _ = T; _ = policy; _ = base_addr; _ = offset; }",
                    "pub fn writeScopedWithPolicy(comptime T: type, policy: interop_policy.DecodedInteropPolicy, base_addr: usize, offset: usize, value: T) narrow.ScopeError!void { _ = T; _ = policy; _ = base_addr; _ = offset; _ = value; }",
                    "pub fn read16Scoped(scope: narrow.UnsafeScopeTag, base_addr: usize, offset: usize) narrow.ScopeError!u16 { _ = scope; _ = base_addr; _ = offset; }",
                    "pub fn write16Scoped() void {}",
                    "pub fn read32Scoped(scope: narrow.UnsafeScopeTag, base_addr: usize, offset: usize) narrow.ScopeError!u32 { _ = scope; _ = base_addr; _ = offset; }",
                    "pub fn write32Scoped() void {}",
                    "pub fn read8Policy(policy: interop_policy.DecodedInteropPolicy, base_addr: usize, offset: usize) narrow.ScopeError!u8 { _ = policy; _ = base_addr; _ = offset; }",
                    "pub fn write8Policy() void {}",
                    "pub fn read16Policy(policy: interop_policy.DecodedInteropPolicy, base_addr: usize, offset: usize) narrow.ScopeError!u16 { _ = policy; _ = base_addr; _ = offset; }",
                    "pub fn write16Policy() void {}",
                    "pub fn read32Policy(policy: interop_policy.DecodedInteropPolicy, base_addr: usize, offset: usize) narrow.ScopeError!u32 { _ = policy; _ = base_addr; _ = offset; }",
                    "pub fn write32Policy() void {}",
                    "pub fn write64Policy() void {}",
                    'test "phase3 mmio wrapper consumes decoded interop policy" {}',
                    'test "phase3 mmio wrapper keeps declared scope explicit across widths" {}',
                    'test "phase3 mmio wrapper rejects misaligned scoped accesses" {}',
                    "",
                ]
            ),
        )
        issues = validate(root)
        assert (
            "missing_mmio_snippet:pub fn read64Policy(policy: interop_policy.DecodedInteropPolicy, base_addr: usize, offset: usize) narrow.ScopeError!u64 {"
            in issues
        )

        _write(
            root,
            POLICY_UNSAFE_MMIO_CONSUMER_CHECK_REL,
            "\n".join(
                snippet
                for snippet in REQUIRED_POLICY_UNSAFE_MMIO_CONSUMER_CHECK_SNIPPETS
                if snippet != 'test "phase3 mmio wrapper consumes decoded interop policy"'
            ) + "\n",
        )
        issues = validate(root)
        assert (
            'missing_policy_unsafe_mmio_consumer_check_snippet:test "phase3 mmio wrapper consumes decoded interop policy"'
            in issues
        )

        _write(
            root,
            LAYOUT_ASSERT_REL,
            "\n".join(
                [
                    "pub fn assertInteropPolicyLayout() void {}",
                    "pub fn assertMmioRangeLayout() void {}",
                    'test "phase3 layout assertions cover canonical bindings" {',
                    "    assertInteropPolicyLayout();",
                    "}",
                    "",
                ]
            ),
        )
        issues = validate(root)
        assert "missing_layout_assert_snippet:pub fn assertRbtreeRootViewLayout() void {" in issues
        assert "missing_layout_assert_snippet:assertRbtreeRootViewLayout();" in issues

        _write(
            root,
            POLICY_UNSAFE_BUILD_REL,
            "\n".join(
                [
                    "const interop_policy_module = b.createModule(.{",
                    'interop_policy_module.addImport("abi_bindings", abi_bindings_module);',
                    'interop_policy_module.addImport("panic_policy", panic_policy_module);',
                    'interop_policy_module.addImport("allocator_policy", allocator_policy_module);',
                    'interop_policy_module.addImport("narrow_unsafe", narrow_unsafe_module);',
                    "const mmio_module = b.createModule(.{",
                    'mmio_module.addImport("abi_bindings", abi_bindings_module);',
                    'mmio_module.addImport("interop_policy", interop_policy_module);',
                    'mmio_module.addImport("narrow_unsafe", narrow_unsafe_module);',
                    'root_module.addImport("interop_policy", interop_policy_module);',
                    'root_module.addImport("layout_assert", layout_assert_module);',
                    'root_module.addImport("mmio", mmio_module);',
                    '"phase3-policy-unsafe-test",',
                    "",
                ]
            ),
        )
        issues = validate(root)
        assert "missing_policy_build_snippet:const rbtree_bindings_module = b.createModule(.{" in issues
        assert 'missing_policy_build_snippet:.root_source_file = b.path("../bindings/rbtree.zig"),' in issues
        assert 'missing_policy_build_snippet:layout_assert_module.addImport("rbtree_bindings", rbtree_bindings_module);' in issues

        _write(
            root,
            POLICY_UNSAFE_BUILD_REL,
            "\n".join(
                snippet
                for snippet in REQUIRED_POLICY_BUILD_SNIPPETS
                if snippet != 'root_module.addImport("mmio", mmio_module);'
            ) + "\n",
        )
        issues = validate(root)
        assert 'missing_policy_build_snippet:root_module.addImport("mmio", mmio_module);' in issues

    print("PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the dedicated Phase 3 policy and unsafe boundary survey.")
    parser.add_argument("--self-test", action="store_true", help="Run isolated validator checks.")
    parser.add_argument("root", nargs="?", help="Optional repo root override.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(Path(args.root).resolve() if args.root else ROOT)
    if issues:
        print("PHASE3_POLICY_UNSAFE_SURVEY=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE3_POLICY_UNSAFE_SURVEY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
