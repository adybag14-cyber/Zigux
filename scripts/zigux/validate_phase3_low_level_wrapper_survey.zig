const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_LOW_LEVEL_WRAPPER_SURVEY=pass";
pub const self_test_pass_marker = "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass";

const CURRENT_MANIFEST_SCOPE = [_][]const u8{
    "shared ABI bindings, directly coupled helper decoding, header-family follow-through, notifier layouts, export-status layout, and header-compatibility replay",
};

const CURRENT_NEXT_SAFE_STEP = [_][]const u8{
    "keep the shared Phase 3 policy, export/UAPI, low-level wrapper packet, and retired generated-packet guard aligned with the dedicated replay routes and only reopen this manifest if the checker, focused builds, or reminder surfaces drift again",
};

const REQUIRED_MARKERS__Documentation_zigux_phase3-low-level-wrapper-boundary-survey_md = [_][]const u8{
    "PHASE3_LOW_LEVEL_WRAPPER_SCOPE=the roadmap and bootstrap ledger still reserve a bounded Phase 3 low-level wrapper family for approved atomic, barrier, and MMIO wrappers, and current master now directly exposes one atomic helper shard, one barrier helper companion, one MMIO helper companion, one directly readable unsafe-policy companion, one shared narrow-unsafe decoder plus directly readable interop-policy raw-pointer bridge entrypoints, this dedicated survey note, a dedicated survey validator, one focused low-level-wrapper replay shard, one dedicated shared build companion, one shared tests-root reminder, one workflow-backed replay route, and two returned shared Makefile replay gates",
    "PHASE3_LOW_LEVEL_WRAPPER_GAP=direct current-head readback reaches Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md, zigux/helpers/atomic.zig, zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/helpers/unsafe_policy.zig, zigux/unsafe/narrow.zig, scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig, zigux/tests/phase3_low_level_wrappers.zig, zigux/tests/phase3_low_level_wrappers_build.zig, zigux/tests/README.md, zigux/tests/build.zig, zigux/Makefile, and .github/workflows/zigux-bootstrap.yml; adjacent shared Phase 3 validator, shared ABI checker, shared ABI catalog helper, export/UAPI survey-validator, and catalog-selftest guard surfaces now read separately on current master, while the low-level-wrapper packet stays bounded to its own helper-local evidence",
    "PHASE3_LOW_LEVEL_WRAPPER_NEXT_STEP=keep low-level wrapper follow-through bounded to shared validation truthfulness around the landed range-bounded MMIO typed accessors, the directly coupled unsafe-policy companion, the shared narrow-unsafe interop-policy bridge entrypoints, the dedicated build companion, the shared tests-root reminder, the workflow-backed low-level-wrapper replay route, the direct zig build phase3-low-level-wrappers replay route, the direct zig build phase3-low-level-wrappers-test replay route, and the returned Makefile replay gates while the adjacent catalog-selftest guard stays outside this wrapper packet",
    "`zigux/helpers/atomic.zig`",
    "`zigux/helpers/barrier.zig`",
    "`zigux/helpers/mmio.zig`",
    "`zigux/helpers/unsafe_policy.zig`",
    "`zigux/unsafe/narrow.zig`",
    "`scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig`",
    "`zigux/tests/phase3_low_level_wrappers.zig`",
    "`zigux/tests/phase3_low_level_wrappers_build.zig`",
    "`zigux/tests/README.md`",
    "`zigux/tests/build.zig`",
    "`zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig`",
    "`zigux/Makefile`",
    "`make -C zigux phase3-low-level-wrappers`",
    "`zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig`",
    "`make -C zigux phase3-low-level-wrappers-test`",
    "`scripts\\zigux/check_phase3_selftest_surface.zig`",
    "`scripts/zigux/check_phase3_wrapper_templates.zig`",
    "`scripts\\zigux/check_phase3_wrapper_templates.zig`",
    "Current `master` also keeps `zigux/Makefile`, `make -C zigux phase3-low-level-wrappers`, and `make -C zigux phase3-low-level-wrappers-test` explicit beside the dedicated shared build companion, so the low-level-wrapper packet now has both the direct Zig replay commands and the returned shared Makefile replay gates without widening into broader Phase 3 completion claims.",
    "Current `master` also keeps `.github/workflows/zigux-bootstrap.yml` explicit with the shipped low-level-wrapper self-test, survey check, focused replay, and shared tests-root replay steps, so the bounded reminder packet should treat that bootstrap workflow route as current support evidence rather than leaving the workflow-backed wrapper gate implicit behind the dedicated validator and Makefile route.",
    "That workflow-backed replay step now belongs to the same bounded reminder packet as the dedicated survey validator and the returned Makefile replay gates, so later lane-local cleanup should reread those four support surfaces together instead of treating the workflow route as optional background context.",
    "Current `master` also keeps `scripts\\zigux/check_phase3_selftest_surface.zig` directly readable as the shared Phase 3 selftest-surface guard for the returned validator-support, shared-tests-route, export/UAPI, catalog, and low-level-wrapper reminder packet. That newer shared guard should stay framed here as adjacent cross-packet support rather than as extra low-level-wrapper-local proof.",
    "Current `master` also keeps `scripts/zigux/check_phase3_wrapper_templates.zig` together with `scripts\\zigux/check_phase3_wrapper_templates.zig` directly readable as the adjacent stale-wrapper cleanup pair for historical shared-runner wrapper retirement, and that churn-control support should stay framed here as adjacent cross-packet evidence rather than as extra low-level-wrapper-local proof.",
    "Reviewers should treat the low-level wrapper family as materially landed as a bounded packet on current `master`, with no remaining helper-local gap inside the atomic, barrier, and MMIO leaf wrappers themselves: the packet now covers one atomic helper shard, one barrier helper companion, one MMIO helper companion, the landed range-bounded MMIO typed accessors, one directly readable unsafe-policy companion, the shared narrow-unsafe decoder plus interop-policy raw-pointer bridge entrypoints, the dedicated survey validator, one focused low-level-wrapper replay shard, one dedicated shared build companion, two returned shared Makefile replay gates, and two direct replay commands, while the separately readable Phase 3 catalog-selftest guard stays adjacent cross-packet support rather than extra low-level-wrapper proof.",
    "Current `master` also keeps `MmioRange`, `rangeScoped()`, `rangeInteropPolicy()`, `rangeInteropPolicyBytes()`, `rangeInteropPolicyByte()`, and the width-specific `read8InteropPolicyBytes()`/`write8InteropPolicyBytes()`/`read8InteropPolicyByte()`/`write8InteropPolicyByte()`/`read16InteropPolicyBytes()`/`write16InteropPolicyBytes()`/`read16InteropPolicyByte()`/`write16InteropPolicyByte()`/`read32InteropPolicyBytes()`/`write32InteropPolicyBytes()`/`read32InteropPolicyByte()`/`write32InteropPolicyByte()`/`read64InteropPolicyBytes()`/`write64InteropPolicyBytes()`/`read64InteropPolicyByte()`/`write64InteropPolicyByte()` entrypoints directly readable in `zigux/helpers/mmio.zig`, so the bounded low-level-wrapper survey should treat those MMIO range and width-specific wrappers as landed helper-local evidence rather than collapsing MMIO coverage to the generic typed accessors alone.",
    "The live Phase 3 tree now carries the roadmap-approved atomic and barrier wrapper leafs plus a broad MMIO helper packet, and current `master` also keeps the range-bounded MMIO typed accessors `constPointerAt()`, `pointerAt()`, `readAt()`, `writeAt()`, `exchangeAt()`, and `writeMaskedAt()` directly readable in `zigux/helpers/mmio.zig`. Against the roadmap's approved atomic, barrier, and MMIO wrapper requirement, that means the bounded low-level-wrapper packet no longer has the earlier helper-body MMIO gap around `MmioRange` follow-through.",
    "The honest same-lane next step is therefore not new wrapper-body expansion. It is truthfulness maintenance: keep the survey note, the dedicated survey validator, the focused replay shard, the dedicated shared build companion, the returned Makefile replay gates, and the workflow-backed replay route aligned with those landed range-bounded MMIO accessors so future lane-local drift does not reintroduce a fake gap into the wrapper packet.",
};

