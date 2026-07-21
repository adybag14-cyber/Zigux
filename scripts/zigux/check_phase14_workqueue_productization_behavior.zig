const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE14_WORKQUEUE_PRODUCTIZATION_BEHAVIOR_SELF_TEST=pass";

const EXACT_CHECKS = [_][]const u8{
    "zig run scripts/zigux/check_phase14_shared_smoke_route.zig -- --self-test",
    "zig run scripts/zigux/check_phase14_shared_smoke_route.zig --",
    "zig run scripts/zigux/check_phase14_tests_readme_smoke_summary.zig -- --self-test",
    "zig run scripts/zigux/check_phase14_tests_readme_smoke_summary.zig --",
    "zig run scripts/zigux/validate_phase14.zig -- --self-test",
    "zig run scripts/zigux/validate_phase14.zig",
    "zig run scripts/zigux/check_phase14_rollback_threshold_sequencing.zig -- --self-test",
    "zig run scripts/zigux/check_phase14_rollback_threshold_sequencing.zig --",
    "zig run scripts/zigux/check_phase14_release_boundary_exact_counts.zig -- --self-test",
    "zig run scripts/zigux/check_phase14_release_boundary_exact_counts.zig --",
    "make -C zigux phase14-validate",
};

const SURVEY_MARKERS = [_][]const u8{
    "`PHASE14_STATUS=blocked_maintenance`",
    "`PHASE14_LANE_KEY=P14-L04`",
    "`PHASE14_CURRENT_SLICE=phase14-workqueue-scheduler-visible-worker-state-refinement`",
    "`PHASE14_REVIEWABILITY_TEST=zigux/tests/phase14_workqueue_reviewability.zig`",
    "productization behavior is only considered verified",
    "They do not promote the workqueue bridge to owner status",
};

const SLICE_MARKERS = [_][]const u8{
    "`PHASE14_LANE_KEY=P14-L04`",
    "`PHASE14_STATUS=blocked_maintenance`",
    "`PHASE14_REVIEWABILITY_TEST=zigux/tests/phase14_workqueue_reviewability.zig`",
    "shared-packet evidence rather than a bridge-local trust promotion signal",
};

const MANIFEST_MARKERS = [_][]const u8{
    "\"lane_key\": \"P14-L04\"",
    "\"current_lane_posture\": \"blocked_maintenance\"",
    "\"productization_posture\": \"shared_packet_local_only\"",
    "\"productization_behavior_note\": \"These checks verify shared packet-local productization behavior around the current phase14-validate route and its reminder surfaces. They do not replace the direct workqueue reviewability replay as the bridge-local trust gate.\"",
};

const REVIEWABILITY_MARKERS = [_][]const u8{
    "const expected_productization_exact_checks = [_][]const u8{",
    "\"zig run scripts/zigux/check_phase14_shared_smoke_route.zig -- --self-test\",",
    "\"zig run scripts/zigux/check_phase14_release_boundary_exact_counts.zig --\",",
    "\"make -C zigux phase14-validate\",",
};

const MAKEFILE_MARKERS = [_][]const u8{
    "phase14-validate:",
    "scripts/zigux/check_phase14_shared_smoke_route.zig --self-test",
    "scripts/zigux/check_phase14_shared_smoke_route.zig",
    "scripts/zigux/check_phase14_tests_readme_smoke_summary.zig --self-test",
    "scripts/zigux/check_phase14_tests_readme_smoke_summary.zig",
    "scripts\zigux/validate_phase14.zig --self-test",
    "scripts\zigux/validate_phase14.zig",
    "scripts/zigux/check_phase14_rollback_threshold_sequencing.zig --self-test",
    "scripts/zigux/check_phase14_rollback_threshold_sequencing.zig",
    "scripts/zigux/check_phase14_release_boundary_exact_counts.zig --self-test",
    "scripts/zigux/check_phase14_release_boundary_exact_counts.zig",
};

const MARKER = [_][]const u8{
    "PHASE14_CHECK_PACKET=workqueue_productization_behavior",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (EXACT_CHECKS) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SLICE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REVIEWABILITY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MAKEFILE_MARKERS) |marker| try guard.requireMarker(text, marker);
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
