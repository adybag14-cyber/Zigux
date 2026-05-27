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
    try std.testing.expectEqualStrings("live worker_pool execution", audit.blocked_live_behaviors[0]);
    try std.testing.expectEqualStrings("flush, drain, and cancellation completion ownership", audit.blocked_live_behaviors[1]);
    try std.testing.expectEqualStrings("delayed-work requeue control", audit.blocked_live_behaviors[2]);
    try std.testing.expectEqualStrings("runtime max_active retuning ownership", audit.blocked_live_behaviors[3]);
    try std.testing.expectEqualStrings("scheduler-visible worker-state parity", audit.blocked_live_behaviors[4]);
    try std.testing.expectEqualStrings("rescuer execution ownership", audit.blocked_live_behaviors[5]);
    try std.testing.expectEqualStrings("hotplug-driven worker migration and topology rebinding", audit.blocked_live_behaviors[6]);
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

test "phase14 workqueue bridge wrapper candidates stay explicit and non-executing" {
    const packet = workqueue_bridge.WorkqueueBridgeLab.wrapperCandidatePacket();

    try std.testing.expectEqualStrings("boundary_map_only", packet.posture);
    try std.testing.expectEqual(@as(usize, 2), packet.candidates.len);
    try std.testing.expectEqual(@as(usize, 2), workqueue_bridge.WorkqueueBridgeLab.wrapperCandidateCount());
    try std.testing.expectEqualStrings(workqueue_bridge.WorkqueueBridgeLab.currentSliceId(), packet.current_slice_id);
    try std.testing.expectEqualStrings("submission-routing", packet.candidates[0].id);
    try std.testing.expect(packet.candidates[0].ownership == .boundary_map_only);
    try std.testing.expectEqualStrings("queue_work_on", packet.candidates[0].anchor_symbols[0]);
    try std.testing.expectEqualStrings("__queue_work", packet.candidates[0].anchor_symbols[1]);
    try std.testing.expect(std.mem.indexOf(u8, packet.candidates[0].blocked_by, "pending-bit claims") != null);
    try std.testing.expect(std.mem.indexOf(u8, packet.candidates[0].blocked_by, "live wrapper") != null);
    try std.testing.expectEqualStrings("allocation-and-attrs", packet.candidates[1].id);
    try std.testing.expect(packet.candidates[1].ownership == .boundary_map_only);
    try std.testing.expectEqualStrings("__alloc_workqueue", packet.candidates[1].anchor_symbols[0]);
    try std.testing.expectEqualStrings("devm_alloc_workqueue", packet.candidates[1].anchor_symbols[1]);
    try std.testing.expect(std.mem.indexOf(u8, packet.candidates[1].blocked_by, "rescuer policy") != null);
    try std.testing.expect(std.mem.indexOf(u8, packet.candidates[1].blocked_by, "ordered-workqueue rules") != null);
    try std.testing.expect(std.mem.indexOf(u8, packet.next_focus, "blocked maintenance") != null);
    try std.testing.expect(std.mem.indexOf(u8, packet.next_focus, "shared reminder surface") != null);
}

test "phase14 workqueue bridge flush-drain handoff keeps flusher and cancellation governance explicit and in C" {
    const flush_handoff = workqueue_bridge.WorkqueueBridgeLab.flushDrainHandoff();

    try std.testing.expectEqualStrings("start_flush_work/__flush_workqueue", flush_handoff.anchor_symbol);
    try std.testing.expect(flush_handoff.ownership == .stay_in_c);
    try std.testing.expectEqual(@as(usize, 8), flush_handoff.observed_fields.len);
    try std.testing.expectEqualStrings("wq->work_color", flush_handoff.observed_fields[0]);
    try std.testing.expectEqualStrings("wq->flush_color", flush_handoff.observed_fields[1]);
    try std.testing.expectEqualStrings("wq->nr_pwqs_to_flush", flush_handoff.observed_fields[2]);
    try std.testing.expectEqualStrings("wq->first_flusher", flush_handoff.observed_fields[3]);
    try std.testing.expectEqualStrings("pwq->nr_in_flight", flush_handoff.observed_fields[4]);
    try std.testing.expectEqualStrings("WORK_OFFQ_CANCELING", flush_handoff.observed_fields[5]);
    try std.testing.expectEqualStrings("work->data", flush_handoff.observed_fields[6]);
    try std.testing.expectEqualStrings("WORK_OFFQ_DISABLE_BITS", flush_handoff.observed_fields[7]);
    try std.testing.expectEqualStrings(workqueue_bridge.WorkqueueBridgeLab.currentSliceId(), flush_handoff.current_slice_id);
    try std.testing.expect(std.mem.indexOf(u8, flush_handoff.blocked_by, "insert_wq_barrier()") != null);
    try std.testing.expect(std.mem.indexOf(u8, flush_handoff.blocked_by, "start_flush_work()") != null);
    try std.testing.expect(std.mem.indexOf(u8, flush_handoff.blocked_by, "first-flusher") != null);
    try std.testing.expect(std.mem.indexOf(u8, flush_handoff.blocked_by, "disable_work()") != null);
    try std.testing.expect(std.mem.indexOf(u8, flush_handoff.blocked_by, "__flush_work()") != null);
    try std.testing.expect(std.mem.indexOf(u8, flush_handoff.blocked_by, "cancellation disable depth") != null);
    try std.testing.expect(std.mem.indexOf(u8, flush_handoff.blocked_by, "WORK_OFFQ_DISABLE_BITS") != null);
    try std.testing.expect(std.mem.indexOf(u8, flush_handoff.blocked_by, "WORK_OFFQ_CANCELING") != null);
    try std.testing.expect(std.mem.indexOf(u8, flush_handoff.blocked_by, "__cancel_work_sync()") != null);
    try std.testing.expect(std.mem.indexOf(u8, flush_handoff.next_focus, "blocked maintenance") != null);
    try std.testing.expect(std.mem.indexOf(u8, flush_handoff.next_focus, "shared reminder surface") != null);
}

