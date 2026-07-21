const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE10_FREEZE_BOUNDARY_ROUTE_SELF_TEST=pass";

const VALIDATION_COMMANDS = [_][]const u8{
    "FREEZE_BOUNDARY_COMMAND",
    "zig run scripts/zigux/validate_phase10.zig",
    "zig run scripts/zigux/validate_phase10_closure.zig",
};

const MANIFEST_PATH = [_][]const u8{
    "zigux/tests/phase10_closure_manifest.json",
};

const FREEZE_BOUNDARY_COMMAND = [_][]const u8{
    "zig run scripts/zigux/check_phase10_shared_freeze_boundary.zig --",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (VALIDATION_COMMANDS) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_PATH) |marker| try guard.requireMarker(text, marker);
    for (FREEZE_BOUNDARY_COMMAND) |marker| try guard.requireMarker(text, marker);
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
