const std = @import("std");
const virtio_net = @import("virtio_net");

test "phase12 virtio net syntax lab keeps queue-topology and recovery exports reachable" {
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
    _ = virtio_net.RecoveryAction;
    _ = virtio_net.RecoverySummary;
    _ = virtio_net.RecoveryQueuePlan;

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

    const frozen = try lab.freezeForReset();
    try std.testing.expectEqual(virtio_net.RecoveryAction.freeze, frozen.action);
    try std.testing.expect(!frozen.receive_buffer_refill_required);

    const restored = try lab.restoreAfterReset();
    try std.testing.expectEqual(virtio_net.RecoveryAction.restore, restored.action);
    try std.testing.expectEqual(@as(u16, 1), restored.recovery_generation);
}

test "phase12 virtio net syntax lab keeps mergeable path and recycled room distinct through recovery" {
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
    _ = try mergeable_lab.freezeForReset();
    const mergeable = try mergeable_lab.recoveryQueuePlan();
    try std.testing.expect(mergeable.requires_receive_buffer_refill);
    try std.testing.expect(mergeable.requires_mergeable_buffer_refill);

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
    _ = try recycled_lab.freezeForReset();
    const recycled = try recycled_lab.recoveryQueuePlan();
    try std.testing.expect(recycled.requires_receive_buffer_refill);
    try std.testing.expect(!recycled.requires_mergeable_buffer_refill);
}
