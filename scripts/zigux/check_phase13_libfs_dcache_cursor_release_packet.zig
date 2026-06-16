const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE13_LIBFS_DCACHE_CURSOR_RELEASE_PACKET_SELF_TEST=pass";

const DOC_MARKERS = [_][]const u8{
    "`fs/libfs.c`",
    "`fs/libfs_dcache_cursor_release.zig`",
    "`zigux/tests/phase13_libfs_dcache_cursor_release.zig`",
    "`zigux/tests/phase13_libfs_dcache_cursor_release_manifest.json`",
    "`scripts/zigux/check_phase13_libfs_dcache_cursor_release_packet.zig`",
    "`dcache_dir_close()`",
    "shared Phase 13 build route",
    "fresh packet-local reread",
};

const HELPER_MARKERS = [_][]const u8{
    "pub const DcacheCursorReleasePacketDescriptor",
    "claims_live_cursor_unlink: bool = false",
    "claims_lock_ordering: bool = false",
    "pub fn planDcacheDirClose(",
    "waiting_for_end_of_directory",
    "waiting_for_cursor_consumption",
    "ready_for_teardown",
};

const REPLAY_MARKERS = [_][]const u8{
    "dcache dir close planner keeps cursor teardown reviewable",
    "waiting_for_end_of_directory",
    "waiting_for_cursor_consumption",
    "ready_for_teardown",
};

const EXPECTED_GAPS = [_][]const u8{
    "phase13-libfs-dcache-dir-close-release-planner",
    "starter_landed",
    "phase13-libfs-dcache-cursor-release-review-packet",
    "starter_landed",
    "phase13-build-gate",
    "missing_on_current_master",
    "phase13-libfs-live-cursor-unlink",
    "blocked_on_dcache_state",
    "phase13-libfs-live-cursor-release-lock-ordering",
    "blocked_on_locking",
};

const DOC_PATH = [_][]const u8{
    "Documentation/zigux/phase13-libfs-dcache-cursor-release-planner.md",
};

const HELPER_PATH = [_][]const u8{
    "fs/libfs_dcache_cursor_release.zig",
};

const REPLAY_PATH = [_][]const u8{
    "zigux/tests/phase13_libfs_dcache_cursor_release.zig",
};

const MANIFEST_PATH = [_][]const u8{
    "zigux/tests/phase13_libfs_dcache_cursor_release_manifest.json",
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