test "phase14 workqueue bridge scheduler-visible worker-state handoff stays explicit and in C" {
    const scheduler_handoff = workqueue_bridge.WorkqueueBridgeLab.schedulerVisibleWorkerStateHandoff();

    try std.testing.expectEqualStrings("wq_worker_running", scheduler_handoff.running_anchor_symbol);
    try std.testing.expectEqualStrings("wq_worker_sleeping", scheduler_handoff.sleeping_anchor_symbol);
    try std.testing.expect(scheduler_handoff.ownership == .stay_in_c);
    try std.testing.expectEqual(@as(usize, 3), scheduler_handoff.observed_fields.len);
    try std.testing.expectEqualStrings("WORKER_NOT_RUNNING", scheduler_handoff.observed_fields[0]);
    try std.testing.expectEqualStrings("pool->nr_running", scheduler_handoff.observed_fields[1]);
    try std.testing.expectEqualStrings("pool->flags", scheduler_handoff.observed_fields[2]);
    try std.testing.expectEqualStrings(workqueue_bridge.WorkqueueBridgeLab.currentSliceId(), scheduler_handoff.current_slice_id);
    try std.testing.expect(std.mem.indexOf(u8, scheduler_handoff.blocked_by, "wq_worker_running() and wq_worker_sleeping()") != null);
    try std.testing.expect(std.mem.indexOf(u8, scheduler_handoff.blocked_by, "wakeups") != null);
    try std.testing.expect(std.mem.indexOf(u8, scheduler_handoff.blocked_by, "pool->lock") != null);
    try std.testing.expect(std.mem.indexOf(u8, scheduler_handoff.next_focus, "blocked maintenance") != null);
    try std.testing.expect(std.mem.indexOf(u8, scheduler_handoff.next_focus, "shared reminder surface") != null);
}

test "phase14 workqueue bridge max-active retuning handoff stays explicit and in C" {
    const retuning_handoff = workqueue_bridge.WorkqueueBridgeLab.maxActiveRetuningHandoff();

    try std.testing.expectEqualStrings("workqueue_set_max_active/__queue_work", retuning_handoff.anchor_symbol);
    try std.testing.expect(retuning_handoff.ownership == .stay_in_c);
    try std.testing.expectEqual(@as(usize, 4), retuning_handoff.observed_fields.len);
    try std.testing.expectEqualStrings("pwq->inactive_works", retuning_handoff.observed_fields[0]);
    try std.testing.expectEqualStrings("pwq->nr_active", retuning_handoff.observed_fields[1]);
    try std.testing.expectEqualStrings("wq->max_active", retuning_handoff.observed_fields[2]);
    try std.testing.expectEqualStrings("pool->last_progress_ts", retuning_handoff.observed_fields[3]);
    try std.testing.expectEqualStrings(workqueue_bridge.WorkqueueBridgeLab.currentSliceId(), retuning_handoff.current_slice_id);
    try std.testing.expect(std.mem.indexOf(u8, retuning_handoff.blocked_by, "inactive-list promotion") != null);
    try std.testing.expect(std.mem.indexOf(u8, retuning_handoff.blocked_by, "ordered-workqueue sequencing") != null);
    try std.testing.expect(std.mem.indexOf(u8, retuning_handoff.blocked_by, "runtime max_active retuning") != null);
    try std.testing.expect(std.mem.indexOf(u8, retuning_handoff.blocked_by, "stay-in-C governance") != null);
    try std.testing.expect(std.mem.indexOf(u8, retuning_handoff.next_focus, "blocked maintenance") != null);
    try std.testing.expect(std.mem.indexOf(u8, retuning_handoff.next_focus, "shared reminder surface") != null);
}
