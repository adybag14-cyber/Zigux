#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess

from phase3_catalog import (
    Phase3Paths,
    Phase3Slice,
    artifact_diff_phase3_section_needs_rewrite,
    audit_phase3_doc_sync,
    audit_phase3_slug_sanity,
    discover_phase3_slices,
)
from phase3_check_lib import find_zig, render_wrapper_stub, shared_runner_gate_for_slug


ROOT = Path(__file__).resolve().parents[2]
BUILD_FILE_REL = "zigux/tests/build.zig"
ABI_LOW_LEVEL_BUILD_FILE_REL = "zigux/tests/phase3_low_level_wrappers_build.zig"
ABI_EXPORT_UAPI_BUILD_FILE_REL = "zigux/tests/phase3_export_uapi_build.zig"
ABI_POLICY_UNSAFE_BUILD_FILE_REL = "zigux/tests/phase3_policy_unsafe_build.zig"
ABI_REQUIRED_MANIFEST_FILES = (
    "include/zigux/abi.h",
    "include/linux/zigux.h",
    "zigux/bindings/abi.zig",
    "zigux/kernel/export_shim.zig",
    "zigux/uapi/version.zig",
    "zigux/helpers/layout_assert.zig",
    "zigux/helpers/panic_policy.zig",
    "zigux/helpers/allocator_policy.zig",
    "zigux/helpers/interop_policy.zig",
    "zigux/helpers/atomic.zig",
    "zigux/helpers/barrier.zig",
    "zigux/helpers/mmio.zig",
    "zigux/unsafe/narrow.zig",
    ABI_LOW_LEVEL_BUILD_FILE_REL,
    "zigux/tests/phase3_low_level_wrappers.zig",
    ABI_POLICY_UNSAFE_BUILD_FILE_REL,
    "zigux/tests/phase3_policy_unsafe.zig",
    "zigux/tests/phase3_abi.zig",
    ABI_EXPORT_UAPI_BUILD_FILE_REL,
    "zigux/tests/phase3_export_uapi.zig",
    "zigux/tests/phase3_abi_dump.zig",
    "zigux/tests/fixtures/phase3_abi/expected.json",
    "zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c",
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "scripts/zigux/validate_phase3_core.py",
    "scripts/zigux/validate_phase3_selftest.py",
)
ABI_REQUIRED_DOC_MARKERS = (
    "PHASE3_EXPORT_SHIM_SCOPE=explicit-status-plus-boundary-header",
    "PHASE3_UAPI_SCOPE=version-and-boundary-header",
    "PHASE3_LAYOUT_ASSERT_SCOPE=canonical-bindings",
    "PHASE3_PANIC_POLICY=explicit-modes-only",
    "PHASE3_ALLOCATOR_POLICY=explicit-modes-only",
    "PHASE3_INTEROP_POLICY_SCOPE=whole-record-decode-explicit-mode-and-scope-validation",
    "PHASE3_UNSAFE_SCOPE=narrow-mmio-and-raw-pointer-bridge",
    "PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig",
    "PHASE3_EXPORT_UAPI_GATE=zig build phase3-export-uapi-test --build-file zigux/tests/phase3_export_uapi_build.zig",
    "PHASE3_LOW_LEVEL_GATE=zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "PHASE3_POLICY_UNSAFE_GATE=zig build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig",
    "PHASE3_ATOMIC_SCOPE=load-store-exchange-compare-exchange-fetch-add-fetch-sub-fetch-and-fetch-and-fetch-or-fetch-xor",
    "PHASE3_BARRIER_SCOPE=acquire-release-full",
    "PHASE3_MMIO_SCOPE=range-read16-read32-write16-write32-plus-scoped-read16-write16-read32-write32",
)
ABI_REQUIRED_SOURCE_MARKERS = {
    "zigux/kernel/export_shim.zig": (
        "pub fn header(flags: u16) abi.BoundaryHeader {",
        "pub fn isCompatibleHeader(boundary_header: abi.BoundaryHeader) bool {",
        "pub fn isCanonicalHeader(boundary_header: abi.BoundaryHeader) bool {",
        "pub fn normalize(status: abi.ExportStatus) abi.ExportStatus {",
        'test "phase3 export shim keeps failure encoding explicit"',
        'test "phase3 export shim normalizes explicit status decoding"',
        'test "phase3 export shim separates canonical headers from broader compatibility"',
    ),
    "zigux/uapi/version.zig": (
        "pub const abi_version: u16 = abi.ABI_VERSION;",
        "pub fn boundaryHeader(flags: u16) Header {",
        "pub fn isCompatible(header: Header) bool {",
        "pub fn isCanonical(header: Header) bool {",
        'test "phase3 uapi version follows abi version"',
        'test "phase3 uapi boundary header stays explicit and compatible"',
        'test "phase3 uapi boundary header distinguishes canonical and future-compatible shapes"',
    ),
    "zigux/helpers/layout_assert.zig": (
        'test "phase3 layout assertions cover canonical bindings"',
        'assertOffset(abi.InteropPolicy, "unsafe_scope", 2);',
    ),
    "zigux/helpers/panic_policy.zig": (
        "pub fn actionFor(mode: abi.PanicMode) Action {",
        "pub fn modeFromInteropPolicyByte(panic_mode: u8) ?abi.PanicMode {",
        "pub fn recognizesInteropPolicyByte(panic_mode: u8) bool {",
        "pub fn canReturnPolicyByte(panic_mode: u8) bool {",
        'test "phase3 panic policy stays explicit"',
    ),
    "zigux/helpers/allocator_policy.zig": (
        "pub fn initFlowFor(mode: abi.AllocatorMode) InitFlow {",
        "pub fn modeFromInteropPolicyByte(allocator_mode: u8) ?abi.AllocatorMode {",
        "pub fn recognizesInteropPolicyByte(allocator_mode: u8) bool {",
        "pub fn requiresExplicitCallerPolicyByte(allocator_mode: u8) bool {",
        "pub fn permitsGlobalFallbackPolicyByte(allocator_mode: u8) bool {",
        "pub fn initializesOwnedStatePolicyByte(allocator_mode: u8) bool {",
        "pub fn requiresResetOnInitPolicyByte(allocator_mode: u8) bool {",
        'test "phase3 allocator policy stays explicit"',
    ),
    "zigux/helpers/interop_policy.zig": (
        "pub fn decode(policy: abi.InteropPolicy) DecodeError!DecodedInteropPolicy {",
        "pub fn recognizes(policy: abi.InteropPolicy) bool {",
        'test "phase3 interop policy decoder keeps the boundary typed"',
        'test "phase3 interop policy decoder rejects invalid bytes and reserved bits"',
    ),
    "zigux/helpers/atomic.zig": (
        "pub fn load(comptime T: type, ptr: *const T, comptime order: std.builtin.AtomicOrder) T {",
        "pub fn compareExchange(",
        'test "phase3 atomic wrappers behave predictably"',
    ),
    "zigux/helpers/barrier.zig": (
        "pub fn acquire() void {",
        "pub fn release() void {",
        "pub fn full() void {",
        'test "phase3 barrier wrappers stay local to each barrier probe"',
    ),
    "zigux/helpers/mmio.zig": (
        "pub fn range(base_addr: usize, length: u32, stride: u32) abi.MmioRange {",
        "pub fn read16Scoped(scope: narrow.UnsafeScopeTag, base_addr: usize, offset: usize) narrow.ScopeError!u16 {",
        "pub fn write16Scoped(",
        "pub fn read32Scoped(scope: narrow.UnsafeScopeTag, base_addr: usize, offset: usize) narrow.ScopeError!u32 {",
        "pub fn write32(base_addr: usize, offset: usize, value: u32) void {",
        'test "phase3 mmio wrapper uses bounded volatile access"',
        'test "phase3 mmio wrapper keeps declared scope explicit across widths"',
        'test "phase3 mmio wrapper rejects misaligned scoped accesses"',
    ),
    "zigux/unsafe/narrow.zig": (
        "pub const UnsafeScopeTag = enum(u8) {",
        "pub fn ensureAddressAlignedFor(comptime T: type, addr: usize) ScopeError!void {",
        "raw_pointer_bridge = 2,",
        'test "phase3 narrow unsafe scope stays explicit"',
        'test "phase3 narrow unsafe scoped helpers reject misaligned addresses"',
    ),
    "zigux/tests/phase3_export_uapi.zig": (
        'test "phase3 export shim and uapi stay aligned"',
        "try std.testing.expectEqual(header, uapi_version.boundaryHeader(0x44));",
        "try std.testing.expect(export_shim.isCanonicalHeader(header));",
        "try std.testing.expect(uapi_version.isCanonical(header));",
    ),
    "zigux/tests/phase3_low_level_wrappers.zig": (
        'test "phase3 low-level wrappers stay inside the documented ABI surface"',
        "atomic.compareExchange(u32, &value, 12, 21, .seq_cst, .seq_cst)",
        "barrier.full();",
        "const desc = mmio.range(base, 12, 4);",
        "try std.testing.expectError(error.UnsafeScopeDenied, mmio.write16Scoped(.none, base, 0, 0x99));",
        "try mmio.write32Scoped(.volatile_mmio, base, 4, 0xaabbccdd);",
        'test "phase3 low-level wrapper ABI range shape stays stable"',
        "layout_assert.assertMmioRangeLayout();",
        'test "phase3 low-level wrappers keep the narrow unsafe scope contract explicit"',
        "try std.testing.expectError(error.MisalignedAccess, narrow.scopedPointerAt(u32, .volatile_mmio, 1, 0));",
    ),
    "zigux/tests/phase3_policy_unsafe.zig": (
        'test "phase3 policy helpers stay ABI aligned"',
        "panic_policy.canReturnPolicyByte(@intFromEnum(abi.PanicMode.warn))",
        "allocator_policy.permitsGlobalFallbackPolicyByte(@intFromEnum(abi.AllocatorMode.kernel_heap))",
        "allocator_policy.requiresResetOnInitPolicyByte(@intFromEnum(abi.AllocatorMode.arena))",
        'test "phase3 policy layout stays explicit at the ABI boundary"',
        "layout_assert.assertInteropPolicyLayout();",
        'test "phase3 policy decoder validates the whole interop record"',
        'test "phase3 policy decoder rejects partial or reserved policy bytes"',
        'test "phase3 narrow unsafe helpers stay explicit"',
        "try std.testing.expectEqual(base + @sizeOf(u32), narrow.byteOffset(base, @sizeOf(u32)));",
        'test "phase3 policy gate decodes interop-policy unsafe bytes explicitly"',
        'test "phase3 policy gate enforces the declared unsafe scope"',
    ),
}
ABI_REQUIRED_EXPECTED_CONSTANTS = {
    "facility_kernel": 1,
    "status_flag_error": 1,
    "panic_abort": 0,
    "allocator_caller_provided": 0,
    "unsafe_scope_raw_pointer_bridge": 2,
}

