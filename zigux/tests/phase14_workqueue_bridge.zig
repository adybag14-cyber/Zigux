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

test "phase14 workqueue bridge manifest records the boundary-map foothold and remaining gap" {
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
    try std.testing.expectEqualStrings("P14-Y01", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 14", manifest.phase);
    try std.testing.expectEqualStrings("kernel/workqueue.c", manifest.anchor);
    try std.testing.expectEqualStrings("542acd7b12c52211ef9a8bd790fa2e2b3367cbf0", manifest.surveyed_commit);
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

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase14-workqueue-bridge-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_note);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE14_LANE_KEY=P14-Y01") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE14_SURVEYED_COMMIT=542acd7b12c52211ef9a8bd790fa2e2b3367cbf0") != null);

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
    var saw_pending_audit = false;
    var saw_flush_color_audit = false;
    var saw_drain_cancel_audit = false;
    var saw_disable_delayed_followup = false;
    var saw_delayed_disable_wrapper_followup = false;
    var saw_delayed_submission_alias_followup = false;
    var saw_delayed_timer_handoff_followup = false;
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
        if (std.mem.eql(u8, gap.id, "phase14-workqueue-pending-bit-audit")) {
            saw_pending_audit = true;
            try std.testing.expectEqualStrings("kernel/workqueue_bridge.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "try_to_grab_pending") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue_work_on()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "pwq->refcnt") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-workqueue-flush-color-followup")) {
            saw_flush_color_audit = true;
            try std.testing.expectEqualStrings("kernel/workqueue_bridge.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "__flush_workqueue()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "start_flush_work()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "pwq_dec_nr_in_flight()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-workqueue-drain-cancel-followup")) {
            saw_drain_cancel_audit = true;
            try std.testing.expectEqualStrings("kernel/workqueue_bridge.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "drain_workqueue()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "__flush_work()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "__cancel_work_sync()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-workqueue-disable-delayed-followup")) {
            saw_disable_delayed_followup = true;
            try std.testing.expectEqualStrings("kernel/workqueue_bridge.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "__cancel_work()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "clear_pending_if_disabled()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "__cancel_work_sync()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "WORK_CANCEL_DELAYED") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-workqueue-delayed-disable-wrapper-followup")) {
            saw_delayed_disable_wrapper_followup = true;
            try std.testing.expectEqualStrings("kernel/workqueue_bridge.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "disable_delayed_work()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "disable_delayed_work_sync()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "enable_delayed_work()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-workqueue-delayed-submission-alias-followup")) {
            saw_delayed_submission_alias_followup = true;
            try std.testing.expectEqualStrings("kernel/workqueue_bridge.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue_delayed_work_on()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "mod_delayed_work_on()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "__queue_delayed_work()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "dwork->timer") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-workqueue-delayed-timer-handoff-followup")) {
            saw_delayed_timer_handoff_followup = true;
            try std.testing.expectEqualStrings("kernel/workqueue_bridge.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "delayed_work_timer_fn()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "__queue_work()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "timer-base") != null);
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

    try std.testing.expectEqual(@as(usize, 17), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
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
    try std.testing.expect(saw_pending_audit);
    try std.testing.expect(saw_flush_color_audit);
    try std.testing.expect(saw_drain_cancel_audit);
    try std.testing.expect(saw_disable_delayed_followup);
    try std.testing.expect(saw_delayed_disable_wrapper_followup);
    try std.testing.expect(saw_delayed_submission_alias_followup);
    try std.testing.expect(saw_delayed_timer_handoff_followup);
    try std.testing.expect(saw_blocker);
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
    try std.testing.expectEqual(@as(usize, 18), audit.checkpoints.len);
    try std.testing.expectEqual(@as(usize, 5), audit.blocked_live_behaviors.len);
    try std.testing.expectEqual(@as(usize, 18), workqueue_bridge.WorkqueueBridgeLab.auditCheckpointCount());
    try std.testing.expect(std.mem.indexOf(u8, workqueue_bridge.WorkqueueBridgeLab.nextAuditFocus(), "blocked maintenance") != null);
    try std.testing.expect(std.mem.indexOf(u8, workqueue_bridge.WorkqueueBridgeLab.nextAuditFocus(), "timer-base") != null);
    try std.testing.expect(std.mem.indexOf(u8, workqueue_bridge.WorkqueueBridgeLab.nextAuditFocus(), "CPU-affinity") != null);
    try std.testing.expect(std.mem.indexOf(u8, workqueue_bridge.WorkqueueBridgeLab.nextAuditFocus(), "requeue ownership") != null);
    try std.testing.expectEqualStrings("manager-role-serialization", audit.checkpoints[0].id);
    try std.testing.expectEqualStrings("pool->last_progress_ts", audit.checkpoints[1].observed_fields[0]);
    try std.testing.expectEqualStrings("max-active-ordering-gate", audit.checkpoints[2].id);
    try std.testing.expectEqualStrings("wq->max_active", audit.checkpoints[2].observed_fields[2]);
    try std.testing.expectEqualStrings("pending-bit-claim-window", audit.checkpoints[3].id);
    try std.testing.expect(audit.checkpoints[3].guard == .pending_bit_with_irqs_disabled);
    try std.testing.expectEqualStrings("unbound-pwq-refcnt-retry", audit.checkpoints[4].id);
    try std.testing.expect(audit.checkpoints[4].guard == .pwq_refcnt_retry_loop);
    try std.testing.expectEqualStrings("last-pool-reentrancy-handoff", audit.checkpoints[5].id);
    try std.testing.expect(audit.checkpoints[5].guard == .last_pool_lock_handoff);
    try std.testing.expectEqualStrings("flush-workqueue-color-cascade", audit.checkpoints[6].id);
    try std.testing.expect(audit.checkpoints[6].guard == .flush_color_cascade_under_wq_mutex);
    try std.testing.expectEqualStrings("wq->flusher_overflow", audit.checkpoints[6].observed_fields[3]);
    try std.testing.expectEqualStrings("flush-work-barrier-insertion", audit.checkpoints[7].id);
    try std.testing.expect(audit.checkpoints[7].guard == .flush_barrier_insert_under_pool_lock);
    try std.testing.expectEqualStrings("wq->saved_max_active", audit.checkpoints[7].observed_fields[3]);
    try std.testing.expectEqualStrings("pwq-in-flight-color-release", audit.checkpoints[8].id);
    try std.testing.expect(audit.checkpoints[8].guard == .in_flight_color_release_completion);
    try std.testing.expectEqualStrings("wq->first_flusher", audit.checkpoints[8].observed_fields[3]);
    try std.testing.expectEqualStrings("drain-reflush-and-cancel-sync", audit.checkpoints[9].id);
    try std.testing.expect(audit.checkpoints[9].guard == .drain_reflush_and_cancel_sync);
    try std.testing.expectEqualStrings("wq->nr_drainers", audit.checkpoints[9].observed_fields[0]);
    try std.testing.expectEqualStrings("barr.done", audit.checkpoints[9].observed_fields[2]);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[9].blocked_by, "__WQ_DRAINING") != null);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[9].blocked_by, "re-enables the work item") != null);
    try std.testing.expectEqualStrings("disable-depth-and-delayed-cancel-sync", audit.checkpoints[10].id);
    try std.testing.expect(audit.checkpoints[10].guard == .disable_depth_and_delayed_cancel_sync);
    try std.testing.expectEqualStrings("WORK_OFFQ_DISABLE_MASK", audit.checkpoints[10].observed_fields[0]);
    try std.testing.expectEqualStrings("WORK_OFFQ_BH", audit.checkpoints[10].observed_fields[3]);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[10].blocked_by, "clear_pending_if_disabled()") != null);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[10].blocked_by, "might_sleep()") != null);
    try std.testing.expectEqualStrings("delayed-disable-wrapper-aliases", audit.checkpoints[11].id);
    try std.testing.expect(audit.checkpoints[11].guard == .delayed_disable_wrapper_aliases);
    try std.testing.expectEqualStrings("delayed-submission-alias-handoff", audit.checkpoints[12].id);
    try std.testing.expect(audit.checkpoints[12].guard == .delayed_submission_alias_handoff);
    try std.testing.expectEqualStrings("dwork->timer", audit.checkpoints[12].observed_fields[0]);
    try std.testing.expectEqualStrings("cpu", audit.checkpoints[12].observed_fields[3]);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[12].blocked_by, "queue_delayed_work_on()") != null);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[12].blocked_by, "mod_delayed_work_on()") != null);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[12].blocked_by, "__queue_delayed_work()") != null);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[12].blocked_by, "__queue_work()") != null);
    try std.testing.expectEqualStrings("delayed-timer-expiry-handoff", audit.checkpoints[13].id);
    try std.testing.expect(audit.checkpoints[13].guard == .delayed_timer_expiry_requeue_handoff);
    try std.testing.expectEqualStrings("dwork->timer", audit.checkpoints[13].observed_fields[0]);
    try std.testing.expectEqualStrings("WORK_STRUCT_PENDING_BIT", audit.checkpoints[13].observed_fields[2]);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[13].blocked_by, "delayed_work_timer_fn()") != null);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[13].blocked_by, "__queue_work()") != null);
    try std.testing.expectEqualStrings("process-one-work-execution-window", audit.checkpoints[14].id);
    try std.testing.expect(audit.checkpoints[14].guard == .callback_execution_outside_pool_lock);
    try std.testing.expectEqualStrings("worker-thread-idle-sleep-handoff", audit.checkpoints[15].id);
    try std.testing.expect(audit.checkpoints[15].guard == .idle_sleep_transition);
    try std.testing.expect(audit.checkpoints[16].guard == .scheduler_callback_under_pool_lock);
    try std.testing.expect(audit.checkpoints[17].guard == .mayday_lock_then_pool_lock);
}

test "phase14 workqueue bridge survey status block keeps review packet aligned" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase14-workqueue-bridge-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE14_SLICE=workqueue-blocked-maintenance") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE14_LANE_KEY=P14-Y01") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "landed `phase14-workqueue-delayed-timer-handoff-followup`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "delayed_work_timer_fn()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "__queue_work()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Leave this lane in blocked maintenance") != null);

    const slice_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase14-workqueue-bridge-slice.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(slice_note);

    try std.testing.expect(std.mem.indexOf(u8, slice_note, "parked in blocked maintenance") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "mod_delayed_work_on()") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "try_to_grab_pending()") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "__queue_delayed_work()") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "timer-base") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "CPU-affinity") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "requeue ownership") != null);
}
