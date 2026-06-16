const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE14_RING_BUFFER_SHARED_ROUTE_GAP_SELF_TEST=pass";

const NOTE_MARKERS = [_][]const u8{
    "PHASE14_GAP=ring-buffer-shared-route-checker-undercount",
    "PHASE14_REPAIR_TARGET=scripts/zigux/check_phase14_shared_smoke_route.zig",
    "RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH",
    "survey_summary.phase14_validate_runs_ring_buffer_compile_route_checker == true",
    "survey_summary.shared_manifest_records_ring_buffer_compile_route_checker == true",
};

const VALIDATOR_MARKERS = [_][]const u8{
    "RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH = (n    \"scripts/zigux/check_phase14_ring_buffer_compile_route.zig\"n)",
    "run_guardrail_checker(n                args.root,n                RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH,n                self_test=False,",
};

const SHARED_ROUTE_CURRENT_GAP_MARKERS = [_][]const u8{
    "SKBUFF_COMPILE_ROUTE_CHECKER_PATH = \"scripts/zigux/check_phase14_skbuff_compile_route.zig\"",
    "RCU_COMPILE_ROUTE_CHECKER_PATH = \"scripts/zigux/check_phase14_rcu_compile_route.zig\"",
    "phase14_validate_runs_skbuff_compile_route_checker",
    "phase14_validate_runs_rcu_compile_route_checker",
};

const SHARED_ROUTE_EXPECTED_MISSING_MARKERS = [_][]const u8{
    "RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH",
    "phase14_validate_runs_ring_buffer_compile_route_checker",
    "shared_manifest_records_ring_buffer_compile_route_checker",
};

const REQUIRED_MANIFEST_VALUES = [_][]const u8{
    "p14_l05_anti_regression_readback",
    "observed_checker_gap",
    "scripts\zigux/validate_phase14.zig already runs the ring-buffer compile-route checker and this manifest already records the ring-buffer summary booleans, but scripts/zigux/check_phase14_shared_smoke_route.zig currently fail-closes only the validator-side skbuff and RCU compile-route calls.",
    "p14_l05_anti_regression_readback",
    "next_checker_only_repair",
    "Teach scripts/zigux/check_phase14_shared_smoke_route.zig to require RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH, its run_guardrail_checker call, and the existing phase14_validate_runs_ring_buffer_compile_route_checker plus shared_manifest_records_ring_buffer_compile_route_checker manifest booleans.",
    "survey_summary",
    "phase14_validate_runs_ring_buffer_compile_route_checker",
    "survey_summary",
    "shared_manifest_records_ring_buffer_compile_route_checker",
};

const MARKER = [_][]const u8{
    "PHASE14_CHECK_PACKET=ring_buffer_shared_route_gap",
};

const RCU_COMPILE_ROUTE_CHECKER_PATH = [_][]const u8{
    "scripts/zigux/check_phase14_rcu_compile_route.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (VALIDATOR_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SHARED_ROUTE_CURRENT_GAP_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SHARED_ROUTE_EXPECTED_MISSING_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_MANIFEST_VALUES) |marker| try guard.requireMarker(text, marker);
    for (MARKER) |marker| try guard.requireMarker(text, marker);
    for (RCU_COMPILE_ROUTE_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
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
