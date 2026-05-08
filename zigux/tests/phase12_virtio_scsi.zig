const std = @import("std");
const virtio_scsi = @import("virtio_scsi");

test "phase12 virtio scsi queue planner stays anchored to virtio_scsi.c" {
    const descriptor = virtio_scsi.VirtioScsiQueueLab.descriptor();
    try std.testing.expectEqualStrings("virtio_scsi_queue_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_queue_family_planner);
    try std.testing.expect(descriptor.provides_host_shape_summary);
    try std.testing.expect(!descriptor.touches_live_dma);
    try std.testing.expect(!descriptor.touches_scsi_host);
    try std.testing.expect(descriptor.touches_transport_reset);

    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    const layout = try lab.planQueueLayout(8, 3);
    try std.testing.expectEqual(@as(u16, 8), layout.request_queues);
    try std.testing.expectEqual(@as(u16, 3), layout.requested_poll_queues);
    try std.testing.expectEqual(@as(u16, 5), layout.default_queues);
    try std.testing.expectEqual(@as(u16, 3), layout.poll_queues);
    try std.testing.expectEqual(@as(u16, 10), layout.total_queues);
    try std.testing.expectEqual(@as(u16, virtio_scsi.control_queue_index), layout.control_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_queue_index), layout.event_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_scsi.request_queue_base), layout.first_request_queue_index);
    try std.testing.expectEqual(@as(?u16, 7), layout.first_poll_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), layout.event_buffer_count);
}

test "phase12 virtio scsi probe snapshot keeps queue clamp and probe-only boundary explicit" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    const snapshot = try lab.probeConfigSnapshot(4, 4, 128, 64, 32, 16, 2048);
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", snapshot.anchor);
    try std.testing.expectEqual(@as(u16, 4), snapshot.num_queues);
    try std.testing.expectEqual(@as(u16, 4), snapshot.requested_poll_queues);
    try std.testing.expectEqual(@as(u32, 128), snapshot.seg_max);
    try std.testing.expectEqual(@as(u32, 64), snapshot.cmd_per_lun);
    try std.testing.expectEqual(@as(u32, 32), snapshot.max_target);
    try std.testing.expectEqual(@as(u32, 16), snapshot.max_lun);
    try std.testing.expectEqual(@as(u32, 2048), snapshot.max_sectors);
    try std.testing.expectEqual(@as(u16, 1), snapshot.default_queues);
    try std.testing.expectEqual(@as(u16, 3), snapshot.poll_queues);
    try std.testing.expectEqual(@as(u16, 6), snapshot.total_queues);
    try std.testing.expectEqual(@as(u16, virtio_scsi.control_queue_index), snapshot.control_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_queue_index), snapshot.event_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_scsi.request_queue_base), snapshot.first_request_queue_index);
    try std.testing.expectEqual(@as(?u16, 3), snapshot.first_poll_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), snapshot.event_buffer_count);
    try std.testing.expect(snapshot.uses_control_queue);
    try std.testing.expect(snapshot.uses_event_queue);
    try std.testing.expect(snapshot.respects_poll_queue_clamp);
    try std.testing.expect(snapshot.preserves_probe_only_scope);
    try std.testing.expect(snapshot.blocks_dma_submission);

    const request_queue = try lab.requestQueue(0);
    try std.testing.expectEqual(@as(u16, 0), request_queue.local_index);
    try std.testing.expectEqual(@as(u16, 2), request_queue.global_index);
    try std.testing.expectEqual(virtio_scsi.RequestQueueKind.request, request_queue.kind);

    const poll_queue = try lab.requestQueue(1);
    try std.testing.expectEqual(@as(u16, 1), poll_queue.local_index);
    try std.testing.expectEqual(@as(u16, 3), poll_queue.global_index);
    try std.testing.expectEqual(virtio_scsi.RequestQueueKind.request_poll, poll_queue.kind);
}

