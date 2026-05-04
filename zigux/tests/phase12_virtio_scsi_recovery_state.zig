const std = @import("std");
const virtio_scsi = @import("virtio_scsi");

test "phase12 virtio scsi restore clears stale queue depth before a later freeze" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();

    const captured = try lab.captureQueueDepthSummary(.{
        .host_limit = .{
            .probe = .{
                .num_queues = 6,
                .requested_poll_queues = 2,
                .cmd_per_lun = 13,
                .max_target = 9,
                .max_lun = 4,
                .max_sectors = 1024,
            },
            .synthetic_can_queue = 7,
        },
        .requested_depth = 12,
    });
    try std.testing.expectEqual(@as(u32, 7), captured.clamped_queue_depth);

    _ = try lab.freezeForTransportReset();
    const restored = try lab.restoreAfterTransportReset();
    try std.testing.expect(restored.requires_queue_layout_replan);
    try std.testing.expect(restored.cleared_probe_snapshot);
    try std.testing.expect(restored.cleared_host_limit_summary);
    try std.testing.expect(restored.cleared_queue_depth_summary);
    try std.testing.expect(restored.cleared_io_queue_map_summary);

    const relaid = try lab.planQueueLayout(3, 0);
    try std.testing.expectEqual(@as(u16, 3), relaid.request_queues);
    try std.testing.expectEqual(@as(u16, 3), relaid.default_queues);
    try std.testing.expectEqual(@as(u16, 0), relaid.poll_queues);

    const second_freeze = try lab.freezeForTransportReset();
    try std.testing.expectEqual(@as(u16, 1), second_freeze.recovery_generation);
    try std.testing.expectEqual(@as(u16, 3), second_freeze.remembered_request_queues);
    try std.testing.expectEqual(@as(u16, 0), second_freeze.remembered_poll_queues);

    const plan = try lab.recoveryQueuePlan();
    try std.testing.expectEqual(@as(u16, 3), plan.request_queues);
    try std.testing.expectEqual(@as(u16, 3), plan.default_queues);
    try std.testing.expectEqual(@as(u16, 0), plan.poll_queues);
    try std.testing.expectEqual(@as(?u16, null), plan.first_poll_queue_index);

    try std.testing.expectError(error.QueueDepthSummaryUnavailable, lab.recoveryQueueDepthSummary());
}

test "phase12 virtio scsi second freeze refreshes restore summary after replanning" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();

    _ = try lab.planQueueLayout(6, 2);
    _ = try lab.freezeForTransportReset();
    _ = try lab.restoreAfterTransportReset();

    const replanned = try lab.planQueueLayout(3, 0);
    try std.testing.expectEqual(@as(u16, 3), replanned.request_queues);
    try std.testing.expectEqual(@as(u16, 3), replanned.default_queues);
    try std.testing.expectEqual(@as(u16, 0), replanned.poll_queues);

    const second_freeze = try lab.freezeForTransportReset();
    try std.testing.expectEqual(@as(u16, 1), second_freeze.recovery_generation);
    try std.testing.expectEqual(@as(u16, 3), second_freeze.remembered_request_queues);
    try std.testing.expectEqual(@as(u16, 0), second_freeze.remembered_poll_queues);

    const restore = try lab.recoveryRestoreSummary();
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", restore.anchor);
    try std.testing.expectEqual(@as(u16, 3), restore.request_queues);
    try std.testing.expectEqual(@as(u16, 3), restore.default_queues);
    try std.testing.expectEqual(@as(u16, 0), restore.read_queues);
    try std.testing.expectEqual(@as(u16, 0), restore.poll_queues);
    try std.testing.expectEqual(@as(u16, 5), restore.total_queues);
    try std.testing.expectEqual(@as(u16, virtio_scsi.control_queue_index), restore.control_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_queue_index), restore.event_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_scsi.request_queue_base), restore.first_request_queue_index);
    try std.testing.expectEqual(@as(?u16, null), restore.first_poll_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), restore.event_buffer_count);
    try std.testing.expect(restore.requires_find_vqs);
    try std.testing.expect(restore.requires_io_queue_map_restore);
    try std.testing.expect(restore.requires_device_ready);
    try std.testing.expect(restore.requires_event_rearm);
    try std.testing.expect(restore.find_vqs_before_device_ready);
    try std.testing.expect(restore.device_ready_before_event_rearm);
    try std.testing.expect(restore.preserves_scsi_host_registration);
    try std.testing.expect(!restore.reruns_host_scan);
}

test "phase12 virtio scsi recovery event refill summary follows replanned frozen topology" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryEventRefillSummary());

    _ = try lab.planQueueLayout(6, 2);
    _ = try lab.freezeForTransportReset();

    const first = try lab.recoveryEventRefillSummary();
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", first.anchor);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_queue_index), first.event_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), first.event_buffer_count);
    try std.testing.expectEqual(@as(u16, 6), first.request_queue_count);
    try std.testing.expectEqual(@as(u16, 2), first.poll_queue_count);
    try std.testing.expect(first.requires_event_queue_refill);
    try std.testing.expect(first.requires_event_buffer_repost);
    try std.testing.expect(first.requires_kick_event_all);

    _ = try lab.restoreAfterTransportReset();

    const replanned = try lab.planQueueLayout(3, 0);
    try std.testing.expectEqual(@as(u16, 3), replanned.request_queues);
    try std.testing.expectEqual(@as(u16, 0), replanned.poll_queues);
    _ = try lab.freezeForTransportReset();

    const second = try lab.recoveryEventRefillSummary();
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", second.anchor);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_queue_index), second.event_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), second.event_buffer_count);
    try std.testing.expectEqual(@as(u16, 3), second.request_queue_count);
    try std.testing.expectEqual(@as(u16, 0), second.poll_queue_count);
    try std.testing.expect(second.requires_event_queue_refill);
    try std.testing.expect(second.requires_event_buffer_repost);
    try std.testing.expect(second.requires_kick_event_all);

    _ = try lab.restoreAfterTransportReset();
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryEventRefillSummary());
}
