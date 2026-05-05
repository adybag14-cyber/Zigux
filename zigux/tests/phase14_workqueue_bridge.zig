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
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_live_concurrency");
}

fn readFixture(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(32 * 1024),
    );
}

test "phase14 workqueue bridge manifest records the boundary-map foothold and remaining gap" {
    const manifest_json = try readFixture(std.testing.allocator, "zigux/tests/phase14_workqueue_bridge_manifest.json");
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P14-L01", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 14", manifest.phase);
    try std.testing.expectEqualStrings("kernel/workqueue.c", manifest.anchor);
    try std.testing.expectEqualStrings("9e278f632d6d5097cb8cfc2dc61744ae105baa8c", manifest.surveyed_commit);
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
    try std.testing.expectEqual(@as(usize, 14), manifest.gaps.len);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_build_gate = false;
    var saw_make_target = false;
    var saw_export_shim = false;
    var saw_boundary_map = false;
    var saw_test_gate = false;
    var saw_slice_note = false;
    var saw_survey_note = false;
    var saw_audit_outline = false;
    var saw_max_active_audit = false;
    var saw_lock_handoff_audit = false;
    var saw_pending_bit_followup = false;
    var saw_delayed_submission_followup = false;
    var saw_delayed_timer_followup = false;
    var saw_blocker = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_live_concurrency")) {
            blocked_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase14-build-gate")) {
            saw_build_gate = true;
            try std.testing.expectEqualStrings("zigux/tests/phase14_build.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase14-make-target")) {
            saw_make_target = true;
            try std.testing.expectEqualStrings("zigux/Makefile", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase14-kernel-export-shim-foundation")) {
            saw_export_shim = true;
            try std.testing.expectEqualStrings("zigux/kernel/export_shim.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "kernel namespace") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-workqueue-boundary-map-starter")) {
            saw_boundary_map = true;
            try std.testing.expectEqualStrings("kernel/workqueue_bridge.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue_work_on") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "manage_workers") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "stay-in-C") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-workqueue-test-gate")) {
            saw_test_gate = true;
            try std.testing.expectEqualStrings("zigux/tests/phase14_workqueue_bridge.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase14-workqueue-slice-note")) {
            saw_slice_note = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-workqueue-bridge-slice.md", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase14-workqueue-survey-note")) {
            saw_survey_note = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-workqueue-bridge-survey.md", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase14-workqueue-concurrency-audit-outline")) {
            saw_audit_outline = true;
            try std.testing.expectEqualStrings("kernel/workqueue_bridge.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "pool->manager") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "WORK_STRUCT_PENDING_BIT") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "pwq->refcnt") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "pwq->mayday_cursor") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-workqueue-max-active-audit")) {
            saw_max_active_audit = true;
            try std.testing.expectEqualStrings("kernel/workqueue_bridge.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "inactive_works") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "workqueue_set_max_active") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-workqueue-lock-handoff-audit")) {
            saw_lock_handoff_audit = true;
            try std.testing.expectEqualStrings("kernel/workqueue_bridge.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "last_pool->lock") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "worker_thread") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-workqueue-pending-bit-followup")) {
            saw_pending_bit_followup = true;
            try std.testing.expectEqualStrings("kernel/workqueue_bridge.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "try_to_grab_pending") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "pwq->refcnt") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-workqueue-delayed-submission-alias-followup")) {
            saw_delayed_submission_followup = true;
            try std.testing.expectEqualStrings("kernel/workqueue_bridge.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue_delayed_work_on") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "__queue_delayed_work") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-workqueue-delayed-timer-expiry-followup")) {
            saw_delayed_timer_followup = true;
            try std.testing.expectEqualStrings("kernel/workqueue_bridge.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("ready_next", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "delayed_work_timer_fn") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "__queue_work") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-workqueue-live-execution-blocker")) {
            saw_blocker = true;
            try std.testing.expectEqualStrings("zigux/tests/phase14_workqueue_bridge.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("blocked_on_live_concurrency", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "worker_pool") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "scheduler") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 12), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 1), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_build_gate);
    try std.testing.expect(saw_make_target);
    try std.testing.expect(saw_export_shim);
    try std.testing.expect(saw_boundary_map);
    try std.testing.expect(saw_test_gate);
    try std.testing.expect(saw_slice_note);
    try std.testing.expect(saw_survey_note);
    try std.testing.expect(saw_audit_outline);
    try std.testing.expect(saw_max_active_audit);
    try std.testing.expect(saw_lock_handoff_audit);
    try std.testing.expect(saw_pending_bit_followup);
    try std.testing.expect(saw_delayed_submission_followup);
    try std.testing.expect(saw_delayed_timer_followup);
    try std.testing.expect(saw_blocker);
}

test "phase14 workqueue bridge survey note pins the lane key and surveyed commit" {
    const survey_note = try readFixture(std.testing.allocator, "Documentation/zigux/phase14-workqueue-bridge-survey.md");
    defer std.testing.allocator.free(survey_note);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE14_STATUS=active") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE14_LANE_KEY=P14-L01") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE14_SURVEYED_COMMIT=9e278f632d6d5097cb8cfc2dc61744ae105baa8c") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE14_SLICE=workqueue-delayed-submission-alias-audit") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase14-workqueue-pending-bit-followup") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase14-workqueue-delayed-submission-alias-followup") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase14-workqueue-delayed-timer-expiry-followup") != null);
}

