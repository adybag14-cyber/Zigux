const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_LOW_LEVEL_WRAPPER_SURVEY=pass";
pub const self_test_pass_marker = "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass";

const self_test_output_markers = [_][]const u8{
    "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass",
    "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST_CASE_COUNT=",
};

const live_output_markers = [_][]const u8{
    "validated Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
    "PHASE3_LOW_LEVEL_WRAPPER_SURVEY=pass",
};

const FileContract = struct {
    rel: []const u8,
    markers: []const []const u8,
};

const markers_0 = [_][]const u8{
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

const markers_1 = [_][]const u8{
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

const markers_2 = [_][]const u8{
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

const markers_3 = [_][]const u8{
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

const markers_4 = [_][]const u8{
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

const markers_5 = [_][]const u8{
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

const markers_6 = [_][]const u8{
    "pub const MmioRange = extern struct {",
    "pub fn assertMmioRangeLayout() LayoutError!void {",
};

const markers_7 = [_][]const u8{
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

const markers_8 = [_][]const u8{
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

const markers_9 = [_][]const u8{
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

const markers_10 = [_][]const u8{
    "fn addPhase3LowLevelWrappers(",
    ".root_source_file = b.path(\"../helpers/atomic.zig\"),",
    ".root_source_file = b.path(\"../helpers/barrier.zig\"),",
    ".root_source_file = b.path(\"../helpers/mmio.zig\"),",
    "\"phase3-low-level-wrappers\"",
    "\"phase3-test\"",
    "phase3_low_level_wrapper_step.dependOn(&phase3_low_level_wrappers.step);",
    "phase3_test_step.dependOn(&phase3_low_level_wrappers.step);",
};

const markers_11 = [_][]const u8{
    "phase3-low-level-wrappers:",
    "phase3-low-level-wrappers-test:",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-low-level-wrappers --build-file zigux/tests/build.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "phase3: phase3-validate phase3-export-uapi-layout phase3-export-shim-test phase3-low-level-wrappers phase3-policy-unsafe-test phase3-test phase3-policy-dump phase3-dump",
};

const markers_12 = [_][]const u8{
    "\"PHASE3_SELFTEST_SURFACE_SELF_TEST=pass\"",
};

const markers_13 = [_][]const u8{
    "name: Self-test current Phase 3 low-level wrapper survey validator",
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

const contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md", .markers = &markers_0 },
    .{ .rel = "zigux/helpers/atomic.zig", .markers = &markers_1 },
    .{ .rel = "zigux/helpers/barrier.zig", .markers = &markers_2 },
    .{ .rel = "zigux/helpers/mmio.zig", .markers = &markers_3 },
    .{ .rel = "zigux/helpers/unsafe_policy.zig", .markers = &markers_4 },
    .{ .rel = "zigux/unsafe/narrow.zig", .markers = &markers_5 },
    .{ .rel = "zigux/helpers/layout_assert.zig", .markers = &markers_6 },
    .{ .rel = "zigux/tests/phase3_low_level_wrappers.zig", .markers = &markers_7 },
    .{ .rel = "zigux/tests/phase3_low_level_wrappers_build.zig", .markers = &markers_8 },
    .{ .rel = "zigux/tests/README.md", .markers = &markers_9 },
    .{ .rel = "zigux/tests/build.zig", .markers = &markers_10 },
    .{ .rel = "zigux/Makefile", .markers = &markers_11 },
    .{ .rel = "scripts/zigux/check_phase3_selftest_surface.zig", .markers = &markers_12 },
    .{ .rel = ".github/workflows/zigux-bootstrap.yml", .markers = &markers_13 },
};

fn printOutputMarkers(io: Io, markers: []const []const u8) !void {
    for (markers) |marker| {
        if (std.mem.endsWith(u8, marker, "=")) {
            try guard.printLine(io, "{s}{d}", .{ marker, contracts.len });
        } else {
            try guard.printLine(io, "{s}", .{marker});
        }
    }
}

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(path);
        const text = try guard.readUtf8File(io, allocator, path);
        defer allocator.free(text);
        for (contract.markers) |marker| try guard.requireMarker(text, marker);
    }
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try printOutputMarkers(io, &self_test_output_markers);
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
        if (std.mem.eql(u8, arg, "--zig") or std.mem.eql(u8, arg, "--cc")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            continue;
        }
        std.process.exit(2);
    }

    if (self_test) std.process.exit(try runSelfTest(io, allocator));

    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try printOutputMarkers(io, &live_output_markers);
}
