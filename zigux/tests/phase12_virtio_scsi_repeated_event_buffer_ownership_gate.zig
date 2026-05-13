const std = @import("std");
const virtio_scsi = @import("virtio_scsi");

test "phase12 virtio scsi repeated event-buffer ownership summary tracks replanned topology" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();

    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryEventBufferOwnershipSummary());

    _ = try lab.planQueueLayout(6, 2);
    _ = try lab.freezeForTransportReset();

    const first = try lab.recoveryEventBufferOwnershipSummary();
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", first.anchor);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_queue_index), first.event_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), first.remembered_event_buffer_count);
    try std.testing.expectEqual(@as(u16, 6), first.request_queue_count);
    try std.testing.expectEqual(@as(u16, 2), first.poll_queue_count);
    try std.testing.expect(first.event_buffers_reserved_for_event_queue);
    try std.testing.expect(!first.request_queues_can_borrow_event_buffers);
    try std.testing.expect(first.requires_device_ready_before_event_rearm);
    try std.testing.expect(first.requires_event_rearm_before_request_queue_reuse);

    _ = try lab.restoreAfterTransportReset();
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryEventBufferOwnershipSummary());

    _ = try lab.planQueueLayout(4, 1);
    _ = try lab.freezeForTransportReset();

    const second = try lab.recoveryEventBufferOwnershipSummary();
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", second.anchor);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_queue_index), second.event_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), second.remembered_event_buffer_count);
    try std.testing.expectEqual(@as(u16, 4), second.request_queue_count);
    try std.testing.expectEqual(@as(u16, 1), second.poll_queue_count);
    try std.testing.expect(second.event_buffers_reserved_for_event_queue);
    try std.testing.expect(!second.request_queues_can_borrow_event_buffers);
    try std.testing.expect(second.requires_device_ready_before_event_rearm);
    try std.testing.expect(second.requires_event_rearm_before_request_queue_reuse);
}