const REQUIRED_MARKERS__zigux_helpers_atomic_zig = [_][]const u8{
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
};

const REQUIRED_MARKERS__zigux_helpers_barrier_zig = [_][]const u8{
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
};

const REQUIRED_MARKERS__zigux_helpers_mmio_zig = [_][]const u8{
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
};

const REQUIRED_MARKERS__zigux_helpers_unsafe_policy_zig = [_][]const u8{
    "pub fn scopeFromInteropPolicyBytes(scope: u8, reserved: u8) ?abi.UnsafeScope {",
    "pub fn scopeFromInteropPolicy(policy: abi.InteropPolicy) ?abi.UnsafeScope {",
    "pub fn permitsVolatileMmio(scope: abi.UnsafeScope) bool {",
    "pub fn permitsVolatileMmioInteropPolicy(policy: abi.InteropPolicy) bool {",
    "pub fn allowsVolatileMmioInteropPolicy(policy: abi.InteropPolicy) bool {",
    "pub fn requireVolatileMmioInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {",
    "pub fn permitsRawPointerBridge(scope: abi.UnsafeScope) bool {",
    "pub fn permitsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {",
    "pub fn allowsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {",
    "pub fn requireRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {",
    "pub fn allowsRawPointerBridgePolicyBytes(scope: u8, reserved: u8) bool {",
    "pub fn requireRawPointerBridgePolicyBytes(scope: u8, reserved: u8) UnsafeScopeError!void {",
    "pub fn permitsRawPointerBridgeByte(scope: u8) bool {",
    "pub fn allowsRawPointerBridgeByte(scope: u8) bool {",
    "pub fn requireRawPointerBridgeByte(scope: u8) UnsafeScopeError!void {",
};

