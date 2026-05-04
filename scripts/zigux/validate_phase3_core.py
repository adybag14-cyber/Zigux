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
ABI_EXPORT_UAPI_LAYOUT_BUILD_FILE_REL = "zigux/tests/phase3_export_uapi_layout_build.zig"
ABI_EXPORT_UAPI_LAYOUT_TEST_REL = "zigux/tests/phase3_export_uapi_layout.zig"
ABI_POLICY_UNSAFE_BUILD_FILE_REL = "zigux/tests/phase3_policy_unsafe_build.zig"
ABI_LOW_LEVEL_SURVEY_CHECK_REL = "scripts/zigux/validate-phase3-low-level-wrapper-survey.py"
ABI_EXPORT_UAPI_SURVEY_CHECK_REL = "scripts/zigux/validate-phase3-export-uapi-survey.py"
ABI_POLICY_UNSAFE_SURVEY_CHECK_REL = "scripts/zigux/validate-phase3-policy-unsafe-survey.py"
ABI_POLICY_UNSAFE_MMIO_CONSUMER_REL = "scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py"
ABI_REQUIRED_MANIFEST_FILES = (
    "include/zigux/abi.h",
    "include/linux/zigux.h",
    "Documentation/zigux/review-checklist.md",
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
    BUILD_FILE_REL,
    ABI_LOW_LEVEL_BUILD_FILE_REL,
    "zigux/tests/phase3_low_level_wrappers.zig",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    ABI_POLICY_UNSAFE_BUILD_FILE_REL,
    "zigux/tests/phase3_policy_unsafe.zig",
    ABI_POLICY_UNSAFE_MMIO_CONSUMER_REL,
    "zigux/tests/phase3_abi.zig",

    "zigux/tests/phase3_rbtree_shared_contract.zig",

    ABI_EXPORT_UAPI_BUILD_FILE_REL,
    "zigux/tests/phase3_export_uapi.zig",
    ABI_EXPORT_UAPI_LAYOUT_BUILD_FILE_REL,
    ABI_EXPORT_UAPI_LAYOUT_TEST_REL,
    "zigux/tests/phase3_abi_dump.zig",
    "zigux/tests/fixtures/phase3_abi/expected.json",
    "zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c",
    "Documentation/zigux/phase3-abi-slice.md",
    "Documentation/zigux/phase3-roadmap-gap-survey.md",
    "Documentation/zigux/phase3-rbtree-interop-survey.md",
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    "scripts/zigux/check-phase3-abi.py",

    "scripts/zigux/check-phase3-abi-layout-packet.py",

    "scripts/zigux/check-phase3-rbtree-shared-lift-contract.py",

    "scripts/zigux/run-phase3-checks.py",
    "scripts/zigux/phase3_check_lib.py",
    "scripts/zigux/validate-phase3-roadmap-gap-survey.py",
    "scripts/zigux/validate-phase3-rbtree-interop-survey.py",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md",
    ABI_POLICY_UNSAFE_SURVEY_CHECK_REL,
    "scripts/zigux/validate_phase3_header_binding_markers.py",
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
    "PHASE3_ATOMIC_SCOPE=load-store-exchange-compare-exchange-compare-exchange-weak-fetch-add-fetch-sub-fetch-and-fetch-or-fetch-xor-fetch-min-fetch-max",
    "PHASE3_BARRIER_SCOPE=acquire-release-acquire-release-combined-full",
    "PHASE3_MMIO_SCOPE=range-read8-read16-read32-read64-write8-write16-write32-write64-plus-scoped-read8-write8-read16-write16-read32-write32-read64-write64-plus-policy-read8-write8-read16-write16-read32-write32-read64-write64-and-generic-policy-bridges",
    "PHASE3_ROADMAP_ANCHORS=rust-exports-lib-bitmap-lib-rbtree-lib-cpumask",
    "PHASE3_CURRENT_INTEROP_FAMILIES=bitmap-cpumask-rbtree-list-hlist-errptr-xarray-idr-ida-minor-alloc-dev-region-cdev-chrdev",
    "PHASE3_CURRENT_INTEROP_FAMILIES_DETAIL=bitmap-cpumask-rbtree-dedicated-boundary-list-hlist-errptr-xarray-idr-ida-minor-alloc-dev-region-cdev-chrdev-notify-ack-window-delivery-guard",
    "PHASE3_CURRENT_INTEROP_GAP=repo-now-carries-curated-phase3-parity-slices-beyond-the-original-roadmap-anchor-set",
    "PHASE3_CURRENT_INTEROP_GAP_DETAIL=live-build-graph-now-carries-deep-chrdev-tail-packets-while-the-shared-phase3-abi-replay-already-covers-rbtree-root-view-through-dedicated-bindings-and-the-curated-shared-abi-h-plus-abi-zig-lift-is-still-missing",
    "PHASE3_NEXT_SAFE_STEP=shared-rbtree-root-view-lift-only-before-any-more-shared-abi-growth",
)

