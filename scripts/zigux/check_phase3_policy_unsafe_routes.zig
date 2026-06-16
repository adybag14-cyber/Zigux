const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_POLICY_UNSAFE_ROUTES=pass";
pub const self_test_pass_marker = "PHASE3_POLICY_UNSAFE_ROUTES_SELF_TEST=pass";

const REQUIRED_MARKERS__zigux_tests_phase3_policy_dump_zig = [_][]const u8{
    "fn rawBridgeReplay(policy: abi.InteropPolicy) RawBridgeReplay {",
    "\"safe-default\"",
    "\"mmio-bug\"",
    "\"raw-bridge-warn\"",
    "\"reserved-invalid\"",
    "\"bridge_read_ok={any}\"",
    "\"bridge_write_ok={any}\"",
    "const narrow_surface = @import(\"narrow_surface\");",
};

const REQUIRED_MARKERS__zigux_tests_phase3_policy_dump_build_zig = [_][]const u8{
    ".root_source_file = b.path(\"../bindings/abi.zig\"),",
    ".root_source_file = b.path(\"../helpers/panic_policy.zig\"),",
    ".root_source_file = b.path(\"../helpers/allocator_policy.zig\"),",
    ".root_source_file = b.path(\"../helpers/unsafe_policy.zig\"),",
    ".root_source_file = b.path(\"../unsafe/narrow.zig\"),",
    ".root_source_file = b.path(\"phase3_policy_dump.zig\"),",
    "\"phase3-policy-dump\"",
    "\"Dump the focused Phase 3 policy and unsafe substrate replay surface\"",
};

const REQUIRED_MARKERS__zigux_tests_phase3_low_level_wrappers_zig = [_][]const u8{
    "test \"phase3 low-level wrappers keep MMIO unsafe-scope gates explicit across shared handoff\" {",
    "test \"phase3 low-level wrappers keep MMIO byte-policy shorthand aligned with reserved-byte gates\" {",
    "test \"phase3 low-level wrappers keep direct MMIO scope gates explicit\" {",
    "test \"phase3 low-level wrappers keep raw-pointer bridge scope gates explicit beside MMIO policy gates\" {",
    "test \"phase3 low-level wrappers keep raw-pointer bridge byte coverage explicit\" {",
    "test \"phase3 low-level wrappers keep raw-pointer bridge interop-policy helpers explicit\" {",
};

const REQUIRED_MARKERS__zigux_tests_phase3_low_level_wrappers_build_zig = [_][]const u8{
    ".root_source_file = b.path(\"../helpers/atomic.zig\"),",
    ".root_source_file = b.path(\"../helpers/barrier.zig\"),",
    ".root_source_file = b.path(\"../helpers/mmio.zig\"),",
    ".root_source_file = b.path(\"../helpers/unsafe_policy.zig\"),",
    ".root_source_file = b.path(\"../unsafe/narrow.zig\"),",
    ".root_source_file = b.path(\"phase3_low_level_wrappers.zig\"),",
    "\"phase3-low-level-wrappers-test\"",
};

const REQUIRED_MARKERS__zigux_helpers_unsafe_policy_zig = [_][]const u8{
    "pub fn requiresVolatileMmioAccessInteropPolicy(policy: abi.InteropPolicy) bool {",
    "pub fn requiresRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {",
    "pub fn allowsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {",
    "pub fn requiresDedicatedAuditInteropPolicy(policy: abi.InteropPolicy) bool {",
};

const REQUIRED_MARKERS__zigux_helpers_mmio_zig = [_][]const u8{
    "pub fn readInteropPolicy(comptime T: type, policy: abi.InteropPolicy, ptr: *const volatile T) PolicyError!T {",
    "pub fn writeInteropPolicy(comptime T: type, policy: abi.InteropPolicy, ptr: *volatile T, value: T) PolicyError!void {",
    "pub fn exchangeInteropPolicy(comptime T: type, policy: abi.InteropPolicy, ptr: *volatile T, value: T) PolicyError!T {",
    "pub fn writeMaskedInteropPolicy(",
    "pub fn readInteropPolicyBytes(",
    "pub fn exchangeInteropPolicyBytes(",
};

const REQUIRED_MARKERS__zigux_unsafe_narrow_zig = [_][]const u8{
    "pub const Surface = enum {",
    "pub fn accessBoundaryFromInteropPolicy(policy: abi.InteropPolicy) ?AccessBoundary {",
    "pub fn requireRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {",
    "pub fn constSliceAtInteropPolicy(comptime T: type, address: usize, len: usize, policy: abi.InteropPolicy) RawPointerBridgeError![]align(1) const T {",
    "pub fn writeValueAtInteropPolicy(comptime T: type, address: usize, value: T, policy: abi.InteropPolicy) RawPointerBridgeError!void {",
};

const SELF_TEST_CASES = [_][]const u8{
    "\"bridge_write_ok={any}\"",
    "\"phase3-policy-dump\"",
    "test \"phase3 low-level wrappers keep raw-pointer bridge byte coverage explicit\" {",
    "\"phase3-low-level-wrappers-test\"",
    "pub fn requiresRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {",
    "pub fn exchangeInteropPolicyBytes(",
    "pub fn constSliceAtInteropPolicy(comptime T: type, address: usize, len: usize, policy: abi.InteropPolicy) RawPointerBridgeError![]align(1) const T {",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_markers__zigux_tests_phase3_policy_dump_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/policy/dump/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_policy_dump_zig_path);
    const text_required_markers__zigux_tests_phase3_policy_dump_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_policy_dump_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_policy_dump_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_policy_dump_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_policy_dump_zig, marker);
    const text_required_markers__zigux_tests_phase3_policy_dump_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/policy/dump/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_policy_dump_build_zig_path);
    const text_required_markers__zigux_tests_phase3_policy_dump_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_policy_dump_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_policy_dump_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_policy_dump_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_policy_dump_build_zig, marker);
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
    const text_required_markers__zigux_helpers_unsafe_policy_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/unsafe/policy/zig");
    defer allocator.free(text_required_markers__zigux_helpers_unsafe_policy_zig_path);
    const text_required_markers__zigux_helpers_unsafe_policy_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_unsafe_policy_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_unsafe_policy_zig);
    for (REQUIRED_MARKERS__zigux_helpers_unsafe_policy_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_unsafe_policy_zig, marker);
    const text_required_markers__zigux_helpers_mmio_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/mmio/zig");
    defer allocator.free(text_required_markers__zigux_helpers_mmio_zig_path);
    const text_required_markers__zigux_helpers_mmio_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_mmio_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_mmio_zig);
    for (REQUIRED_MARKERS__zigux_helpers_mmio_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_mmio_zig, marker);
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
