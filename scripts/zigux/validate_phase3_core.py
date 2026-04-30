#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import tempfile

from phase3_catalog import (
    Phase3Paths,
    audit_phase3_slug_sanity,
    artifact_diff_phase3_lines,
    discover_phase3_slug_rename_candidates,
    discover_phase3_slices,
)
from phase3_check_lib import (
    build_step_for_slug as runner_build_step_for_slug,
    description_for_slug as runner_description_for_slug,
    find_zig,
    legacy_wrapper_gate_for_slug,
    render_wrapper_stub,
    shared_runner_gate_for_slug,
)


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
        'test "phase3 panic policy stays explicit"',
    ),
    "zigux/helpers/allocator_policy.zig": (
        "pub fn initFlowFor(mode: abi.AllocatorMode) InitFlow {",
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
        "pub fn store(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) void {",
        "pub fn exchange(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {",
        "pub fn fetchAdd(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {",
        "pub fn fetchSub(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {",
        "pub fn fetchAnd(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {",
        "pub fn fetchOr(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {",
        "pub fn fetchXor(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {",
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
        "try std.testing.expectError(error.MisalignedAccess, scopedConstSliceAt(u32, .raw_pointer_bridge, base + 1, 1));",
    ),
    "zigux/tests/phase3_export_uapi.zig": (
        'test "phase3 export shim and uapi stay aligned"',
        "try std.testing.expectEqual(header, uapi_version.boundaryHeader(0x44));",
        "try std.testing.expect(export_shim.isCanonicalHeader(header));",
        "try std.testing.expect(uapi_version.isCanonical(header));",
        "try std.testing.expect(!export_shim.isCompatibleHeader(undersized_header));",
        "try std.testing.expect(!uapi_version.isCompatible(mismatched_version_header));",
        "try std.testing.expect(!export_shim.isCanonicalHeader(future_compatible_header));",
        "try std.testing.expect(!uapi_version.isCanonical(future_compatible_header));",
        "try std.testing.expect(export_shim.isCompatibleHeader(future_compatible_header));",
        "try std.testing.expect(uapi_version.isCompatible(future_compatible_header));",
        "try std.testing.expectEqual(abi.ABI_VERSION, uapi_version.abi_version);",
    ),
    "zigux/tests/phase3_low_level_wrappers.zig": (
        'test "phase3 low-level wrappers stay inside the documented ABI surface"',
        'test "phase3 low-level wrapper ABI range shape stays stable"',
        'test "phase3 low-level wrappers keep the narrow unsafe scope contract explicit"',
        "atomic.fetchSub(u32, &value, 4, .seq_cst)",
        "atomic.compareExchange(u32, &value, 12, 21, .seq_cst, .seq_cst)",
        "atomic.fetchOr(u32, &value, 0b1000, .seq_cst)",
        "atomic.fetchAnd(u32, &value, 0b0111, .seq_cst)",
        "atomic.fetchXor(u32, &value, 0b1111, .seq_cst)",
        "const mismatch = atomic.compareExchange(u32, &value, 9, 19, .seq_cst, .seq_cst);",
        "barrier.acquire();",
        "barrier.release();",
        "barrier.full();",
        "const desc = mmio.range(base, 12, 4);",
        "mmio.write16(base, 2, 0xabcd);",
        "mmio.read16(base, 2)",
        "mmio.write32(base, 8, 0x12345678);",
        "mmio.read32(base, 8)",
        "try std.testing.expectError(error.UnsafeScopeDenied, mmio.write16Scoped(.none, base, 0, 0x99));",
        "try std.testing.expectError(error.UnsafeScopeDenied, mmio.read32Scoped(.raw_pointer_bridge, base, 0));",
        "try std.testing.expectError(error.MisalignedAccess, mmio.write16Scoped(.volatile_mmio, base, 1, 0x99));",
        "try std.testing.expectError(error.MisalignedAccess, mmio.read16Scoped(.volatile_mmio, base, 1));",
        "try std.testing.expectError(error.MisalignedAccess, mmio.write32Scoped(.volatile_mmio, base, 2, 0x99));",
        "try std.testing.expectError(error.MisalignedAccess, mmio.read32Scoped(.volatile_mmio, base, 2));",
        "mmio.write16Scoped(.volatile_mmio, base, 0, 0xbeef);",
        "mmio.read16Scoped(.volatile_mmio, base, 0)",
        "try mmio.write32Scoped(.volatile_mmio, base, 4, 0xaabbccdd);",
        "mmio.read32Scoped(.volatile_mmio, base, 4)",
    ),
    "zigux/tests/phase3_policy_unsafe.zig": (
        'test "phase3 policy helpers stay ABI aligned"',
        'test "phase3 policy decoder validates the whole interop record"',
        'test "phase3 policy decoder rejects partial or reserved policy bytes"',
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
LIST_HLIST_REQUIRED_DOC_MARKERS = (
    "PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug list-hlist",
    "PHASE3_LIST_HLIST_BOUNDARY=descriptor-only-no-container-of-no-lockless-no-rcu-no-notifier-chains",
)


def _required_manifest_files_for_slug(slug: str) -> tuple[str, ...]:
    return ABI_REQUIRED_MANIFEST_FILES if slug == "abi" else ()


def _required_doc_markers_for_slug(slug: str) -> tuple[str, ...]:
    if slug == "abi":
        return ABI_REQUIRED_DOC_MARKERS
    if slug == "list-hlist":
        return LIST_HLIST_REQUIRED_DOC_MARKERS
    return ()


def _required_source_markers_for_slug(slug: str) -> dict[str, tuple[str, ...]]:
    return ABI_REQUIRED_SOURCE_MARKERS if slug == "abi" else {}


def _has_build_step(build_file: Path, step_name: str) -> bool:
    return re.search(r'b\.step\(\s*"' + re.escape(step_name) + r'"', build_file.read_text(encoding="utf-8")) is not None