test "phase14 workqueue bridge descriptor stays at boundary-map posture" {
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

    try std.testing.expectEqual(@as(usize, 5), map.areas.len);
    try std.testing.expectEqual(@as(usize, 2), workqueue_bridge.WorkqueueBridgeLab.stayInCDecisionCount());
    try std.testing.expectEqual(@as(usize, 11), audit.checkpoints.len);
    try std.testing.expectEqual(@as(usize, 5), audit.blocked_live_behaviors.len);
    try std.testing.expectEqual(@as(usize, 11), workqueue_bridge.WorkqueueBridgeLab.auditCheckpointCount());
    try std.testing.expect(std.mem.indexOf(u8, workqueue_bridge.WorkqueueBridgeLab.nextAuditFocus(), "delayed_work_timer_fn()") != null);
    try std.testing.expect(std.mem.indexOf(u8, workqueue_bridge.WorkqueueBridgeLab.nextAuditFocus(), "__queue_work()") != null);
    try std.testing.expectEqualStrings("manager-role-serialization", audit.checkpoints[0].id);
    try std.testing.expectEqualStrings("pool->last_progress_ts", audit.checkpoints[1].observed_fields[0]);
    try std.testing.expectEqualStrings("max-active-ordering-gate", audit.checkpoints[2].id);
    try std.testing.expectEqualStrings("wq->max_active", audit.checkpoints[2].observed_fields[2]);
    try std.testing.expectEqualStrings("pending-bit-claim-handoff", audit.checkpoints[3].id);
    try std.testing.expect(audit.checkpoints[3].guard == .pending_bit_claim_window);
    try std.testing.expectEqualStrings("WORK_STRUCT_PENDING", audit.checkpoints[3].observed_fields[1]);
    try std.testing.expectEqualStrings("unbound-pwq-refcnt-retry", audit.checkpoints[4].id);
    try std.testing.expect(audit.checkpoints[4].guard == .unbound_pwq_refcnt_retry);
    try std.testing.expectEqualStrings("pwq->refcnt", audit.checkpoints[4].observed_fields[0]);
    try std.testing.expectEqualStrings("delayed-submission-alias-handoff", audit.checkpoints[5].id);
    try std.testing.expect(audit.checkpoints[5].guard == .delayed_submission_alias_window);
    try std.testing.expectEqualStrings("dwork->timer", audit.checkpoints[5].observed_fields[0]);
    try std.testing.expectEqualStrings("last-pool-reentrancy-handoff", audit.checkpoints[6].id);
    try std.testing.expect(audit.checkpoints[6].guard == .last_pool_lock_handoff);
    try std.testing.expectEqualStrings("process-one-work-execution-window", audit.checkpoints[7].id);
    try std.testing.expect(audit.checkpoints[7].guard == .callback_execution_outside_pool_lock);
    try std.testing.expectEqualStrings("worker-thread-idle-sleep-handoff", audit.checkpoints[8].id);
    try std.testing.expect(audit.checkpoints[8].guard == .idle_sleep_transition);
    try std.testing.expect(audit.checkpoints[9].guard == .scheduler_callback_under_pool_lock);
    try std.testing.expect(audit.checkpoints[10].guard == .mayday_lock_then_pool_lock);
}
