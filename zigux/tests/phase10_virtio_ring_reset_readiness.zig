const std = @import("std");
const virtio_ring = @import("virtio_ring");
const virtio_ring_reset_readiness = @import("virtio_ring_reset_readiness");

test "phase10 virtio ring reset-readiness replay keeps queue-local blocker progression explicit" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(4, 8, .packed_ring, true, true);

    var summary = try virtio_ring_reset_readiness.summarizeResetReadiness(&ring, 4);
    try std.testing.expect(virtio_ring_reset_readiness.queueCanReset(summary));
    try std.testing.expect(!virtio_ring_reset_readiness.queueNeedsUsedPoll(summary));
    try std.testing.expect(!virtio_ring_reset_readiness.queueHasResetDebt(summary));

    try ring.publishDescriptorChain(4);
    try ring.publishDescriptorChain(4);

    summary = try virtio_ring_reset_readiness.summarizeResetReadiness(&ring, 4);
    try std.testing.expectEqualStrings("unpublished_chains", @tagName(summary.blocker.?));
    try std.testing.expectEqual(@as(u16, 2), summary.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 2), summary.outstanding_chain_count);
    try std.testing.expect(!virtio_ring_reset_readiness.queueCanReset(summary));
    try std.testing.expect(virtio_ring_reset_readiness.queueHasResetDebt(summary));

    const kick = try ring.prepareKick(4);
    try std.testing.expect(kick.needs_kick);
    try std.testing.expectEqual(@as(u16, 2), kick.num_added);

    summary = try virtio_ring_reset_readiness.summarizeResetReadiness(&ring, 4);
    try std.testing.expectEqualStrings("outstanding_chains", @tagName(summary.blocker.?));
    try std.testing.expectEqual(@as(u16, 0), summary.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 2), summary.outstanding_chain_count);
    try std.testing.expect(!virtio_ring_reset_readiness.queueCanReset(summary));

    try ring.recordUsedChains(4, 2);

    summary = try virtio_ring_reset_readiness.summarizeResetReadiness(&ring, 4);
    try std.testing.expectEqualStrings("unpolled_used_chains", @tagName(summary.blocker.?));
    try std.testing.expectEqual(@as(u16, 2), summary.pending_used_chain_count);
    try std.testing.expect(!virtio_ring_reset_readiness.queueCanReset(summary));
    try std.testing.expect(virtio_ring_reset_readiness.queueNeedsUsedPoll(summary));

    const poll = try ring.pollUsedBuffers(4);
    try std.testing.expectEqual(@as(u16, 2), poll.newly_used_chain_count);

    summary = try virtio_ring_reset_readiness.summarizeResetReadiness(&ring, 4);
    try std.testing.expect(summary.blocker == null);
    try std.testing.expect(virtio_ring_reset_readiness.queueCanReset(summary));
    try std.testing.expect(!virtio_ring_reset_readiness.queueNeedsUsedPoll(summary));
    try std.testing.expect(!virtio_ring_reset_readiness.queueHasResetDebt(summary));
}

test "phase10 virtio ring reset-readiness replay keeps broken fences distinct from callback and queue debt" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(5, 8, .split, true, false);
    try ring.publishDescriptorChain(5);

    _ = try ring.markBroken(5);

    var summary = try virtio_ring_reset_readiness.summarizeResetReadiness(&ring, 5);
    try std.testing.expect(summary.broken);
    try std.testing.expect(!summary.callback_enabled);
    try std.testing.expectEqualStrings("queue_broken", @tagName(summary.blocker.?));
    try std.testing.expect(!virtio_ring_reset_readiness.queueCanReset(summary));
    try std.testing.expect(virtio_ring_reset_readiness.queueHasResetDebt(summary));

    _ = try ring.clearBroken(5);

    summary = try virtio_ring_reset_readiness.summarizeResetReadiness(&ring, 5);
    try std.testing.expect(!summary.broken);
    try std.testing.expectEqualStrings("unpublished_chains", @tagName(summary.blocker.?));
    try std.testing.expect(!virtio_ring_reset_readiness.queueCanReset(summary));
    try std.testing.expect(virtio_ring_reset_readiness.queueHasResetDebt(summary));
}
