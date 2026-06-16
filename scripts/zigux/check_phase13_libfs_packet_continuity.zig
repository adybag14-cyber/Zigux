const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE13_LIBFS_PACKET_CONTINUITY_SELF_TEST=pass";

const SURVEY_MARKERS = [_][]const u8{
    "PHASE13_SLICE=libfs-helper-filesystem-boundary-survey",
    "phase13-libfs-addressability-helper",
    "phase13-libfs-reviewability-gate",
    "blocked `phase13-build-gate`",
    "blocked `phase13-libfs-live-dcache-mutation`",
    "blocked `phase13-libfs-live-inode-state`",
    "offset-map lifecycle helper such as destroy planning",
    "Keep verification-only published-tree replays on `P13-L03`.",
};

const TEST_MARKERS = [_][]const u8{
    "test \"offset add planning keeps busy-remap and managed-offset boundaries explicit\"",
    "test \"offset remove planning keeps zero-offset noop and managed-slot erase explicit\"",
    "\"id\": \"phase13-libfs-addressability-helper\"",
    "\"id\": \"phase13-libfs-reviewability-gate\"",
    "\"id\": \"phase13-build-gate\"",
    "\"id\": \"phase13-libfs-live-dcache-mutation\"",
    "\"id\": \"phase13-libfs-live-inode-state\"",
    "simple_offset_add()",
    "simple_offset_remove()",
    "generic_check_addressable()",
};

const REVIEWABILITY_MARKERS = [_][]const u8{
    "test \"offset add and rename helpers stay reviewable as managed-slot planners rather than live directory mutation\"",
    "test \"offset remove planning stays reviewable as erase-only lifecycle bookkeeping\"",
    "planSimpleOffsetAdd",
    "planSimpleOffsetRemove",
};

const MANIFEST_EXPECTATIONS = [_][]const u8{
    "phase13-libfs-helper-starter",
    "starter_landed",
    "phase13-libfs-offset-add-planner",
    "starter_landed",
    "phase13-libfs-offset-remove-planner",
    "starter_landed",
    "phase13-libfs-offset-rename-planner",
    "starter_landed",
    "phase13-libfs-transaction-acquire-helper",
    "starter_landed",
    "phase13-libfs-transaction-release-helper",
    "starter_landed",
    "phase13-libfs-transaction-publish-helper",
    "starter_landed",
    "phase13-libfs-addressability-helper",
    "starter_landed",
    "phase13-libfs-reviewability-gate",
    "starter_landed",
    "phase13-libfs-survey-note",
    "starter_landed",
    "phase13-build-gate",
    "blocked_on_shared_build_surface",
    "phase13-libfs-live-dcache-mutation",
    "blocked_on_dcache_state",
    "phase13-libfs-live-inode-state",
    "blocked_on_inode_state",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (TEST_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REVIEWABILITY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_EXPECTATIONS) |marker| try guard.requireMarker(text, marker);
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
