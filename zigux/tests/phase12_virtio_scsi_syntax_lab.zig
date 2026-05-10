const std = @import("std");

const virtio_scsi = @import("virtio_scsi");

test "phase12 virtio scsi syntax lab keeps queue planning exports reachable" {
    const descriptor = virtio_scsi.VirtioScsiQueueLab.descriptor();

    _ = virtio_scsi.ModuleDescriptor;
    _ = virtio_scsi.QueueLayoutSummary;
    _ = virtio_scsi.ProbeConfigSnapshot;
    _ = virtio_scsi.HostShapeRequest;
    _ = virtio_scsi.HostShapeSummary;
    _ = virtio_scsi.RequestQueueSummary;
    _ = virtio_scsi.QueueWindowSummary;
    _ = virtio_scsi.RecoveryFreezeSummary;
    _ = virtio_scsi.RecoveryRestoreSummary;
    _ = virtio_scsi.RecoveryRestoreQueueRebindSummary;
    _ = virtio_scsi.RecoveryEventBufferOwnershipSummary;
    _ = virtio_scsi.RecoveryEventRearmSummary;
    _ = virtio_scsi.RecoveryRollbackSummary;

    try std.testing.expectEqualStrings("virtio_scsi_queue_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_queue_family_planner);
    try std.testing.expect(descriptor.provides_host_shape_summary);
    try std.testing.expect(!descriptor.touches_live_dma);
    try std.testing.expect(!descriptor.touches_scsi_host);
    try std.testing.expect(descriptor.touches_transport_reset);

    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    const layout = try lab.planQueueLayout(4, 2);
    try std.testing.expectEqualStrings(descriptor.anchor, layout.anchor);
    try std.testing.expectEqual(@as(u16, 4), layout.request_queues);
    try std.testing.expectEqual(@as(u16, 2), layout.requested_poll_queues);
    try std.testing.expectEqual(@as(u16, 2), layout.default_queues);
    try std.testing.expectEqual(@as(u16, 2), layout.poll_queues);
    try std.testing.expect(layout.total_queues >= layout.request_queues);
    try std.testing.expectEqual(@as(?u16, 4), layout.first_poll_queue_index);

    const probe = try lab.probeConfigSnapshot(4, 2, 128, 64, 255, 32, 1024);
    try std.testing.expectEqual(@as(u16, 4), probe.num_queues);
    try std.testing.expectEqual(@as(u16, 2), probe.requested_poll_queues);
    try std.testing.expectEqual(layout.default_queues, probe.default_queues);
    try std.testing.expectEqual(layout.poll_queues, probe.poll_queues);
    try std.testing.expect(probe.uses_control_queue);
    try std.testing.expect(probe.uses_event_queue);
    try std.testing.expect(probe.respects_poll_queue_clamp);
    try std.testing.expect(probe.preserves_probe_only_scope);
    try std.testing.expect(probe.blocks_dma_submission);

    const host = try lab.captureHostShapeSummary(.{
        .num_queues = 4,
        .requested_poll_queues = 2,
        .seg_max = 128,
        .cmd_per_lun = 64,
        .max_target = 255,
        .max_lun = 32,
        .max_sectors = 1024,
    });
    try std.testing.expectEqualStrings(descriptor.anchor, host.anchor);
    try std.testing.expectEqual(@as(u16, 4), host.request_queues);
    try std.testing.expectEqual(layout.default_queues, host.default_queues);
    try std.testing.expectEqual(layout.poll_queues, host.poll_queues);
    try std.testing.expectEqual(@as(u16, 4), host.nr_hw_queues);
    try std.testing.expectEqual(@as(u16, 3), host.nr_maps);
    try std.testing.expect(host.uses_map_queues);
    try std.testing.expect(host.uses_commit_rqs);
    try std.testing.expect(host.uses_mq_poll);
    try std.testing.expect(host.preserves_pre_registration_scope);

    const request_queue = try lab.requestQueue(3);
    try std.testing.expectEqual(@as(u16, 3), request_queue.local_index);
    try std.testing.expectEqual(@as(u16, 5), request_queue.global_index);

    const window = try lab.queueWindowSummary();
    try std.testing.expectEqual(@as(u16, 0), window.control_queue_index);
    try std.testing.expectEqual(@as(u16, 1), window.event_queue_index);
    try std.testing.expectEqual(@as(u16, 2), window.first_default_queue_index);
    try std.testing.expectEqual(@as(u16, 3), window.last_default_queue_index);
    try std.testing.expectEqual(@as(?u16, 4), window.first_poll_queue_index);
    try std.testing.expectEqual(@as(?u16, 5), window.last_poll_queue_index);
}

test "phase12 virtio scsi syntax lab keeps transport-reset recovery summaries reachable" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    const layout = try lab.planQueueLayout(4, 2);

    const freeze = try lab.freezeForTransportReset();
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", freeze.anchor);
    try std.testing.expectEqual(layout.request_queues, freeze.request_queues);
    try std.testing.expectEqual(layout.default_queues, freeze.default_queues);
    try std.testing.expectEqual(layout.poll_queues, freeze.poll_queues);
    try std.testing.expectEqual(layout.event_buffer_count, freeze.event_buffer_count);
    try std.testing.expectEqual(@as(u16, 1), freeze.recovery_generation);
    try std.testing.expect(freeze.blocks_queue_planning_until_restore);
    try std.testing.expect(freeze.blocks_request_queue_access_until_restore);

    const restore = try lab.recoveryRestoreSummary();
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", restore.anchor);
    try std.testing.expectEqual(layout.request_queues, restore.request_queues);
    try std.testing.expectEqual(layout.default_queues, restore.default_queues);
    try std.testing.expectEqual(layout.poll_queues, restore.poll_queues);
    try std.testing.expectEqual(layout.event_buffer_count, restore.event_buffer_count);
    try std.testing.expect(restore.requires_transport_reset);
    try std.testing.expect(restore.restores_event_queue_before_scsi_host_ready);
    try std.testing.expect(restore.rearms_event_queue_after_restore);
    try std.testing.expect(restore.device_ready_before_event_rearm);
    try std.testing.expect(restore.preserves_scsi_host_registration);
    try std.testing.expect(restore.reruns_host_scan);

    const rebind = try lab.recoveryRestoreQueueRebindSummary();
    try std.testing.expectEqual(layout.control_queue_index, rebind.control_queue_index);
    try std.testing.expectEqual(layout.event_queue_index, rebind.event_queue_index);
    try std.testing.expectEqual(layout.default_queues, rebind.default_queue_count);
    try std.testing.expectEqual(layout.poll_queues, rebind.poll_queue_count);
    try std.testing.expectEqual(layout.total_queues, rebind.total_queues);
    try std.testing.expect(rebind.recreates_control_and_event_queues);
    try std.testing.expect(rebind.recreates_request_queues_before_device_ready);
    try std.testing.expect(rebind.defers_event_buffers_until_after_device_ready);

    const ownership = try lab.recoveryEventBufferOwnershipSummary();
    try std.testing.expectEqual(layout.event_queue_index, ownership.event_queue_index);
    try std.testing.expectEqual(layout.request_queues, ownership.request_queues);
    try std.testing.expectEqual(layout.default_queues, ownership.default_queues);
    try std.testing.expectEqual(layout.poll_queues, ownership.poll_queues);
    try std.testing.expectEqual(layout.event_buffer_count, ownership.event_buffer_count);
    try std.testing.expect(ownership.event_queue_reserved_during_freeze);
    try std.testing.expect(ownership.event_buffers_stay_on_event_queue);
    try std.testing.expect(ownership.request_queues_cannot_borrow_event_buffers);
    try std.testing.expect(ownership.defers_event_buffers_until_after_device_ready);
    try std.testing.expect(ownership.requires_restore_rearm_before_reuse);

    const rearm = try lab.recoveryEventRearmSummary();
    try std.testing.expectEqual(layout.event_queue_index, rearm.event_queue_index);
    try std.testing.expectEqual(layout.request_queues, rearm.request_queues);
    try std.testing.expectEqual(layout.default_queues, rearm.default_queues);
    try std.testing.expectEqual(layout.poll_queues, rearm.poll_queues);
    try std.testing.expectEqual(layout.event_buffer_count, rearm.event_buffer_count);
    try std.testing.expect(rearm.reuses_frozen_event_queue_index);
    try std.testing.expect(rearm.requires_device_ready_before_rearm);
    try std.testing.expect(rearm.rearms_event_queue_before_event_recycling);
    try std.testing.expect(rearm.rearms_event_queue_before_request_queue_reuse);

    const rollback = try lab.recoveryRollbackSummary();
    try std.testing.expectEqual(layout.request_queues, rollback.request_queues);
    try std.testing.expectEqual(layout.default_queues, rollback.default_queues);
    try std.testing.expectEqual(layout.poll_queues, rollback.poll_queues);
    try std.testing.expectEqual(layout.total_queues, rollback.total_queues);
    try std.testing.expectEqual(layout.event_buffer_count, rollback.event_buffer_count);
    try std.testing.expectEqual(@as(u16, 1), rollback.recovery_generation);
    try std.testing.expect(rollback.blocks_queue_planning_until_restore);
    try std.testing.expect(rollback.blocks_request_queue_access_until_restore);
    try std.testing.expect(rollback.keeps_frozen_layout_for_restore);
    try std.testing.expect(rollback.clears_live_layout_after_restore);
    try std.testing.expect(rollback.requires_replan_before_queue_reuse);
}
