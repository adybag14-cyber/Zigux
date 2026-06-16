const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_UNSAFE_POLICY_RAW_BRIDGE=pass";
pub const self_test_pass_marker = "PHASE3_UNSAFE_POLICY_RAW_BRIDGE_SELF_TEST=pass";

const REQUIRED_MARKERS__zigux_helpers_unsafe_policy_zig = [_][]const u8{
    "pub fn permitsRawPointerBridge(scope: abi.UnsafeScope) bool {",
    "pub fn permitsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {",
    "pub fn allowsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {",
    "pub fn requireRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {",
    "pub fn allowsRawPointerBridgePolicyBytes(scope: u8, reserved: u8) bool {",
    "pub fn requireRawPointerBridgePolicyBytes(scope: u8, reserved: u8) UnsafeScopeError!void {",
    "pub fn permitsRawPointerBridgeByte(scope: u8) bool {",
    "pub fn allowsRawPointerBridgeByte(scope: u8) bool {",
    "pub fn requireRawPointerBridgeByte(scope: u8) UnsafeScopeError!void {",
    "pub fn pointerAtInteropPolicyBytes(",
    "pub fn pointerAtInteropPolicy(",
    "pub fn pointerAtByte(",
    "pub fn constPointerAtInteropPolicyBytes(",
    "pub fn constPointerAtInteropPolicy(",
    "pub fn constPointerAtByte(",
    "pub fn sliceAtInteropPolicyBytes(",
    "pub fn sliceAtInteropPolicy(",
    "pub fn sliceAtByte(",
    "pub fn constSliceAtInteropPolicyBytes(",
    "pub fn constSliceAtInteropPolicy(",
    "pub fn constSliceAtByte(",
    "pub fn writeValueAtInteropPolicyBytes(",
    "pub fn writeValueAtInteropPolicy(",
    "pub fn writeValueAtByte(",
    "test \"phase3 unsafe policy keeps raw-pointer bridge relays helper-local\" {",
};

const REQUIRED_MARKERS__zigux_unsafe_narrow_zig = [_][]const u8{
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
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
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
