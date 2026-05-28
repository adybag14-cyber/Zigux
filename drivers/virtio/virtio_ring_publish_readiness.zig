const std = @import("std");
const virtio_ring = @import("virtio_ring");

pub const QueuePublishReadinessSummary = virtio_ring.QueuePublishReadinessSummary;

pub fn summarizePublishReadiness(
    ring: *const virtio_ring.VirtioRingLab,
    queue_index: u16,
) !QueuePublishReadinessSummary {
    return ring.queuePublishReadinessSummary(queue_index);
}

pub fn queueCanPublish(summary: QueuePublishReadinessSummary) bool {
    return summary.publish_ready;
}

pub fn queueHasPublishCapacity(summary: QueuePublishReadinessSummary) bool {
    return summary.available_descriptor_count != 0;
}

test "phase10 virtio ring publish-readiness wrapper keeps empty queues publishable" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(1, 8, .split, true, false);

    const summary = try summarizePublishReadiness(&ring, 1);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, 1), summary.queue_index);
    try std.testing.expectEqual(@as(u16, 8), summary.descriptor_count);
    try std.testing.expectEqual(@as(u16, 0), summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 0), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), summary.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 8), summary.available_descriptor_count);
    try std.testing.expect(!summary.broken);
    try std.testing.expect(summary.blocker == null);
    try std.testing.expect(queueCanPublish(summary));
    try std.testing.expect(queueHasPublishCapacity(summary));
}

test "phase10 virtio ring publish-readiness wrapper keeps unpublished chains visible while remaining queue-local publishable" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(2, 8, .split, true, false);

    try ring.publishDescriptorChain(2);
    try ring.publishDescriptorChain(2);

    var summary = try summarizePublishReadiness(&ring, 2);
    try std.testing.expectEqual(@as(u16, 2), summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 2), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 2), summary.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 6), summary.available_descriptor_count);
    try std.testing.expect(summary.blocker == null);
    try std.testing.expect(queueCanPublish(summary));
    try std.testing.expect(queueHasPublishCapacity(summary));

    const kick = try ring.prepareKick(2);
    try std.testing.expect(kick.needs_kick);
    try std.testing.expectEqual(@as(u16, 2), kick.num_added);

    summary = try summarizePublishReadiness(&ring, 2);
    try std.testing.expectEqual(@as(u16, 2), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), summary.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 6), summary.available_descriptor_count);
    try std.testing.expect(summary.blocker == null);
    try std.testing.expect(queueCanPublish(summary));
    try std.testing.expect(queueHasPublishCapacity(summary));
}

test "phase10 virtio ring publish-readiness wrapper blocks full queues until used chains return capacity" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(3, 8, .packed_ring, true, true);

    inline for (0..8) |_| {
        try ring.publishDescriptorChain(3);
    }

    var summary = try summarizePublishReadiness(&ring, 3);
    try std.testing.expectEqual(@as(u16, 8), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 8), summary.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 0), summary.available_descriptor_count);
    try std.testing.expectEqualStrings("queue_full", @tagName(summary.blocker.?));
    try std.testing.expect(!queueCanPublish(summary));
    try std.testing.expect(!queueHasPublishCapacity(summary));

    _ = try ring.prepareKick(3);
    try ring.recordUsedChains(3, 2);

    summary = try summarizePublishReadiness(&ring, 3);
    try std.testing.expectEqual(@as(u16, 6), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), summary.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 2), summary.available_descriptor_count);
    try std.testing.expect(summary.blocker == null);
    try std.testing.expect(queueCanPublish(summary));
    try std.testing.expect(queueHasPublishCapacity(summary));
}

test "phase10 virtio ring publish-readiness wrapper regains publish capacity before used buffers are polled" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(4, 8, .split, true, false);

    inline for (0..8) |_| {
        try ring.publishDescriptorChain(4);
    }
    _ = try ring.prepareKick(4);
    try ring.recordUsedChains(4, 3);

    const summary = try summarizePublishReadiness(&ring, 4);
    try std.testing.expectEqual(@as(u16, 5), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), summary.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 3), summary.available_descriptor_count);
    try std.testing.expect(summary.blocker == null);
    try std.testing.expect(queueCanPublish(summary));
    try std.testing.expect(queueHasPublishCapacity(summary));

    const reset_readiness = try ring.queueResetReadinessSummary(4);
    try std.testing.expect(!reset_readiness.reset_ready);
    try std.testing.expectEqualStrings("unpolled_used_chains", @tagName(reset_readiness.blocker.?));
    try std.testing.expectEqual(@as(u16, 3), reset_readiness.pending_used_chain_count);
}

