const std = @import("std");
const virtio_scsi = @import("virtio_scsi");

test "phase12 virtio scsi repeated replan gate keeps the second-cycle recovery packet explicit" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    _ = try lab.planQueueLayout(6, 2);
    _ = try lab.freezeForTransportReset();
    _ = try lab.restoreAfterTransportReset();

    _ = try lab.captureQueueDepthSummary(.{
        .host_limit = .{
            .probe = .{
                .num_queues = 4,
                .requested_poll_queues = 1,
                .cmd_per_lun = 13,
                .max_target = 9,
                .max_lun = 4,
                .max_sectors = 1024,
            },
            .synthetic_can_queue = 7,
        },
        .requested_depth = 12,
    });

    const replanned = try lab.planQueueLayout(4, 1);
    try std.testing.expectEqual(@as(u16, 3), replanned.default_queues);
    try std.testing.expectEqual(@as(u16, 1), replanned.poll_queues);
    try std.testing.expectEqual(@as(?u16, 5), replanned.first_poll_queue_index);

    const second_freeze = try lab.freezeForTransportReset();
    try std.testing.expectEqual(@as(u16, 1), second_freeze.recovery_generation);
    try std.testing.expectEqual(@as(u16, 4), second_freeze.remembered_request_queues);
    try std.testing.expectEqual(@as(u16, 1), second_freeze.remembered_poll_queues);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), second_freeze.remembered_event_buffer_count);

    const second_plan = try lab.recoveryQueuePlan();
    try std.testing.expectEqual(@as(u16, 4), second_plan.request_queues);
    try std.testing.expectEqual(@as(u16, 3), second_plan.default_queues);
    try std.testing.expectEqual(@as(u16, 1), second_plan.poll_queues);
    try std.testing.expectEqual(@as(u16, 6), second_plan.total_queues);
    try std.testing.expectEqual(@as(?u16, 5), second_plan.first_poll_queue_index);
    try std.testing.expect(second_plan.requires_control_queue_restore);
    try std.testing.expect(second_plan.requires_event_queue_refill);
    try std.testing.expect(second_plan.requires_request_queue_restore);

    const second_depth = try lab.recoveryQueueDepthSummary();
    try std.testing.expectEqual(@as(u32, 12), second_depth.requested_depth);
    try std.testing.expectEqual(@as(u32, 7), second_depth.effective_can_queue);
    try std.testing.expectEqual(@as(u32, 7), second_depth.effective_cmd_per_lun);
    try std.testing.expectEqual(@as(u32, 7), second_depth.clamped_queue_depth);
    try std.testing.expect(second_depth.tracks_queue_depth);
    try std.testing.expect(second_depth.requires_change_queue_depth_restore);

    const second_map = try lab.recoveryIoQueueMapSummary();
    try std.testing.expectEqual(@as(u16, 3), second_map.nr_maps);
    try std.testing.expectEqual(@as(u16, 3), second_map.default_queue_count);
    try std.testing.expectEqual(@as(u16, 1), second_map.poll_queue_count);
    try std.testing.expectEqual(@as(u16, 3), second_map.read_queue_offset);
    try std.testing.expectEqual(@as(u16, 3), second_map.poll_queue_offset);
    try std.testing.expect(second_map.requires_blk_mq_map_restore);
    try std.testing.expect(second_map.requires_virtio_affinity_restore);
    try std.testing.expect(second_map.requires_poll_map_restore);

    const second_restore = try lab.restoreAfterTransportReset();
    try std.testing.expectEqual(@as(u16, 2), second_restore.recovery_generation);
    try std.testing.expect(second_restore.request_planning_available);
    try std.testing.expect(second_restore.event_recycling_enabled);
    try std.testing.expectEqual(@as(u16, 4), second_restore.remembered_request_queues);
    try std.testing.expectEqual(@as(u16, 1), second_restore.remembered_poll_queues);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), second_restore.remembered_event_buffer_count);
}
