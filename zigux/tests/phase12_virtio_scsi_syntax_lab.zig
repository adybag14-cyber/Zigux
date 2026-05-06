const std = @import("std");

const virtio_scsi = @import("virtio_scsi");

test "phase12 virtio scsi syntax lab keeps bounded queue-lab exports reachable" {
    const descriptor = virtio_scsi.VirtioScsiQueueLab.descriptor();

    _ = virtio_scsi.ModuleDescriptor;
    _ = virtio_scsi.RequestQueueKind;
    _ = virtio_scsi.RecoveryAction;
    _ = virtio_scsi.QueueLayoutSummary;
    _ = virtio_scsi.RequestQueueSummary;
    _ = virtio_scsi.ProbeConfigSnapshot;
    _ = virtio_scsi.RecoverySummary;
    _ = virtio_scsi.RecoveryRestoreSummary;
    _ = virtio_scsi.RecoveryRestoreQueueRebindSummary;
    _ = virtio_scsi.RecoveryEventBufferOwnershipSummary;
    _ = virtio_scsi.RecoveryEventRearmSummary;
    _ = virtio_scsi.RecoveryRollbackSummary;
    _ = virtio_scsi.VirtioScsiQueueLab;

    try std.testing.expectEqualStrings("virtio_scsi_queue_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_queue_family_planner);
    try std.testing.expect(!descriptor.touches_live_dma);
    try std.testing.expect(!descriptor.touches_scsi_host);
    try std.testing.expect(descriptor.touches_transport_reset);
}

test "phase12 virtio scsi syntax lab keeps queue-family constants and defaults stable" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    const layout = try lab.planQueueLayout(6, 2);

    try std.testing.expectEqual(@as(u16, 0), virtio_scsi.control_queue_index);
    try std.testing.expectEqual(@as(u16, 1), virtio_scsi.event_queue_index);
    try std.testing.expectEqual(@as(u16, 2), virtio_scsi.request_queue_base);
    try std.testing.expectEqual(@as(u16, 8), virtio_scsi.event_buffer_count);
    try std.testing.expectEqual(@as(u16, 1), virtio_scsi.min_request_queues);
    try std.testing.expectEqual(@as(u16, 4), layout.default_queues);
    try std.testing.expectEqual(@as(u16, 2), layout.poll_queues);
    try std.testing.expectEqual(@as(u16, 8), layout.total_queues);
    try std.testing.expectEqual(@as(?u16, 6), layout.first_poll_queue_index);
    try std.testing.expectEqual(virtio_scsi.RequestQueueKind.request, (try lab.requestQueue(0)).kind);
    try std.testing.expectEqual(virtio_scsi.RequestQueueKind.request_poll, (try lab.requestQueue(4)).kind);
}

test "phase12 virtio scsi syntax lab keeps probe-config snapshot variants reachable" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    const snapshot = try lab.probeConfigSnapshot(7, 3, 128, 64, 255, 4096, 2048);

    try std.testing.expectEqual(@as(u16, 7), snapshot.num_queues);
    try std.testing.expectEqual(@as(u16, 3), snapshot.requested_poll_queues);
    try std.testing.expectEqual(@as(u32, 128), snapshot.seg_max);
    try std.testing.expectEqual(@as(u32, 64), snapshot.cmd_per_lun);
    try std.testing.expectEqual(@as(u32, 255), snapshot.max_target);
    try std.testing.expectEqual(@as(u32, 4096), snapshot.max_lun);
    try std.testing.expectEqual(@as(u32, 2048), snapshot.max_sectors);
    try std.testing.expect(snapshot.uses_control_queue);
    try std.testing.expect(snapshot.uses_event_queue);
    try std.testing.expect(snapshot.respects_poll_queue_clamp);
    try std.testing.expect(snapshot.preserves_probe_only_scope);
    try std.testing.expect(snapshot.blocks_dma_submission);
}

test "phase12 virtio scsi syntax lab keeps recovery summaries reachable through freeze and restore" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    _ = try lab.planQueueLayout(7, 2);

    const frozen = try lab.freezeForTransportReset();
    const restore_summary = try lab.recoveryRestoreSummary();
    const rebind_summary = try lab.recoveryRestoreQueueRebindSummary();
    const ownership_summary = try lab.recoveryEventBufferOwnershipSummary();
    const rearm_summary = try lab.recoveryEventRearmSummary();
    const rollback_summary = try lab.recoveryRollbackSummary();
    const restored = try lab.restoreAfterTransportReset();

    try std.testing.expectEqual(virtio_scsi.RecoveryAction.freeze, frozen.action);
    try std.testing.expectEqual(virtio_scsi.RecoveryAction.restore, restored.action);
    try std.testing.expect(restore_summary.requires_find_vqs);
    try std.testing.expect(restore_summary.find_vqs_before_device_ready);
    try std.testing.expect(restore_summary.device_ready_before_event_rearm);
    try std.testing.expect(rebind_summary.recreates_control_and_event_queues);
    try std.testing.expect(rebind_summary.recreates_request_queues_before_device_ready);
    try std.testing.expect(rebind_summary.defers_event_buffers_until_after_device_ready);
    try std.testing.expect(ownership_summary.event_queue_reserved_during_freeze);
    try std.testing.expect(ownership_summary.event_buffers_stay_on_event_queue);
    try std.testing.expect(ownership_summary.request_queues_cannot_borrow_event_buffers);
    try std.testing.expect(rearm_summary.reuses_frozen_event_queue_index);
    try std.testing.expect(rearm_summary.requires_device_ready_before_rearm);
    try std.testing.expect(rollback_summary.blocks_queue_planning_until_restore);
    try std.testing.expect(rollback_summary.keeps_frozen_layout_for_restore);
    try std.testing.expect(rollback_summary.clears_live_layout_after_restore);
    try std.testing.expectEqual(@as(u16, 1), restored.recovery_generation);
}
