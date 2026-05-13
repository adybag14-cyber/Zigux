const std = @import("std");
const workqueue_bridge = @import("workqueue_bridge");

const SurveySummary = struct {
    workqueue_c_lines: usize,
    workqueue_internal_h_lines: usize,
    test_workqueue_c_lines: usize,
    preexisting_kernel_export_shim_present: bool,
    preexisting_phase14_build_present: bool,
    preexisting_phase14_make_target_present: bool,
    preexisting_workqueue_bridge_present: bool,
    preexisting_phase14_workqueue_test_present: bool,
    preexisting_phase14_workqueue_manifest_present: bool,
    preexisting_phase14_workqueue_slice_note_present: bool,
    preexisting_phase14_workqueue_survey_note_present: bool,
};

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    survey_summary: SurveySummary,
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "blocked_on_live_concurrency");
}

test "phase14 workqueue bridge manifest records the blocked-maintenance packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase14_workqueue_bridge_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P14-L04", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 14", manifest.phase);
    try std.testing.expectEqualStrings("kernel/workqueue.c", manifest.anchor);
    try std.testing.expectEqualStrings("9b98d3b9c812840bf279508030be0b8de093736c", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.workqueue_c_lines >= 8400);
    try std.testing.expect(manifest.survey_summary.workqueue_internal_h_lines >= 80);
    try std.testing.expect(manifest.survey_summary.test_workqueue_c_lines >= 290);
    try std.testing.expect(manifest.survey_summary.preexisting_kernel_export_shim_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase14_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase14_make_target_present);
    try std.testing.expect(manifest.survey_summary.preexisting_workqueue_bridge_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase14_workqueue_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase14_workqueue_manifest_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase14_workqueue_slice_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase14_workqueue_survey_note_present);
    try std.testing.expectEqual(@as(usize, 18), manifest.gaps.len);

    var starter_landed_count: usize = 0;
    var blocked_count: usize = 0;

    const expected_gap_ids = [_][]const u8{
        "phase14-build-gate",
        "phase14-make-target",
        "phase14-kernel-export-shim-foundation",
        "phase14-workqueue-boundary-map-starter",
        "phase14-workqueue-test-gate",
        "phase14-workqueue-slice-note",
        "phase14-workqueue-survey-note",
        "phase14-workqueue-concurrency-audit-outline",
        "phase14-workqueue-max-active-audit",
        "phase14-workqueue-lock-handoff-audit",
        "phase14-workqueue-pending-bit-followup",
        "phase14-workqueue-delayed-submission-alias-followup",
        "phase14-workqueue-delayed-timer-expiry-followup",
        "phase14-workqueue-delayed-requeue-governance",
        "phase14-workqueue-flush-drain-governance",
        "phase14-workqueue-rescuer-mayday-governance",
        "phase14-workqueue-scheduler-visible-worker-state-refinement",
        "phase14-workqueue-live-execution-blocker",
    };

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));
        try std.testing.expectEqualStrings(expected_gap_ids[i], gap.id);

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_live_concurrency")) {
            blocked_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase14-workqueue-boundary-map-starter")) {
            try std.testing.expectEqualStrings("kernel/workqueue_bridge.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue_work_on") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "stay-in-C") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase14-workqueue-pending-bit-followup")) {
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "try_to_grab_pending") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "pwq->refcnt") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase14-workqueue-flush-drain-governance")) {
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "work_color") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "flush_color") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase14-workqueue-scheduler-visible-worker-state-refinement")) {
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "wq_worker_running()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "WORKER_NOT_RUNNING") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase14-workqueue-live-execution-blocker")) {
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "worker_pool") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hotplug") != null);
        }
    }

    try std.testing.expectEqual(@as(usize, 17), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
}

test "phase14 workqueue bridge descriptor matches the blocked-maintenance bridge" {
    const descriptor = workqueue_bridge.WorkqueueBridgeLab.descriptor();
    const map = workqueue_bridge.WorkqueueBridgeLab.boundaryMap();
    const audit = workqueue_bridge.WorkqueueBridgeLab.concurrencyAudit();

    try std.testing.expectEqualStrings("workqueue_boundary_map_lab", descriptor.name);
    try std.testing.expectEqualStrings("kernel/workqueue.c", descriptor.anchor);
    try std.testing.expectEqualStrings("boundary_map_only", descriptor.posture);
    try std.testing.expect(descriptor.provides_boundary_map);
    try std.testing.expect(descriptor.provides_concurrency_audit_outline);
    try std.testing.expect(descriptor.provides_stay_in_c_decisions);
    try std.testing.expect(!descriptor.touches_live_worker_pools);
    try std.testing.expect(!descriptor.touches_live_work_execution);
    try std.testing.expect(!descriptor.touches_scheduler_hooks);
    try std.testing.expectEqual(@as(usize, 8), map.areas.len);
    try std.testing.expectEqual(@as(usize, 6), workqueue_bridge.WorkqueueBridgeLab.stayInCDecisionCount());
    try std.testing.expectEqual(@as(usize, 15), audit.checkpoints.len);
    try std.testing.expectEqual(@as(usize, 7), audit.blocked_live_behaviors.len);
    try std.testing.expectEqual(@as(usize, 15), workqueue_bridge.WorkqueueBridgeLab.auditCheckpointCount());
    try std.testing.expectEqualStrings("phase14-workqueue-scheduler-visible-worker-state-refinement", workqueue_bridge.WorkqueueBridgeLab.currentSliceId());
    try std.testing.expectEqualStrings("phase14-workqueue-scheduler-visible-worker-state-refinement", audit.current_slice_id);
    try std.testing.expect(std.mem.indexOf(u8, workqueue_bridge.WorkqueueBridgeLab.nextAuditFocus(), "blocked maintenance") != null);
    try std.testing.expectEqualStrings("delayed-work-timer-and-requeue", map.areas[2].id);
    try std.testing.expectEqualStrings("runtime-max-active-retuning", map.areas[5].id);
    try std.testing.expectEqualStrings("hotplug-topology-rebinding", map.areas[6].id);
    try std.testing.expectEqualStrings("pending-bit-claim-window", audit.checkpoints[8].id);
    try std.testing.expectEqualStrings("delayed-submission-aliases", audit.checkpoints[9].id);
    try std.testing.expectEqualStrings("delayed-timer-expiry-handoff", audit.checkpoints[10].id);
    try std.testing.expectEqualStrings("delayed-requeue-governance", audit.checkpoints[11].id);
    try std.testing.expectEqualStrings("flush-drain-color-governance", audit.checkpoints[12].id);
    try std.testing.expectEqualStrings("hotplug-topology-rebinding", audit.checkpoints[13].id);
    try std.testing.expectEqualStrings("scheduler-visible-worker-state-refinement", audit.checkpoints[14].id);
}
