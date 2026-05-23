const std = @import("std");
const virtio_ring = @import("virtio_ring");
const publish_readiness = @import("virtio_ring_publish_readiness");

test "phase10 virtio ring publish-readiness replay keeps unpublished chains and reclaimed capacity explicit" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(2, 8, .split, true, false);

    try ring.publishDescriptorChain(2);
    try ring.publishDescriptorChain(2);

    var summary = try publish_readiness.summarizePublishReadiness(&ring, 2);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, 2), summary.queue_index);
    try std.testing.expectEqual(@as(u16, 2), summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 2), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 2), summary.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 6), summary.available_descriptor_count);
    try std.testing.expect(publish_readiness.queueCanPublish(summary));
    try std.testing.expect(publish_readiness.queueHasPublishCapacity(summary));

    _ = try ring.prepareKick(2);
    try ring.recordUsedChains(2, 1);

    summary = try publish_readiness.summarizePublishReadiness(&ring, 2);
    try std.testing.expectEqual(@as(u16, 2), summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 1), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), summary.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 7), summary.available_descriptor_count);
    try std.testing.expect(summary.blocker == null);
    try std.testing.expect(publish_readiness.queueCanPublish(summary));
    try std.testing.expect(publish_readiness.queueHasPublishCapacity(summary));

    var reset_readiness = try ring.queueResetReadinessSummary(2);
    try std.testing.expect(!reset_readiness.reset_ready);
    try std.testing.expectEqualStrings("outstanding_chains", @tagName(reset_readiness.blocker.?));
    try std.testing.expectEqual(@as(u16, 1), reset_readiness.pending_used_chain_count);

    try ring.recordUsedChains(2, 1);
    reset_readiness = try ring.queueResetReadinessSummary(2);
    try std.testing.expect(!reset_readiness.reset_ready);
    try std.testing.expectEqualStrings("unpolled_used_chains", @tagName(reset_readiness.blocker.?));
    try std.testing.expectEqual(@as(u16, 2), reset_readiness.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), reset_readiness.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 2), reset_readiness.pending_used_chain_count);
}

test "phase10 virtio ring publish-readiness replay keeps broken full queues fenced until used work returns" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(6, 8, .packed_ring, true, true);

    inline for (0..8) |_| {
        try ring.publishDescriptorChain(6);
    }

    _ = try ring.markBroken(6);
    var summary = try publish_readiness.summarizePublishReadiness(&ring, 6);
    try std.testing.expect(summary.broken);
    try std.testing.expectEqual(@as(u16, 8), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 8), summary.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 0), summary.available_descriptor_count);
    try std.testing.expectEqualStrings("queue_broken", @tagName(summary.blocker.?));
    try std.testing.expect(!publish_readiness.queueCanPublish(summary));
    try std.testing.expect(!publish_readiness.queueHasPublishCapacity(summary));

    _ = try ring.clearBroken(6);
    summary = try publish_readiness.summarizePublishReadiness(&ring, 6);
    try std.testing.expect(!summary.broken);
    try std.testing.expectEqualStrings("queue_full", @tagName(summary.blocker.?));
    try std.testing.expect(!publish_readiness.queueCanPublish(summary));
    try std.testing.expect(!publish_readiness.queueHasPublishCapacity(summary));

    _ = try ring.prepareKick(6);
    try ring.recordUsedChains(6, 3);

    summary = try publish_readiness.summarizePublishReadiness(&ring, 6);
    try std.testing.expectEqual(@as(u16, 5), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), summary.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 3), summary.available_descriptor_count);
    try std.testing.expect(summary.blocker == null);
    try std.testing.expect(publish_readiness.queueCanPublish(summary));
    try std.testing.expect(publish_readiness.queueHasPublishCapacity(summary));
}
