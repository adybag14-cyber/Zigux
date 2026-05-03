const std = @import("std");
const virtio_scsi = @import("virtio_scsi");

test "phase12 virtio scsi recovery event refill summary mirrors frozen event queue state" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryEventRefillSummary());

    _ = try lab.planQueueLayout(6, 2);
    _ = try lab.freezeForTransportReset();

    const summary = try lab.recoveryEventRefillSummary();
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_queue_index), summary.event_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), summary.event_buffer_count);
    try std.testing.expectEqual(@as(u16, 6), summary.request_queue_count);
    try std.testing.expectEqual(@as(u16, 2), summary.poll_queue_count);
    try std.testing.expect(summary.requires_event_queue_refill);
    try std.testing.expect(summary.requires_event_buffer_repost);
    try std.testing.expect(summary.requires_kick_event_all);

    _ = try lab.restoreAfterTransportReset();
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryEventRefillSummary());
}

test "phase12 virtio scsi recovery event refill summary refreshes after replanning" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();

    _ = try lab.planQueueLayout(5, 2);
    _ = try lab.freezeForTransportReset();
    _ = try lab.restoreAfterTransportReset();

    _ = try lab.planQueueLayout(3, 0);
    _ = try lab.freezeForTransportReset();

    const summary = try lab.recoveryEventRefillSummary();
    try std.testing.expectEqual(@as(u16, 3), summary.request_queue_count);
    try std.testing.expectEqual(@as(u16, 0), summary.poll_queue_count);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), summary.event_buffer_count);
    try std.testing.expect(summary.requires_event_buffer_repost);
    try std.testing.expect(summary.requires_kick_event_all);
}
