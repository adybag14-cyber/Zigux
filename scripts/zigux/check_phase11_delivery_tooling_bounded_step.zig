const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_DELIVERY_TOOLING_BOUNDED_STEP_SELF_TEST=pass";

const DEFAULT_ROOT = [_][]const u8{
    "Path.resolve.parents[2]iflen>3elsePath.cwd",
};

const EXPECTED_GOLDEN_CHECKER_COMMANDS = [_][]const u8{
    "[python",
    "str",
    "--self-test]",
    "[python",
    "str]",
};

const EXPECTED_GOLDEN_MARKERS = [_][]const u8{
    "scripts/zigux/check_phase11_deterministic_fixture_golden_output.zig",
    "zigux/tests/fixtures/phase11_validate_checks.json",
    "inside the deterministic validator packet",
};

const EXPECTED_VALIDATE_ROUTE = [_][]const u8{
    "make -C zigux phase11-validate",
};

const EXPECTED_VALIDATE_SCRIPT = [_][]const u8{
    "scripts\zigux/validate_phase11.zig",
};

const EXPECTED_GOLDEN_STATUS = [_][]const u8{
    "standalone_pending_aggregate_route",
};

const EXPECTED_GOLDEN_CHECKER_NAME = [_][]const u8{
    "phase11-deterministic-fixture-golden-output",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (DEFAULT_ROOT) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_GOLDEN_CHECKER_COMMANDS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_GOLDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_VALIDATE_ROUTE) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_VALIDATE_SCRIPT) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_GOLDEN_STATUS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_GOLDEN_CHECKER_NAME) |marker| try guard.requireMarker(text, marker);
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
