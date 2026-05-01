const std = @import("std");
const virtio_scsi = @import("../../drivers/scsi/virtio_scsi.zig");

test "phase12 virtio scsi restore forces fresh post-rollback throughput captures" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    _ = try lab.captureProbeSnapshot(.{
        .num_queues = 4,
        .requested_poll_queues = 1,
        .seg_max = 64,
        .cmd_per_lun = 16,
        .max_target = 7,
        .max_lun = 1,
        .max_sectors = 1024,
    });
    _ = try lab.freezeForTransportReset();

    try std.testing.expectError(error.TransportFrozen, lab.captureProbeSnapshot(.{
        .num_queues = 5,
        .requested_poll_queues = 2,
    }));
    try std.testing.expectError(error.TransportFrozen, lab.captureHostLimitSummary(.{
        .probe = .{
            .num_queues = 5,
            .requested_poll_queues = 2,
            .cmd_per_lun = 9,
        },
        .synthetic_can_queue = 7,
    }));
    try std.testing.expectError(error.TransportFrozen, lab.captureQueueDepthSummary(.{
        .host_limit = .{
            .probe = .{
                .num_queues = 5,
                .requested_poll_queues = 2,
                .cmd_per_lun = 9,
            },
            .synthetic_can_queue = 7,
        },
        .requested_depth = 4,
    }));
    try std.testing.expectError(error.TransportFrozen, lab.captureIoQueueMapSummary(5, 2));

    _ = try lab.restoreAfterTransportReset();

    const recaptured = try lab.captureHostLimitSummary(.{
        .probe = .{
            .num_queues = 5,
            .requested_poll_queues = 2,
            .cmd_per_lun = 9,
            .max_target = 3,
            .max_lun = 2,
            .max_sectors = 1536,
        },
        .synthetic_can_queue = 7,
    });
    try std.testing.expectEqual(@as(u32, 7), recaptured.effective_can_queue);
    try std.testing.expectEqual(@as(u32, 7), recaptured.effective_cmd_per_lun);
    try std.testing.expectEqual(@as(u16, 5), recaptured.nr_hw_queues);
    try std.testing.expectEqual(@as(u32, 4), recaptured.max_target);
    try std.testing.expectEqual(@as(u32, 0x4003), recaptured.max_lun);
    try std.testing.expectEqual(@as(u32, 1536), recaptured.max_sectors);

    const requeued = try lab.captureQueueDepthSummary(.{
        .host_limit = .{
            .probe = .{
                .num_queues = 5,
                .requested_poll_queues = 2,
                .cmd_per_lun = 9,
                .max_target = 3,
                .max_lun = 2,
                .max_sectors = 1536,
            },
            .synthetic_can_queue = 7,
        },
        .requested_depth = 11,
    });
    try std.testing.expectEqual(@as(u32, 11), requeued.requested_depth);
    try std.testing.expectEqual(@as(u32, 7), requeued.effective_can_queue);
    try std.testing.expectEqual(@as(u32, 7), requeued.effective_cmd_per_lun);
    try std.testing.expectEqual(@as(u32, 7), requeued.clamped_queue_depth);
    try std.testing.expect(requeued.tracks_queue_depth);
    try std.testing.expect(requeued.uses_change_queue_depth);

    const remapped = try lab.captureIoQueueMapSummary(5, 2);
    try std.testing.expectEqual(@as(u16, 3), remapped.nr_maps);
    try std.testing.expectEqual(@as(u16, 3), remapped.default_queue_count);
    try std.testing.expectEqual(@as(u16, 2), remapped.poll_queue_count);
    try std.testing.expectEqual(@as(u16, 0), remapped.default_queue_offset);
    try std.testing.expectEqual(@as(u16, 3), remapped.read_queue_offset);
    try std.testing.expectEqual(@as(u16, 3), remapped.poll_queue_offset);
    try std.testing.expect(remapped.default_queues_use_virtio_affinity);
    try std.testing.expect(remapped.poll_queues_use_blk_mq_mapping);
}
