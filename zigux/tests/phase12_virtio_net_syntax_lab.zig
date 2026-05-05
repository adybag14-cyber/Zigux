const std = @import("std");

const virtio_net = @import("virtio_net");

test "phase12 virtio net syntax lab keeps bounded probe exports reachable" {
    const descriptor = virtio_net.VirtioNetProbeLab.descriptor();

    _ = virtio_net.ModuleDescriptor;
    _ = virtio_net.RecoveryAction;
    _ = virtio_net.QueueFallbackReason;
    _ = virtio_net.RecoveryState;
    _ = virtio_net.QueueRecoveryAction;
    _ = virtio_net.RssSummary;
    _ = virtio_net.QueueResumeReadiness;
    _ = virtio_net.QueueResumeScope;
    _ = virtio_net.HeaderShape;
    _ = virtio_net.ReceiveBufferMode;
    _ = virtio_net.BigPacketReason;
    _ = virtio_net.ReceiveQueueRefillPath;
    _ = virtio_net.HeaderScatterPolicy;
    _ = virtio_net.XdpConstraint;
    _ = virtio_net.ProbeRequest;
    _ = virtio_net.ProbeSnapshot;
    _ = virtio_net.QueueRecoverySummary;
    _ = virtio_net.QueueResumeSummary;
    _ = virtio_net.MergeableReceiveRefillSummary;

    try std.testing.expectEqualStrings("virtio_net_probe_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_probe_queue_snapshot);
    try std.testing.expect(!descriptor.touches_live_dma);
    try std.testing.expect(!descriptor.touches_napi_poll);
    try std.testing.expect(!descriptor.touches_netdev_lifecycle);
    try std.testing.expect(descriptor.touches_transport_recovery);
}

test "phase12 virtio net syntax lab keeps review enums stable" {
    try std.testing.expectEqual(
        virtio_net.QueueRecoveryAction.clamp_queue_pairs,
        virtio_net.QueueRecoveryAction.clamp_queue_pairs,
    );
    try std.testing.expectEqual(virtio_net.RecoveryState.stable, virtio_net.RecoveryState.stable);
    try std.testing.expectEqual(
        virtio_net.QueueFallbackReason.invalid_max_queue_pairs,
        virtio_net.QueueFallbackReason.invalid_max_queue_pairs,
    );
    try std.testing.expectEqual(
        virtio_net.RssSummary.downgraded_single_queue,
        virtio_net.RssSummary.downgraded_single_queue,
    );
    try std.testing.expectEqual(
        virtio_net.QueueResumeReadiness.ready,
        virtio_net.QueueResumeReadiness.ready,
    );
    try std.testing.expectEqual(
        virtio_net.QueueResumeScope.data_control_and_rss,
        virtio_net.QueueResumeScope.data_control_and_rss,
    );
    try std.testing.expectEqual(
        virtio_net.HeaderShape.hash_report_tunnel,
        virtio_net.HeaderShape.hash_report_tunnel,
    );
    try std.testing.expectEqual(
        virtio_net.ReceiveBufferMode.mergeable,
        virtio_net.ReceiveBufferMode.mergeable,
    );
    try std.testing.expectEqual(
        virtio_net.BigPacketReason.guest_gso,
        virtio_net.BigPacketReason.guest_gso,
    );
    try std.testing.expectEqual(
        virtio_net.ReceiveQueueRefillPath.recycled_room_reuse,
        virtio_net.ReceiveQueueRefillPath.recycled_room_reuse,
    );
    try std.testing.expectEqual(
        virtio_net.HeaderScatterPolicy.separate_header_sg,
        virtio_net.HeaderScatterPolicy.separate_header_sg,
    );
    try std.testing.expectEqual(
        virtio_net.XdpConstraint.blocked_by_split_header,
        virtio_net.XdpConstraint.blocked_by_split_header,
    );
}

test "phase12 virtio net syntax lab keeps alternate review variants reachable" {
    try std.testing.expectEqual(
        virtio_net.RecoveryState.reset_required,
        virtio_net.RecoveryState.reset_required,
    );
    try std.testing.expectEqual(
        virtio_net.QueueRecoveryAction.require_reset,
        virtio_net.QueueRecoveryAction.require_reset,
    );
    try std.testing.expectEqual(
        virtio_net.QueueResumeReadiness.requires_feature_renegotiation,
        virtio_net.QueueResumeReadiness.requires_feature_renegotiation,
    );
    try std.testing.expectEqual(
        virtio_net.QueueResumeScope.data_and_control_queue,
        virtio_net.QueueResumeScope.data_and_control_queue,
    );
    try std.testing.expectEqual(
        virtio_net.HeaderShape.mrg_rxbuf,
        virtio_net.HeaderShape.mrg_rxbuf,
    );
    try std.testing.expectEqual(
        virtio_net.ReceiveBufferMode.big_packets,
        virtio_net.ReceiveBufferMode.big_packets,
    );
    try std.testing.expectEqual(
        virtio_net.BigPacketReason.mtu_above_default,
        virtio_net.BigPacketReason.mtu_above_default,
    );
    try std.testing.expectEqual(
        virtio_net.ReceiveQueueRefillPath.fresh_allocation,
        virtio_net.ReceiveQueueRefillPath.fresh_allocation,
    );
    try std.testing.expectEqual(
        virtio_net.HeaderScatterPolicy.combined_header_and_data,
        virtio_net.HeaderScatterPolicy.combined_header_and_data,
    );
    try std.testing.expectEqual(
        virtio_net.XdpConstraint.ready,
        virtio_net.XdpConstraint.ready,
    );
}

test "phase12 virtio net syntax lab keeps fallback and base variants reachable" {
    try std.testing.expectEqual(virtio_net.RecoveryAction.freeze, virtio_net.RecoveryAction.freeze);
    try std.testing.expectEqual(virtio_net.RecoveryAction.restore, virtio_net.RecoveryAction.restore);
    try std.testing.expectEqual(
        virtio_net.QueueFallbackReason.none,
        virtio_net.QueueFallbackReason.none,
    );
    try std.testing.expectEqual(
        virtio_net.QueueFallbackReason.multiqueue_not_negotiated,
        virtio_net.QueueFallbackReason.multiqueue_not_negotiated,
    );
    try std.testing.expectEqual(
        virtio_net.QueueFallbackReason.missing_control_vq,
        virtio_net.QueueFallbackReason.missing_control_vq,
    );
    try std.testing.expectEqual(
        virtio_net.QueueFallbackReason.requested_queue_pairs_clamped,
        virtio_net.QueueFallbackReason.requested_queue_pairs_clamped,
    );
    try std.testing.expectEqual(
        virtio_net.RssSummary.not_requested,
        virtio_net.RssSummary.not_requested,
    );
    try std.testing.expectEqual(
        virtio_net.RssSummary.requested_but_unavailable,
        virtio_net.RssSummary.requested_but_unavailable,
    );
    try std.testing.expectEqual(
        virtio_net.RssSummary.hash_report_only,
        virtio_net.RssSummary.hash_report_only,
    );
    try std.testing.expectEqual(
        virtio_net.QueueResumeScope.data_queues_only,
        virtio_net.QueueResumeScope.data_queues_only,
    );
    try std.testing.expectEqual(virtio_net.HeaderShape.legacy, virtio_net.HeaderShape.legacy);
    try std.testing.expectEqual(
        virtio_net.HeaderShape.hash_report,
        virtio_net.HeaderShape.hash_report,
    );
    try std.testing.expectEqual(
        virtio_net.ReceiveBufferMode.small,
        virtio_net.ReceiveBufferMode.small,
    );
    try std.testing.expectEqual(
        virtio_net.BigPacketReason.none,
        virtio_net.BigPacketReason.none,
    );
    try std.testing.expectEqual(
        virtio_net.XdpConstraint.not_requested,
        virtio_net.XdpConstraint.not_requested,
    );
    try std.testing.expectEqual(
        virtio_net.XdpConstraint.blocked_by_big_packets,
        virtio_net.XdpConstraint.blocked_by_big_packets,
    );
}