test "phase12 virtio scsi queue window summary keeps default and poll queue ranges explicit" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    _ = try lab.planQueueLayout(8, 3);

    const summary = try lab.queueWindowSummary();
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, virtio_scsi.control_queue_index), summary.control_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_queue_index), summary.event_queue_index);
    try std.testing.expectEqual(@as(u16, 2), summary.first_default_queue_index);
    try std.testing.expectEqual(@as(u16, 6), summary.last_default_queue_index);
    try std.testing.expectEqual(@as(u16, 5), summary.default_queue_count);
    try std.testing.expectEqual(@as(?u16, 7), summary.first_poll_queue_index);
    try std.testing.expectEqual(@as(?u16, 9), summary.last_poll_queue_index);
    try std.testing.expectEqual(@as(u16, 3), summary.poll_queue_count);
    try std.testing.expectEqual(@as(u16, 10), summary.total_queues);
    try std.testing.expect(summary.preserves_control_event_gap);
    try std.testing.expect(summary.keeps_default_queues_before_poll_queues);

    _ = try lab.freezeForTransportReset();
    try std.testing.expectError(error.TransportFrozen, lab.queueWindowSummary());
}

test "phase12 virtio scsi queue window summary keeps non-poll queue layouts compact" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    _ = try lab.planQueueLayout(1, 4);

    const summary = try lab.queueWindowSummary();
    try std.testing.expectEqual(@as(u16, 2), summary.first_default_queue_index);
    try std.testing.expectEqual(@as(u16, 2), summary.last_default_queue_index);
    try std.testing.expectEqual(@as(u16, 1), summary.default_queue_count);
    try std.testing.expectEqual(@as(?u16, null), summary.first_poll_queue_index);
    try std.testing.expectEqual(@as(?u16, null), summary.last_poll_queue_index);
    try std.testing.expectEqual(@as(u16, 0), summary.poll_queue_count);
    try std.testing.expectEqual(@as(u16, 3), summary.total_queues);
    try std.testing.expect(summary.keeps_default_queues_before_poll_queues);
}

test "phase12 virtio scsi host shape summary keeps pre-registration host fields reviewable" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    const summary = try lab.captureHostShapeSummary(.{
        .num_queues = 8,
        .requested_poll_queues = 3,
        .seg_max = 128,
        .cmd_per_lun = 64,
        .max_target = 31,
        .max_lun = 15,
        .max_sectors = 2048,
    });

    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, 8), summary.request_queues);
    try std.testing.expectEqual(@as(u16, 5), summary.default_queues);
    try std.testing.expectEqual(@as(u16, 3), summary.poll_queues);
    try std.testing.expectEqual(@as(u32, 128), summary.sg_tablesize);
    try std.testing.expectEqual(@as(u32, 64), summary.cmd_per_lun);
    try std.testing.expectEqual(@as(u32, 2048), summary.max_sectors);
    try std.testing.expectEqual(@as(u32, 32), summary.max_id);
    try std.testing.expectEqual(@as(u32, 0x4010), summary.max_lun);
    try std.testing.expectEqual(@as(u32, virtio_scsi.default_cdb_size), summary.max_cmd_len);
    try std.testing.expectEqual(@as(u16, 8), summary.nr_hw_queues);
    try std.testing.expectEqual(@as(u16, 3), summary.nr_maps);
    try std.testing.expectEqual(@as(u32, virtio_scsi.default_dma_boundary), summary.dma_boundary);
    try std.testing.expect(summary.uses_map_queues);
    try std.testing.expect(summary.uses_commit_rqs);
    try std.testing.expect(summary.uses_mq_poll);
    try std.testing.expect(summary.preserves_pre_registration_scope);
}

test "phase12 virtio scsi host shape summary defaults non-poll hosts and blocks frozen planning" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    const summary = try lab.captureHostShapeSummary(.{
        .num_queues = 1,
        .requested_poll_queues = 9,
        .seg_max = 0,
        .cmd_per_lun = 0,
        .max_target = 0,
        .max_lun = 0,
        .max_sectors = 0,
    });

    try std.testing.expectEqual(@as(u16, 1), summary.default_queues);
    try std.testing.expectEqual(@as(u16, 0), summary.poll_queues);
    try std.testing.expectEqual(@as(u32, 1), summary.sg_tablesize);
    try std.testing.expectEqual(@as(u32, virtio_scsi.default_cmd_per_lun), summary.cmd_per_lun);
    try std.testing.expectEqual(@as(u32, virtio_scsi.default_max_sectors), summary.max_sectors);
    try std.testing.expectEqual(@as(u32, 1), summary.max_id);
    try std.testing.expectEqual(@as(u32, 0x4001), summary.max_lun);
    try std.testing.expectEqual(@as(u16, 1), summary.nr_maps);
    try std.testing.expect(!summary.uses_mq_poll);

    _ = try lab.planQueueLayout(2, 1);
    _ = try lab.freezeForTransportReset();
    try std.testing.expectError(error.TransportFrozen, lab.captureHostShapeSummary(.{
        .num_queues = 2,
        .requested_poll_queues = 1,
        .seg_max = 32,
        .cmd_per_lun = 8,
        .max_target = 1,
        .max_lun = 1,
        .max_sectors = 512,
    }));
}

