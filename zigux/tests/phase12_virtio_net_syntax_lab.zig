const std = @import("std");
const virtio_net = @import("virtio_net");

test "phase12 virtio net syntax lab keeps queue-topology, refill, recovery, and control sequencing exports reachable" {
    _ = virtio_net.ModuleDescriptor;
    _ = virtio_net.ProbeRequest;
    _ = virtio_net.ProbeSnapshot;
    _ = virtio_net.QueueTopologySummary;
    _ = virtio_net.MergeableReceiveBufferRequest;
    _ = virtio_net.MergeableReceiveBufferPlan;
    _ = virtio_net.ReceiveRefillPath;
    _ = virtio_net.ReceiveRefillSummary;
    _ = virtio_net.QueueFallbackReason;
    _ = virtio_net.HeaderShape;
    _ = virtio_net.ReceiveBufferMode;
    _ = virtio_net.BigPacketReason;
    _ = virtio_net.RecoveryAction;
    _ = virtio_net.RecoverySummary;
    _ = virtio_net.RecoveryQueuePlan;
    _ = virtio_net.ControlQueueSequencingSummary;

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
        .uses_hash_report = false,
        .uses_udp_tunnel_headers = false,
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

    const refill = try lab.summarizeReceiveRefill(.{
        .packet_bytes = 1500,
        .existing_room_bytes = 0,
        .headroom_bytes = virtio_net.default_headroom_bytes,
        .mergeable_rx_bufs = true,
    });
    try std.testing.expectEqual(virtio_net.ReceiveRefillPath.allocate_single_page, refill.refill_path);
    try std.testing.expect(refill.publishes_receive_buffers);

    const frozen = try lab.freezeForReset();
    try std.testing.expectEqual(virtio_net.RecoveryAction.freeze, frozen.action);
    try std.testing.expect(frozen.receive_buffer_refill_required);

    const sequencing = try lab.summarizeControlQueueSequencing();
    try std.testing.expect(!sequencing.control_queue_present);
    try std.testing.expectEqual(@as(?u16, null), sequencing.control_queue_index);
    try std.testing.expect(!sequencing.restore_control_before_receive);
    try std.testing.expect(!sequencing.restore_control_before_transmit);
    try std.testing.expect(!sequencing.refill_after_control_restore);
    try std.testing.expect(sequencing.runtime_control_commands_blocked);

    const restored = try lab.restoreAfterReset();
    try std.testing.expectEqual(virtio_net.RecoveryAction.restore, restored.action);
    try std.testing.expectEqual(@as(u16, 1), restored.recovery_generation);
}

test "phase12 virtio net syntax lab keeps control queue restore separate from runtime commands" {
    var lab = virtio_net.VirtioNetProbeLab.init();
    _ = lab.captureProbeSnapshot(.{
        .requested_queue_pairs = 2,
        .device_queue_pairs = 2,
        .has_control_vq = true,
        .has_rss = false,
        .uses_hash_report = true,
        .uses_udp_tunnel_headers = false,
    });
    _ = try lab.summarizeQueueTopology(.{
        .requested_queue_pairs = 2,
        .device_queue_pairs = 2,
        .has_control_vq = true,
        .has_rss = false,
        .uses_hash_report = true,
        .uses_udp_tunnel_headers = false,
    });
    _ = try lab.summarizeReceiveRefill(.{
        .packet_bytes = 5000,
        .existing_room_bytes = 0,
        .headroom_bytes = 128,
        .mergeable_rx_bufs = true,
    });
    _ = try lab.freezeForReset();

    const sequencing = try lab.summarizeControlQueueSequencing();
    try std.testing.expect(sequencing.control_queue_present);
    try std.testing.expectEqual(@as(?u16, 4), sequencing.control_queue_index);
    try std.testing.expect(sequencing.restore_control_before_receive);
    try std.testing.expect(sequencing.restore_control_before_transmit);
    try std.testing.expect(sequencing.refill_after_control_restore);
    try std.testing.expectEqual(@as(u16, 0), sequencing.recovery_generation);
    try std.testing.expect(sequencing.runtime_control_commands_blocked);
}

