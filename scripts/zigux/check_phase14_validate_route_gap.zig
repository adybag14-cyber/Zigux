const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE14_VALIDATE_ROUTE_GAP_SELF_TEST=pass";

const TESTS_README_RERUN_LINES = [_][]const u8{
    "tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check_phase14_tests_readme_smoke_summary.zig --self-test",
    "tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check_phase14_tests_readme_smoke_summary.zig",
};

const VALIDATOR_PATH = [_][]const u8{
    "scripts\zigux/validate_phase14.zig",
};

const MAKEFILE_PATH = [_][]const u8{
    "zigux/Makefile",
};

const VALIDATE_TARGET_LINE = [_][]const u8{
    "\\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase14.zig",
};

const PHASE14_WRAPPER_LINE = [_][]const u8{
    "phase14: phase14-validate phase14-smoke phase14-test",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (TESTS_README_RERUN_LINES) |marker| try guard.requireMarker(text, marker);
    for (VALIDATOR_PATH) |marker| try guard.requireMarker(text, marker);
    for (MAKEFILE_PATH) |marker| try guard.requireMarker(text, marker);
    for (VALIDATE_TARGET_LINE) |marker| try guard.requireMarker(text, marker);
    for (PHASE14_WRAPPER_LINE) |marker| try guard.requireMarker(text, marker);
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
