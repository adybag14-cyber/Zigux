const std = @import("std");
const virtio_scsi = @import("virtio_scsi");

test "phase12 virtio scsi queue planner stays anchored to virtio_scsi.c" {
    const descriptor = virtio_scsi.VirtioScsiQueueLab.descriptor();
    try std.testing.expectEqualStrings("virtio_scsi_queue_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_queue_family_planner);
    try std.testing.expect(!descriptor.touches_live_dma);
    try std.testing.expect(!descriptor.touches_scsi_host);
    try std.testing.expect(!descriptor.touches_transport_reset);

    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    const layout = try lab.planQueueLayout(8, 3);
    try std.testing.expectEqual(@as(u16, 8), layout.request_queues);
    try std.testing.expectEqual(@as(u16, 3), layout.requested_poll_queues);
    try std.testing.expectEqual(@as(u16, 5), layout.default_queues);
    try std.testing.expectEqual(@as(u16, 0), layout.read_queues);
    try std.testing.expectEqual(@as(u16, 3), layout.poll_queues);
    try std.testing.expectEqual(@as(u16, 10), layout.total_queues);
    try std.testing.expectEqual(@as(u16, virtio_scsi.control_queue_index), layout.control_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_queue_index), layout.event_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_scsi.request_queue_base), layout.first_request_queue_index);
    try std.testing.expectEqual(@as(?u16, 7), layout.first_poll_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), layout.event_buffer_count);
}

test "phase12 virtio scsi clamps poll queues and classifies request families" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    const layout = try lab.planQueueLayout(4, 9);
    try std.testing.expectEqual(@as(u16, 1), layout.default_queues);
    try std.testing.expectEqual(@as(u16, 3), layout.poll_queues);
    try std.testing.expectEqual(@as(?u16, 3), layout.first_poll_queue_index);

    const first = try lab.requestQueue(0);
    try std.testing.expectEqual(@as(u16, 0), first.local_index);
    try std.testing.expectEqual(@as(u16, 2), first.global_index);
    try std.testing.expectEqual(virtio_scsi.RequestQueueKind.request, first.kind);

    const second = try lab.requestQueue(1);
    try std.testing.expectEqual(@as(u16, 3), second.global_index);
    try std.testing.expectEqual(virtio_scsi.RequestQueueKind.request_poll, second.kind);

    const fourth = try lab.requestQueue(3);
    try std.testing.expectEqual(@as(u16, 5), fourth.global_index);
    try std.testing.expectEqual(virtio_scsi.RequestQueueKind.request_poll, fourth.kind);
}

test "phase12 virtio scsi keeps one default queue and rejects missing layouts" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    try std.testing.expectError(error.QueueLayoutUnavailable, lab.requestQueue(0));
    try std.testing.expectError(error.InvalidRequestQueueCount, lab.planQueueLayout(0, 0));

    const single = try lab.planQueueLayout(1, 4);
    try std.testing.expectEqual(@as(u16, 1), single.default_queues);
    try std.testing.expectEqual(@as(u16, 0), single.poll_queues);
    try std.testing.expectEqual(@as(?u16, null), single.first_poll_queue_index);

    try std.testing.expectError(error.RequestQueueIndexOutOfRange, lab.requestQueue(1));
}