ABI_REVIEW_CHECKLIST_MARKERS = (
    "- if the change touches the shared Phase 3 ABI substrate packet, do `include/zigux/abi.h`, `include/linux/zigux.h`, `zigux/bindings/abi.zig`, `zigux/tests/phase3_abi.zig`, and `zigux/tests/fixtures/phase3_abi/expected.json` still agree on the same canonical boundary layouts, constants, and fixture-backed dump contract?",
    "- if the change touches the shared Phase 3 ABI substrate packet, do `zigux/kernel/export_shim.zig`, `zigux/uapi/version.zig`, `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, and `scripts/zigux/validate-phase3-export-uapi-survey.py` still keep explicit status codes plus canonical-versus-compatible boundary-header checks reviewable in one place?",
    "- if the change touches the shared Phase 3 ABI substrate packet, do `zigux/helpers/panic_policy.zig`, `zigux/helpers/allocator_policy.zig`, `zigux/helpers/interop_policy.zig`, `zigux/helpers/atomic.zig`, `zigux/helpers/barrier.zig`, `zigux/helpers/mmio.zig`, `zigux/unsafe/narrow.zig`, `zigux/tests/phase3_low_level_wrappers.zig`, and `zigux/tests/phase3_policy_unsafe.zig` still keep policy-byte decoding, denied-scope checks, misalignment guards, and overflow guards explicit under the focused replay gates?",
)
PHASE3_SHARED_RBTREE_RECORD_MARKERS = (
    "const empty_root = rbtree.empty();",
    "try std.testing.expect(!rbtree.hasRoot(empty_root));",
    "const cached_root: rbtree.RootView = .{",
    "try std.testing.expect(rbtree.hasRoot(cached_root));",
    "const uncached_root: rbtree.RootView = .{",
    "try std.testing.expect(rbtree.hasRoot(uncached_root));",
)

