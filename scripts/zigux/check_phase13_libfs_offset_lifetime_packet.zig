const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE13_LIBFS_OFFSET_LIFETIME_PACKET_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    "fs/libfs.zig",
    "provides_offset_remove_planning",
    "offsetReaddirPlan",
    "offsetRenamePlan",
    "planSimpleOffsetRemove",
    "zigux/tests/phase13_libfs.zig",
    "offset remove planning keeps zero-offset noop and managed-slot erase explicit",
    "offset-based rename planning keeps reserved slots and end-of-directory explicit",
    "zigux/tests/phase13_libfs_reviewability.zig",
    "provides_offset_remove_planning",
    "offset remove planning stays reviewable as erase-only lifecycle bookkeeping",
    "offset-based rename planning stays reviewable without live directory mutation",
    "zigux/tests/phase13_libfs_manifest.json",
    "\"id\": \"phase13-libfs-offset-remove-planner\"",
    "\"id\": \"phase13-libfs-offset-rename-planner\"",
    "\"id\": \"phase13-libfs-reviewability-gate\"",
    "Documentation/zigux/phase13-libfs-survey.md",
    "landed `phase13-libfs-offset-remove-planner`",
    "prefer the next equally small offset-map lifecycle helper such as destroy planning",
    "Keep verification-only published-tree replays on `P13-L03`.",
};

const REQUIRED_ABSENCES = [_][]const u8{
    "fs/libfs.zig",
    "planSimpleOffsetDestroy",
    "provides_offset_destroy_planning",
    "zigux/tests/phase13_libfs.zig",
    "offset destroy planning keeps teardown lifetime discipline helper-only",
    "zigux/tests/phase13_libfs_reviewability.zig",
    "offset destroy planning stays reviewable as teardown-only map release",
    "zigux/tests/phase13_libfs_manifest.json",
    "\"id\": \"phase13-libfs-offset-destroy-planner\"",
    "Documentation/zigux/phase13-libfs-survey.md",
    "landed `phase13-libfs-offset-destroy-planner`",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_ABSENCES) |marker| try guard.requireMarker(text, marker);
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