test "phase12 virtio scsi freeze and restore summaries keep recovery-state transitions explicit" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    _ = try lab.planQueueLayout(5, 2);

    const frozen = try lab.freezeForTransportReset();
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", frozen.anchor);
    try std.testing.expectEqual(virtio_scsi.RecoveryAction.freeze, frozen.action);
    try std.testing.expect(!frozen.was_frozen);
    try std.testing.expect(frozen.is_frozen);
    try std.testing.expect(!frozen.request_planning_available);
    try std.testing.expect(!frozen.event_recycling_enabled);
    try std.testing.expectEqual(@as(u16, 5), frozen.remembered_request_queues);
    try std.testing.expectEqual(@as(u16, 2), frozen.remembered_poll_queues);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), frozen.remembered_event_buffer_count);
    try std.testing.expectEqual(@as(u16, 0), frozen.recovery_generation);

    const restored = try lab.restoreAfterTransportReset();
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", restored.anchor);
    try std.testing.expectEqual(virtio_scsi.RecoveryAction.restore, restored.action);
    try std.testing.expect(restored.was_frozen);
    try std.testing.expect(!restored.is_frozen);
    try std.testing.expect(restored.request_planning_available);
    try std.testing.expect(restored.event_recycling_enabled);
    try std.testing.expectEqual(@as(u16, 5), restored.remembered_request_queues);
    try std.testing.expectEqual(@as(u16, 2), restored.remembered_poll_queues);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), restored.remembered_event_buffer_count);
    try std.testing.expectEqual(@as(u16, 1), restored.recovery_generation);
    try std.testing.expectError(error.QueueLayoutUnavailable, lab.queueWindowSummary());
}