PHASE3_SHARED_RBTREE_ROOT_MARKERS = (
    "// PHASE3_SHARED_RBTREE_SAMPLE_RECORDS=empty-root,cached-leftmost-root,uncached-root",
    *PHASE3_SHARED_RBTREE_RECORD_MARKERS,
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
        "pub fn isCurrentAbiVersion(version: u16) bool {",
        "pub fn isCompatibleSize(size: u32) bool {",
        "pub fn isCanonicalSize(size: u32) bool {",
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
        "pub fn initializesOwnedState(self: DecodedInteropPolicy) bool {",
        "pub fn requiresResetOnInit(self: DecodedInteropPolicy) bool {",
        'test "phase3 interop policy decoder keeps the boundary typed"',
        'test "phase3 interop policy decoder keeps allocator init requirements explicit"',
        'test "phase3 interop policy decoder rejects invalid bytes and reserved bits"',
    ),
    "zigux/helpers/atomic.zig": (
        "pub fn load(comptime T: type, ptr: *const T, comptime order: std.builtin.AtomicOrder) T {",
        "pub fn fetchMin(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {",
        "pub fn fetchMax(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {",
        "pub fn compareExchange(",
        'test "phase3 atomic wrappers behave predictably"',
    ),
    "zigux/helpers/barrier.zig": (
        "pub fn acquire() void {",
        "pub fn release() void {",
        "pub fn acquireRelease() void {",
        "pub fn full() void {",
        'test "phase3 barrier wrappers stay local to each barrier probe"',
    ),
    "zigux/helpers/mmio.zig": (
        "pub fn range(base_addr: usize, length: u32, stride: u32) abi.MmioRange {",
        "pub fn readScopedWithPolicy(",
        "pub fn writeScopedWithPolicy(",
        "pub fn read16Scoped(scope: narrow.UnsafeScopeTag, base_addr: usize, offset: usize) narrow.ScopeError!u16 {",
        "pub fn write16Scoped(",
        "pub fn read32Scoped(scope: narrow.UnsafeScopeTag, base_addr: usize, offset: usize) narrow.ScopeError!u32 {",
        "pub fn write32Scoped(",
        "pub fn read32Policy(policy: interop_policy.DecodedInteropPolicy, base_addr: usize, offset: usize) narrow.ScopeError!u32 {",
        "pub fn write32Policy(",
        "pub fn read64Scoped(scope: narrow.UnsafeScopeTag, base_addr: usize, offset: usize) narrow.ScopeError!u64 {",
        "pub fn write64Scoped(",
        "pub fn read64Policy(policy: interop_policy.DecodedInteropPolicy, base_addr: usize, offset: usize) narrow.ScopeError!u64 {",
        "pub fn write64Policy(",
        "pub fn read64(base_addr: usize, offset: usize) u64 {",
        "pub fn write64(base_addr: usize, offset: usize, value: u64) void {",
        'test "phase3 mmio wrapper uses bounded volatile access"',
        'test "phase3 mmio wrapper consumes decoded interop policy"',
        'test "phase3 mmio wrapper keeps declared scope explicit across widths"',
        'test "phase3 mmio wrapper rejects misaligned scoped accesses"',
        'test "phase3 mmio wrapper rejects overflowed scoped accesses"',
    ),
    "zigux/unsafe/narrow.zig": (
        "pub const UnsafeScopeTag = enum(u8) {",
        "pub fn ensureAddressAlignedFor(comptime T: type, addr: usize) ScopeError!void {",
        "pub fn checkedSpanEnd(comptime T: type, base: usize, len: usize) ScopeError!usize {",
        "raw_pointer_bridge = 2,",
        'test "phase3 narrow unsafe scope stays explicit"',
        'test "phase3 narrow unsafe scoped helpers reject misaligned addresses"',
        'test "phase3 narrow unsafe scoped helpers reject overflowed address math"',
    ),
    "zigux/tests/phase3_export_uapi.zig": (
        'test "phase3 export shim and uapi stay aligned"',
        "try std.testing.expectEqual(header, uapi_version.boundaryHeader(0x44));",
        "try std.testing.expect(uapi_version.isCurrentAbiVersion(header.abi_version));",
        "try std.testing.expect(uapi_version.isCanonicalSize(header.size));",
        "try std.testing.expect(export_shim.isCanonicalHeader(header));",
        "try std.testing.expect(uapi_version.isCanonical(header));",
        "try std.testing.expect(!uapi_version.isCompatibleSize(undersized_header.size));",
        "try std.testing.expect(!uapi_version.isCurrentAbiVersion(mismatched_version_header.abi_version));",
        "try std.testing.expect(uapi_version.isCompatibleSize(future_compatible_header.size));",
    ),
    "zigux/tests/phase3_export_uapi_build.zig": (
        '.root_source_file = b.path("../kernel/export_shim.zig"),',
        'export_shim_module.addImport("abi_bindings", abi_bindings_module);',
        '.root_source_file = b.path("../uapi/version.zig"),',
        'uapi_version_module.addImport("abi_bindings", abi_bindings_module);',
        '.root_source_file = b.path("phase3_export_uapi.zig"),',
        'export_shim_module.addImport("uapi_version", uapi_version_module);',
        'root_module.addImport("abi_bindings", abi_bindings_module);',
        'root_module.addImport("export_shim", export_shim_module);',
        'root_module.addImport("uapi_version", uapi_version_module);',
        '"phase3-export-uapi-test",',
    ),
    "zigux/tests/phase3_low_level_wrappers.zig": (
        'test "phase3 low-level wrappers stay inside the documented ABI surface"',
        "atomic.fetchSub(u32, &value, 4, .seq_cst)",
        "atomic.fetchOr(u32, &value, 0b1000, .seq_cst)",
        "atomic.fetchAnd(u32, &value, 0b0111, .seq_cst)",
        "atomic.fetchXor(u32, &value, 0b1111, .seq_cst)",
        "atomic.fetchMax(u32, &value, 29, .seq_cst)",
        "atomic.fetchMin(u32, &value, 17, .seq_cst)",
        "atomic.compareExchange(u32, &value, 12, 21, .seq_cst, .seq_cst)",
        "const weak_mismatch = atomic.compareExchangeWeak(u32, &weak_value, 31, 55, .seq_cst, .seq_cst);",
        "barrier.acquireRelease();",
        "barrier.full();",
        "const desc = mmio.range(base, 12, 4);",
        "try std.testing.expectError(error.UnsafeScopeDenied, mmio.write16Scoped(.none, base, 0, 0x99));",
        "try mmio.write32Scoped(.volatile_mmio, base, 4, 0xaabbccdd);",
        "try std.testing.expectError(error.AddressOverflow, mmio.write8Scoped(.volatile_mmio, std.math.maxInt(usize), 1, 0x99));",
        "try std.testing.expectError(error.AddressOverflow, mmio.read32Scoped(.volatile_mmio, std.math.maxInt(usize), 4));",
        "mmio.write64(base64, @sizeOf(u64), 0x0123_4567_89ab_cdef);",
        "try std.testing.expectError(error.UnsafeScopeDenied, mmio.write64Scoped(.none, base64, 0, 0x99));",
        "try std.testing.expectError(error.MisalignedAccess, mmio.write64Scoped(.volatile_mmio, base64, 4, 0x99));",
        "try std.testing.expectError(error.AddressOverflow, mmio.write64Scoped(.volatile_mmio, std.math.maxInt(usize), 8, 0x99));",
        "try mmio.write64Scoped(.volatile_mmio, base64, 0, 0xfedc_ba98_7654_3210);",
        "try std.testing.expectEqual(@as(u64, 0xfedc_ba98_7654_3210), try mmio.read64Scoped(.volatile_mmio, base64, 0));",
        "try mmio.write64Policy(mmio_policy, base64, @sizeOf(u64), 0x1111_2222_3333_4444);",
        "try std.testing.expectEqual(@as(u64, 0x1111_2222_3333_4444), try mmio.read64Policy(mmio_policy, base64, @sizeOf(u64)));",
        "try std.testing.expectError(error.UnsafeScopeDenied, mmio.write64Policy(raw_pointer_policy, base64, 0, 1));",
        'test "phase3 low-level wrapper ABI range shape stays stable"',
        'test "phase3 low-level wrappers keep the narrow unsafe scope contract explicit"',
    ),
    "zigux/tests/phase3_policy_unsafe.zig": (
        'test "phase3 policy helpers stay ABI aligned"',
        "panic_policy.canReturnPolicyByte(@intFromEnum(abi.PanicMode.warn))",
        "allocator_policy.permitsGlobalFallbackPolicyByte(@intFromEnum(abi.AllocatorMode.kernel_heap))",
        "allocator_policy.initializesOwnedStatePolicyByte(@intFromEnum(abi.AllocatorMode.kernel_heap))",
        "allocator_policy.requiresResetOnInitPolicyByte(@intFromEnum(abi.AllocatorMode.arena))",
        'test "phase3 policy decoder validates the whole interop record"',
        'test "phase3 policy decoder keeps allocator init and reset requirements reviewable"',
        'test "phase3 policy decoder rejects partial or reserved policy bytes"',
        "try std.testing.expectError(error.InvalidPanicMode, interop_policy.decode(.{",
        "try std.testing.expectError(error.InvalidAllocatorMode, interop_policy.decode(.{",
        'test "phase3 policy gate decodes interop-policy unsafe bytes explicitly"',
        "const invalid_scope_policy = abi.InteropPolicy{",
        "const reserved_policy = abi.InteropPolicy{",
        "try std.testing.expect(!narrow.recognizesInteropPolicyBytes(invalid_scope_policy.unsafe_scope, invalid_scope_policy.reserved));",
        "try std.testing.expect(!narrow.recognizesInteropPolicyBytes(reserved_policy.unsafe_scope, reserved_policy.reserved));",
        'test "phase3 policy gate enforces the declared unsafe scope"',
        "try std.testing.expectError(error.UnsafeScopeDenied, narrow.scopedPointerAt(u32, .none, base, 0));",
        "try std.testing.expectError(error.UnsafeScopeDenied, narrow.scopedConstSliceAt(u32, .volatile_mmio, base, 1));",
        "try std.testing.expectError(error.UnsafeScopeDenied, narrow.scopedConstPointerAt(u32, .volatile_mmio, base));",
        'test "phase3 policy gate rejects overflowed unsafe address math"',
        "try std.testing.expectError(error.AddressOverflow, narrow.checkedByteOffset(max, 1));",
        "try std.testing.expectError(error.AddressOverflow, narrow.checkedSpanBytes(u32, max));",
        "try std.testing.expectError(error.AddressOverflow, narrow.checkedSpanEnd(u32, 4, max));",
        "try std.testing.expectError(error.AddressOverflow, narrow.scopedPointerAt(u32, .volatile_mmio, max, 1));",
        "try std.testing.expectError(error.AddressOverflow, narrow.scopedConstSliceAt(u32, .raw_pointer_bridge, 4, max));",
    ),
    "zigux/tests/phase3_policy_unsafe_build.zig": (
        '.root_source_file = b.path("phase3_policy_unsafe.zig"),',
        'root_module.addImport("panic_policy", panic_policy_module);',
        'root_module.addImport("allocator_policy", allocator_policy_module);',
        'root_module.addImport("layout_assert", layout_assert_module);',
        'root_module.addImport("narrow_unsafe", narrow_unsafe_module);',
        '"phase3-policy-unsafe-test",',
    ),
    "zigux/tests/phase3_abi.zig": (
        'test "phase3 abi slice uses stable canonical layouts" {',
        "layout_assert.assertMmioRangeLayout();",
        'test "phase3 abi slice keeps explicit constants and statuses reviewable" {',
        "try std.testing.expectEqual(@as(u8, 2), @intFromEnum(abi.UnsafeScope.raw_pointer_bridge));",
        'test "phase3 abi slice keeps the boundary helpers constructible" {',
        "try std.testing.expect(export_shim.isCanonicalHeader(header));",
        "try std.testing.expect(uapi_version.isCanonical(header));",
        "try std.testing.expectEqual(panic_policy.Action.abort_now, panic_policy.actionFor(.abort));",
        "try std.testing.expect(allocator_policy.requiresExplicitCaller(.caller_provided));",
        "const range = mmio.range(0x1000, 0x40, 4);",
        "try std.testing.expectEqual(narrow.UnsafeScopeTag.raw_pointer_bridge, narrow.scopeFromInteropPolicyBytes(2, 0).?);",
        *PHASE3_SHARED_RBTREE_ROOT_MARKERS,
    ),
}
ABI_REQUIRED_EXPECTED_CONSTANTS = {
    "facility_kernel": 1,
    "status_flag_error": 1,
    "panic_abort": 0,
    "panic_bug": 1,
    "panic_warn": 2,
    "allocator_caller_provided": 0,
    "allocator_kernel_heap": 1,
    "allocator_arena": 2,
    "unsafe_scope_none": 0,
    "unsafe_scope_volatile_mmio": 1,
    "unsafe_scope_raw_pointer_bridge": 2,
}