COMMON_DOC_MARKERS = (
    "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py",
    "PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig",
)

ASSERT_RE = re.compile(r"assert(?:Size|Offset)\(abi\.([A-Za-z0-9_]+),")
DUMP_LAYOUT_RE = re.compile(r'writeLayoutPrefix\(writer,\s*"([^"]+)"')
DUMP_GENERIC_LAYOUT_RE = re.compile(r'writeStructLayout\(writer,\s*"([^"]+)"')
EXPECTED_LAYOUT_RE = re.compile(r'\\"(zigux_[a-z0-9_]+)\\":\{\\\"size\\\":%zu')
HARNESS_GENERIC_LAYOUT_RE = re.compile(r'\{"(zigux_[a-z0-9_]+)",\s*sizeof\(struct')


def select_slices(entries: list[Phase3Slice], selected_slugs: list[str]) -> list[Phase3Slice]:
    slices = list(entries)
    selected = set(selected_slugs)
    if selected:
        slices = [entry for entry in slices if entry.slug in selected]
        missing = sorted(selected.difference({entry.slug for entry in slices}))
        if missing:
            raise SystemExit(f"unknown Phase 3 slugs: {', '.join(missing)}")
    return slices


def _missing_markers(path: Path, markers: tuple[str, ...]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return [marker for marker in markers if marker not in text]


def validate_manifest(entry: Phase3Slice, required_files: tuple[str, ...] = ()) -> list[str]:
     issues: list[str] = []
    if entry.manifest_path is None or not entry.manifest_path.exists():
        return [f"{entry.slug}: missing manifest for discovered slice"]

    try:
        manifest = json.loads(entry.manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{entry.slug}: invalid manifest json in {entry.manifest_path.relative_to(entry.root)}: {exc}"]

    files = manifest.get("files")
    if not isinstance(files, list):
        return [f"{entry.slug}: manifest files list missing in {entry.manifest_path.relative_to(entry.root)}"]

    expected_core_files = (
        entry.doc_path.relative_to(entry.root).as_posix(),
        entry.dump_path.relative_to(entry.root).as_posix(),
        entry.expected_path.relative_to(entry.root).as_posix()