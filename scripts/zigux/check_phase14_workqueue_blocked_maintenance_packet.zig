const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE14_WORKQUEUE_BLOCKED_MAINTENANCE_PACKET_SELF_TEST=pass";

const REQUIRED_REPLAY_BEFORE_TRUSTING = [_][]const u8{
    "zig test zigux/tests/phase14_workqueue_reviewability.zig",
};

const REQUIRED_PRODUCTIZATION_CHECKS = [_][]const u8{
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

const REQUIRED_MARKERS = [_][]const u8{
    "PHASE14_LANE_KEY=P14-L04",
    "PHASE14_STATUS=blocked_maintenance",
    "PHASE14_SLICE=phase14-workqueue-scheduler-visible-worker-state-refinement",
    "zigux/tests/phase14_workqueue_reviewability.zig",
    "phase14-workqueue-live-execution-blocker",
    "blocked maintenance",
    "PHASE14_STATUS=blocked_maintenance",
    "PHASE14_LANE_KEY=P14-L04",
    "PHASE14_SURVEYED_COMMIT=9b98d3b9c812840bf279508030be0b8de093736c",
    "phase14-workqueue-scheduler-visible-worker-state-refinement",
    "shared Phase 14 smoke packet",
    "zig test zigux/tests/phase14_workqueue_reviewability.zig",
    "make -C zigux phase14-validate",
    "missing `phase14-smoke`, `phase14-test`, and `phase14` wrappers",
    "## Phase 14",
    "Phase 14 flow - the current scripts-root shared smoke packet stays reviewable",
    "`kernel/workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_reviewability.zig`, and `zigux/tests/phase14_workqueue_bridge_manifest.json` keep the directly readable workqueue reviewability shard explicit",
    "return \"phase14-workqueue-scheduler-visible-worker-state-refinement\";",
    ".posture = \"blocked_maintenance\",",
    "\"zigux/tests/phase14_workqueue_reviewability.zig\"",
    "\"Documentation/zigux/phase14-workqueue-bridge-slice.md\"",
    "\"Documentation/zigux/phase14-workqueue-bridge-survey.md\"",
    ".blocked_by = \"phase14-workqueue-live-execution-blocker\",",
    "try std.testing.expectEqualStrings(\"phase14-workqueue-scheduler-visible-worker-state-refinement\", workqueue_bridge.WorkqueueBridgeLab.currentSliceId());",
    "try std.testing.expect(std.mem.indexOf(u8, handoff.next_future_target, \"blocked maintenance\") != null);",
    "try std.testing.expect(std.mem.indexOf(u8, cancel_handoff.blocked_by, \"pending-bit and completion rules\") != null);",
    "try std.testing.expectEqualStrings(\"P14-L04\", manifest.lane_key);",
    "try expectGapStatus(manifest, \"phase14-workqueue-scheduler-visible-worker-state-refinement\", \"starter_landed\");",
    "try expectGapStatus(manifest, \"phase14-workqueue-live-execution-blocker\", \"blocked_on_live_concurrency\");",
    "try std.testing.expect(std.mem.indexOf(u8, survey_note, \"make -C zigux phase14-validate\") != null);",
    "try std.testing.expect(std.mem.indexOf(u8, review_checklist, \"same study-only stay-in-C posture\") != null);",
};

const REQUIRED_MANIFEST_FIELDS = [_][]const u8{
    "lane_key",
    "P14-L04",
    "phase",
    "Phase 14",
    "surveyed_commit",
    "9b98d3b9c812840bf279508030be0b8de093736c",
    "anchor",
    "kernel/workqueue.c",
};

const REQUIRED_MAINTENANCE_FIELDS = [_][]const u8{
    "current_lane_posture",
    "blocked_maintenance",
    "productization_posture",
    "shared_packet_local_only",
};

const REQUIRED_GAPS = [_][]const u8{
    "phase14-workqueue-boundary-map-starter",
    "starter_landed",
    "phase14-workqueue-delayed-timer-expiry-followup",
    "starter_landed",
    "phase14-workqueue-delayed-requeue-governance",
    "starter_landed",
    "phase14-workqueue-flush-drain-governance",
    "starter_landed",
    "phase14-workqueue-rescuer-mayday-governance",
    "starter_landed",
    "phase14-workqueue-scheduler-visible-worker-state-refinement",
    "starter_landed",
    "phase14-workqueue-live-execution-blocker",
    "blocked_on_live_concurrency",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_REPLAY_BEFORE_TRUSTING) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_PRODUCTIZATION_CHECKS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_MANIFEST_FIELDS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_MAINTENANCE_FIELDS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_GAPS) |marker| try guard.requireMarker(text, marker);
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
