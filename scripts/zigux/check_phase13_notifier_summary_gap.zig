const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE13_NOTIFIER_SUMMARY_GAP_SELF_TEST=pass";

const MISSING_NOTE_MARKERS = [_][]const u8{
    "`Documentation/zigux/phase13-notifier-list-survey.md`",
    "`zigux/tests/phase13_notifier_list_manifest.json`",
    "`zigux/tests/phase13_notifier_list_reviewability.zig`",
    "`zigux/tests/phase13_build.zig`",
};

const SCRIPTS_README_GAP_MARKERS = [_][]const u8{
    "`zigux/tests/phase13_notifier_list_manifest.json`",
    "`zigux/tests/phase13_notifier_list_reviewability.zig`",
    "`zigux/tests/phase13_build.zig`",
};

const STILL_MISSING_DIRECT_MARKERS = [_][]const u8{
    "`scripts/zigux/check_phase13_notifier_packet.zig`",
    "`include/zigux/notifier_abi.h`",
    "`zigux/helpers/list_view.zig`",
    "`zigux/helpers/hlist_view.zig`",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (MISSING_NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SCRIPTS_README_GAP_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (STILL_MISSING_DIRECT_MARKERS) |marker| try guard.requireMarker(text, marker);
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