test "phase12 virtio net syntax lab keeps mergeable path and recycled room distinct through refill and recovery" {
    var mergeable_lab = virtio_net.VirtioNetProbeLab.init();
    _ = mergeable_lab.captureProbeSnapshot(.{
        .requested_queue_pairs = 2,
        .device_queue_pairs = 2,
        .has_control_vq = true,
        .has_rss = false,
        .uses_hash_report = true,
        .uses_udp_tunnel_headers = false,
    });
    _ = try mergeable_lab.summarizeQueueTopology(.{
        .requested_queue_pairs = 2,
        .device_queue_pairs = 2,
        .has_control_vq = true,
        .has_rss = false,
        .uses_hash_report = true,
        .uses_udp_tunnel_headers = false,
    });
    _ = try mergeable_lab.planMergeableReceiveBuffer(.{
        .packet_bytes = 5000,
        .existing_room_bytes = 0,
        .headroom_bytes = 128,
        .mergeable_rx_bufs = true,
    });
    const mergeable_refill = try mergeable_lab.summarizeReceiveRefill(.{
        .packet_bytes = 5000,
        .existing_room_bytes = 0,
        .headroom_bytes = 128,
        .mergeable_rx_bufs = true,
    });
    try std.testing.expectEqual(virtio_net.ReceiveRefillPath.allocate_mergeable_chain, mergeable_refill.refill_path);
    _ = try mergeable_lab.freezeForReset();
    const mergeable = try mergeable_lab.recoveryQueuePlan();
    try std.testing.expect(mergeable.requires_receive_buffer_refill);
    try std.testing.expect(mergeable.requires_mergeable_buffer_refill);
    const mergeable_sequence = try mergeable_lab.summarizeControlQueueSequencing();
    try std.testing.expect(mergeable_sequence.control_queue_present);
    try std.testing.expect(mergeable_sequence.refill_after_control_restore);

    var recycled_lab = virtio_net.VirtioNetProbeLab.init();
    _ = recycled_lab.captureProbeSnapshot(.{
        .requested_queue_pairs = 2,
        .device_queue_pairs = 2,
        .has_control_vq = false,
        .has_rss = false,
        .uses_hash_report = true,
        .uses_udp_tunnel_headers = false,
    });
    _ = try recycled_lab.summarizeQueueTopology(.{
        .requested_queue_pairs = 2,
        .device_queue_pairs = 2,
        .has_control_vq = false,
        .has_rss = false,
        .uses_hash_report = true,
        .uses_udp_tunnel_headers = false,
    });
    _ = try recycled_lab.planMergeableReceiveBuffer(.{
        .packet_bytes = 2048,
        .existing_room_bytes = 4096,
        .headroom_bytes = 32,
        .mergeable_rx_bufs = true,
    });
    const recycled_refill = try recycled_lab.summarizeReceiveRefill(.{
        .packet_bytes = 2048,
        .existing_room_bytes = 4096,
        .headroom_bytes = 32,
        .mergeable_rx_bufs = true,
    });
    try std.testing.expectEqual(virtio_net.ReceiveRefillPath.reuse_existing_room, recycled_refill.refill_path);
    _ = try recycled_lab.freezeForReset();
    const recycled = try recycled_lab.recoveryQueuePlan();
    try std.testing.expect(recycled.requires_receive_buffer_refill);
    try std.testing.expect(!recycled.requires_mergeable_buffer_refill);
    const recycled_sequence = try recycled_lab.summarizeControlQueueSequencing();
    try std.testing.expect(!recycled_sequence.control_queue_present);
    try std.testing.expect(!recycled_sequence.refill_after_control_restore);
}
