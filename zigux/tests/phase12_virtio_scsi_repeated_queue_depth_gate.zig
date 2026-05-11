const std = @import("std");
const virtio_scsi = @import("../../drivers/scsi/virtio_scsi.zig");

test "phase12 virtio scsi repeated freeze refreshes queue depth recovery clamp after replanning" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    _ = try lab.planQueueLayout(6, 2);
    _ = try lab.freezeForTransportReset();
    _ = try lab.restoreAfterTransportReset();

    const replanned = try lab.planQueueLayout(4, 1);
    try std.testing.expectEqual(@as(u16, 3), replanned.default_queues);
    try std.testing.expectEqual(@as(u16, 1), replanned.poll_queues);
    try std.testing.expectEqual(@as(?u16, 5), replanned.first_poll_queue_index);

    const recaptured_depth = try lab.captureQueueDepthSummary(.{
        .host_limit = .{
            .probe = .{
                .num_queues = 4,
                .requested_poll_queues = 1,
                .cmd_per_lun = 9,
                .max_target = 3,
                .max_lun = 2,
                .max_sectors = 1536,
            },
            .synthetic_can_queue = 6,
        },
        .requested_depth = 11,
    });
    try std.testing.expectEqual(@as(u32, 6), recaptured_depth.effective_can_queue);
    try std.testing.expectEqual(@as(u32, 6), recaptured_depth.effective_cmd_per_lun);
    try std.testing.expectEqual(@as(u32, 6), recaptured_depth.clamped_queue_depth);

    const second_freeze = try lab.freezeForTransportReset();
    try std.testing.expectEqual(@as(u16, 1), second_freeze.recovery_generation);
    try std.testing.expectEqual(@as(u16, 4), second_freeze.remembered_request_queues);
    try std.testing.expectEqual(@as(u16, 1), second_freeze.remembered_poll_queues);

    const second_depth = try lab.recoveryQueueDepthSummary();
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", second_depth.anchor);
    try std.testing.expectEqual(@as(u32, 11), second_depth.requested_depth);
    try std.testing.expectEqual(@as(u32, 6), second_depth.effective_can_queue);
    try std.testing.expectEqual(@as(u32, 6), second_depth.effective_cmd_per_lun);
    try std.testing.expectEqual(@as(u32, 6), second_depth.clamped_queue_depth);
    try std.testing.expect(second_depth.tracks_queue_depth);
    try std.testing.expect(second_depth.requires_change_queue_depth_restore);

    _ = try lab.restoreAfterTransportReset();
}
