const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "CHECK_PHASE3_UNSAFE_POLICY_RELAYS=pass";
pub const self_test_pass_marker = "CHECK_PHASE3_UNSAFE_POLICY_RELAYS_SELF_TEST=pass";

const RELAY_GROUPS = [_][]const u8{
    "return scopeFromInteropPolicyBytes(scope, reserved);",
    "return scopeFromInteropPolicy(policy);",
    "return scopeFromByte(scope);",
    "return narrow.scopeFromInteropPolicyBytes(scope, reserved);",
    "return narrow.scopeFromInteropPolicy(policy);",
    "return narrow.scopeFromByte(scope);",
    "return narrow.recognizesInteropPolicyBytes(scope, reserved);",
    "return narrow.recognizesInteropPolicy(policy);",
    "return narrow.recognizesByte(scope);",
    "return narrow.allowsTypedOnlyAccess(scope);",
    "return narrow.permitsNoUnsafe(scope);",
    "return narrow.permitsVolatileMmio(scope);",
    "return narrow.permitsRawPointerBridge(scope);",
    "return narrow.allowsVolatileMmio(scope);",
    "return narrow.allowsRawPointerBridge(scope);",
    "return narrow.pointerAtInteropPolicyBytes(T, address, byte_len, scope, reserved);",
    "return narrow.pointerAtInteropPolicy(T, address, byte_len, policy);",
    "return narrow.pointerAtByte(T, address, byte_len, scope);",
    "return narrow.constPointerAtInteropPolicyBytes(T, address, scope, reserved);",
    "return narrow.constPointerAtInteropPolicy(T, address, policy);",
    "return narrow.constPointerAtByte(T, address, scope);",
    "return narrow.sliceAtInteropPolicyBytes(T, address, len, scope, reserved);",
    "return narrow.sliceAtInteropPolicy(T, address, len, policy);",
    "return narrow.sliceAtByte(T, address, len, scope);",
    "return narrow.constSliceAtInteropPolicyBytes(T, address, len, scope, reserved);",
    "return narrow.constSliceAtInteropPolicy(T, address, len, policy);",
    "return narrow.constSliceAtByte(T, address, len, scope);",
    "return narrow.writeValueAtInteropPolicyBytes(T, address, value, scope, reserved);",
    "return narrow.writeValueAtInteropPolicy(T, address, value, policy);",
    "return narrow.writeValueAtByte(T, address, value, scope);",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_relay_groups_path = try guard.joinPath(allocator, root, "zigux/helpers/unsafe_policy.zig");
    defer allocator.free(text_relay_groups_path);
    const text_relay_groups = try guard.readUtf8File(io, allocator, text_relay_groups_path);
    defer allocator.free(text_relay_groups);
    for (RELAY_GROUPS) |marker| try guard.requireMarker(text_relay_groups, marker);
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
