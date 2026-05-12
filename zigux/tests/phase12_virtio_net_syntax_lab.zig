const std = @import("std");
const virtio_net = @import("virtio_net");

test "phase12 virtio net syntax lab keeps queue-topology and mergeable-buffer exports reachable" {
    _ = virtio_net.ModuleDescriptor;
    _ = virtio_net.ProbeRequest;
    _ = virtio_net.ProbeSnapshot;
    _ = virtio_net.QueueTopologySummary;
    _ = virtio_net.MergeableReceiveBufferRequest;
    _ = virtio_net.MergeableReceiveBufferPlan;
    _ = virtio_net.QueueFallbackReason;
    _ = virtio_net.HeaderShape;
    _ = virtio_net.ReceiveBufferMode;
    _ = virtio_net.BigPacketReason;

    var lab = virtio_net.VirtioNetProbeLab.init();
    const snapshot = lab.captureProbeSnapshot(.{
        .requested_queue_pairs = 0,
        .device_queue_pairs = 0,
        .has_control_vq = false,
        .has_rss = false,
        .uses_hash_report = false,
        .uses_udp_tunnel_headers = false,
    });
    try std.testing.expectEqual(@as(u16, virtio_net.default_queue_pairs), snapshot.effective_queue_pairs);
    try std.testing.expectEqual(virtio_net.QueueFallbackReason.device_single_queue, snapshot.fallback_reason);
    try std.testing.expectEqual(virtio_net.HeaderShape.legacy, snapshot.header_shape);
    try std.testing.expectEqual(@as(u16, virtio_net.default_headroom_bytes), snapshot.hdr_len_bytes);

    const topology = try lab.summarizeQueueTopology(.{
        .requested_queue_pairs = 0,
        .device_queue_pairs = 0,
        .has_control_vq = false,
        .has_rss = true,
    });
    try std.testing.expectEqual(@as(u16, 2), topology.total_queue_count);
    try std.testing.expectEqual(@as(?u16, null), topology.first_control_queue_index);
    try std.testing.expect(!topology.multi_queue);
    try std.testing.expect(!topology.rss_enabled);

    const single_page_plan = try lab.planMergeableReceiveBuffer(.{
        .packet_bytes = 1500,
        .existing_room_bytes = 0,
        .headroom_bytes = virtio_net.default_headroom_bytes,
        .mergeable_rx_bufs = true,
    });
    try std.testing.expectEqual(virtio_net.ReceiveBufferMode.single_page, single_page_plan.buffer_mode);
    try std.testing.expectEqual(virtio_net.BigPacketReason.none, single_page_plan.big_packet_reason);
}

test "phase12 virtio net syntax lab keeps mergeable path and recycled room distinct" {
    var lab = virtio_net.VirtioNetProbeLab.init();

    const recycled = try lab.planMergeableReceiveBuffer(.{
        .packet_bytes = 2048,
        .existing_room_bytes = 4096,
        .headroom_bytes = 32,
        .mergeable_rx_bufs = true,
    });
    try std.testing.expectEqual(virtio_net.ReceiveBufferMode.recycled_room, recycled.buffer_mode);
    try std.testing.expect(recycled.reuses_existing_room);

    const mergeable = try lab.planMergeableReceiveBuffer(.{
        .packet_bytes = 5000,
        .existing_room_bytes = 0,
        .headroom_bytes = 128,
        .mergeable_rx_bufs = true,
    });
    try std.testing.expectEqual(virtio_net.ReceiveBufferMode.mergeable, mergeable.buffer_mode);
    try std.testing.expect(!mergeable.reuses_existing_room);
    try std.testing.expect(mergeable.uses_mergeable_path);
}
