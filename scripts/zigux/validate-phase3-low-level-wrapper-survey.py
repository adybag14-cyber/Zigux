#!/usr/bin/env python3
"""Fail-close the current Phase 3 low-level wrapper survey packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


NOTE_PATH = Path("Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")
ATOMIC_PATH = Path("zigux/helpers/atomic.zig")
BARRIER_PATH = Path("zigux/helpers/barrier.zig")
MMIO_PATH = Path("zigux/helpers/mmio.zig")
UNSAFE_POLICY_PATH = Path("zigux/helpers/unsafe_policy.zig")
NARROW_PATH = Path("zigux/unsafe/narrow.zig")
LAYOUT_ASSERT_PATH = Path("zigux/helpers/layout_assert.zig")
WRAPPER_REPLAY_PATH = Path("zigux/tests/phase3_low_level_wrappers.zig")
WRAPPER_BUILD_PATH = Path("zigux/tests/phase3_low_level_wrappers_build.zig")
SHARED_TESTS_README_PATH = Path("zigux/tests/README.md")
SHARED_TESTS_BUILD_PATH = Path("zigux/tests/build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
SELFTEST_SURFACE_PATH = Path("scripts/zigux/check-phase3-selftest-surface.py")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

CURRENT_MANIFEST_SCOPE = (
    "shared ABI bindings, directly coupled helper decoding, header-family "
    "follow-through, notifier layouts, export-status layout, and "
    "header-compatibility replay"
)
CURRENT_NEXT_SAFE_STEP = (
    "keep the shared Phase 3 policy, export/UAPI, and low-level wrapper packet "
    "aligned with the dedicated replay routes and only reopen this manifest if the "
    "checker, focused builds, or reminder surfaces drift again"
)

REQUIRED_MARKERS = {
    NOTE_PATH: (
        "PHASE3_LOW_LEVEL_WRAPPER_SCOPE=the roadmap and bootstrap ledger still reserve a bounded Phase 3 low-level wrapper family for approved atomic, barrier, and MMIO wrappers, and current master now directly exposes one atomic helper shard, one barrier helper companion, one MMIO helper companion, one directly readable unsafe-policy companion, one shared narrow-unsafe decoder plus directly readable interop-policy raw-pointer bridge entrypoints, this dedicated survey note, a dedicated survey validator, one focused low-level-wrapper replay shard, one dedicated shared build companion, one shared tests-root reminder, one workflow-backed replay route, and two returned shared Makefile replay gates",
        "PHASE3_LOW_LEVEL_WRAPPER_GAP=direct current-head readback reaches Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md, zigux/helpers/atomic.zig, zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/helpers/unsafe_policy.zig, zigux/unsafe/narrow.zig, scripts/zigux/validate-phase3-low-level-wrapper-survey.py, zigux/tests/phase3_low_level_wrappers.zig, zigux/tests/phase3_low_level_wrappers_build.zig, zigux/tests/README.md, zigux/tests/build.zig, zigux/Makefile, and .github/workflows/zigux-bootstrap.yml; adjacent shared Phase 3 validator, shared ABI checker, shared ABI catalog helper, export/UAPI survey-validator, and catalog-selftest guard surfaces now read separately on current master, while the low-level-wrapper packet stays bounded to its own helper-local evidence",
        "PHASE3_LOW_LEVEL_WRAPPER_NEXT_STEP=keep low-level wrapper follow-through bounded to shared validation truthfulness around the directly coupled unsafe-policy companion, the shared narrow-unsafe interop-policy bridge entrypoints, the dedicated build companion, the shared tests-root reminder, the workflow-backed low-level-wrapper replay route, the direct zig build phase3-low-level-wrappers replay route, the direct zig build phase3-low-level-wrappers-test replay route, and the returned Makefile replay gates while the adjacent catalog-selftest guard stays outside this wrapper packet",
        "`zigux/helpers/atomic.zig`",
        "`zigux/helpers/barrier.zig`",
        "`zigux/helpers/mmio.zig`",
        "`zigux/helpers/unsafe_policy.zig`",
        "`zigux/unsafe/narrow.zig`",
        "`scripts/zigux/validate-phase3-low-level-wrapper-survey.py`",
        "`zigux/tests/phase3_low_level_wrappers.zig`",
        "`zigux/tests/phase3_low_level_wrappers_build.zig`",
        "`zigux/tests/README.md`",
        "`zigux/tests/build.zig`",
        "`zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig`",
        "`zigux/Makefile`",
        "`make -C zigux phase3-low-level-wrappers`",
        "`zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig`",
        "`make -C zigux phase3-low-level-wrappers-test`",
        "`scripts/zigux/check-phase3-selftest-surface.py`",
        "`scripts/zigux/generate-phase3-check-wrappers.py`",
        "`scripts/zigux/check-phase3-wrapper-templates.py`",
        "Current `master` also keeps `zigux/Makefile`, `make -C zigux phase3-low-level-wrappers`, and `make -C zigux phase3-low-level-wrappers-test` explicit beside the dedicated shared build companion, so the low-level-wrapper packet now has both the direct Zig replay commands and the returned shared Makefile replay gates without widening into broader Phase 3 completion claims.",
        "Current `master` also keeps `.github/workflows/zigux-bootstrap.yml` explicit with the shipped low-level-wrapper self-test, survey check, focused replay, and shared tests-root replay steps, so the bounded reminder packet should treat that bootstrap workflow route as current support evidence rather than leaving the workflow-backed wrapper gate implicit behind the dedicated validator and Makefile route.",
        "That workflow-backed replay step now belongs to the same bounded reminder packet as the dedicated survey validator and the returned shared Makefile replay gates, so later lane-local cleanup should reread those four support surfaces together instead of treating the workflow route as optional background context.",
        "Current `master` also keeps `scripts/zigux/check-phase3-selftest-surface.py` directly readable as the shared Phase 3 selftest-surface guard for the returned validator-support, shared-tests-route, export/UAPI, catalog, and low-level-wrapper reminder packet. That newer shared guard should stay framed here as adjacent cross-packet support rather than as extra low-level-wrapper-local proof.",
        "Current `master` also keeps `scripts/zigux/generate-phase3-check-wrappers.py` together with `scripts/zigux/check-phase3-wrapper-templates.py` directly readable as the adjacent stale-wrapper cleanup pair for historical shared-runner wrapper retirement, and that churn-control support should stay framed here as adjacent cross-packet evidence rather than as extra low-level-wrapper-local proof.",
        "Reviewers should treat the low-level wrapper family as materially landed as a bounded packet on current `master`, with one remaining helper-local MMIO follow-through: the packet now covers one atomic helper shard, one barrier helper companion, one MMIO helper companion, one directly readable unsafe-policy companion, the shared narrow-unsafe decoder plus interop-policy raw-pointer bridge entrypoints, the dedicated survey validator, one focused low-level-wrapper replay shard, one dedicated shared build companion, two returned shared Makefile replay gates, and two direct replay commands, while the separately readable Phase 3 catalog-selftest guard stays adjacent cross-packet support rather than extra low-level-wrapper proof.",
        "Current `master` also keeps `MmioRange`, `rangeScoped()`, `rangeInteropPolicy()`, `rangeInteropPolicyBytes()`, `rangeInteropPolicyByte()`, and the width-specific `read8InteropPolicyBytes()`/`write8InteropPolicyBytes()`/`read8InteropPolicyByte()`/`write8InteropPolicyByte()`/`read16InteropPolicyBytes()`/`write16InteropPolicyBytes()`/`read16InteropPolicyByte()`/`write16InteropPolicyByte()`/`read32InteropPolicyBytes()`/`write32InteropPolicyBytes()`/`read32InteropPolicyByte()`/`write32InteropPolicyByte()`/`read64InteropPolicyBytes()`/`write64InteropPolicyBytes()`/`read64InteropPolicyByte()`/`write64InteropPolicyByte()` entrypoints directly readable in `zigux/helpers/mmio.zig`, so the bounded low-level-wrapper survey should treat those MMIO range and width-specific wrappers as landed helper-local evidence rather than collapsing MMIO coverage to the generic typed accessors alone.",
        "The live Phase 3 tree now carries the roadmap-approved atomic and barrier wrapper leafs plus a broad MMIO helper packet, but one bounded MMIO follow-through still remains inside the current low-level wrapper lane: `MmioRange` only blesses base address, length, and stride, while the typed accessors in `zigux/helpers/mmio.zig` still operate on raw base-address plus offset parameters instead of carrying `range.length` through direct read, write, exchange, and masked-update helpers.",
        "That same helper-local MMIO surface still needs one narrow closure step: range-bounded typed accessors that reject misaligned or out-of-window offsets after `rangeScoped()` or the `rangeInteropPolicy*()` constructors have materialized a `MmioRange`. Until that lands, reviewers should treat `MmioRange` as a validated descriptor plus width-specific base-address helper family, not as full in-range MMIO access closure.",
        "The live Phase 3 tree is no longer missing any roadmap-approved atomic, barrier, or MMIO wrapper leaf inside the current low-level wrapper packet. `zigux/helpers/atomic.zig` now directly exposes order-bounds and reusable order-validation helpers through `compareExchangeFailureOrderAllowed()`, `validateCompareExchangeOrders()`, `strongestAllowedFailureOrder()`, `weakestAllowedFailureOrder()`, `loadOrderAllowed()`, `validateLoadOrder()`, `storeOrderAllowed()`, `validateStoreOrder()`, `rmwOrderAllowed()`, and `validateRmwOrder()`, alongside the order-checked `load()`, `store()`, `exchange()`, `compareExchangeStrong()`, `compareExchangeWeak()`, and `fetchAdd()`/`fetchSub()`/`fetchNand()`/`fetchOr()`/`fetchAnd()`/`fetchXor()`/`fetchMin()`/`fetchMax()` helpers; `zigux/helpers/barrier.zig` now keeps `compiler()`, `fence()`, `fenceOrderAllowed()`, `validateFenceOrder()`, `acquire()`, `release()`, `full()`, `acquireRelease()`, `fullFence()`, and `storeLoad()` explicit beside `FenceError`; and `zigux/helpers/mmio.zig` keeps typed, scoped, byte-policy, whole-record interop-policy, exchange, and masked volatile accessors directly readable on current `master`.",
    ),
    ATOMIC_PATH: (
        "pub fn strongestAllowedFailureOrder(success: Ordering) ?Ordering {",
        "pub fn weakestAllowedFailureOrder(success: Ordering) ?Ordering {",
        "pub fn compareExchangeFailureOrderAllowed(success: Ordering, failure: Ordering) bool {",
        "pub fn validateCompareExchangeOrders(",
        "pub fn loadOrderAllowed(order: Ordering) bool {",
        "pub fn validateLoadOrder(comptime order: Ordering) LoadError!void {",
        "pub fn storeOrderAllowed(order: Ordering) bool {",
        "pub fn validateStoreOrder(comptime order: Ordering) StoreError!void {",
        "pub fn rmwOrderAllowed(order: Ordering) bool {",
        "pub fn validateRmwOrder(comptime order: Ordering) RmwError!void {",
        "pub fn load(comptime T: type, ptr: *const T, comptime order: Ordering) LoadError!T {",
        "pub fn store(comptime T: type, ptr: *T, value: T, comptime order: Ordering) StoreError!void {",
        "pub fn exchange(",
        "pub fn compareExchangeStrong(",
        "pub fn compareExchangeWeak(",
        "pub fn fetchAdd(",
        "pub fn fetchSub(",
        "pub fn fetchNand(",
        "pub fn fetchOr(",
        "pub fn fetchAnd(",
        "pub fn fetchXor(",
        "pub fn fetchMin(",
        "pub fn fetchMax(",
    ),
    BARRIER_PATH: (
        "pub const FenceError = error{",
        "pub fn fenceOrderAllowed(order: Ordering) bool {",
        "pub fn validateFenceOrder(comptime order: Ordering) FenceError!void {",
        "pub fn compiler() void {",
        "pub fn fence(comptime order: Ordering) FenceError!void {",
        "pub fn acquire() void {",
        "pub fn release() void {",
        "pub fn full() void {",
        "pub fn acquireRelease() void {",
        "pub fn fullFence() void {",
        "pub fn storeLoad() void {",
    ),
    MMIO_PATH: (
        "pub const MmioRange = extern struct {",
        "pub fn allowsInteropPolicy(policy: abi.InteropPolicy) bool {",
        "pub fn allowsInteropPolicyBytes(unsafe_scope: u8, reserved: u8) bool {",
        "pub fn allowsInteropPolicyByte(unsafe_scope: u8) bool {",
        "pub fn requireVolatileMmioScope(scope: abi.UnsafeScope) PolicyError!void {",
        "pub fn requireInteropPolicy(policy: abi.InteropPolicy) PolicyError!void {",
        "pub fn requireInteropPolicyBytes(unsafe_scope: u8, reserved: u8) PolicyError!void {",
        "pub fn requireInteropPolicyByte(unsafe_scope: u8) PolicyError!void {",
        "pub fn read(comptime T: type, ptr: *const volatile T) T {",
        "pub fn write(comptime T: type, ptr: *volatile T, value: T) void {",
        "pub fn exchange(comptime T: type, ptr: *volatile T, value: T) T {",
        "pub fn writeMasked(comptime T: type, ptr: *volatile T, clear_mask: T, set_mask: T) T {",
        "pub fn readScoped(comptime T: type, scope: abi.UnsafeScope, ptr: *const volatile T) PolicyError!T {",
        "pub fn writeScoped(comptime T: type, scope: abi.UnsafeScope, ptr: *volatile T, value: T) PolicyError!void {",
        "pub fn exchangeScoped(comptime T: type, scope: abi.UnsafeScope, ptr: *volatile T, value: T) PolicyError!T {",
        "pub fn writeMaskedScoped(",
        "pub fn rangeScoped(base_addr: usize, length: u32, stride: u32, scope: abi.UnsafeScope) PolicyError!MmioRange {",
        "pub fn rangeInteropPolicy(base_addr: usize, length: u32, stride: u32, policy: abi.InteropPolicy) PolicyError!MmioRange {",
        "pub fn rangeInteropPolicyBytes(base_addr: usize, length: u32, stride: u32, unsafe_scope: u8, reserved: u8) PolicyError!MmioRange {",
        "pub fn rangeInteropPolicyByte(base_addr: usize, length: u32, stride: u32, unsafe_scope: u8) PolicyError!MmioRange {",
        "pub fn readInteropPolicy(comptime T: type, policy: abi.InteropPolicy, ptr: *const volatile T) PolicyError!T {",
        "pub fn writeInteropPolicy(comptime T: type, policy: abi.InteropPolicy, ptr: *volatile T, value: T) PolicyError!void {",
        "pub fn exchangeInteropPolicy(comptime T: type, policy: abi.InteropPolicy, ptr: *volatile T, value: T) PolicyError!T {",
        "pub fn writeMaskedInteropPolicy(",
        "pub fn readInteropPolicyBytes(",
        "pub fn readInteropPolicyByte(comptime T: type, unsafe_scope: u8, ptr: *const volatile T) PolicyError!T {",
        "pub fn writeInteropPolicyBytes(",
        "pub fn writeInteropPolicyByte(",
        "pub fn exchangeInteropPolicyBytes(",
        "pub fn exchangeInteropPolicyByte(",
        "pub fn writeMaskedInteropPolicyBytes(",
        "pub fn writeMaskedInteropPolicyByte(",
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
        "pub fn scopeFromInteropPolicyBytes(scope: u8, reserved: u8) ?abi.UnsafeScope {",
        "pub fn scopeFromInteropPolicy(policy: abi.InteropPolicy) ?abi.UnsafeScope {",
        "pub fn permitsVolatileMmio(mode: abi.UnsafeScope) bool {",
        "pub fn permitsVolatileMmioInteropPolicy(policy: abi.InteropPolicy) bool {",
        "pub fn allowsVolatileMmioInteropPolicy(policy: abi.InteropPolicy) bool {",
        "pub fn requireVolatileMmioInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {",
        "pub fn permitsRawPointerBridge(mode: abi.UnsafeScope) bool {",
        "pub fn permitsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {",
        "pub fn allowsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {",
        "pub fn requireRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {",
        "pub fn allowsRawPointerBridgePolicyBytes(scope: u8, reserved: u8) bool {",
        "pub fn requireRawPointerBridgePolicyBytes(scope: u8, reserved: u8) UnsafeScopeError!void {",
        "pub fn permitsRawPointerBridgeByte(scope: u8) bool {",
        "pub fn allowsRawPointerBridgeByte(scope: u8) bool {",
        "pub fn requireRawPointerBridgeByte(scope: u8) UnsafeScopeError!void {",
    ),
    NARROW_PATH: (
        "pub fn scopeFromInteropPolicyBytes(unsafe_scope: u8, reserved: u8) ?UnsafeScopeTag {",
        "pub fn permitsRawPointerBridge(scope: UnsafeScopeTag) bool {",
        "pub fn permitsRawPointerBridgePolicyBytes(unsafe_scope: u8, reserved: u8) bool {",
        "pub fn permitsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {",
        "pub fn requireRawPointerBridgePolicyBytes(unsafe_scope: u8, reserved: u8) UnsafeScopeError!void {",
        "pub fn requireRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {",
        "pub fn pointerAtInteropPolicyBytes(comptime T: type, address: usize, byte_len: usize, unsafe_scope: u8, reserved: u8) RawPointerBridgeError!*align(1) T {",
        "pub fn pointerAtInteropPolicy(comptime T: type, address: usize, byte_len: usize, policy: abi.InteropPolicy) RawPointerBridgeError!*align(1) T {",
        "pub fn pointerAtByte(comptime T: type, address: usize, byte_len: usize, scope: u8) RawPointerBridgeError!*align(1) T {",
        "pub fn constPointerAtInteropPolicyBytes(comptime T: type, address: usize, unsafe_scope: u8, reserved: u8) RawPointerBridgeError!*align(1) const T {",
        "pub fn constPointerAtInteropPolicy(comptime T: type, address: usize, policy: abi.InteropPolicy) RawPointerBridgeError!*align(1) const T {",
        "pub fn constPointerAtByte(comptime T: type, address: usize, scope: u8) RawPointerBridgeError!*align(1) const T {",
        "pub fn sliceAtInteropPolicyBytes(comptime T: type, address: usize, len: usize, unsafe_scope: u8, reserved: u8) RawPointerBridgeError![]align(1) T {",
        "pub fn sliceAtInteropPolicy(comptime T: type, address: usize, len: usize, policy: abi.InteropPolicy) RawPointerBridgeError![]align(1) T {",
        "pub fn sliceAtByte(comptime T: type, address: usize, len: usize, scope: u8) RawPointerBridgeError![]align(1) T {",
        "pub fn constSliceAtInteropPolicyBytes(comptime T: type, address: usize, len: usize, unsafe_scope: u8, reserved: u8) RawPointerBridgeError![]align(1) const T {",
        "pub fn constSliceAtInteropPolicy(comptime T: type, address: usize, len: usize, policy: abi.InteropPolicy) RawPointerBridgeError![]align(1) const T {",
        "pub fn constSliceAtByte(comptime T: type, address: usize, len: usize, scope: u8) RawPointerBridgeError![]align(1) const T {",
        "pub fn writeValueAtInteropPolicyBytes(comptime T: type, address: usize, value: T, unsafe_scope: u8, reserved: u8) RawPointerBridgeError!void {",
        "pub fn writeValueAtInteropPolicy(comptime T: type, address: usize, value: T, policy: abi.InteropPolicy) RawPointerBridgeError!void {",
        "pub fn writeValueAtByte(comptime T: type, address: usize, value: T, scope: u8) RawPointerBridgeError!void {",
        "pub fn exchangeValueAtInteropPolicyBytes(comptime T: type, address: usize, byte_len: usize, value: T, unsafe_scope: u8, reserved: u8) RawPointerBridgeError!T {",
        "pub fn exchangeValueAtInteropPolicy(comptime T: type, address: usize, byte_len: usize, value: T, policy: abi.InteropPolicy) RawPointerBridgeError!T {",
        "pub fn exchangeValueAtByte(comptime T: type, address: usize, byte_len: usize, value: T, scope: u8) RawPointerBridgeError!T {",
    ),
    LAYOUT_ASSERT_PATH: (
        "pub const MmioRange = extern struct {",
        "pub fn assertMmioRangeLayout() LayoutError!void {",
    ),
    WRAPPER_REPLAY_PATH: (
        'test "phase3 low-level wrappers keep atomic ordering, barriers, and MMIO handoffs aligned" {',
        'test "phase3 low-level wrappers keep helper-local MMIO layout assertions explicit" {',
        "try layout_assert.assertMmioRangeLayout();",
        'test "phase3 low-level wrappers keep masked MMIO updates explicit after compare-exchange setup" {',
        'test "phase3 low-level wrappers keep monotonic strong compare-exchange mismatch explicit before MMIO publish" {',
        'test "phase3 low-level wrappers keep MMIO unsafe-scope gates explicit across shared handoff" {',
        'test "phase3 low-level wrappers keep MMIO byte-policy shorthand aligned with reserved-byte gates" {',
        'test "phase3 low-level wrappers keep MMIO single-byte interop-policy shorthands explicit" {',
        'test "phase3 low-level wrappers keep whole-record MMIO interop-policy helpers explicit" {',
        'test "phase3 low-level wrappers keep direct MMIO scope gates explicit" {',
        'test "phase3 low-level wrappers keep atomic load-store exchange and MMIO echo explicit" {',
        'test "phase3 low-level wrappers keep additive and bitwise atomic updates explicit before MMIO publish" {',
        'test "phase3 low-level wrappers keep subtractive, xor, and clamp-style atomic updates explicit before MMIO publish" {',
        'test "phase3 low-level wrappers keep exchange-style MMIO policy handoffs explicit" {',
        'test "phase3 low-level wrappers keep raw-pointer bridge scope gates explicit beside MMIO policy gates" {',
        'test "phase3 low-level wrappers keep raw-pointer bridge byte coverage explicit" {',
        'test "phase3 low-level wrappers keep raw-pointer bridge interop-policy helpers explicit" {',
        'test "phase3 low-level wrappers keep atomic order-gate failures explicit before MMIO publish" {',
        'test "phase3 low-level wrappers keep MMIO range helpers and width aliases explicit beside raw bridge gates" {',
        "barrier.storeLoad();",
        "try mmio.writeInteropPolicyBytes(u32, 1, 0, register_ptr, state);",
        "try std.testing.expectEqual(@as(u32, 0x00AA_5501), try mmio.readInteropPolicyBytes(u32, 1, 0, const_register_ptr));",
        "try std.testing.expectEqual(@as(u32, 0x1234_5678), try mmio.exchangeInteropPolicyByte(u32, 1, register_ptr, 0xCAFE_BABE));",
        "const direct_ptr = try narrow.pointerAtInteropPolicyBytes(",
        "const direct_const_ptr = try narrow.constPointerAtInteropPolicyBytes(",
        "const policy_slice = try narrow.sliceAtInteropPolicy(u32, bridge_addr, bridge_words.len, raw_policy);",
        "try narrow.writeValueAtInteropPolicyBytes(",
        "try narrow.writeValueAtInteropPolicy(u32, second_addr, 0x0BAD_F00D, raw_policy);",
        "try std.testing.expectEqual(@as(u32, 73), try narrow.exchangeValueAtInteropPolicyBytes(u32, third_addr, @sizeOf(u32), 79, 2, 0));",
        "try std.testing.expectEqual(@as(u32, 47), try narrow.exchangeValueAtInteropPolicy(u32, second_addr, @sizeOf(u32), 61, raw_policy));",
        "try std.testing.expectEqual(@as(u32, 61), try narrow.exchangeValueAtByte(u32, second_addr, @sizeOf(u32), 47, 2));",
        "const scoped_range = try mmio.rangeScoped(base_addr, 16, 4, .volatile_mmio);",
        "const policy_range = try mmio.rangeInteropPolicy(base_addr, 16, 4, mmio_policy);",
        "const byte_range = try mmio.rangeInteropPolicyByte(base_addr, 16, 4, mmio_scope);",
        "try mmio.write64InteropPolicyBytes(base_addr, 8, 0x0123_4567_89AB_CDEF, mmio_scope, 0);",
        "try narrow.readValueAtInteropPolicyBytes(u64, base_addr + 8, @sizeOf(u64), raw_scope, 0),",
        "try std.testing.expectError(error.UnsafeScopeDenied, narrow.constPointerAtByte(u32, base_addr + 4, mmio_scope));",
    ),
    WRAPPER_BUILD_PATH: (
        '.root_source_file = b.path("../helpers/atomic.zig"),',
        '.root_source_file = b.path("../helpers/barrier.zig"),',
        '.root_source_file = b.path("../helpers/layout_assert.zig"),',
        '.root_source_file = b.path("../helpers/mmio.zig"),',
        'layout_assert.addImport("abi_bindings", abi_bindings);',
        'narrow.addImport("abi_bindings", abi_bindings);',
        'root_module.addImport("atomic", atomic);',
        'root_module.addImport("barrier", barrier);',
        'root_module.addImport("layout_assert", layout_assert);',
        'root_module.addImport("unsafe_policy", unsafe_policy);',
        'root_module.addImport("narrow", narrow);',
        'mmio.addImport("abi_bindings", abi_bindings);',
        'mmio.addImport("unsafe_policy", unsafe_policy);',
        '"phase3-low-level-wrappers-test"',
    ),
    SHARED_TESTS_README_PATH: (
        "## Phase 3 shared substrate packet",
        "`Documentation/zigux/phase3-export-uapi-boundary-survey.md`",
        "`scripts/zigux/validate-phase3-export-uapi-survey.py`",
        "`Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`",
        "`scripts/zigux/validate-phase3-low-level-wrapper-survey.py`",
        "`zigux/tests/phase3_low_level_wrappers.zig`",
        "`zigux/tests/phase3_low_level_wrappers_build.zig`",
        "`zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig`",
        "`zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig`",
        "`zig build phase3-test --build-file zigux/tests/build.zig`",
    ),
    SHARED_TESTS_BUILD_PATH: (
        "fn addPhase3LowLevelWrappers(",
        '.root_source_file = b.path("../helpers/atomic.zig"),',
        '.root_source_file = b.path("../helpers/barrier.zig"),',
        '.root_source_file = b.path("../helpers/mmio.zig"),',
        '"phase3-low-level-wrappers"',
        '"phase3-test"',
        "phase3_low_level_wrapper_step.dependOn(&phase3_low_level_wrappers.step);",
        "phase3_test_step.dependOn(&phase3_low_level_wrappers.step);",
    ),
    MAKEFILE_PATH: (
        "phase3-low-level-wrappers:",
        "phase3-low-level-wrappers-test:",
        "cd $(ZIGUX_ROOT) && $(ZIG) build phase3-low-level-wrappers --build-file zigux/tests/build.zig",
        "cd $(ZIGUX_ROOT) && $(ZIG) build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
        "phase3: phase3-validate phase3-export-uapi-layout phase3-low-level-wrappers phase3-test phase3-policy-dump phase3-dump",
    ),
    SELFTEST_SURFACE_PATH: (
        'Path("scripts/zigux/validate-phase3-validator-support-surface.py")',
        'Path("scripts/zigux/check-phase3-shared-tests-routes.py")',
        'Path("scripts/zigux/validate-phase3-export-uapi-survey.py")',
        'Path("scripts/zigux/check-phase3-catalog-selftest.py")',
        'Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py")',
        '"PHASE3_SELFTEST_SURFACE_SELF_TEST=pass"',
    ),
    WORKFLOW_PATH: (
        "name: Self-test current Phase 3 low-level wrapper survey validator",
        "run: python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test",
        "name: Check current Phase 3 low-level wrapper survey packet",
        "name: Run current Phase 3 low-level wrapper replay",
        "run: zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
        "name: Run current Phase 3 low-level wrapper make route",
        "run: make -C zigux phase3-low-level-wrappers",
        "name: Run current Phase 3 focused low-level wrapper make route",
        "run: make -C zigux phase3-low-level-wrappers-test",
        "name: Run current Phase 3 shared tests-root packet",
        "run: zig build phase3-test --build-file zigux/tests/build.zig",
    ),
}

REQUIRED_MANIFEST_FIELDS = {
    "phase": "Phase 3",
    "lane": "abi-runtime",
    "slug": "phase3-abi-packet",
    "status": "shared_abi_and_header_family_binding_surface_present",
    "scope": CURRENT_MANIFEST_SCOPE,
    "next_safe_step": CURRENT_NEXT_SAFE_STEP,
}

REQUIRED_MANIFEST_PACKET_FILES = (
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
    "zigux/helpers/atomic.zig",
    "zigux/helpers/barrier.zig",
    "zigux/helpers/layout_assert.zig",
    "zigux/helpers/mmio.zig",
    "zigux/helpers/unsafe_policy.zig",
    "zigux/unsafe/narrow.zig",
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "zigux/tests/phase3_low_level_wrappers.zig",
    "zigux/tests/phase3_low_level_wrappers_build.zig",
    "zigux/tests/README.md",
    "zigux/tests/build.zig",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
)

REQUIRED_MANIFEST_REPLAY_ROUTES = (
    "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test",
    "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig",
    "make -C zigux phase3-low-level-wrappers",
    "zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "make -C zigux phase3-low-level-wrappers-test",
    "zig build phase3-test --build-file zigux/tests/build.zig",
)

SELF_TEST_CASES = tuple(
    (relative_path, marker)
    for relative_path, markers in REQUIRED_MARKERS.items()
    for marker in markers
)

SELF_TEST_FIELD_CASES = (
    ("scope", "stale-scope"),
    ("next_safe_step", "stale-next-step"),
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _append_duplicate_list_entry_issues(label: str, values: list[object], issues: list[str]) -> None:
    seen: dict[str, int] = {}
    for index, value in enumerate(values):
        key = repr(value)
        first_index = seen.get(key)
        if first_index is None:
            seen[key] = index
            continue
        issues.append(
            f"{label} duplicate entry: {value!r} (first index {first_index}, duplicate index {index})"
        )


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

    manifest_path = repo_root / MANIFEST_PATH
    try:
        manifest = json.loads(_read(manifest_path))
    except FileNotFoundError:
        issues.append(f"missing repo file: {MANIFEST_PATH.as_posix()}")
        return issues
    except json.JSONDecodeError as exc:
        issues.append(f"invalid JSON in {MANIFEST_PATH.as_posix()}: {exc}")
        return issues

    for field, expected in REQUIRED_MANIFEST_FIELDS.items():
        actual = manifest.get(field)
        if actual != expected:
            issues.append(f"phase3_abi_manifest.json wrong {field}: {actual!r} != {expected!r}")

    packet_files = manifest.get("packet_files")
    replay_routes = manifest.get("replay_routes")
    repo_reality_gaps = manifest.get("repo_reality_gaps")

    if not isinstance(packet_files, list):
        issues.append("phase3_abi_manifest.json packet_files is not a list")
    else:
        _append_duplicate_list_entry_issues(
            "phase3_abi_manifest.json packet_files",
            packet_files,
            issues,
        )
        for entry in REQUIRED_MANIFEST_PACKET_FILES:
            if entry not in packet_files:
                issues.append(f"phase3_abi_manifest.json missing packet_files entry: {entry}")

    if not isinstance(replay_routes, list):
        issues.append("phase3_abi_manifest.json replay_routes is not a list")
    else:
        _append_duplicate_list_entry_issues(
            "phase3_abi_manifest.json replay_routes",
            replay_routes,
            issues,
        )
        for entry in REQUIRED_MANIFEST_REPLAY_ROUTES:
            if entry not in replay_routes:
                issues.append(f"phase3_abi_manifest.json missing replay route: {entry}")

    if not isinstance(repo_reality_gaps, list):
        issues.append("phase3_abi_manifest.json repo_reality_gaps is not a list")
    else:
        _append_duplicate_list_entry_issues(
            "phase3_abi_manifest.json repo_reality_gaps",
            repo_reality_gaps,
            issues,
        )
        for gap in repo_reality_gaps:
            if gap in REQUIRED_MANIFEST_PACKET_FILES:
                issues.append(
                    "phase3_abi_manifest.json misclassified low-level-wrapper packet file as repo gap: "
                    f"{gap}"
                )
            if gap in REQUIRED_MANIFEST_REPLAY_ROUTES:
                issues.append(
                    "phase3_abi_manifest.json misclassified low-level-wrapper replay route as repo gap: "
                    f"{gap}"
                )

    return issues


def _populate_repo(root: Path) -> None:
    for relative_path, markers in REQUIRED_MARKERS.items():
        _write(root / relative_path, "\n".join(markers) + "\n")

    manifest = {
        "phase": REQUIRED_MANIFEST_FIELDS["phase"],
        "lane": REQUIRED_MANIFEST_FIELDS["lane"],
        "slug": REQUIRED_MANIFEST_FIELDS["slug"],
        "status": REQUIRED_MANIFEST_FIELDS["status"],
        "scope": CURRENT_MANIFEST_SCOPE,
        "packet_files": list(REQUIRED_MANIFEST_PACKET_FILES),
        "replay_routes": list(REQUIRED_MANIFEST_REPLAY_ROUTES),
        "repo_reality_gaps": [],
        "next_safe_step": CURRENT_NEXT_SAFE_STEP,
    }
    _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_low_level_wrapper_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in SELF_TEST_CASES:
            _populate_repo(root)
            path = root / relative_path
            path.write_text(_read(path).replace(marker, ""), encoding="utf-8")
            issues = validate_repo(root)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

        for field, bad_value in SELF_TEST_FIELD_CASES:
            _populate_repo(root)
            manifest_path = root / MANIFEST_PATH
            manifest = json.loads(_read(manifest_path))
            manifest[field] = bad_value
            _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
            issues = validate_repo(root)
            expected = (
                f"phase3_abi_manifest.json wrong {field}: "
                f"{bad_value!r} != {REQUIRED_MANIFEST_FIELDS[field]!r}"
            )
            if expected not in issues:
                print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
                print(f"expected manifest field drift was not reported: {expected}")
                return 1

        _populate_repo(root)
        manifest_path = root / MANIFEST_PATH
        manifest = json.loads(_read(manifest_path))
        manifest["packet_files"].remove("zigux/helpers/layout_assert.zig")
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        if "phase3_abi_manifest.json missing packet_files entry: zigux/helpers/layout_assert.zig" not in issues:
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("expected missing low-level-wrapper layout-assert packet file was not reported")
            return 1

        _populate_repo(root)
        manifest = json.loads(_read(manifest_path))
        manifest["packet_files"].remove("zigux/helpers/mmio.zig")
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        if "phase3_abi_manifest.json missing packet_files entry: zigux/helpers/mmio.zig" not in issues:
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("expected missing low-level-wrapper packet file was not reported")
            return 1

        _populate_repo(root)
        manifest = json.loads(_read(manifest_path))
        manifest["packet_files"].remove(".github/workflows/zigux-bootstrap.yml")
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        if "phase3_abi_manifest.json missing packet_files entry: .github/workflows/zigux-bootstrap.yml" not in issues:
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("expected missing low-level-wrapper workflow packet file was not reported")
            return 1

        _populate_repo(root)
        manifest = json.loads(_read(manifest_path))
        manifest["packet_files"].remove("zigux/helpers/unsafe_policy.zig")
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        if "phase3_abi_manifest.json missing packet_files entry: zigux/helpers/unsafe_policy.zig" not in issues:
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("expected missing low-level-wrapper unsafe-policy packet file was not reported")
            return 1

        _populate_repo(root)
        manifest = json.loads(_read(manifest_path))
        manifest["replay_routes"].remove(
            "zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig"
        )
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        if (
            "phase3_abi_manifest.json missing replay route: zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig"
            not in issues
        ):
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("expected missing low-level-wrapper replay route was not reported")
            return 1

        _populate_repo(root)
        manifest = json.loads(_read(manifest_path))
        manifest["replay_routes"].remove("make -C zigux phase3-low-level-wrappers")
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        if "phase3_abi_manifest.json missing replay route: make -C zigux phase3-low-level-wrappers" not in issues:
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("expected missing low-level-wrapper Makefile replay route was not reported")
            return 1

        _populate_repo(root)
        manifest = json.loads(_read(manifest_path))
        manifest["replay_routes"].remove("make -C zigux phase3-low-level-wrappers-test")
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        if "phase3_abi_manifest.json missing replay route: make -C zigux phase3-low-level-wrappers-test" not in issues:
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("expected focused low-level-wrapper replay route was not reported")
            return 1

        _populate_repo(root)
        manifest = json.loads(_read(manifest_path))
        manifest["replay_routes"].remove("zig build phase3-test --build-file zigux/tests/build.zig")
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        if "phase3_abi_manifest.json missing replay route: zig build phase3-test --build-file zigux/tests/build.zig" not in issues:
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("expected missing shared tests-root replay route was not reported")
            return 1

        _populate_repo(root)
        manifest = json.loads(_read(manifest_path))
        manifest["packet_files"].append("zigux/helpers/mmio.zig")
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        if not any(issue.startswith("phase3_abi_manifest.json packet_files duplicate entry:") for issue in issues):
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("expected duplicate low-level-wrapper packet file was not reported")
            return 1

        _populate_repo(root)
        manifest = json.loads(_read(manifest_path))
        manifest["replay_routes"].append("make -C zigux phase3-low-level-wrappers")
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        if not any(issue.startswith("phase3_abi_manifest.json replay_routes duplicate entry:") for issue in issues):
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("expected duplicate low-level-wrapper replay route was not reported")
            return 1

        _populate_repo(root)
        manifest = json.loads(_read(manifest_path))
        manifest["replay_routes"].append("make -C zigux phase3-low-level-wrappers-test")
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        if not any(issue.startswith("phase3_abi_manifest.json replay_routes duplicate entry:") for issue in issues):
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("expected duplicate focused low-level-wrapper replay route was not reported")
            return 1

        _populate_repo(root)
        manifest = json.loads(_read(manifest_path))
        manifest["repo_reality_gaps"] = ["zigux/helpers/mmio.zig"]
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        if (
            "phase3_abi_manifest.json misclassified low-level-wrapper packet file as repo gap: zigux/helpers/mmio.zig"
            not in issues
        ):
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("expected low-level-wrapper repo-gap misclassification was not reported")
            return 1

        _populate_repo(root)
        manifest = json.loads(_read(manifest_path))
        manifest["repo_reality_gaps"] = ["make -C zigux phase3-low-level-wrappers"]
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        if (
            "phase3_abi_manifest.json misclassified low-level-wrapper replay route as repo gap: make -C zigux phase3-low-level-wrappers"
            not in issues
        ):
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("expected low-level-wrapper replay-route repo-gap misclassification was not reported")
            return 1

        _populate_repo(root)
        manifest = json.loads(_read(manifest_path))
        manifest["repo_reality_gaps"] = ["make -C zigux phase3-low-level-wrappers-test"]
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        if (
            "phase3_abi_manifest.json misclassified low-level-wrapper replay route as repo gap: make -C zigux phase3-low-level-wrappers-test"
            not in issues
        ):
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("expected focused low-level-wrapper replay-route repo-gap misclassification was not reported")
            return 1

        _populate_repo(root)
        manifest = json.loads(_read(manifest_path))
        manifest["repo_reality_gaps"] = [
            "zigux/helpers/mmio.zig",
            "zigux/helpers/mmio.zig",
        ]
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        if not any(issue.startswith("phase3_abi_manifest.json repo_reality_gaps duplicate entry:") for issue in issues):
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("expected duplicate repo-gap marker was not reported")
            return 1

    print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass")
    print(f"PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES) + len(SELF_TEST_FIELD_CASES) + 15}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 low-level wrapper survey packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 low-level wrapper packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY=fail")
        print("\n".join(issues))
        return 1

    print(f"validated {NOTE_PATH.as_posix()}")
    print(f"validated {ATOMIC_PATH.as_posix()}")
    print(f"validated {BARRIER_PATH.as_posix()}")
    print(f"validated {MMIO_PATH.as_posix()}")
    print(f"validated {UNSAFE_POLICY_PATH.as_posix()}")
    print(f"validated {NARROW_PATH.as_posix()}")
    print(f"validated {LAYOUT_ASSERT_PATH.as_posix()}")
    print(f"validated {WRAPPER_REPLAY_PATH.as_posix()}")
    print(f"validated {WRAPPER_BUILD_PATH.as_posix()}")
    print(f"validated {SHARED_TESTS_README_PATH.as_posix()}")
    print(f"validated {SHARED_TESTS_BUILD_PATH.as_posix()}")
    print(f"validated {MAKEFILE_PATH.as_posix()}")
    print(f"validated {SELFTEST_SURFACE_PATH.as_posix()}")
    print(f"validated {WORKFLOW_PATH.as_posix()}")
    print(f"validated {MANIFEST_PATH.as_posix()}")
    print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