test "phase12 virtio scsi repeated freeze restore tracks the replanned recovery boundary" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    _ = try lab.planQueueLayout(6, 2);
    _ = try lab.freezeForTransportReset();

    const first_plan = try lab.recoveryRestoreSummary();
    try std.testing.expectEqual(@as(u16, 6), first_plan.request_queues);
    try std.testing.expectEqual(@as(u16, 4), first_plan.default_queues);
    try std.testing.expectEqual(@as(u16, 2), first_plan.poll_queues);
    try std.testing.expectEqual(@as(?u16, 6), first_plan.first_poll_queue_index);

    const first_rollback = try lab.recoveryRollbackSummary();
    try std.testing.expectEqual(@as(u16, 0), first_rollback.recovery_generation);
    try std.testing.expect(first_rollback.keeps_frozen_layout_for_restore);
    try std.testing.expect(first_rollback.requires_replan_before_queue_reuse);

    const first_restore = try lab.restoreAfterTransportReset();
    try std.testing.expectEqual(@as(u16, 1), first_restore.recovery_generation);
    try std.testing.expectEqual(@as(u16, 6), first_restore.remembered_request_queues);
    try std.testing.expectEqual(@as(u16, 2), first_restore.remembered_poll_queues);
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryRestoreSummary());
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryRestoreQueueRebindSummary());
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryRequestQueueRestartSummary());

    const replanned = try lab.planQueueLayout(4, 1);
    try std.testing.expectEqual(@as(u16, 3), replanned.default_queues);
    try std.testing.expectEqual(@as(u16, 1), replanned.poll_queues);
    try std.testing.expectEqual(@as(?u16, 5), replanned.first_poll_queue_index);

    const second_freeze = try lab.freezeForTransportReset();
    try std.testing.expectEqual(@as(u16, 1), second_freeze.recovery_generation);
    try std.testing.expectEqual(@as(u16, 4), second_freeze.remembered_request_queues);
    try std.testing.expectEqual(@as(u16, 1), second_freeze.remembered_poll_queues);

    const second_plan = try lab.recoveryRestoreSummary();
    try std.testing.expectEqual(@as(u16, 4), second_plan.request_queues);
    try std.testing.expectEqual(@as(u16, 3), second_plan.default_queues);
    try std.testing.expectEqual(@as(u16, 1), second_plan.poll_queues);
    try std.testing.expectEqual(@as(u16, 6), second_plan.total_queues);
    try std.testing.expectEqual(@as(?u16, 5), second_plan.first_poll_queue_index);

    const second_rebind = try lab.recoveryRestoreQueueRebindSummary();
    try std.testing.expectEqual(@as(u16, 3), second_rebind.default_queue_count);
    try std.testing.expectEqual(@as(u16, 1), second_rebind.poll_queue_count);
    try std.testing.expectEqual(@as(u16, 2), second_rebind.first_default_queue_index);
    try std.testing.expectEqual(@as(u16, 4), second_rebind.last_default_queue_index);
    try std.testing.expectEqual(@as(?u16, 5), second_rebind.first_poll_queue_index);
    try std.testing.expectEqual(@as(?u16, 5), second_rebind.last_poll_queue_index);

    const second_restart = try lab.recoveryRequestQueueRestartSummary();
    try std.testing.expectEqual(@as(u16, 4), second_restart.request_queues);
    try std.testing.expectEqual(@as(u16, 3), second_restart.default_queues);
    try std.testing.expectEqual(@as(u16, 1), second_restart.poll_queues);
    try std.testing.expectEqual(@as(u16, 6), second_restart.total_queues);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_queue_index), second_restart.event_queue_index);
    try std.testing.expectEqual(@as(u16, 2), second_restart.first_request_queue_index);
    try std.testing.expectEqual(@as(?u16, 5), second_restart.first_poll_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), second_restart.event_buffer_count);
    try std.testing.expectEqual(@as(u16, 1), second_restart.recovery_generation);
    try std.testing.expect(second_restart.requires_find_vqs_before_restart);
    try std.testing.expect(second_restart.requires_device_ready_before_restart);
    try std.testing.expect(second_restart.requires_event_rearm_before_restart);
    try std.testing.expect(second_restart.requires_replan_before_restart);
    try std.testing.expect(second_restart.preserves_default_before_poll_partition);

    const second_ownership = try lab.recoveryEventBufferOwnershipSummary();
    try std.testing.expectEqual(@as(u16, 4), second_ownership.request_queues);
    try std.testing.expectEqual(@as(u16, 3), second_ownership.default_queues);
    try std.testing.expectEqual(@as(u16, 1), second_ownership.poll_queues);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), second_ownership.event_buffer_count);
    try std.testing.expect(second_ownership.event_queue_reserved_during_freeze);
    try std.testing.expect(second_ownership.event_buffers_stay_on_event_queue);
    try std.testing.expect(second_ownership.request_queues_cannot_borrow_event_buffers);
    try std.testing.expect(second_ownership.requires_restore_rearm_before_reuse);

    const second_rearm = try lab.recoveryEventRearmSummary();
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_queue_index), second_rearm.event_queue_index);
    try std.testing.expectEqual(@as(u16, 4), second_rearm.request_queues);
    try std.testing.expectEqual(@as(u16, 3), second_rearm.default_queues);
    try std.testing.expectEqual(@as(u16, 1), second_rearm.poll_queues);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), second_rearm.event_buffer_count);
    try std.testing.expect(second_rearm.reuses_frozen_event_queue_index);
    try std.testing.expect(second_rearm.requires_device_ready_before_rearm);
    try std.testing.expect(second_rearm.rearms_event_queue_before_event_recycling);
    try std.testing.expect(second_rearm.rearms_event_queue_before_request_queue_reuse);

    const second_rollback = try lab.recoveryRollbackSummary();
    try std.testing.expectEqual(@as(u16, 1), second_rollback.recovery_generation);
    try std.testing.expectEqual(@as(u16, 4), second_rollback.request_queues);
    try std.testing.expectEqual(@as(u16, 3), second_rollback.default_queues);
    try std.testing.expectEqual(@as(u16, 1), second_rollback.poll_queues);
    try std.testing.expectEqual(@as(u16, 6), second_rollback.total_queues);
    try std.testing.expect(second_rollback.clears_live_layout_after_restore);

    const second_restore = try lab.restoreAfterTransportReset();
    try std.testing.expectEqual(@as(u16, 2), second_restore.recovery_generation);
    try std.testing.expectEqual(@as(u16, 4), second_restore.remembered_request_queues);
    try std.testing.expectEqual(@as(u16, 1), second_restore.remembered_poll_queues);
}