const REQUIRED_MARKERS__zigux_unsafe_narrow_zig = [_][]const u8{
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
};

const REQUIRED_MARKERS__zigux_helpers_layout_assert_zig = [_][]const u8{
    "pub const MmioRange = extern struct {",
    "pub fn assertMmioRangeLayout() LayoutError!void {",
};

const REQUIRED_MARKERS__zigux_tests_phase3_low_level_wrappers_zig = [_][]const u8{
    "test \"phase3 low-level wrappers keep atomic ordering, barriers, and MMIO handoffs aligned\" {",
    "test \"phase3 low-level wrappers keep helper-local MMIO layout assertions explicit\" {",
    "try layout_assert.assertMmioRangeLayout();",
    "test \"phase3 low-level wrappers keep masked MMIO updates explicit after compare-exchange setup\" {",
    "test \"phase3 low-level wrappers keep monotonic strong compare-exchange mismatch explicit before MMIO publish\" {",
    "test \"phase3 low-level wrappers keep MMIO unsafe-scope gates explicit across shared handoff\" {",
    "test \"phase3 low-level wrappers keep MMIO byte-policy shorthand aligned with reserved-byte gates\" {",
    "test \"phase3 low-level wrappers keep MMIO single-byte interop-policy shorthands explicit\" {",
    "test \"phase3 low-level wrappers keep whole-record MMIO interop-policy helpers explicit\" {",
    "test \"phase3 low-level wrappers keep direct MMIO scope gates explicit\" {",
    "test \"phase3 low-level wrappers keep atomic load-store exchange and MMIO echo explicit\" {",
    "test \"phase3 low-level wrappers keep additive and bitwise atomic updates explicit before MMIO publish\" {",
    "test \"phase3 low-level wrappers keep subtractive, xor, and clamp-style atomic updates explicit before MMIO publish\" {",
    "test \"phase3 low-level wrappers keep exchange-style MMIO policy handoffs explicit\" {",
    "test \"phase3 low-level wrappers keep raw-pointer bridge scope gates explicit beside MMIO policy gates\" {",
    "test \"phase3 low-level wrappers keep raw-pointer bridge byte coverage explicit\" {",
    "test \"phase3 low-level wrappers keep raw-pointer bridge interop-policy helpers explicit\" {",
    "test \"phase3 low-level wrappers keep atomic order-gate failures explicit before MMIO publish\" {",
    "test \"phase3 low-level wrappers keep MMIO range helpers and width aliases explicit beside raw bridge gates\" {",
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
};

