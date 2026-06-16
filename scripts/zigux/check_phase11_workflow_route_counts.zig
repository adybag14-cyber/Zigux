const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_WORKFLOW_ROUTE_COUNTS_SELF_TEST=pass";

const FORBIDDEN_RUN_LINES = [_][]const u8{
    "run: make -C zigux phase11",
    "run: make -C zigux phase11-contract",
};

const SELFTEST_STEP_NAME = [_][]const u8{
    "Self-test current Phase 11 workflow route checker",
};

const SELFTEST_STEP_RUN = [_][]const u8{
    "zig run scripts/zigux/check_phase11_workflow_route_counts.zig -- --self-test",
};

const CHECK_STEP_NAME = [_][]const u8{
    "Check current Phase 11 workflow route packet",
};

const CHECK_STEP_RUN = [_][]const u8{
    "zig run scripts/zigux/check_phase11_workflow_route_counts.zig --",
};

const VALIDATE_STEP_NAME = [_][]const u8{
    "Validate current Phase 11 support bundle",
};

const VALIDATE_STEP_RUN = [_][]const u8{
    "make -C zigux phase11-validate",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (FORBIDDEN_RUN_LINES) |marker| try guard.requireMarker(text, marker);
    for (SELFTEST_STEP_NAME) |marker| try guard.requireMarker(text, marker);
    for (SELFTEST_STEP_RUN) |marker| try guard.requireMarker(text, marker);
    for (CHECK_STEP_NAME) |marker| try guard.requireMarker(text, marker);
    for (CHECK_STEP_RUN) |marker| try guard.requireMarker(text, marker);
    for (VALIDATE_STEP_NAME) |marker| try guard.requireMarker(text, marker);
    for (VALIDATE_STEP_RUN) |marker| try guard.requireMarker(text, marker);
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
