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
