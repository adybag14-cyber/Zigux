const std = @import("std");
const virtio_scsi = @import("virtio_scsi");

test "phase12 virtio scsi queue planner stays anchored to virtio_scsi.c" {
    const descriptor = virtio_scsi.VirtioScsiQueueLab.descriptor();
    try std.testing.expectEqualStrings("virtio_scsi_queue_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_queue_family_planner);
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

test "phase12 virtio scsi repeated freeze restore tracks the replanned recovery boundary" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    _ = try lab.planQueueLayout(6, 2);
    _ = try lab.freezeForTransportReset();

    const first_plan = try lab.recoveryRestoreSummary();
    try std.testing.expectEqual(@as(u16, 6), first_plan.request_queues);
    try std.testing.expectEqual(@as(u16, 4), first_plan.default_queues);
    try std.testing.expectEqual(@as(u16, 2), first_plan.poll_queues);
    try std.testing.expectEqual(@as(?u16, 6), first_plan.first_poll_queue_index);

    const first_restore = try lab.restoreAfterTransportReset();
    try std.testing.expectEqual(@as(u16, 1), first_restore.recovery_generation);
    try std.testing.expectEqual(@as(u16, 6), first_restore.remembered_request_queues);
    try std.testing.expectEqual(@as(u16, 2), first_restore.remembered_poll_queues);
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryRestoreSummary());
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryRestoreQueueRebindSummary());

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

    const second_restore = try lab.restoreAfterTransportReset();
    try std.testing.expectEqual(@as(u16, 2), second_restore.recovery_generation);
    try std.testing.expectEqual(@as(u16, 4), second_restore.remembered_request_queues);
    try std.testing.expectEqual(@as(u16, 1), second_restore.remembered_poll_queues);
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