COMMON_DOC_MARKERS = (
    "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py",
    "PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig",
)
LOW_LEVEL_WRAPPER_EXPORTS = {
    "zigux/helpers/atomic.zig": (
        "load",
        "store",
        "exchange",
        "fetchAdd",
        "fetchSub",
        "fetchAnd",
        "fetchOr",
        "fetchXor",
        "fetchMin",
        "fetchMax",
        "compareExchange",
        "compareExchangeWeak",
    ),
    "zigux/helpers/barrier.zig": (
        "acquire",
        "release",
        "acquireRelease",
        "full",
    ),
    "zigux/helpers/mmio.zig": (
        "range",
        "readScopedWithPolicy",
        "writeScopedWithPolicy",
        "read8Scoped",
        "write8Scoped",
        "read16Scoped",
        "write16Scoped",
        "read32Scoped",
        "write32Scoped",
        "read64Scoped",
        "write64Scoped",
        "read8Policy",
        "write8Policy",
        "read16Policy",
        "write16Policy",
        "read32Policy",
        "write32Policy",
        "read64Policy",
        "write64Policy",
        "read8",
        "write8",
        "read16",
        "write16",
        "read32",
        "write32",
        "read64",
        "write64",
    ),
}

def _phase3_paths_for_root(root: Path) -> Phase3Paths:
    return Phase3Paths(
        root=root,
        docs_dir=root / "Documentation" / "zigux",
        scripts_dir=root / "scripts" / "zigux",
        tests_dir=root / "zigux" / "tests",
        fixtures_dir=root / "zigux" / "tests" / "fixtures",
    )

