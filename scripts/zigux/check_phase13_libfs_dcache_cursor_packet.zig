const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE13_LIBFS_DCACHE_CURSOR_PACKET_SELF_TEST=pass";

const DOC_MARKERS = [_][]const u8{
    "`fs/libfs.c`",
    "`fs/libfs_dcache_cursor.zig`",
    "`zigux/tests/phase13_libfs_dcache_cursor.zig`",
    "`zigux/tests/phase13_libfs_dcache_cursor_manifest.json`",
    "`scripts/zigux/check_phase13_libfs_dcache_cursor_packet.zig`",
    "`dcache_dir_open()`",
    "`dcache_readdir()`",
    "shared Phase 13 build route",
    "`dcache_dir_close()` cursor release planner",
};

const HELPER_MARKERS = [_][]const u8{
    "pub const DcacheCursorPacketDescriptor",
    ".provides_dcache_dir_open_planning = true",
    ".provides_dcache_readdir_preconditions = true",
    ".claims_live_cursor_dentry_traversal = false",
    "pub fn planDcacheDirOpen(",
    "pub fn planDcacheReaddir(",
    "ready_at_end_of_directory",
    "missing_private_cursor",
};

const REPLAY_MARKERS = [_][]const u8{
    "dcache dir open planner keeps cursor private and skips sibling mutation claims",
    "dcache readdir planner stays on preconditions and end-of-directory gating",
    "missing_private_cursor",
    "ready_at_end_of_directory",
};

const EXPECTED_GAPS = [_][]const u8{
    "phase13-libfs-dcache-dir-open-precondition-planner",
    "starter_landed",
    "phase13-libfs-dcache-readdir-precondition-planner",
    "starter_landed",
    "phase13-libfs-dcache-cursor-review-packet",
    "starter_landed",
    "phase13-build-gate",
    "missing_on_current_master",
    "phase13-libfs-live-cursor-traversal",
    "blocked_on_dcache_state",
};

const DOC_PATH = [_][]const u8{
    "Documentation/zigux/phase13-libfs-dcache-cursor-planner.md",
};

const HELPER_PATH = [_][]const u8{
    "fs/libfs_dcache_cursor.zig",
};

const REPLAY_PATH = [_][]const u8{
    "zigux/tests/phase13_libfs_dcache_cursor.zig",
};

const MANIFEST_PATH = [_][]const u8{
    "zigux/tests/phase13_libfs_dcache_cursor_manifest.json",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (DOC_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (HELPER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REPLAY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_GAPS) |marker| try guard.requireMarker(text, marker);
    for (DOC_PATH) |marker| try guard.requireMarker(text, marker);
    for (HELPER_PATH) |marker| try guard.requireMarker(text, marker);
    for (REPLAY_PATH) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_PATH) |marker| try guard.requireMarker(text, marker);
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    const io = std.Io.Threaded.init(allocator, .{});
    defer io.deinit();
    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);

    var self_test = false;
    for (args[1..]) |arg| {
        if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
    }

    if (self_test) {
        try checkText("");
        try guard.printLine(io, "{s}", .{pass_marker});
        return;
    }

    const root = try guard.repoRootFromScript(allocator);
    defer allocator.free(root);
    const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
    const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
    defer allocator.free(workflow_path);
    const text = try guard.readUtf8File(io, allocator, workflow_path);
    defer allocator.free(text);
    try checkText(text);
    try guard.printLine(io, "{s}", .{pass_marker});
}
