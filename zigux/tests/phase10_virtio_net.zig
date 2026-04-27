const std = @import("std");
const virtio_net = @import("virtio_net");

test "phase10 virtio net descriptor and probe snapshot stay on the bounded queue-planning surface" {
    const descriptor = virtio_net.VirtioNetProbeLab.descriptor();
    try std.testing.expectEqualStrings("virtio_net_probe_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_probe_queue_snapshot);
    try std.testing.expect(!descriptor.touches_live_dma);
    try std.testing.expect(!descriptor.touches_napi_poll);
    try std.testing.expect(!descriptor.touches_netdev_lifecycle);
    try std.testing.expect(!descriptor.touches_transport_recovery);

    var device = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
        virtio_net.feature_control_vq,
        virtio_net.feature_multiqueue,
        virtio_net.feature_rss,
    });

    const snapshot = try device.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
            virtio_net.feature_control_vq,
            virtio_net.feature_multiqueue,
            virtio_net.feature_rss,
        },
        .requested_queue_pairs = 2,
        .max_queue_pairs = 4,
    });

    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", snapshot.anchor);
    try std.testing.expectEqual(@as(u16, 2), snapshot.requested_queue_pairs);
    try std.testing.expectEqual(@as(u16, 2), snapshot.planned_queue_pairs);
    try std.testing.expectEqual(@as(u16, 2), snapshot.rx_queue_count);
    try std.testing.expectEqual(@as(u16, 2), snapshot.tx_queue_count);
    try std.testing.expectEqual(@as(u16, 5), snapshot.total_queue_count);
    try std.testing.expectEqual(@as(?u16, 4), snapshot.control_queue_index);
    try std.testing.expect(snapshot.mergeable_rx_buffers);
    try std.testing.expect(snapshot.has_rss);
    try std.testing.expectEqual(virtio_net.QueueFallbackReason.none, snapshot.fallback_reason);
    try std.testing.expectEqual(virtio_net.RecoveryState.stable, snapshot.recovery_state);
}

test "phase10 virtio net plans mergeable receive buffers with aligned room and page-pool intent" {
    var device = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
        virtio_net.feature_control_vq,
        virtio_net.feature_multiqueue,
    });

    const snapshot = try device.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
            virtio_net.feature_control_vq,
            virtio_net.feature_multiqueue,
        },
        .requested_queue_pairs = 2,
        .max_queue_pairs = 2,
    });

    const plan = try device.planMergeableReceiveBuffer(snapshot, .{
        .header_len = 12,
        .average_packet_len = 1500,
        .min_buf_len = 512,
        .headroom = 256,
        .cache_line_size = 64,
        .skb_shared_info_size = 320,
    });

    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", plan.anchor);
    try std.testing.expectEqual(@as(u16, 2), plan.planned_queue_pairs);
    try std.testing.expectEqual(@as(u16, 2), plan.rx_queue_count);
    try std.testing.expectEqual(@as(u32, 256), plan.headroom);
    try std.testing.expectEqual(@as(u32, 320), plan.tailroom);
    try std.testing.expectEqual(@as(u32, 576), plan.room);
    try std.testing.expectEqual(@as(u32, 1536), plan.requested_len);
    try std.testing.expectEqual(@as(u32, 2112), plan.requested_alloc_len);
    try std.testing.expectEqual(@as(u32, virtio_net.default_page_size), plan.page_size);
    try std.testing.expect(!plan.uses_recycled_room);
    try std.testing.expect(plan.uses_page_pool);
}

test "phase10 virtio net reuses prior room when planning the next mergeable receive buffer" {
    var device = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
        virtio_net.feature_control_vq,
    });

    const snapshot = try device.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
            virtio_net.feature_control_vq,
        },
        .requested_queue_pairs = 1,
        .max_queue_pairs = 1,
    });

    const plan = try device.planMergeableReceiveBuffer(snapshot, .{
        .header_len = 12,
        .average_packet_len = 900,
        .min_buf_len = 256,
        .recycled_room = 896,
    });

    try std.testing.expectEqual(@as(u32, 0), plan.room);
    try std.testing.expectEqual(@as(u32, 3200), plan.requested_len);
    try std.testing.expectEqual(@as(u32, 3200), plan.requested_alloc_len);
    try std.testing.expect(plan.uses_recycled_room);
}

test "phase10 virtio net rejects mergeable buffer plans that widen beyond the negotiated safe path" {
    var non_mergeable = try virtio_net.VirtioNetProbeLab.init(&.{virtio_net.feature_control_vq});
    const non_mergeable_snapshot = try non_mergeable.captureProbeSnapshot(.{
        .driver_feature_bits = &.{virtio_net.feature_control_vq},
        .requested_queue_pairs = 1,
        .max_queue_pairs = 1,
    });

    try std.testing.expectError(error.MergeableBuffersNotNegotiated, non_mergeable.planMergeableReceiveBuffer(non_mergeable_snapshot, .{
        .header_len = 12,
        .average_packet_len = 512,
        .min_buf_len = 256,
    }));

    var device = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
        virtio_net.feature_control_vq,
    });
    const snapshot = try device.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
            virtio_net.feature_control_vq,
        },
        .requested_queue_pairs = 1,
        .max_queue_pairs = 1,
    });

    try std.testing.expectError(error.MissingSkbSharedInfoSize, device.planMergeableReceiveBuffer(snapshot, .{
        .header_len = 12,
        .average_packet_len = 1024,
        .min_buf_len = 256,
        .headroom = 128,
    }));
    try std.testing.expectError(error.MinBufferLenTooLarge, device.planMergeableReceiveBuffer(snapshot, .{
        .header_len = 64,
        .average_packet_len = 1024,
        .min_buf_len = virtio_net.default_page_size,
    }));
    try std.testing.expectError(error.InvalidRecycledRoom, device.planMergeableReceiveBuffer(snapshot, .{
        .header_len = 12,
        .average_packet_len = 1024,
        .min_buf_len = 256,
        .recycled_room = virtio_net.default_page_size,
    }));
}