ASSERT_RE = re.compile(r"assert(?:Size|Offset)\(abi\.([A-Za-z0-9_]+),")
DUMP_LAYOUT_RE = re.compile(r'writeLayoutPrefix\(writer,\s*"([^"]+)"')
DUMP_GENERIC_LAYOUT_RE = re.compile(r'writeStructLayout\(writer,\s*"([^"]+)"')
EXPECTED_LAYOUT_RE = re.compile(r'\\"(zigux_[a-z0-9_]+)\\":\{\\\"size\\\":%zu')
HARNESS_GENERIC_LAYOUT_RE = re.compile(r'\{"(zigux_[a-z0-9_]+)",\s*sizeof\(struct')
PUB_FN_RE = re.compile(r"^pub fn ([A-Za-z0-9_]+)\(", re.MULTILINE)


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
        entry.expected_path.relative_to(entry.root).as_posix(),
        entry.harness_path.relative_to(entry.root).as_posix(),
    )
    listed = set(files)
    for rel in (*expected_core_files, *required_files):
        if rel not in listed:
            issues.append(f"{entry.slug}: manifest missing {rel}")
    for rel in files:
        if not (entry.root / rel).exists():
            issues.append(f"{entry.slug}: manifest references missing file {rel}")
    file_count = manifest.get("file_count")
    if file_count != len(files):
        issues.append(f"{entry.slug}: manifest file_count {file_count!r} does not match listed files {len(files)}")
    if manifest.get("phase") != "Phase 3":
        issues.append(f"{entry.slug}: manifest phase is {manifest.get('phase')!r}, expected 'Phase 3'")
    return issues