test "phase10 virtio ring publish-readiness wrapper keeps broken queues fenced even when slots remain" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(5, 8, .split, false, false);
    try ring.publishDescriptorChain(5);

    _ = try ring.markBroken(5);
    var summary = try summarizePublishReadiness(&ring, 5);
    try std.testing.expect(summary.broken);
    try std.testing.expectEqual(@as(u16, 7), summary.available_descriptor_count);
    try std.testing.expectEqualStrings("queue_broken", @tagName(summary.blocker.?));
    try std.testing.expect(!queueCanPublish(summary));
    try std.testing.expect(queueHasPublishCapacity(summary));

    _ = try ring.clearBroken(5);
    summary = try summarizePublishReadiness(&ring, 5);
    try std.testing.expect(!summary.broken);
    try std.testing.expect(summary.blocker == null);
    try std.testing.expect(queueCanPublish(summary));
}

test "phase10 virtio ring publish-readiness wrapper falls back to queue-full after a broken full queue is cleared" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(6, 8, .packed_ring, true, true);

    inline for (0..8) |_| {
        try ring.publishDescriptorChain(6);
    }

    _ = try ring.markBroken(6);
    var summary = try summarizePublishReadiness(&ring, 6);
    try std.testing.expect(summary.broken);
    try std.testing.expectEqual(@as(u16, 8), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 8), summary.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 0), summary.available_descriptor_count);
    try std.testing.expectEqualStrings("queue_broken", @tagName(summary.blocker.?));
    try std.testing.expect(!queueCanPublish(summary));
    try std.testing.expect(!queueHasPublishCapacity(summary));

    _ = try ring.clearBroken(6);
    summary = try summarizePublishReadiness(&ring, 6);
    try std.testing.expect(!summary.broken);
    try std.testing.expectEqual(@as(u16, 8), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 8), summary.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 0), summary.available_descriptor_count);
    try std.testing.expectEqualStrings("queue_full", @tagName(summary.blocker.?));
    try std.testing.expect(!queueCanPublish(summary));
    try std.testing.expect(!queueHasPublishCapacity(summary));
}

test "phase10 virtio ring publish-readiness wrapper preserves capacity accounting across avail-index rollover" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(7, 8, .split, true, false);

    for (0..8191) |_| {
        for (0..8) |_| {
            try ring.publishDescriptorChain(7);
        }
        _ = try ring.prepareKick(7);
        try ring.recordUsedChains(7, 8);
        _ = try ring.pollUsedBuffers(7);
    }

    for (0..7) |_| {
        try ring.publishDescriptorChain(7);
    }
    _ = try ring.prepareKick(7);
    try ring.recordUsedChains(7, 7);
    _ = try ring.pollUsedBuffers(7);

    var summary = try summarizePublishReadiness(&ring, 7);
    try std.testing.expectEqual(@as(u16, std.math.maxInt(u16)), summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 0), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), summary.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 8), summary.available_descriptor_count);
    try std.testing.expect(summary.blocker == null);
    try std.testing.expect(queueCanPublish(summary));
    try std.testing.expect(queueHasPublishCapacity(summary));

    try ring.publishDescriptorChain(7);
    summary = try summarizePublishReadiness(&ring, 7);
    try std.testing.expectEqual(@as(u16, 0), summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 1), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 1), summary.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 7), summary.available_descriptor_count);
    try std.testing.expect(summary.blocker == null);
    try std.testing.expect(queueCanPublish(summary));
    try std.testing.expect(queueHasPublishCapacity(summary));

    _ = try ring.prepareKick(7);
    try ring.recordUsedChains(7, 1);
    _ = try ring.pollUsedBuffers(7);

    summary = try summarizePublishReadiness(&ring, 7);
    try std.testing.expectEqual(@as(u16, 0), summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 0), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), summary.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 8), summary.available_descriptor_count);
    try std.testing.expect(summary.blocker == null);
    try std.testing.expect(queueCanPublish(summary));
    try std.testing.expect(queueHasPublishCapacity(summary));
}