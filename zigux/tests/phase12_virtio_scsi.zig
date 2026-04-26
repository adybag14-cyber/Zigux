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

test "phase12 virtio scsi probe snapshot records config defaults and queue topology" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    const snapshot = try lab.captureProbeSnapshot(.{
        .config_num_queues = 8,
        .config_seg_max = 128,
        .config_cmd_per_lun = 64,
        .config_max_target = 31,
        .config_max_lun = 255,
        .config_max_sectors = 2048,
        .cpu_queue_limit = 6,
        .blk_mq_queue_limit = 5,
        .requested_poll_queues = 2,
    });

    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", snapshot.anchor);
    try std.testing.expectEqual(@as(u16, 8), snapshot.configured_request_queues);
    try std.testing.expectEqual(@as(u16, 6), snapshot.cpu_queue_limit);
    try std.testing.expectEqual(@as(u16, 5), snapshot.blk_mq_queue_limit);
    try std.testing.expectEqual(@as(u16, 5), snapshot.request_queues);
    try std.testing.expectEqual(@as(u32, 128), snapshot.seg_max);
    try std.testing.expectEqual(@as(u32, 64), snapshot.cmd_per_lun);
    try std.testing.expectEqual(@as(u32, 31), snapshot.max_target);
    try std.testing.expectEqual(@as(u32, 32), snapshot.num_targets);
    try std.testing.expectEqual(@as(u32, 255), snapshot.max_lun);
    try std.testing.expectEqual(@as(u32, 2048), snapshot.max_sectors);
    try std.testing.expectEqual(@as(u16, 5), snapshot.layout.request_queues);
    try std.testing.expectEqual(@as(u16, 3), snapshot.layout.default_queues);
    try std.testing.expectEqual(@as(u16, 2), snapshot.layout.poll_queues);
    try std.testing.expectEqual(@as(u16, 7), snapshot.layout.total_queues);
    try std.testing.expectEqual(@as(?u16, 5), snapshot.layout.first_poll_queue_index);
}

test "phase12 virtio scsi probe snapshot defaults zeros and rejects invalid queue caps" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    const snapshot = try lab.captureProbeSnapshot(.{
        .config_num_queues = 0,
        .config_seg_max = 0,
        .config_cmd_per_lun = 0,
        .config_max_target = 0,
        .config_max_lun = 0,
        .config_max_sectors = 0,
        .cpu_queue_limit = 4,
        .blk_mq_queue_limit = 8,
        .requested_poll_queues = 3,
    });

    try std.testing.expectEqual(@as(u16, 1), snapshot.configured_request_queues);
    try std.testing.expectEqual(@as(u16, 1), snapshot.request_queues);
    try std.testing.expectEqual(@as(u32, 1), snapshot.seg_max);
    try std.testing.expectEqual(@as(u32, 1), snapshot.cmd_per_lun);
    try std.testing.expectEqual(@as(u32, 1), snapshot.num_targets);
    try std.testing.expectEqual(@as(u32, 0), snapshot.max_lun);
    try std.testing.expectEqual(@as(u32, 0xFFFF), snapshot.max_sectors);
    try std.testing.expectEqual(@as(u16, 1), snapshot.layout.default_queues);
    try std.testing.expectEqual(@as(u16, 0), snapshot.layout.poll_queues);
    try std.testing.expectEqual(@as(?u16, null), snapshot.layout.first_poll_queue_index);

    try std.testing.expectError(error.InvalidQueueLimit, lab.captureProbeSnapshot(.{
        .config_num_queues = 2,
        .config_seg_max = 1,
        .config_cmd_per_lun = 1,
        .config_max_target = 0,
        .config_max_lun = 0,
        .config_max_sectors = 1,
        .cpu_queue_limit = 0,
        .blk_mq_queue_limit = 2,
        .requested_poll_queues = 0,
    }));
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

test "phase12 virtio scsi probe snapshot refreshes queue layout for later queue lookups" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    _ = try lab.captureProbeSnapshot(.{
        .config_num_queues = 6,
        .config_seg_max = 32,
        .config_cmd_per_lun = 8,
        .config_max_target = 3,
        .config_max_lun = 7,
        .config_max_sectors = 256,
        .cpu_queue_limit = 6,
        .blk_mq_queue_limit = 6,
        .requested_poll_queues = 2,
    });

    const first_layout_queue = try lab.requestQueue(4);
    try std.testing.expectEqual(@as(u16, 6), first_layout_queue.global_index);
    try std.testing.expectEqual(virtio_scsi.RequestQueueKind.request_poll, first_layout_queue.kind);

    const refreshed = try lab.captureProbeSnapshot(.{
        .config_num_queues = 2,
        .config_seg_max = 64,
        .config_cmd_per_lun = 16,
        .config_max_target = 1,
        .config_max_lun = 3,
        .config_max_sectors = 128,
        .cpu_queue_limit = 2,
        .blk_mq_queue_limit = 4,
        .requested_poll_queues = 1,
    });

    try std.testing.expectEqual(@as(u16, 2), refreshed.request_queues);
    try std.testing.expectEqual(@as(u16, 1), refreshed.layout.default_queues);
    try std.testing.expectEqual(@as(u16, 1), refreshed.layout.poll_queues);
    try std.testing.expectEqual(@as(?u16, 3), refreshed.layout.first_poll_queue_index);

    const refreshed_queue = try lab.requestQueue(1);
    try std.testing.expectEqual(@as(u16, 3), refreshed_queue.global_index);
    try std.testing.expectEqual(virtio_scsi.RequestQueueKind.request_poll, refreshed_queue.kind);
    try std.testing.expectError(error.RequestQueueIndexOutOfRange, lab.requestQueue(2));
}
