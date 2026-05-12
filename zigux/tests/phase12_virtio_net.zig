const std = @import("std");
const virtio_net = @import("virtio_net");

test "phase12 virtio net probe starter stays anchored to virtio_net.c" {
    const descriptor = virtio_net.VirtioNetProbeLab.descriptor();
    try std.testing.expectEqualStrings("virtio_net_probe_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_probe_snapshot);
    try std.testing.expect(descriptor.provides_queue_topology_summary);
    try std.testing.expect(descriptor.provides_mergeable_receive_buffer_planner);
    try std.testing.expect(descriptor.provides_queue_recovery_planner);
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

test "phase12 virtio net recovery plan remembers the frozen queue layout and mergeable refill" {
    var lab = virtio_net.VirtioNetProbeLab.init();

    try std.testing.expectError(error.ProbeSnapshotUnavailable, lab.freezeForReset());

    _ = lab.captureProbeSnapshot(.{
        .requested_queue_pairs = 4,
        .device_queue_pairs = 2,
        .has_control_vq = true,
        .has_rss = true,
        .uses_hash_report = true,
        .uses_udp_tunnel_headers = false,
    });
    try std.testing.expectError(error.QueueTopologyUnavailable, lab.freezeForReset());
    _ = try lab.summarizeQueueTopology(.{
        .requested_queue_pairs = 4,
        .device_queue_pairs = 2,
        .has_control_vq = true,
        .has_rss = true,
        .uses_hash_report = true,
        .uses_udp_tunnel_headers = false,
    });
    _ = try lab.planMergeableReceiveBuffer(.{
        .packet_bytes = 6000,
        .existing_room_bytes = 0,
        .headroom_bytes = 64,
        .mergeable_rx_bufs = true,
    });

    const frozen = try lab.freezeForReset();
    try std.testing.expectEqual(virtio_net.RecoveryAction.freeze, frozen.action);
    try std.testing.expect(!frozen.was_resetting);
    try std.testing.expect(frozen.is_resetting);
    try std.testing.expectEqual(@as(u16, 2), frozen.remembered_queue_pairs);
    try std.testing.expectEqual(@as(u16, 5), frozen.remembered_total_queue_count);
    try std.testing.expectEqual(@as(u16, 1), frozen.remembered_control_queue_count);
    try std.testing.expect(frozen.receive_buffer_refill_required);
    try std.testing.expect(frozen.mergeable_buffer_refill_required);
    try std.testing.expectEqual(@as(u16, 0), frozen.recovery_generation);
    try std.testing.expectError(error.TransportResetInProgress, lab.freezeForReset());

    const plan = try lab.recoveryQueuePlan();
    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", plan.anchor);
    try std.testing.expectEqual(@as(u16, 2), plan.effective_queue_pairs);
    try std.testing.expectEqual(@as(u16, 2), plan.receive_queue_count);
    try std.testing.expectEqual(@as(u16, 2), plan.transmit_queue_count);
    try std.testing.expectEqual(@as(u16, 0), plan.first_receive_queue_index);
    try std.testing.expectEqual(@as(u16, 2), plan.first_transmit_queue_index);
    try std.testing.expectEqual(@as(?u16, 4), plan.first_control_queue_index);
    try std.testing.expectEqual(@as(u16, 5), plan.total_queue_count);
    try std.testing.expect(plan.rss_enabled);
    try std.testing.expect(plan.requires_receive_queue_restore);
    try std.testing.expect(plan.requires_transmit_queue_restore);
    try std.testing.expect(plan.requires_control_queue_restore);
    try std.testing.expect(plan.requires_receive_buffer_refill);
    try std.testing.expect(plan.requires_mergeable_buffer_refill);

    const restored = try lab.restoreAfterReset();
    try std.testing.expectEqual(virtio_net.RecoveryAction.restore, restored.action);
    try std.testing.expect(restored.was_resetting);
    try std.testing.expect(!restored.is_resetting);
    try std.testing.expectEqual(@as(u16, 1), restored.recovery_generation);
    try std.testing.expect(restored.receive_buffer_refill_required);
    try std.testing.expect(restored.mergeable_buffer_refill_required);
    try std.testing.expectError(error.TransportNotResetting, lab.recoveryQueuePlan());
    try std.testing.expectError(error.TransportNotResetting, lab.restoreAfterReset());
}

test "phase12 virtio net recovery plan distinguishes recycled-room refill from mergeable refill" {
    var lab = virtio_net.VirtioNetProbeLab.init();

    _ = lab.captureProbeSnapshot(.{
        .requested_queue_pairs = 1,
        .device_queue_pairs = 1,
        .has_control_vq = false,
        .has_rss = false,
        .uses_hash_report = false,
        .uses_udp_tunnel_headers = false,
    });
    _ = try lab.summarizeQueueTopology(.{
        .requested_queue_pairs = 1,
        .device_queue_pairs = 1,
        .has_control_vq = false,
        .has_rss = false,
        .uses_hash_report = false,
        .uses_udp_tunnel_headers = false,
    });
    _ = try lab.planMergeableReceiveBuffer(.{
        .packet_bytes = 2048,
        .existing_room_bytes = 4096,
        .headroom_bytes = 32,
        .mergeable_rx_bufs = true,
    });

    _ = try lab.freezeForReset();
    const plan = try lab.recoveryQueuePlan();
    try std.testing.expectEqual(@as(u16, 1), plan.effective_queue_pairs);
    try std.testing.expectEqual(@as(u16, 2), plan.total_queue_count);
    try std.testing.expectEqual(@as(?u16, null), plan.first_control_queue_index);
    try std.testing.expect(plan.requires_receive_queue_restore);
    try std.testing.expect(plan.requires_transmit_queue_restore);
    try std.testing.expect(!plan.requires_control_queue_restore);
    try std.testing.expect(plan.requires_receive_buffer_refill);
    try std.testing.expect(!plan.requires_mergeable_buffer_refill);
}
