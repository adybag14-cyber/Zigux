const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE14_VALIDATOR_SELF_TEST=pass";

const ROLLBACK_AND_GUARDRAIL_CHECKERS = [_][]const u8{
    "ROLLBACK_THRESHOLD_SEQUENCING_CHECKER_PATH",
    "SKBUFF_STAY_IN_C_GUARDRAIL_CHECKER_PATH",
    "SKBUFF_COMPILE_ROUTE_CHECKER_PATH",
    "RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH",
    "RCU_COMPILE_ROUTE_CHECKER_PATH",
    "RCU_ROLLBACK_GUARDRAIL_CHECKER_PATH",
};

const MAKEFILE_DIRECT_ROLLBACK_GUARDRAILS = [_][]const u8{
    "scripts/zigux/check_phase14_rollback_threshold_sequencing.zig --self-test",
    "scripts/zigux/check_phase14_rollback_threshold_sequencing.zig",
    "scripts/zigux/check_phase14_skbuff_stay_in_c_guardrail.zig --self-test",
    "scripts/zigux/check_phase14_skbuff_stay_in_c_guardrail.zig",
    "scripts/zigux/check_phase14_rcu_rollback_guardrail.zig --self-test",
    "scripts/zigux/check_phase14_rcu_rollback_guardrail.zig",
};

const VALIDATOR_REQUIRED_MARKERS = [_][]const u8{
    "SUBCHECKER_PATHS = [",
    "run_guardrail_checker(base, rel_path, self_test=True)",
    "run_guardrail_checker(n                    args.root,",
    "self_test=False",
    "dedicated rollback-threshold sequencing checker",
    "dedicated skbuff stay-in-C",
    "dedicated RCU rollback guardrail",
    "PHASE14_VALIDATOR_SELF_TEST=pass",
};

const MARKER_CASES = [_][]const u8{
    "{marker_lookups}",
};

const VALIDATOR_PATH = [_][]const u8{
    "scripts\zigux/validate_phase14.zig",
};

const MAKEFILE_PATH = [_][]const u8{
    "zigux/Makefile",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (ROLLBACK_AND_GUARDRAIL_CHECKERS) |marker| try guard.requireMarker(text, marker);
    for (MAKEFILE_DIRECT_ROLLBACK_GUARDRAILS) |marker| try guard.requireMarker(text, marker);
    for (VALIDATOR_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MARKER_CASES) |marker| try guard.requireMarker(text, marker);
    for (VALIDATOR_PATH) |marker| try guard.requireMarker(text, marker);
    for (MAKEFILE_PATH) |marker| try guard.requireMarker(text, marker);
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
