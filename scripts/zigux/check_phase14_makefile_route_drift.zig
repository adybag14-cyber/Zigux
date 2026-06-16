const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE14_MAKEFILE_ROUTE_DRIFT_SELF_TEST=pass";

const REQUIRED_ROUTE_MARKERS = [_][]const u8{
    "make -C zigux phase14-validatephase14-validate:",
    "make -C zigux phase14-smokephase14-smoke:",
    "make -C zigux phase14-testphase14-test:",
};

const REQUIRED_AGGREGATE_COMMAND = [_][]const u8{
    "make -C zigux phase14",
};

const REQUIRED_AGGREGATE_TARGET = [_][]const u8{
    "phase14: phase14-validate phase14-smoke phase14-test",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_ROUTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_AGGREGATE_COMMAND) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_AGGREGATE_TARGET) |marker| try guard.requireMarker(text, marker);
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