test "phase12 virtio scsi recovery event ownership and rollback keep the frozen layout non-reusable" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    _ = try lab.planQueueLayout(7, 3);

    const request_queue = try lab.requestQueue(0);
    try std.testing.expectEqual(@as(u16, 2), request_queue.global_index);
    try std.testing.expectEqual(virtio_scsi.RequestQueueKind.request, request_queue.kind);

    const poll_queue = try lab.requestQueue(4);
    try std.testing.expectEqual(@as(u16, 6), poll_queue.global_index);
    try std.testing.expectEqual(virtio_scsi.RequestQueueKind.request_poll, poll_queue.kind);

    _ = try lab.freezeForTransportReset();
    try std.testing.expectError(error.TransportFrozen, lab.requestQueue(0));

    const ownership = try lab.recoveryEventBufferOwnershipSummary();
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", ownership.anchor);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_queue_index), ownership.event_queue_index);
    try std.testing.expectEqual(@as(u16, 7), ownership.request_queues);
    try std.testing.expectEqual(@as(u16, 4), ownership.default_queues);
    try std.testing.expectEqual(@as(u16, 3), ownership.poll_queues);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), ownership.event_buffer_count);
    try std.testing.expect(ownership.event_queue_reserved_during_freeze);
    try std.testing.expect(ownership.event_buffers_stay_on_event_queue);
    try std.testing.expect(ownership.request_queues_cannot_borrow_event_buffers);
    try std.testing.expect(ownership.defers_event_buffers_until_after_device_ready);
    try std.testing.expect(ownership.requires_restore_rearm_before_reuse);

    const rollback = try lab.recoveryRollbackSummary();
    try std.testing.expectEqual(@as(u16, 7), rollback.request_queues);
    try std.testing.expectEqual(@as(u16, 4), rollback.default_queues);
    try std.testing.expectEqual(@as(u16, 3), rollback.poll_queues);
    try std.testing.expectEqual(@as(u16, 9), rollback.total_queues);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), rollback.event_buffer_count);
    try std.testing.expectEqual(@as(u16, 0), rollback.recovery_generation);
    try std.testing.expect(rollback.blocks_queue_planning_until_restore);
    try std.testing.expect(rollback.blocks_request_queue_access_until_restore);
    try std.testing.expect(rollback.keeps_frozen_layout_for_restore);
    try std.testing.expect(rollback.clears_live_layout_after_restore);
    try std.testing.expect(rollback.requires_replan_before_queue_reuse);

    const restore = try lab.restoreAfterTransportReset();
    try std.testing.expectEqual(@as(u16, 1), restore.recovery_generation);
    try std.testing.expectError(error.QueueLayoutUnavailable, lab.requestQueue(0));
}

test "phase12 virtio scsi recovery event rearm summary stays tied to the frozen queue layout" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    _ = try lab.planQueueLayout(8, 3);
    _ = try lab.freezeForTransportReset();

    const summary = try lab.recoveryEventRearmSummary();
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_queue_index), summary.event_queue_index);
    try std.testing.expectEqual(@as(u16, 8), summary.request_queues);
    try std.testing.expectEqual(@as(u16, 5), summary.default_queues);
    try std.testing.expectEqual(@as(u16, 3), summary.poll_queues);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), summary.event_buffer_count);
    try std.testing.expect(summary.reuses_frozen_event_queue_index);
    try std.testing.expect(summary.requires_device_ready_before_rearm);
    try std.testing.expect(summary.rearms_event_queue_before_event_recycling);
    try std.testing.expect(summary.rearms_event_queue_before_request_queue_reuse);
}

test "phase12 virtio scsi recovery event rearm summary requires a frozen transport" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryEventRearmSummary());
}

test "phase12 virtio scsi request queue restart summary requires a frozen transport" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryRequestQueueRestartSummary());
}
