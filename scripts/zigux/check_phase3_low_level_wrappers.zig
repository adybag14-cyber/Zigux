const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_LOW_LEVEL_WRAPPERS=pass";
pub const self_test_pass_marker = "PHASE3_LOW_LEVEL_WRAPPERS_SELF_TEST=pass";

const REQUIRED_MARKERS__zigux_tests_phase3_low_level_wrappers_zig = [_][]const u8{
    "const atomic = @import(\"atomic\");",
    "const barrier = @import(\"barrier\");",
    "const layout_assert = @import(\"layout_assert\");",
    "const mmio = @import(\"mmio\");",
    "const unsafe_policy = @import(\"unsafe_policy\");",
    "const narrow = @import(\"narrow\");",
    "test \"phase3 low-level wrappers keep helper-local MMIO layout assertions explicit\" {",
    "try layout_assert.assertMmioRangeLayout();",
    "test \"phase3 low-level wrappers keep MMIO unsafe-scope gates explicit across shared handoff\" {",
    "test \"phase3 low-level wrappers keep raw-pointer bridge scope gates explicit beside MMIO policy gates\" {",
    "test \"phase3 low-level wrappers keep raw-pointer bridge interop-policy helpers explicit\" {",
    "test \"phase3 low-level wrappers keep MMIO range helpers and width aliases explicit beside raw bridge gates\" {",
    "const direct_ptr = try narrow.pointerAtInteropPolicyBytes(",
    "const scoped_range = try mmio.rangeScoped(base_addr, 16, 4, .volatile_mmio);",
    "try std.testing.expect(unsafe_policy.permitsRawPointerBridgeByte(raw_scope));",
    "try mmio.write64InteropPolicyBytes(base_addr, 8, 0x0123_4567_89AB_CDEF, mmio_scope, 0);",
    "test \"phase3 low-level wrappers keep atomic order-gate failures explicit before MMIO publish\" {",
};

const REQUIRED_MARKERS__zigux_tests_phase3_low_level_wrappers_build_zig = [_][]const u8{
    ".root_source_file = b.path(\"../helpers/atomic.zig\"),",
    ".root_source_file = b.path(\"../helpers/barrier.zig\"),",
    ".root_source_file = b.path(\"../helpers/layout_assert.zig\"),",
    ".root_source_file = b.path(\"../helpers/mmio.zig\"),",
    ".root_source_file = b.path(\"../helpers/unsafe_policy.zig\"),",
    ".root_source_file = b.path(\"../unsafe/narrow.zig\"),",
    "layout_assert.addImport(\"abi_bindings\", abi_bindings);",
    "narrow.addImport(\"abi_bindings\", abi_bindings);",
    "unsafe_policy.addImport(\"narrow\", narrow);",
    "mmio.addImport(\"unsafe_policy\", unsafe_policy);",
    "root_module.addImport(\"layout_assert\", layout_assert);",
    "root_module.addImport(\"unsafe_policy\", unsafe_policy);",
    "root_module.addImport(\"narrow\", narrow);",
    "\"phase3-low-level-wrappers-test\"",
};

const REQUIRED_MARKERS__zigux_tests_build_zig = [_][]const u8{
    "fn addPhase3LowLevelWrappers(",
    "\"phase3-low-level-wrappers\"",
    "\"phase3-test\"",
    "phase3_low_level_wrapper_step.dependOn(&phase3_low_level_wrappers.step);",
    "phase3_test_step.dependOn(&phase3_low_level_wrappers.step);",
};

const REQUIRED_MARKERS__zigux_Makefile = [_][]const u8{
    "phase3-low-level-wrappers:",
    "phase3-low-level-wrappers-test:",
    "$(ZIG_REPO_ROOT) build phase3-low-level-wrappers --build-file zigux/tests/build.zig",
    "$(ZIG_REPO_ROOT) build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "phase3: phase3-validate phase3-export-uapi-layout phase3-export-shim-test phase3-low-level-wrappers phase3-policy-unsafe-test phase3-test phase3-policy-dump phase3-dump",
};

const REQUIRED_MARKERS___github_workflows_zigux-bootstrap_yml = [_][]const u8{
    "zig run scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig --self-test",
    "zig run scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig",
    "zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "make -C zigux phase3-low-level-wrappers",
    "make -C zigux phase3-low-level-wrappers-test",
    "zig build phase3-test --build-file zigux/tests/build.zig",
};

