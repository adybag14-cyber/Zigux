const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_TESTS_ROOT_TARGETLESS_WITNESS_SELF_TEST=pass";

const REQUIRED_MARKERS = [_][]const u8{
    "targetless-unregister witness",
    "targetless-unregister witness",
};

const WITNESS_CHECKER = [_][]const u8{
    "`scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig`",
};

const WITNESS_REPLAY = [_][]const u8{
    "`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`",
};

const WITNESS_BUILD = [_][]const u8{
    "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`",
};

const CLEANUP_CHECKER = [_][]const u8{
    "`scripts/zigux/check_phase11_hvc_cleanup_current_head.zig`",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (WITNESS_CHECKER) |marker| try guard.requireMarker(text, marker);
    for (WITNESS_REPLAY) |marker| try guard.requireMarker(text, marker);
    for (WITNESS_BUILD) |marker| try guard.requireMarker(text, marker);
    for (CLEANUP_CHECKER) |marker| try guard.requireMarker(text, marker);
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
