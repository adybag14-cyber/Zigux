const std = @import("std");
const virtio_net = @import("virtio_net");

test "phase12 virtio net syntax lab keeps bounded probe exports reachable" {
    const descriptor = virtio_net.VirtioNetProbeLab.descriptor();

    _ = virtio_net.QueueRecoveryAction;
    _ = virtio_net.RecoveryState;
    _ = virtio_net.QueueResumeReadiness;
    _ = virtio_net.QueueResumeScope;
    _ = virtio_net.HeaderShape;
    _ = virtio_net.ReceiveBufferMode;
    _ = virtio_net.BigPacketReason;
    _ = virtio_net.HeaderScatterPolicy;
    _ = virtio_net.XdpConstraint;
    _ = virtio_net.MergeableReceiveRefillSummary;

    try std.testing.expectEqualStrings("virtio_net_probe_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_probe_queue_snapshot);
    try std.testing.expect(!descriptor.touches_live_dma);
    try std.testing.expect(!descriptor.touches_napi_poll);
    try std.testing.expect(!descriptor.touches_netdev_lifecycle);
}

test "phase12 virtio net syntax lab keeps review enums stable" {
    try std.testing.expectEqual(
        virtio_net.QueueRecoveryAction.clamp_queue_pairs,
        virtio_net.QueueRecoveryAction.clamp_queue_pairs,
    );
    try std.testing.expectEqual(virtio_net.RecoveryState.stable, virtio_net.RecoveryState.stable);
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
        virtio_net.HeaderScatterPolicy.separate_header_sg,
        virtio_net.HeaderScatterPolicy.separate_header_sg,
    );
    try std.testing.expectEqual(
        virtio_net.XdpConstraint.blocked_by_split_header,
        virtio_net.XdpConstraint.blocked_by_split_header,
    );
}
