const std = @import("std");
const virtio_net = @import("virtio_net");

test "phase12 virtio net probe starter stays anchored to virtio_net.c" {
    const descriptor = virtio_net.VirtioNetProbeLab.descriptor();
    try std.testing.expectEqualStrings("virtio_net_probe_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_probe_snapshot);
    try std.testing.expect(descriptor.provides_queue_topology_summary);
    try std.testing.expect(descriptor.provides_mergeable_receive_buffer_planner);
    try std.testing.expect(!descriptor.touches_live_dma);
    try std.testing.expect(!descriptor.touches_net_device);
    try std.testing.expect(!descriptor.touches_control_virtqueue_runtime);

    var lab = virtio_net.VirtioNetProbeLab.init();
    const snapshot = lab.captureProbeSnapshot(.{
        .requested_queue_pairs = 4,
        .device_queue_pairs = 2,
        .has_control_vq = true,
        .has_rss = true,
        .uses_hash_report = true,
        .uses_udp_tunnel_headers = true,
    });
    try std.testing.expectEqual(@as(u16, 4), snapshot.requested_queue_pairs);
    try std.testing.expectEqual(@as(u16, 2), snapshot.device_queue_pairs);
    try std.testing.expectEqual(@as(u16, 2), snapshot.effective_queue_pairs);
    try std.testing.expectEqual(virtio_net.QueueFallbackReason.negotiated_pair_cap, snapshot.fallback_reason);
    try std.testing.expect(snapshot.control_vq_present);
    try std.testing.expect(snapshot.rss_enabled);
    try std.testing.expectEqual(virtio_net.HeaderShape.hash_report_tunnel, snapshot.header_shape);
    try std.testing.expectEqual(@as(u16, virtio_net.tunnel_header_len_bytes), snapshot.hdr_len_bytes);
}

test "phase12 virtio net queue topology summary keeps queue-pair layout explicit" {
    var lab = virtio_net.VirtioNetProbeLab.init();
    const summary = try lab.summarizeQueueTopology(.{
        .requested_queue_pairs = 4,
        .device_queue_pairs = 2,
        .has_control_vq = true,
        .has_rss = true,
    });

    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, 2), summary.effective_queue_pairs);
    try std.testing.expectEqual(@as(u16, 2), summary.receive_queue_count);
    try std.testing.expectEqual(@as(u16, 2), summary.transmit_queue_count);
    try std.testing.expectEqual(@as(u16, 0), summary.first_receive_queue_index);
    try std.testing.expectEqual(@as(u16, 2), summary.first_transmit_queue_index);
    try std.testing.expectEqual(@as(?u16, 4), summary.first_control_queue_index);
    try std.testing.expectEqual(@as(u16, 1), summary.control_queue_count);
    try std.testing.expectEqual(@as(u16, 5), summary.total_queue_count);
    try std.testing.expectEqual(virtio_net.QueueFallbackReason.negotiated_pair_cap, summary.fallback_reason);
    try std.testing.expect(summary.multi_queue);
    try std.testing.expect(summary.control_vq_present);
    try std.testing.expect(summary.rss_enabled);
}

test "phase12 virtio net queue topology summary rejects overflowing queue counts" {
    var lab = virtio_net.VirtioNetProbeLab.init();
    try std.testing.expectError(error.QueueCountOverflow, lab.summarizeQueueTopology(.{
        .requested_queue_pairs = std.math.maxInt(u16),
        .device_queue_pairs = std.math.maxInt(u16),
    }));
}

test "phase12 virtio net mergeable receive buffer plan reuses available room" {
    var lab = virtio_net.VirtioNetProbeLab.init();
    const plan = try lab.planMergeableReceiveBuffer(.{
        .packet_bytes = 1536,
        .existing_room_bytes = 4096,
        .headroom_bytes = 64,
        .mergeable_rx_bufs = true,
    });

    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", plan.anchor);
    try std.testing.expectEqual(@as(u32, 1600), plan.total_bytes);
    try std.testing.expectEqual(@as(u16, 1), plan.required_buffers);
    try std.testing.expectEqual(virtio_net.ReceiveBufferMode.recycled_room, plan.buffer_mode);
    try std.testing.expectEqual(virtio_net.BigPacketReason.none, plan.big_packet_reason);
    try std.testing.expect(plan.reuses_existing_room);
    try std.testing.expect(plan.fits_single_page);
    try std.testing.expect(!plan.uses_mergeable_path);
}

test "phase12 virtio net mergeable receive buffer plan spreads oversized packets" {
    var lab = virtio_net.VirtioNetProbeLab.init();
    const plan = try lab.planMergeableReceiveBuffer(.{
        .packet_bytes = 6000,
        .existing_room_bytes = 0,
        .headroom_bytes = 64,
        .mergeable_rx_bufs = true,
    });

    try std.testing.expectEqual(@as(u32, 6064), plan.total_bytes);
    try std.testing.expectEqual(@as(u16, 2), plan.required_buffers);
    try std.testing.expectEqual(virtio_net.ReceiveBufferMode.mergeable, plan.buffer_mode);
    try std.testing.expectEqual(virtio_net.BigPacketReason.exceeds_single_buffer, plan.big_packet_reason);
    try std.testing.expect(!plan.reuses_existing_room);
    try std.testing.expect(!plan.fits_single_page);
    try std.testing.expect(plan.uses_mergeable_path);
}

test "phase12 virtio net mergeable receive buffer plan rejects oversized packets without feature" {
    var lab = virtio_net.VirtioNetProbeLab.init();
    try std.testing.expectError(error.MergeableReceiveBuffersRequired, lab.planMergeableReceiveBuffer(.{
        .packet_bytes = 6000,
        .existing_room_bytes = 0,
        .headroom_bytes = 64,
        .mergeable_rx_bufs = false,
    }));
}
