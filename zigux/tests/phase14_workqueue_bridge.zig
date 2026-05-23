const std = @import("std");
const workqueue_bridge = @import("workqueue_bridge");

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

test "phase14 workqueue bridge maintenance handoff stays bridge-local and explicit" {
    const handoff = workqueue_bridge.WorkqueueBridgeLab.maintenanceHandoff();

    try std.testing.expectEqualStrings("blocked_maintenance", handoff.posture);
    try std.testing.expectEqual(@as(usize, 6), handoff.reread_surfaces.len);
    try std.testing.expectEqualStrings("kernel/workqueue_bridge.zig", handoff.reread_surfaces[0]);
    try std.testing.expectEqualStrings("zigux/tests/phase14_workqueue_bridge.zig", handoff.reread_surfaces[1]);
    try std.testing.expectEqualStrings("zigux/tests/phase14_workqueue_reviewability.zig", handoff.reread_surfaces[2]);
    try std.testing.expectEqualStrings("zigux/tests/phase14_workqueue_bridge_manifest.json", handoff.reread_surfaces[3]);
    try std.testing.expectEqualStrings("Documentation/zigux/phase14-workqueue-bridge-slice.md", handoff.reread_surfaces[4]);
    try std.testing.expectEqualStrings("Documentation/zigux/phase14-workqueue-bridge-survey.md", handoff.reread_surfaces[5]);
    try std.testing.expectEqual(@as(usize, 3), handoff.reopen_conditions.len);
    try std.testing.expect(std.mem.indexOf(u8, handoff.reopen_conditions[0], "blocked-maintenance posture") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff.reopen_conditions[1], "shared smoke or core traceability packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff.reopen_conditions[2], "delayed-work requeue governance") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff.reopen_conditions[2], "scheduler-visible worker-state transitions") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff.next_future_target, "blocked maintenance") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff.next_future_target, "shared reminder surface") != null);
}

test "phase14 workqueue bridge cancel-path handoff stays explicit and in C" {
    const cancel_handoff = workqueue_bridge.WorkqueueBridgeLab.cancelPathHandoff();

    try std.testing.expectEqualStrings("__cancel_work_sync", cancel_handoff.anchor_symbol);
    try std.testing.expect(cancel_handoff.ownership == .stay_in_c);
    try std.testing.expectEqual(@as(usize, 4), cancel_handoff.observed_fields.len);
    try std.testing.expectEqualStrings("WORK_OFFQ_DISABLE_BITS", cancel_handoff.observed_fields[0]);
    try std.testing.expectEqualStrings("work->data", cancel_handoff.observed_fields[1]);
    try std.testing.expectEqualStrings("__flush_work()", cancel_handoff.observed_fields[2]);
    try std.testing.expectEqualStrings("disable_work()", cancel_handoff.observed_fields[3]);
    try std.testing.expect(std.mem.indexOf(u8, cancel_handoff.blocked_by, "disable depth") != null);
    try std.testing.expect(std.mem.indexOf(u8, cancel_handoff.blocked_by, "pending-bit and completion rules") != null);
}
