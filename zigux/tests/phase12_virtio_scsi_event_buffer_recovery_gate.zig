const std = @import("std");
const virtio_scsi = @import("virtio_scsi");

test "phase12 virtio scsi event-buffer recovery summary records frozen ownership boundaries" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    _ = try lab.planQueueLayout(6, 2);
    _ = try lab.freezeForTransportReset();

    const summary = try lab.recoveryEventBufferOwnershipSummary();
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_queue_index), summary.event_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), summary.remembered_event_buffer_count);
    try std.testing.expectEqual(@as(u16, 6), summary.request_queue_count);
    try std.testing.expectEqual(@as(u16, 2), summary.poll_queue_count);
    try std.testing.expect(summary.event_buffers_reserved_for_event_queue);
    try std.testing.expect(!summary.request_queues_can_borrow_event_buffers);
    try std.testing.expect(summary.requires_device_ready_before_event_rearm);
    try std.testing.expect(summary.requires_event_rearm_before_request_queue_reuse);

    _ = try lab.restoreAfterTransportReset();
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryEventBufferOwnershipSummary());
}

test "phase12 virtio scsi event-buffer recovery summary follows the replanned second freeze" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryEventBufferOwnershipSummary());

    _ = try lab.planQueueLayout(6, 2);
    _ = try lab.freezeForTransportReset();
    _ = try lab.restoreAfterTransportReset();

    _ = try lab.planQueueLayout(4, 1);
    _ = try lab.freezeForTransportReset();

    const summary = try lab.recoveryEventBufferOwnershipSummary();
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_queue_index), summary.event_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), summary.remembered_event_buffer_count);
    try std.testing.expectEqual(@as(u16, 4), summary.request_queue_count);
    try std.testing.expectEqual(@as(u16, 1), summary.poll_queue_count);
    try std.testing.expect(summary.event_buffers_reserved_for_event_queue);
    try std.testing.expect(!summary.request_queues_can_borrow_event_buffers);
    try std.testing.expect(summary.requires_device_ready_before_event_rearm);
    try std.testing.expect(summary.requires_event_rearm_before_request_queue_reuse);
}
