const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE14_RING_BUFFER_COMPILE_ROUTE_SELF_TEST=pass";

const NOTE_MARKERS = [_][]const u8{
    "current public raw-file readback now recovers `zigux/tests/phase14_ring_buffer_survey.zig`, while `zigux/tests/phase14_build.zig` still does not return through this lane's exact contents path",
    "`zig test zigux/tests/phase14_ring_buffer_survey.zig`",
    "`zig build phase14-smoke --build-file zigux/tests/phase14_build.zig`",
    "shared smoke manifest still records that focused build-shard command as historical vocabulary only",
};

const VALIDATOR_MARKERS = [_][]const u8{
    "RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH = \"scripts/zigux/check_phase14_ring_buffer_compile_route.zig\"",
    "run_guardrail_checker(n                args.root,n                RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH,n                self_test=False,",
};

const REQUIRED_MANIFEST_VALUES = [_][]const u8{
    "smoke_shard_commands",
    "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig",
    "survey_summary",
    "phase14_validate_runs_ring_buffer_compile_route_checker",
    "survey_summary",
    "shared_manifest_records_ring_buffer_compile_route_checker",
};

const MARKER = [_][]const u8{
    "PHASE14_CHECK_PACKET=ring_buffer_compile_route",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (VALIDATOR_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_MANIFEST_VALUES) |marker| try guard.requireMarker(text, marker);
    for (MARKER) |marker| try guard.requireMarker(text, marker);
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
