const std = @import("std");
const virtio_scsi = @import("../../drivers/scsi/virtio_scsi.zig");

test "phase12 virtio scsi repeated freeze keeps second-cycle rollback and restore safeguards explicit" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    _ = try lab.planQueueLayout(6, 2);
    _ = try lab.freezeForTransportReset();
    _ = try lab.restoreAfterTransportReset();

    const replanned = try lab.planQueueLayout(4, 1);
    try std.testing.expectEqual(@as(u16, 3), replanned.default_queues);
    try std.testing.expectEqual(@as(u16, 1), replanned.poll_queues);
    try std.testing.expectEqual(@as(?u16, 5), replanned.first_poll_queue_index);

    const second_freeze = try lab.freezeForTransportReset();
    try std.testing.expectEqual(@as(u16, 1), second_freeze.recovery_generation);
    try std.testing.expectEqual(@as(u16, 4), second_freeze.remembered_request_queues);
    try std.testing.expectEqual(@as(u16, 1), second_freeze.remembered_poll_queues);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), second_freeze.remembered_event_buffer_count);

    const second_rebind = try lab.recoveryRestoreQueueRebindSummary();
    try std.testing.expectEqual(@as(u16, 6), second_rebind.total_queues);
    try std.testing.expect(second_rebind.recreates_control_and_event_queues);
    try std.testing.expect(second_rebind.recreates_request_queues_before_device_ready);
    try std.testing.expect(second_rebind.defers_event_buffers_until_after_device_ready);

    const second_rollback = try lab.recoveryRollbackSummary();
    try std.testing.expectEqual(@as(u16, 1), second_rollback.recovery_generation);
    try std.testing.expectEqual(@as(u16, 4), second_rollback.request_queues);
    try std.testing.expectEqual(@as(u16, 3), second_rollback.default_queues);
    try std.testing.expectEqual(@as(u16, 1), second_rollback.poll_queues);
    try std.testing.expectEqual(@as(u16, 6), second_rollback.total_queues);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), second_rollback.event_buffer_count);
    try std.testing.expect(second_rollback.blocks_queue_planning_until_restore);
    try std.testing.expect(second_rollback.blocks_request_queue_access_until_restore);
    try std.testing.expect(second_rollback.keeps_frozen_layout_for_restore);
    try std.testing.expect(second_rollback.clears_live_layout_after_restore);
    try std.testing.expect(second_rollback.requires_replan_before_queue_reuse);

    const second_restore = try lab.restoreAfterTransportReset();
    try std.testing.expectEqual(@as(u16, 2), second_restore.recovery_generation);
    try std.testing.expect(second_restore.request_planning_available);
    try std.testing.expect(second_restore.event_recycling_enabled);
    try std.testing.expectEqual(@as(u16, 4), second_restore.remembered_request_queues);
    try std.testing.expectEqual(@as(u16, 1), second_restore.remembered_poll_queues);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), second_restore.remembered_event_buffer_count);
}