const REQUIRED_MARKERS__zigux_tests_phase3_low_level_wrappers_build_zig = [_][]const u8{
    ".root_source_file = b.path(\"../helpers/atomic.zig\"),",
    ".root_source_file = b.path(\"../helpers/barrier.zig\"),",
    ".root_source_file = b.path(\"../helpers/layout_assert.zig\"),",
    ".root_source_file = b.path(\"../helpers/mmio.zig\"),",
    "layout_assert.addImport(\"abi_bindings\", abi_bindings);",
    "narrow.addImport(\"abi_bindings\", abi_bindings);",
    "root_module.addImport(\"atomic\", atomic);",
    "root_module.addImport(\"barrier\", barrier);",
    "root_module.addImport(\"layout_assert\", layout_assert);",
    "root_module.addImport(\"unsafe_policy\", unsafe_policy);",
    "root_module.addImport(\"narrow\", narrow);",
    "mmio.addImport(\"abi_bindings\", abi_bindings);",
    "mmio.addImport(\"unsafe_policy\", unsafe_policy);",
    "\"phase3-low-level-wrappers-test\"",
};

const REQUIRED_MARKERS__zigux_tests_README_md = [_][]const u8{
    "## Phase 3 shared substrate packet",
    "`Documentation/zigux/phase3-export-uapi-boundary-survey.md`",
    "`scripts\\zigux/validate_phase3_export_uapi_survey.zig`",
    "`Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`",
    "`scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig`",
    "`zigux/tests/phase3_low_level_wrappers.zig`",
    "`zigux/tests/phase3_low_level_wrappers_build.zig`",
    "`zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig`",
    "`zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig`",
    "`zig build phase3-test --build-file zigux/tests/build.zig`",
};

const REQUIRED_MARKERS__zigux_tests_build_zig = [_][]const u8{
    "fn addPhase3LowLevelWrappers(",
    ".root_source_file = b.path(\"../helpers/atomic.zig\"),",
    ".root_source_file = b.path(\"../helpers/barrier.zig\"),",
    ".root_source_file = b.path(\"../helpers/mmio.zig\"),",
    "\"phase3-low-level-wrappers\"",
    "\"phase3-test\"",
    "phase3_low_level_wrapper_step.dependOn(&phase3_low_level_wrappers.step);",
    "phase3_test_step.dependOn(&phase3_low_level_wrappers.step);",
};

const REQUIRED_MARKERS__zigux_Makefile = [_][]const u8{
    "phase3-low-level-wrappers:",
    "phase3-low-level-wrappers-test:",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-low-level-wrappers --build-file zigux/tests/build.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "phase3: phase3-validate phase3-export-uapi-layout phase3-export-shim-test phase3-low-level-wrappers phase3-policy-unsafe-test phase3-test phase3-policy-dump phase3-dump",
};

const REQUIRED_MARKERS__scripts_zigux_check-phase3-selftest-surface_py = [_][]const u8{
    "Path(\"scripts\\zigux/validate_phase3_validator_support_surface.zig\")",
    "Path(\"scripts\\zigux/check_phase3_shared_tests_routes.zig\")",
    "Path(\"scripts\\zigux/validate_phase3_export_uapi_survey.zig\")",
    "Path(\"scripts\\zigux/check_phase3_catalog_selftest.zig\")",
    "Path(\"scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig\")",
    "\"PHASE3_SELFTEST_SURFACE_SELF_TEST=pass\"",
};

const REQUIRED_MARKERS___github_workflows_zigux-bootstrap_yml = [_][]const u8{
    "name: Self-test current Phase 3 low-level wrapper survey validator",
    "run: zig run scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig --self-test",
    "name: Check current Phase 3 low-level wrapper survey packet",
    "name: Run current Phase 3 low-level wrapper replay",
    "run: zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "name: Run current Phase 3 low-level wrapper make route",
    "run: make -C zigux phase3-low-level-wrappers",
    "name: Run current Phase 3 focused low-level wrapper make route",
    "run: make -C zigux phase3-low-level-wrappers-test",
    "name: Run current Phase 3 shared tests-root packet",
    "run: zig build phase3-test --build-file zigux/tests/build.zig",
};