def validate_source_markers(root: Path, required_source_markers: dict[str, tuple[str, ...]]) -> list[str]:
    issues: list[str] = []
    for rel, markers in required_source_markers.items():
        path = root / rel
        if not path.exists():
            issues.append(f"source-marker: missing {rel}")
            continue
        for marker in _missing_markers(path, markers):
            issues.append(f"source-marker: {rel} missing {marker}")
    return issues


def validate_low_level_wrapper_exports(
    root: Path, required_exports: dict[str, tuple[str, ...]] = LOW_LEVEL_WRAPPER_EXPORTS
) -> list[str]:
    issues: list[str] = []
    for rel, expected_exports in required_exports.items():
        path = root / rel
        if not path.exists():
            issues.append(f"low-level-export: missing {rel}")
            continue
        actual_exports = tuple(PUB_FN_RE.findall(path.read_text(encoding="utf-8")))
        unexpected = [name for name in actual_exports if name not in expected_exports]
        missing = [name for name in expected_exports if name not in actual_exports]
        if unexpected:
            issues.append(f"low-level-export: {rel} exports unexpected public helpers: {', '.join(unexpected)}")
        if missing:
            issues.append(f"low-level-export: {rel} is missing documented public helpers: {', '.join(missing)}")
    return issues


def validate_export_uapi_boundary(root: Path) -> list[str]:
    check_path = root / ABI_EXPORT_UAPI_SURVEY_CHECK_REL
    if not check_path.exists():
        return [f"export-uapi-gate: missing {ABI_EXPORT_UAPI_SURVEY_CHECK_REL}"]

    result = subprocess.run(
        ["python3", str(check_path)],
        cwd=str(root),
        text=True,
        capture_output=True,
    )
    if result.returncode == 0:
        return []

    issues: list[str] = []
    for line in result.stdout.splitlines():
        stripped = line.strip()
        if not stripped or stripped == "PHASE3_EXPORT_UAPI_SURVEY=fail":
            continue
        issues.append(f"export-uapi-gate: {stripped}")
    stderr = result.stderr.strip()
    if stderr:
        issues.append(f"export-uapi-gate: stderr: {stderr.splitlines()[-1]}")
    if not issues:
        issues.append(
            f"export-uapi-gate: {ABI_EXPORT_UAPI_SURVEY_CHECK_REL} exited with status {result.returncode}"
        )
    return issues


def validate_low_level_wrapper_boundary(root: Path) -> list[str]:
    check_path = root / ABI_LOW_LEVEL_SURVEY_CHECK_REL
    if not check_path.exists():
        return [f"low-level-wrapper-survey-gate: missing {ABI_LOW_LEVEL_SURVEY_CHECK_REL}"]

    result = subprocess.run(
        ["python3", str(check_path)],
        cwd=str(root),
        text=True,
        capture_output=True,
    )
    if result.returncode == 0:
        return []

    issues: list[str] = []
    for line in result.stdout.splitlines():
        stripped = line.strip()
        if not stripped or stripped == "PHASE3_LOW_LEVEL_WRAPPER_SURVEY=fail":
            continue
        issues.append(f"low-level-wrapper-survey-gate: {stripped}")
    stderr = result.stderr.strip()
    if stderr:
        issues.append(f"low-level-wrapper-survey-gate: stderr: {stderr.splitlines()[-1]}")
    if not issues:
        issues.append(
            f"low-level-wrapper-survey-gate: {ABI_LOW_LEVEL_SURVEY_CHECK_REL} exited with status {result.returncode}"
        )
    return issues


