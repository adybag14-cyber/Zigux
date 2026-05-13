const std = @import("std");
const virtio_scsi = @import("virtio_scsi");

test "phase12 virtio scsi repeated rollback gate reuses only replanned queue and depth state" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();

    _ = try lab.captureQueueDepthSummary(.{
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
    _ = try lab.freezeForTransportReset();
    _ = try lab.restoreAfterTransportReset();

    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryQueuePlan());
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryQueueDepthSummary());
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryIoQueueMapSummary());
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryEventBufferOwnershipSummary());
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryHostScanSummary());

    const replanned_depth = try lab.captureQueueDepthSummary(.{
        .host_limit = .{
            .probe = .{
                .num_queues = 4,
                .requested_poll_queues = 1,
                .cmd_per_lun = 9,
                .max_target = 3,
                .max_lun = 2,
                .max_sectors = 1536,
            },
            .synthetic_can_queue = 3,
        },
        .requested_depth = 9,
    });
    try std.testing.expectEqual(@as(u32, 3), replanned_depth.effective_can_queue);
    try std.testing.expectEqual(@as(u32, 3), replanned_depth.effective_cmd_per_lun);
    try std.testing.expectEqual(@as(u32, 3), replanned_depth.clamped_queue_depth);

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
    try std.testing.expectEqual(@as(u32, 9), second_depth.requested_depth);
    try std.testing.expectEqual(@as(u32, 3), second_depth.effective_can_queue);
    try std.testing.expectEqual(@as(u32, 3), second_depth.effective_cmd_per_lun);
    try std.testing.expectEqual(@as(u32, 3), second_depth.clamped_queue_depth);
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

    const ownership = try lab.recoveryEventBufferOwnershipSummary();
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_queue_index), ownership.event_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), ownership.remembered_event_buffer_count);
    try std.testing.expectEqual(@as(u16, 4), ownership.request_queue_count);
    try std.testing.expectEqual(@as(u16, 1), ownership.poll_queue_count);
    try std.testing.expect(ownership.event_buffers_reserved_for_event_queue);
    try std.testing.expect(!ownership.request_queues_can_borrow_event_buffers);
    try std.testing.expect(ownership.requires_device_ready_before_event_rearm);
    try std.testing.expect(ownership.requires_event_rearm_before_request_queue_reuse);

    const second_host_scan = try lab.recoveryHostScanSummary();
    try std.testing.expectEqual(@as(u16, 4), second_host_scan.remembered_request_queues);
    try std.testing.expectEqual(@as(u16, 1), second_host_scan.remembered_poll_queues);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), second_host_scan.remembered_event_buffer_count);
    try std.testing.expectEqual(@as(u16, 1), second_host_scan.recovery_generation);
    try std.testing.expect(second_host_scan.requires_control_queue_restore_before_scan);
    try std.testing.expect(second_host_scan.requires_event_rearm_before_scan);
    try std.testing.expect(second_host_scan.requires_request_queue_restore_before_scan);
    try std.testing.expect(second_host_scan.requires_async_scan_resume);

    const second_restore = try lab.restoreAfterTransportReset();
    try std.testing.expectEqual(@as(u16, 2), second_restore.recovery_generation);
    try std.testing.expect(second_restore.request_planning_available);
    try std.testing.expect(second_restore.event_recycling_enabled);
    try std.testing.expectEqual(@as(u16, 4), second_restore.remembered_request_queues);
    try std.testing.expectEqual(@as(u16, 1), second_restore.remembered_poll_queues);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), second_restore.remembered_event_buffer_count);

    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryQueuePlan());
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryQueueDepthSummary());
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryIoQueueMapSummary());
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryEventBufferOwnershipSummary());
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryHostScanSummary());
}
