const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_MMIO_WINDOW_CONTRACT=pass";
pub const self_test_pass_marker = "PHASE3_MMIO_WINDOW_CONTRACT_SELF_TEST=pass";

const SELF_TEST_CONTRACT__zigux_helpers_mmio_zig = [_][]const u8{
    "pub const MmioRange = extern struct {",
    "pub fn allowsInteropPolicy(policy: abi.InteropPolicy) bool {",
    "pub fn requireVolatileMmioScope(scope: abi.UnsafeScope) PolicyError!void {",
    "pub fn rangeScoped(base_addr: usize, length: u32, stride: u32, scope: abi.UnsafeScope) PolicyError!MmioRange {",
    "pub fn rangeInteropPolicy(base_addr: usize, length: u32, stride: u32, policy: abi.InteropPolicy) PolicyError!MmioRange {",
    "pub fn rangeInteropPolicyBytes(base_addr: usize, length: u32, stride: u32, unsafe_scope: u8, reserved: u8) PolicyError!MmioRange {",
    "pub fn rangeInteropPolicyByte(base_addr: usize, length: u32, stride: u32, unsafe_scope: u8) PolicyError!MmioRange {",
    "pub fn read8InteropPolicyBytes(base_addr: usize, byte_offset: usize, unsafe_scope: u8, reserved: u8) PolicyError!u8 {",
    "pub fn write8InteropPolicyBytes(base_addr: usize, byte_offset: usize, value: u8, unsafe_scope: u8, reserved: u8) PolicyError!void {",
    "pub fn read32InteropPolicyByte(base_addr: usize, byte_offset: usize, unsafe_scope: u8) PolicyError!u32 {",
    "pub fn write32InteropPolicyByte(base_addr: usize, byte_offset: usize, value: u32, unsafe_scope: u8) PolicyError!void {",
    "pub fn read64InteropPolicyBytes(base_addr: usize, byte_offset: usize, unsafe_scope: u8, reserved: u8) PolicyError!u64 {",
    "pub fn write64InteropPolicyBytes(base_addr: usize, byte_offset: usize, value: u64, unsafe_scope: u8, reserved: u8) PolicyError!void {",
    "test \"phase3 mmio helper keeps helper-local ranges and width aliases explicit\" {",
};

const SELF_TEST_CONTRACT__zigux_tests_phase3_low_level_wrappers_zig = [_][]const u8{
    "test \"phase3 low-level wrappers keep MMIO range helpers and width aliases explicit beside raw bridge gates\" {",
    "const scoped_range = try mmio.rangeScoped(base_addr, 16, 4, .volatile_mmio);",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.rangeInteropPolicy(base_addr, 16, 4, raw_policy));",
    "const policy_range = try mmio.rangeInteropPolicy(base_addr, 16, 4, mmio_policy);",
    "const byte_range = try mmio.rangeInteropPolicyByte(base_addr, 16, 4, mmio_scope);",
    "try mmio.write8InteropPolicyBytes(base_addr, 1, 0x44, mmio_scope, 0);",
    "try std.testing.expectEqual(@as(u8, 0x44), try mmio.read8InteropPolicyBytes(base_addr, 1, mmio_scope, 0));",
    "try mmio.write32InteropPolicyByte(base_addr, 4, 0xCAFE_BABE, mmio_scope);",
    "try std.testing.expectEqual(@as(u32, 0xCAFE_BABE), try mmio.read32InteropPolicyByte(base_addr, 4, mmio_scope));",
    "try mmio.write64InteropPolicyBytes(base_addr, 8, 0x0123_4567_89AB_CDEF, mmio_scope, 0);",
    "try narrow.readValueAtInteropPolicyBytes(u64, base_addr + 8, @sizeOf(u64), raw_scope, 0),",
    "try std.testing.expectError(error.UnsafeScopeDenied, narrow.constPointerAtByte(u32, base_addr + 4, mmio_scope));",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_self_test_contract__zigux_helpers_mmio_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/mmio/zig");
    defer allocator.free(text_self_test_contract__zigux_helpers_mmio_zig_path);
    const text_self_test_contract__zigux_helpers_mmio_zig = try guard.readUtf8File(io, allocator, text_self_test_contract__zigux_helpers_mmio_zig_path);
    defer allocator.free(text_self_test_contract__zigux_helpers_mmio_zig);
    for (SELF_TEST_CONTRACT__zigux_helpers_mmio_zig) |marker| try guard.requireMarker(text_self_test_contract__zigux_helpers_mmio_zig, marker);
    const text_self_test_contract__zigux_tests_phase3_low_level_wrappers_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/low/level/wrappers/zig");
    defer allocator.free(text_self_test_contract__zigux_tests_phase3_low_level_wrappers_zig_path);
    const text_self_test_contract__zigux_tests_phase3_low_level_wrappers_zig = try guard.readUtf8File(io, allocator, text_self_test_contract__zigux_tests_phase3_low_level_wrappers_zig_path);
    defer allocator.free(text_self_test_contract__zigux_tests_phase3_low_level_wrappers_zig);
    for (SELF_TEST_CONTRACT__zigux_tests_phase3_low_level_wrappers_zig) |marker| try guard.requireMarker(text_self_test_contract__zigux_tests_phase3_low_level_wrappers_zig, marker);
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