def validate_policy_unsafe_boundary(root: Path) -> list[str]:
    check_path = root / ABI_POLICY_UNSAFE_SURVEY_CHECK_REL
    if not check_path.exists():
        return [f"policy-unsafe-gate: missing {ABI_POLICY_UNSAFE_SURVEY_CHECK_REL}"]

    result = subprocess.run(
        ["python3", str(check_path)],
        cwd=str(root),
        text=True,
        capture_output=True,
    )
    if result.returncode == 0:
        return []

    issues: list[str] = []
    for line in result.stdout.splitlines():
        stripped = line.strip()
        if not stripped or stripped == "PHASE3_POLICY_UNSAFE_SURVEY=fail":
            continue
        issues.append(f"policy-unsafe-gate: {stripped}")
    stderr = result.stderr.strip()
    if stderr:
        issues.append(f"policy-unsafe-gate: stderr: {stderr.splitlines()[-1]}")
    if not issues:
        issues.append(
            f"policy-unsafe-gate: {ABI_POLICY_UNSAFE_SURVEY_CHECK_REL} exited with status {result.returncode}"
        )
    return issues


def _asserted_abi_layout_count(root: Path) -> int:
    text = (root / "zigux/tests/phase3_abi.zig").read_text(encoding="utf-8")
    names: list[str] = []
    seen: set[str] = set()
    for name in ASSERT_RE.findall(text):
        if name not in seen:
            seen.add(name)
            names.append(name)
    asserted = len(names)
    if "assertBoundaryHeaderLayout()" in text:
        asserted += 1
    if "assertExportStatusLayout()" in text:
        asserted += 1
    if "assertInteropPolicyLayout()" in text:
        asserted += 1
    return asserted


