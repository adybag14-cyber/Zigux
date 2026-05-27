const std = @import("std");
const virtio_ring = @import("virtio_ring");

pub const QueueShapeSummary = virtio_ring.QueueShapeSummary;

pub fn summarizeQueueShape(
    ring: *const virtio_ring.VirtioRingLab,
    queue_index: u16,
) !QueueShapeSummary {
    return ring.queueShapeSummary(queue_index);
}

pub fn queueUsesPackedRing(summary: QueueShapeSummary) bool {
    return summary.layout == .packed_ring;
}

pub fn queueUsesEventIdx(summary: QueueShapeSummary) bool {
    return summary.uses_event_idx;
}

test "phase10 virtio ring queue-shape wrapper keeps split and packed queue definitions explicit" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(0, 8, .split, true, false);
    try ring.defineQueue(3, 16, .packed_ring, false, true);

    var summary = try summarizeQueueShape(&ring, 0);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, 0), summary.queue_index);
    try std.testing.expectEqual(@as(u16, 8), summary.descriptor_count);
    try std.testing.expectEqual(virtio_ring.QueueLayout.split, summary.layout);
    try std.testing.expect(queueUsesEventIdx(summary));
    try std.testing.expect(!queueUsesPackedRing(summary));
    try std.testing.expect(!summary.uses_indirect_descriptors);

    summary = try summarizeQueueShape(&ring, 3);
    try std.testing.expectEqual(@as(u16, 3), summary.queue_index);
    try std.testing.expectEqual(@as(u16, 16), summary.descriptor_count);
    try std.testing.expectEqual(virtio_ring.QueueLayout.packed_ring, summary.layout);
    try std.testing.expect(!queueUsesEventIdx(summary));
    try std.testing.expect(queueUsesPackedRing(summary));
    try std.testing.expect(summary.uses_indirect_descriptors);
}

test "phase10 virtio ring queue-shape wrapper stays queue-local across sparse queue definitions" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(1, 32, .packed_ring, true, true);
    try ring.defineQueue(7, 64, .split, false, false);

    const first = try summarizeQueueShape(&ring, 1);
    try std.testing.expectEqual(@as(u16, 1), first.queue_index);
    try std.testing.expectEqual(@as(u16, 32), first.descriptor_count);
    try std.testing.expect(queueUsesPackedRing(first));
    try std.testing.expect(queueUsesEventIdx(first));
    try std.testing.expect(first.uses_indirect_descriptors);

    const last = try summarizeQueueShape(&ring, 7);
    try std.testing.expectEqual(@as(u16, 7), last.queue_index);
    try std.testing.expectEqual(@as(u16, 64), last.descriptor_count);
    try std.testing.expect(!queueUsesPackedRing(last));
    try std.testing.expect(!queueUsesEventIdx(last));
    try std.testing.expect(!last.uses_indirect_descriptors);

    try std.testing.expectError(error.QueueNotDefined, summarizeQueueShape(&ring, 2));
}