const REQUIRED_MANIFEST_REPLAY_ROUTES = [_][]const u8{
    "zig run scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig --self-test",
    "zig run scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig",
    "zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig",
    "make -C zigux phase3-low-level-wrappers",
    "zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "make -C zigux phase3-low-level-wrappers-test",
    "zig build phase3-test --build-file zigux/tests/build.zig",
};

const SELF_TEST_FIELD_CASES = [_][]const u8{
    "scopestale-scope",
    "next_safe_stepstale-next-step",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_current_manifest_scope_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md");
    defer allocator.free(text_current_manifest_scope_path);
    const text_current_manifest_scope = try guard.readUtf8File(io, allocator, text_current_manifest_scope_path);
    defer allocator.free(text_current_manifest_scope);
    for (CURRENT_MANIFEST_SCOPE) |marker| try guard.requireMarker(text_current_manifest_scope, marker);
    const text_current_next_safe_step_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md");
    defer allocator.free(text_current_next_safe_step_path);
    const text_current_next_safe_step = try guard.readUtf8File(io, allocator, text_current_next_safe_step_path);
    defer allocator.free(text_current_next_safe_step);
    for (CURRENT_NEXT_SAFE_STEP) |marker| try guard.requireMarker(text_current_next_safe_step, marker);
    const text_required_markers__documentation_zigux_phase3-low-level-wrapper-boundary-survey_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-low-level-wrapper-boundary-survey/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase3-low-level-wrapper-boundary-survey_md_path);
    const text_required_markers__documentation_zigux_phase3-low-level-wrapper-boundary-survey_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase3-low-level-wrapper-boundary-survey_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase3-low-level-wrapper-boundary-survey_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase3-low-level-wrapper-boundary-survey_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase3-low-level-wrapper-boundary-survey_md, marker);
    const text_required_markers__zigux_helpers_atomic_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/atomic/zig");
    defer allocator.free(text_required_markers__zigux_helpers_atomic_zig_path);
    const text_required_markers__zigux_helpers_atomic_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_atomic_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_atomic_zig);
    for (REQUIRED_MARKERS__zigux_helpers_atomic_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_atomic_zig, marker);
    const text_required_markers__zigux_helpers_barrier_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/barrier/zig");
    defer allocator.free(text_required_markers__zigux_helpers_barrier_zig_path);
    const text_required_markers__zigux_helpers_barrier_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_barrier_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_barrier_zig);
    for (REQUIRED_MARKERS__zigux_helpers_barrier_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_barrier_zig, marker);
    const text_required_markers__zigux_helpers_mmio_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/mmio/zig");
    defer allocator.free(text_required_markers__zigux_helpers_mmio_zig_path);
    const text_required_markers__zigux_helpers_mmio_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_mmio_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_mmio_zig);
    for (REQUIRED_MARKERS__zigux_helpers_mmio_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_mmio_zig, marker);
    const text_required_markers__zigux_helpers_unsafe_policy_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/unsafe/policy/zig");
    defer allocator.free(text_required_markers__zigux_helpers_unsafe_policy_zig_path);
    const text_required_markers__zigux_helpers_unsafe_policy_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_unsafe_policy_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_unsafe_policy_zig);
    for (REQUIRED_MARKERS__zigux_helpers_unsafe_policy_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_unsafe_policy_zig, marker);
    const text_required_markers__zigux_unsafe_narrow_zig_path = try guard.joinPath(allocator, root, "zigux/unsafe/narrow/zig");
    defer allocator.free(text_required_markers__zigux_unsafe_narrow_zig_path);
    const text_required_markers__zigux_unsafe_narrow_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_unsafe_narrow_zig_path);
    defer allocator.free(text_required_markers__zigux_unsafe_narrow_zig);
    for (REQUIRED_MARKERS__zigux_unsafe_narrow_zig) |marker| try guard.requireMarker(text_required_markers__zigux_unsafe_narrow_zig, marker);
    const text_required_markers__zigux_helpers_layout_assert_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/layout/assert/zig");
    defer allocator.free(text_required_markers__zigux_helpers_layout_assert_zig_path);
    const text_required_markers__zigux_helpers_layout_assert_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_layout_assert_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_layout_assert_zig);
    for (REQUIRED_MARKERS__zigux_helpers_layout_assert_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_layout_assert_zig, marker);
    const text_required_markers__zigux_tests_phase3_low_level_wrappers_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/low/level/wrappers/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_low_level_wrappers_zig_path);
    const text_required_markers__zigux_tests_phase3_low_level_wrappers_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_low_level_wrappers_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_low_level_wrappers_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_low_level_wrappers_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_low_level_wrappers_zig, marker);
    const text_required_markers__zigux_tests_phase3_low_level_wrappers_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/low/level/wrappers/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_low_level_wrappers_build_zig_path);
    const text_required_markers__zigux_tests_phase3_low_level_wrappers_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_low_level_wrappers_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_low_level_wrappers_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_low_level_wrappers_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_low_level_wrappers_build_zig, marker);
    const text_required_markers__zigux_tests_readme_md_path = try guard.joinPath(allocator, root, "zigux/tests/README/md");
    defer allocator.free(text_required_markers__zigux_tests_readme_md_path);
    const text_required_markers__zigux_tests_readme_md = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_readme_md_path);
    defer allocator.free(text_required_markers__zigux_tests_readme_md);
    for (REQUIRED_MARKERS__zigux_tests_README_md) |marker| try guard.requireMarker(text_required_markers__zigux_tests_readme_md, marker);
    const text_required_markers__zigux_tests_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_build_zig_path);
    const text_required_markers__zigux_tests_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_build_zig, marker);
    const text_required_markers__zigux_makefile_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_required_markers__zigux_makefile_path);
    const text_required_markers__zigux_makefile = try guard.readUtf8File(io, allocator, text_required_markers__zigux_makefile_path);
    defer allocator.free(text_required_markers__zigux_makefile);
    for (REQUIRED_MARKERS__zigux_Makefile) |marker| try guard.requireMarker(text_required_markers__zigux_makefile, marker);
    const text_required_markers__scripts_zigux_check-phase3-selftest-surface_py_path = try guard.joinPath(allocator, root, "scripts/zigux/check-phase3-selftest-surface/py");
    defer allocator.free(text_required_markers__scripts_zigux_check-phase3-selftest-surface_py_path);
    const text_required_markers__scripts_zigux_check-phase3-selftest-surface_py = try guard.readUtf8File(io, allocator, text_required_markers__scripts_zigux_check-phase3-selftest-surface_py_path);
    defer allocator.free(text_required_markers__scripts_zigux_check-phase3-selftest-surface_py);
    for (REQUIRED_MARKERS__scripts_zigux_check-phase3-selftest-surface_py) |marker| try guard.requireMarker(text_required_markers__scripts_zigux_check-phase3-selftest-surface_py, marker);
    const text_required_markers___github_workflows_zigux-bootstrap_yml_path = try guard.joinPath(allocator, root, "/github/workflows/zigux-bootstrap/yml");
    defer allocator.free(text_required_markers___github_workflows_zigux-bootstrap_yml_path);
    const text_required_markers___github_workflows_zigux-bootstrap_yml = try guard.readUtf8File(io, allocator, text_required_markers___github_workflows_zigux-bootstrap_yml_path);
    defer allocator.free(text_required_markers___github_workflows_zigux-bootstrap_yml);
    for (REQUIRED_MARKERS___github_workflows_zigux-bootstrap_yml) |marker| try guard.requireMarker(text_required_markers___github_workflows_zigux-bootstrap_yml, marker);
    const text_required_manifest_replay_routes_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md");
    defer allocator.free(text_required_manifest_replay_routes_path);
    const text_required_manifest_replay_routes = try guard.readUtf8File(io, allocator, text_required_manifest_replay_routes_path);
    defer allocator.free(text_required_manifest_replay_routes);
    for (REQUIRED_MANIFEST_REPLAY_ROUTES) |marker| try guard.requireMarker(text_required_manifest_replay_routes, marker);
    const text_self_test_field_cases_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_self_test_field_cases_path);
    const text_self_test_field_cases = try guard.readUtf8File(io, allocator, text_self_test_field_cases_path);
    defer allocator.free(text_self_test_field_cases);
    for (SELF_TEST_FIELD_CASES) |marker| try guard.requireMarker(text_self_test_field_cases, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