def _dump_layout_keys(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    keys = DUMP_LAYOUT_RE.findall(text)
    if keys:
        return keys
    return DUMP_GENERIC_LAYOUT_RE.findall(text)


def _harness_layout_keys(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    keys = EXPECTED_LAYOUT_RE.findall(text)
    if keys:
        return keys
    return HARNESS_GENERIC_LAYOUT_RE.findall(text)


def validate_abi_expected_fixture(root: Path) -> list[str]:
    issues: list[str] = []
    expected_path = root / "zigux/tests/fixtures/phase3_abi/expected.json"
    dump_path = root / "zigux/tests/phase3_abi_dump.zig"
    harness_path = root / "zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c"

    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    if expected.get("abi_version") != 1:
        issues.append(f"abi-fixture: expected abi_version 1, found {expected.get('abi_version')!r}")

    constants = expected.get("constants")
    if not isinstance(constants, dict):
        issues.append("abi-fixture: constants object missing from expected.json")
    else:
        for key, value in ABI_REQUIRED_EXPECTED_CONSTANTS.items():
            if constants.get(key) != value:
                issues.append(f"abi-fixture: constant {key} is {constants.get(key)!r}, expected {value!r}")

    structs = expected.get("structs")
    if not isinstance(structs, dict):
        return [*issues, "abi-fixture: structs object missing from expected.json"]

    expected_keys = list(structs.keys())
    dump_keys = _dump_layout_keys(dump_path)
    harness_keys = _harness_layout_keys(harness_path)
    asserted_count = _asserted_abi_layout_count(root)

    if len(expected_keys) != len(dump_keys):
        issues.append(
            f"abi-fixture: expected.json tracks {len(expected_keys)} layouts but phase3_abi_dump.zig emits {len(dump_keys)}"
        )
    if len(expected_keys) != len(harness_keys):
        issues.append(
            f"abi-fixture: expected.json tracks {len(expected_keys)} layouts but phase3_abi_c_harness.c emits {len(harness_keys)}"
        )
    if len(dump_keys) < asserted_count:
        issues.append(
            f"abi-fixture: phase3_abi_dump.zig only emits {len(dump_keys)} layouts while phase3_abi.zig asserts {asserted_count}"
        )
    if set(expected_keys) != set(dump_keys):
        issues.append("abi-fixture: expected.json and phase3_abi_dump.zig layout keys drift")
    if set(expected_keys) != set(harness_keys):
        issues.append("abi-fixture: expected.json and phase3_abi_c_harness.c layout keys drift")
    return issues


def validate_phase3_review_checklist(root: Path) -> list[str]:
    checklist_path = root / "Documentation/zigux/review-checklist.md"
    return [
        f"review-checklist: missing {marker}"
        for marker in _missing_markers(checklist_path, ABI_REVIEW_CHECKLIST_MARKERS)
    ]


def _validate_slice_docs(entry: Phase3Slice) -> list[str]:
    issues: list[str] = []
    doc_markers = list(COMMON_DOC_MARKERS)
    doc_markers.append(shared_runner_gate_for_slug(entry.slug))
    if entry.slug == "abi":
        doc_markers.extend(ABI_REQUIRED_DOC_MARKERS)
    for marker in _missing_markers(entry.doc_path, tuple(doc_markers)):
        issues.append(f"{entry.slug}: documentation missing {marker}")
    if entry.interop_gate != shared_runner_gate_for_slug(entry.slug):
        issues.append(f"{entry.slug}: documentation interop gate drifted from shared runner")
    return issues


def _validate_wrapper_stub(entry: Phase3Slice) -> list[str]:
    if not entry.check_script.exists():
        return [f"{entry.slug}: missing wrapper {entry.check_script.relative_to(entry.root)}"]
    if entry.check_script.read_text(encoding="utf-8") != render_wrapper_stub():
        return [f"{entry.slug}: wrapper {entry.check_script.relative_to(entry.root)} drifted from shared stub"]
    return []


def _validate_build_smoke(root: Path, entry: Phase3Slice, zig_path: str | None) -> list[str]:
    zig = find_zig(zig_path)
    issues: list[str] = []
    for build_step, build_file_rel in build_smoke_commands(entry):
        result = subprocess.run(
            [zig, "build", build_step, "--build-file", str(root / build_file_rel)],
            cwd=str(root),
            text=True,
            capture_output=True,
        )
        if result.returncode == 0:
            continue
        stderr = result.stderr.strip().splitlines()
        tail = stderr[-1] if stderr else f"exit {result.returncode}"
        issues.append(f"{entry.slug}: build smoke failed for {build_step}: {tail}")
    return issues


def build_smoke_commands(entry: Phase3Slice) -> tuple[tuple[str, str], ...]:
    if entry.slug == "abi":
        return (
            (entry.build_step, BUILD_FILE_REL),
            ("phase3-test", BUILD_FILE_REL),
            ("phase3-low-level-wrappers-test", ABI_LOW_LEVEL_BUILD_FILE_REL),
            ("phase3-export-uapi-test", ABI_EXPORT_UAPI_BUILD_FILE_REL),
            ("phase3-export-uapi-layout-test", ABI_EXPORT_UAPI_LAYOUT_BUILD_FILE_REL),
            ("phase3-policy-unsafe-test", ABI_POLICY_UNSAFE_BUILD_FILE_REL),
        )
    return ((entry.build_step, BUILD_FILE_REL),)


def validate_slices(
    root: Path,
    slices: list[Phase3Slice],
    *,
    check_artifact_diff: bool,
    check_build_smoke: bool,
    check_slug_sanity: bool,
    check_all_wrappers: bool,
    zig_path: str | None,
) -> list[str]:
    issues: list[str] = []
    catalog_entries = discover_phase3_slices(_phase3_paths_for_root(root))
    validating_full_catalog = {entry.slug for entry in slices} == {entry.slug for entry in catalog_entries}
    for entry in slices:
        for path in (entry.doc_path, entry.dump_path, entry.expected_path, entry.harness_path):
            if not path.exists():
                issues.append(f"{entry.slug}: missing {path.relative_to(root)}")
        issues.extend(_validate_slice_docs(entry))
        issues.extend(validate_manifest(entry, ABI_REQUIRED_MANIFEST_FILES if entry.slug == "abi" else ()))
        if check_all_wrappers:
            issues.extend(_validate_wrapper_stub(entry))
        if entry.slug == "abi":
            issues.extend(validate_source_markers(root, ABI_REQUIRED_SOURCE_MARKERS))
            issues.extend(validate_low_level_wrapper_exports(root))
            issues.extend(validate_abi_expected_fixture(root))
            issues.extend(validate_phase3_review_checklist(root))
            issues.extend(validate_export_uapi_boundary(root))
            issues.extend(validate_low_level_wrapper_boundary(root))
            issues.extend(validate_policy_unsafe_boundary(root))
        if check_build_smoke:
            issues.extend(_validate_build_smoke(root, entry, zig_path))

    if check_slug_sanity:
        issues.extend(f"slug-sanity: {issue.to_row()}" for issue in audit_phase3_slug_sanity(slices))

    if check_all_wrappers:
        for issue in audit_phase3_doc_sync(slices, _phase3_paths_for_root(root)):
            if issue.code == "artifact-diff-phase3-stale" and not (check_artifact_diff or validating_full_catalog):
                continue
            issues.append(f"doc-sync: {issue.to_row()}")
    elif check_artifact_diff and artifact_diff_phase3_section_needs_rewrite(
        catalog_entries, root / "Documentation/zigux/artifact-diff.md"
    ):
        issues.append("doc-sync: Documentation/zigux/artifact-diff.md Phase 3 section is stale")

    return issues