const REQUIRED_MARKERS__zigux_helpers_atomic_zig = [_][]const u8{
    "pub fn validateCompareExchangeOrders(",
    "pub fn load(comptime T: type, ptr: *const T, comptime order: Ordering) LoadError!T {",
    "pub fn strongestAllowedFailureOrder(success: Ordering) ?Ordering {",
    "pub fn weakestAllowedFailureOrder(success: Ordering) ?Ordering {",
    "pub fn fetchMax(",
};

const REQUIRED_MARKERS__zigux_helpers_barrier_zig = [_][]const u8{
    "pub fn fence(comptime order: Ordering) FenceError!void {",
    "pub fn validateFenceOrder(comptime order: Ordering) FenceError!void {",
    "pub fn acquireAfterControlDependency() void {",
    "pub fn storeLoad() void {",
    "pub fn afterAtomic() void {",
    "test \"phase3 barrier wrappers keep seq-cst aliases aligned\" {",
    "test \"phase3 barrier wrappers keep acquire-after-control-dependency handoffs reviewable\" {",
    "test \"phase3 barrier wrappers keep post-atomic full barriers explicit\" {",
};

const REQUIRED_MARKERS__zigux_helpers_layout_assert_zig = [_][]const u8{
    "pub const MmioRange = extern struct {",
    "pub fn assertMmioRangeLayout() LayoutError!void {",
};

const REQUIRED_MARKERS__zigux_helpers_mmio_zig = [_][]const u8{
    "pub fn allowsInteropPolicy(policy: abi.InteropPolicy) bool {",
    "pub fn requireInteropPolicy(policy: abi.InteropPolicy) PolicyError!void {",
    "pub fn rangeScoped(base_addr: usize, length: u32, stride: u32, scope: abi.UnsafeScope) PolicyError!MmioRange {",
    "pub fn rangeInteropPolicy(base_addr: usize, length: u32, stride: u32, policy: abi.InteropPolicy) PolicyError!MmioRange {",
    "pub fn rangeInteropPolicyBytes(base_addr: usize, length: u32, stride: u32, unsafe_scope: u8, reserved: u8) PolicyError!MmioRange {",
    "pub fn rangeInteropPolicyByte(base_addr: usize, length: u32, stride: u32, unsafe_scope: u8) PolicyError!MmioRange {",
    "pub fn readInteropPolicy(comptime T: type, policy: abi.InteropPolicy, ptr: *const volatile T) PolicyError!T {",
    "pub fn exchangeInteropPolicyBytes(",
    "pub fn read64InteropPolicyBytes(base_addr: usize, byte_offset: usize, unsafe_scope: u8, reserved: u8) PolicyError!u64 {",
    "pub fn constPointerAt(comptime T: type, range: MmioRange, byte_offset: usize) PolicyError!*const volatile T {",
    "pub fn pointerAt(comptime T: type, range: MmioRange, byte_offset: usize) PolicyError!*volatile T {",
    "pub fn readAt(comptime T: type, range: MmioRange, byte_offset: usize) PolicyError!T {",
    "pub fn writeAt(comptime T: type, range: MmioRange, byte_offset: usize, value: T) PolicyError!void {",
    "pub fn exchangeAt(comptime T: type, range: MmioRange, byte_offset: usize, value: T) PolicyError!T {",
    "pub fn writeMaskedAt(",
    "test \"phase3 mmio helper keeps range-bound accessors inside the blessed MMIO window\" {",
    "test \"phase3 mmio helper rejects overflowing range windows before blessing unsafe access\" {",
};

const REQUIRED_MARKERS__zigux_helpers_unsafe_policy_zig = [_][]const u8{
    "pub fn scopeFromInteropPolicyBytes(scope: u8, reserved: u8) ?abi.UnsafeScope {",
    "pub fn scopeFromInteropPolicy(policy: abi.InteropPolicy) ?abi.UnsafeScope {",
    "pub fn permitsVolatileMmioInteropPolicy(policy: abi.InteropPolicy) bool {",
    "pub fn requireVolatileMmioInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {",
    "pub fn permitsRawPointerBridgeByte(scope: u8) bool {",
    "pub fn requireRawPointerBridgeByte(scope: u8) UnsafeScopeError!void {",
};

