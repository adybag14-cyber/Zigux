const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_POLICY_UNSAFE_WINDOW_REPLAY=pass";
pub const self_test_pass_marker = "PHASE3_POLICY_UNSAFE_WINDOW_REPLAY_SELF_TEST=pass";

const REQUIRED_MARKERS__zigux_helpers_unsafe_policy_zig = [_][]const u8{
    "pub const RawPointerWindow = struct {",
    "pub const RawPointerWindowError = RawPointerBridgeError || error{",
    "fn requireWindowAddress(window: RawPointerWindow, byte_offset: usize, access_len: usize) RawPointerWindowError!usize {",
    "pub fn windowInteropPolicy(",
    "pub fn windowByte(base_addr: usize, byte_len: usize, scope: u8) RawPointerWindowError!RawPointerWindow {",
    "pub fn pointerAtWindow(",
    "pub fn constPointerAtWindow(",
    "pub fn sliceAtWindow(",
    "pub fn constSliceAtWindow(",
    "pub fn readValueAtWindow(",
    "pub fn writeValueAtWindow(",
    "pub fn exchangeValueAtWindow(",
    "test \"phase3 unsafe policy keeps raw-pointer bridge windows bounded\" {",
    "try std.testing.expectError(error.AccessOutsideWindow, pointerAtWindow(u32, window, byte_len));",
    "try std.testing.expectError(error.OffsetOverflow, readValueAtWindow(u32, window, std.math.maxInt(usize)));",
};

const REQUIRED_MARKERS__zigux_tests_phase3_policy_unsafe_zig = [_][]const u8{
    "test \"phase3 policy unsafe replay keeps raw-pointer windows bounded\" {",
    "const window = try unsafe_policy.windowInteropPolicy(base_addr, byte_len, raw);",
    "try testing.expectEqual(window, try unsafe_policy.windowByte(base_addr, byte_len, abi.UNSAFE_RAW_POINTER_BRIDGE));",
    "const first = try unsafe_policy.pointerAtWindow(u32, window, 0);",
    "const second = try unsafe_policy.constPointerAtWindow(u32, window, @sizeOf(u32));",
    "const mutable_slice = try unsafe_policy.sliceAtWindow(u32, window, 0, bridge_words.len);",
    "const replay_slice = try unsafe_policy.constSliceAtWindow(u32, window, 0, bridge_words.len);",
    "try unsafe_policy.writeValueAtWindow(u32, window, @sizeOf(u32) * 2, 73);",
    "try unsafe_policy.exchangeValueAtWindow(u32, window, @sizeOf(u32) * 2, 79),",
    "try testing.expectError(error.AccessOutsideWindow, unsafe_policy.pointerAtWindow(u32, window, byte_len));",
    "try testing.expectError(error.OffsetOverflow, unsafe_policy.readValueAtWindow(u32, window, std.math.maxInt(usize)));",
};

const SELF_TEST_MUTATIONS = [_][]const u8{
    "missing helper window type",
    "missing helper outside-window proof",
    "missing replay test",
    "missing replay write window proof",
    "missing replay overflow proof",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_markers__zigux_helpers_unsafe_policy_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/unsafe/policy/zig");
    defer allocator.free(text_required_markers__zigux_helpers_unsafe_policy_zig_path);
    const text_required_markers__zigux_helpers_unsafe_policy_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_unsafe_policy_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_unsafe_policy_zig);
    for (REQUIRED_MARKERS__zigux_helpers_unsafe_policy_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_unsafe_policy_zig, marker);
    const text_required_markers__zigux_tests_phase3_policy_unsafe_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/policy/unsafe/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_policy_unsafe_zig_path);
    const text_required_markers__zigux_tests_phase3_policy_unsafe_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_policy_unsafe_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_policy_unsafe_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_policy_unsafe_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_policy_unsafe_zig, marker);
    const text_self_test_mutations_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_self_test_mutations_path);
    const text_self_test_mutations = try guard.readUtf8File(io, allocator, text_self_test_mutations_path);
    defer allocator.free(text_self_test_mutations);
    for (SELF_TEST_MUTATIONS) |marker| try guard.requireMarker(text_self_test_mutations, marker);
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
