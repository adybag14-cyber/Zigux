const std = @import("std");

const virtio_net = @import("virtio_net");

test "phase12 virtio net syntax lab keeps bounded probe exports reachable" {
    const descriptor = virtio_net.VirtioNetProbeLab.descriptor();

    _ = virtio_net.ModuleDescriptor;
    _ = virtio_net.RecoveryAction;
    _ = virtio_net.QueueFallbackReason;
    _ = virtio_net.RecoveryState;
    _ = virtio_net.RssRecoveryState;
    _ = virtio_net.QueueRecoveryAction;
    _ = virtio_net.ProbeRequest;
    _ = virtio_net.ProbeSnapshot;
    _ = virtio_net.QueueRecoverySummary;
    _ = virtio_net.QueueResumeReadiness;
    _ = virtio_net.QueueResumeScope;
    _ = virtio_net.QueueResumeSummary;
    _ = virtio_net.ReceiveBufferMode;
    _ = virtio_net.ReceiveRefillSummary;
    _ = virtio_net.MergeableBufferLengthSource;
    _ = virtio_net.MergeableBufferLengthRequest;
    _ = virtio_net.MergeableBufferLengthSummary;
    _ = virtio_net.TransmitRecycleOrder;
    _ = virtio_net.TransmitRecycleSummary;

    try std.testing.expectEqualStrings("virtio_net_probe_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_probe_queue_snapshot);
    try std.testing.expect(!descriptor.touches_live_dma);
    try std.testing.expect(!descriptor.touches_napi_poll);
    try std.testing.expect(!descriptor.touches_netdev_lifecycle);
    try std.testing.expect(descriptor.touches_transport_recovery);
}

test "phase12 virtio net syntax lab keeps current follow-up enums stable" {
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
        virtio_net.RssRecoveryState.downgraded_single_queue,
        virtio_net.RssRecoveryState.downgraded_single_queue,
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
        virtio_net.ReceiveBufferMode.mergeable_rx_buffers,
        virtio_net.ReceiveBufferMode.mergeable_rx_buffers,
    );
    try std.testing.expectEqual(
        virtio_net.MergeableBufferLengthSource.minimum_buffer_floor,
        virtio_net.MergeableBufferLengthSource.minimum_buffer_floor,
    );
    try std.testing.expectEqual(
        virtio_net.TransmitRecycleOrder.after_control_queue_restore_and_rss_reapply,
        virtio_net.TransmitRecycleOrder.after_control_queue_restore_and_rss_reapply,
    );
}

test "phase12 virtio net syntax lab keeps alternate recovery and throughput variants reachable" {
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
        virtio_net.ReceiveBufferMode.one_buffer_per_rx,
        virtio_net.ReceiveBufferMode.one_buffer_per_rx,
    );
    try std.testing.expectEqual(
        virtio_net.MergeableBufferLengthSource.page_size_cap,
        virtio_net.MergeableBufferLengthSource.page_size_cap,
    );
    try std.testing.expectEqual(
        virtio_net.MergeableBufferLengthSource.page_minus_room,
        virtio_net.MergeableBufferLengthSource.page_minus_room,
    );
    try std.testing.expectEqual(
        virtio_net.TransmitRecycleOrder.after_control_queue_restore,
        virtio_net.TransmitRecycleOrder.after_control_queue_restore,
    );
}

test "phase12 virtio net syntax lab keeps base recovery and smoke variants reachable" {
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
        virtio_net.RssRecoveryState.not_requested,
        virtio_net.RssRecoveryState.not_requested,
    );
    try std.testing.expectEqual(
        virtio_net.RssRecoveryState.requested_but_unavailable,
        virtio_net.RssRecoveryState.requested_but_unavailable,
    );
    try std.testing.expectEqual(
        virtio_net.RssRecoveryState.active,
        virtio_net.RssRecoveryState.active,
    );
    try std.testing.expectEqual(
        virtio_net.QueueResumeScope.data_queues_only,
        virtio_net.QueueResumeScope.data_queues_only,
    );
    try std.testing.expectEqual(
        virtio_net.MergeableBufferLengthSource.observed_average_packet,
        virtio_net.MergeableBufferLengthSource.observed_average_packet,
    );
    try std.testing.expectEqual(
        virtio_net.TransmitRecycleOrder.data_queues_only,
        virtio_net.TransmitRecycleOrder.data_queues_only,
    );
}
