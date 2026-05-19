const std = @import("std");
const virtio_ring = @import("virtio_ring");

pub const QueuePublishReadinessSummary = virtio_ring.QueuePublishReadinessSummary;
pub const QueuePublishReadinessBlocker = virtio_ring.QueuePublishReadinessBlocker;

pub fn summarize(
    ring: *const virtio_ring.VirtioRingLab,
    queue_index: u16,
) !QueuePublishReadinessSummary {
    return ring.queuePublishReadinessSummary(queue_index);
}

pub fn blockerTag(blocker: QueuePublishReadinessBlocker) []const u8 {
    return @tagName(blocker);
}

pub fn canPublish(summary: QueuePublishReadinessSummary) bool {
    return summary.can_publish;
}

test "phase10 virtio ring publish readiness stays queue-local across empty draining full and broken states" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(2, 8, .split, true, false);

    var summary = try summarize(&ring, 2);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, 2), summary.queue_index);
    try std.testing.expectEqual(@as(u16, 8), summary.descriptor_count);
    try std.testing.expectEqual(@as(u16, 0), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), summary.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 8), summary.available_descriptor_count);
    try std.testing.expect(!summary.broken);
    try std.testing.expect(canPublish(summary));
    try std.testing.expect(summary.blocker == null);

    try ring.publishDescriptorChain(2);
    try ring.publishDescriptorChain(2);
    summary = try summarize(&ring, 2);
    try std.testing.expectEqual(@as(u16, 2), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 2), summary.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 6), summary.available_descriptor_count);
    try std.testing.expect(canPublish(summary));
    try std.testing.expect(summary.blocker == null);

    _ = try ring.prepareKick(2);
    try ring.recordUsedChains(2, 1);
    summary = try summarize(&ring, 2);
    try std.testing.expectEqual(@as(u16, 1), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), summary.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 7), summary.available_descriptor_count);
    try std.testing.expect(canPublish(summary));

    inline for (0..7) |_| {
        try ring.publishDescriptorChain(2);
    }
    summary = try summarize(&ring, 2);
    try std.testing.expectEqual(@as(u16, 8), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 7), summary.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 0), summary.available_descriptor_count);
    try std.testing.expect(!canPublish(summary));
    try std.testing.expectEqualStrings("queue_full", blockerTag(summary.blocker.?));
    try std.testing.expectError(error.QueueFull, ring.publishDescriptorChain(2));

    _ = try ring.markBroken(2);
    summary = try summarize(&ring, 2);
    try std.testing.expect(summary.broken);
    try std.testing.expectEqual(@as(u16, 0), summary.available_descriptor_count);
    try std.testing.expect(!canPublish(summary));
    try std.testing.expectEqualStrings("queue_broken", blockerTag(summary.blocker.?));

    _ = try ring.clearBroken(2);
    summary = try summarize(&ring, 2);
    try std.testing.expect(!summary.broken);
    try std.testing.expectEqual(@as(u16, 0), summary.available_descriptor_count);
    try std.testing.expect(!canPublish(summary));
    try std.testing.expectEqualStrings("queue_full", blockerTag(summary.blocker.?));
}

test "phase10 virtio ring publish readiness rejects undefined queues" {
    var ring = virtio_ring.VirtioRingLab{};
    try std.testing.expectError(error.QueueNotDefined, summarize(&ring, 1));
}