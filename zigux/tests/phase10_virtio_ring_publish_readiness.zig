const std = @import("std");
const virtio_ring = @import("virtio_ring");
const virtio_ring_publish_readiness = @import("virtio_ring_publish_readiness");

test "phase10 virtio ring publish-readiness replay keeps queue-local publish capacity explicit across unpublished full and reclaimed states" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(2, 8, .packed_ring, true, true);

    try ring.publishDescriptorChain(2);
    try ring.publishDescriptorChain(2);

    var summary = try virtio_ring_publish_readiness.summarizePublishReadiness(&ring, 2);
    try std.testing.expectEqual(@as(u16, 2), summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 2), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 2), summary.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 6), summary.available_descriptor_count);
    try std.testing.expect(summary.blocker == null);
    try std.testing.expect(virtio_ring_publish_readiness.queueCanPublish(summary));
    try std.testing.expect(virtio_ring_publish_readiness.queueHasPublishCapacity(summary));

    inline for (0..6) |_| {
        try ring.publishDescriptorChain(2);
    }

    summary = try virtio_ring_publish_readiness.summarizePublishReadiness(&ring, 2);
    try std.testing.expectEqual(@as(u16, 8), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 8), summary.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 0), summary.available_descriptor_count);
    try std.testing.expectEqualStrings("queue_full", @tagName(summary.blocker.?));
    try std.testing.expect(!virtio_ring_publish_readiness.queueCanPublish(summary));
    try std.testing.expect(!virtio_ring_publish_readiness.queueHasPublishCapacity(summary));

    const kick = try ring.prepareKick(2);
    try std.testing.expect(kick.needs_kick);
    try std.testing.expectEqual(@as(u16, 8), kick.num_added);

    try ring.recordUsedChains(2, 3);
    summary = try virtio_ring_publish_readiness.summarizePublishReadiness(&ring, 2);
    try std.testing.expectEqual(@as(u16, 5), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), summary.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 3), summary.available_descriptor_count);
    try std.testing.expect(summary.blocker == null);
    try std.testing.expect(virtio_ring_publish_readiness.queueCanPublish(summary));
    try std.testing.expect(virtio_ring_publish_readiness.queueHasPublishCapacity(summary));
}

test "phase10 virtio ring publish-readiness replay keeps broken and cleared full queues reviewable without widening into transport work" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(6, 8, .split, false, false);

    inline for (0..8) |_| {
        try ring.publishDescriptorChain(6);
    }

    _ = try ring.markBroken(6);

    var summary = try virtio_ring_publish_readiness.summarizePublishReadiness(&ring, 6);
    try std.testing.expect(summary.broken);
    try std.testing.expectEqual(@as(u16, 8), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 8), summary.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 0), summary.available_descriptor_count);
    try std.testing.expectEqualStrings("queue_broken", @tagName(summary.blocker.?));
    try std.testing.expect(!virtio_ring_publish_readiness.queueCanPublish(summary));
    try std.testing.expect(!virtio_ring_publish_readiness.queueHasPublishCapacity(summary));

    const broken_fence = try ring.brokenQueueSummary(6);
    try std.testing.expect(broken_fence.broken);
    try std.testing.expectEqual(@as(u16, 8), broken_fence.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 8), broken_fence.outstanding_chain_count);

    _ = try ring.clearBroken(6);

    summary = try virtio_ring_publish_readiness.summarizePublishReadiness(&ring, 6);
    try std.testing.expect(!summary.broken);
    try std.testing.expectEqual(@as(u16, 8), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 8), summary.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 0), summary.available_descriptor_count);
    try std.testing.expectEqualStrings("queue_full", @tagName(summary.blocker.?));
    try std.testing.expect(!virtio_ring_publish_readiness.queueCanPublish(summary));
    try std.testing.expect(!virtio_ring_publish_readiness.queueHasPublishCapacity(summary));

    const kick = try ring.prepareKick(6);
    try std.testing.expect(kick.needs_kick);
    try std.testing.expectEqual(@as(u16, 8), kick.num_added);
    try ring.recordUsedChains(6, 2);

    summary = try virtio_ring_publish_readiness.summarizePublishReadiness(&ring, 6);
    try std.testing.expectEqual(@as(u16, 6), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), summary.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 2), summary.available_descriptor_count);
    try std.testing.expect(summary.blocker == null);
    try std.testing.expect(virtio_ring_publish_readiness.queueCanPublish(summary));
    try std.testing.expect(virtio_ring_publish_readiness.queueHasPublishCapacity(summary));
}