const REQUIRED_MARKERS__zigux_unsafe_narrow_zig = [_][]const u8{
    "pub fn scopeFromInteropPolicyBytes(unsafe_scope: u8, reserved: u8) ?UnsafeScopeTag {",
    "pub fn permitsRawPointerBridgePolicyBytes(unsafe_scope: u8, reserved: u8) bool {",
    "pub fn pointerAtInteropPolicyBytes(comptime T: type, address: usize, byte_len: usize, unsafe_scope: u8, reserved: u8) RawPointerBridgeError!*align(1) T {",
    "pub fn pointerAtInteropPolicy(comptime T: type, address: usize, byte_len: usize, policy: abi.InteropPolicy) RawPointerBridgeError!*align(1) T {",
    "pub fn constPointerAtInteropPolicyBytes(comptime T: type, address: usize, unsafe_scope: u8, reserved: u8) RawPointerBridgeError!*align(1) const T {",
    "pub fn sliceAtInteropPolicy(comptime T: type, address: usize, len: usize, policy: abi.InteropPolicy) RawPointerBridgeError![]align(1) T {",
    "pub fn writeValueAtInteropPolicyBytes(comptime T: type, address: usize, value: T, unsafe_scope: u8, reserved: u8) RawPointerBridgeError!void {",
    "pub fn exchangeValueAtInteropPolicy(comptime T: type, address: usize, byte_len: usize, value: T, policy: abi.InteropPolicy) RawPointerBridgeError!T {",
    "pub fn exchangeValueAtByte(comptime T: type, address: usize, byte_len: usize, value: T, scope: u8) RawPointerBridgeError!T {",
};

const SELF_TEST_CASES = [_][]const u8{
    "const layout_assert = @import(\"layout_assert\");",
    "const narrow = @import(\"narrow\");",
    "test \"phase3 low-level wrappers keep MMIO range helpers and width aliases explicit beside raw bridge gates\" {",
    "root_module.addImport(\"layout_assert\", layout_assert);",
    "root_module.addImport(\"unsafe_policy\", unsafe_policy);",
    "root_module.addImport(\"narrow\", narrow);",
    "phase3_low_level_wrapper_step.dependOn(&phase3_low_level_wrappers.step);",
    "phase3: phase3-validate phase3-export-uapi-layout phase3-export-shim-test phase3-low-level-wrappers phase3-policy-unsafe-test phase3-test phase3-policy-dump phase3-dump",
    "zig run scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig --self-test",
    "pub fn afterAtomic() void {",
    "test \"phase3 barrier wrappers keep post-atomic full barriers explicit\" {",
    "pub fn assertMmioRangeLayout() LayoutError!void {",
    "pub fn readAt(comptime T: type, range: MmioRange, byte_offset: usize) PolicyError!T {",
    "pub fn permitsRawPointerBridgeByte(scope: u8) bool {",
    "pub fn pointerAtInteropPolicyBytes(comptime T: type, address: usize, byte_len: usize, unsafe_scope: u8, reserved: u8) RawPointerBridgeError!*align(1) T {",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
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
    const text_required_markers___github_workflows_zigux-bootstrap_yml_path = try guard.joinPath(allocator, root, "/github/workflows/zigux-bootstrap/yml");
    defer allocator.free(text_required_markers___github_workflows_zigux-bootstrap_yml_path);
    const text_required_markers___github_workflows_zigux-bootstrap_yml = try guard.readUtf8File(io, allocator, text_required_markers___github_workflows_zigux-bootstrap_yml_path);
    defer allocator.free(text_required_markers___github_workflows_zigux-bootstrap_yml);
    for (REQUIRED_MARKERS___github_workflows_zigux-bootstrap_yml) |marker| try guard.requireMarker(text_required_markers___github_workflows_zigux-bootstrap_yml, marker);
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
    const text_required_markers__zigux_helpers_layout_assert_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/layout/assert/zig");
    defer allocator.free(text_required_markers__zigux_helpers_layout_assert_zig_path);
    const text_required_markers__zigux_helpers_layout_assert_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_layout_assert_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_layout_assert_zig);
    for (REQUIRED_MARKERS__zigux_helpers_layout_assert_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_layout_assert_zig, marker);
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
    const text_self_test_cases_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_self_test_cases_path);
    const text_self_test_cases = try guard.readUtf8File(io, allocator, text_self_test_cases_path);
    defer allocator.free(text_self_test_cases);
    for (SELF_TEST_CASES) |marker| try guard.requireMarker(text_self_test_cases, marker);
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
