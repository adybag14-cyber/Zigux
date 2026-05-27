const std = @import("std");
const virtio_ring = @import("virtio_ring");

pub const UsedBufferPollSummary = virtio_ring.UsedBufferPollSummary;

pub fn summarizeUsedBufferPoll(
    ring: *virtio_ring.VirtioRingLab,
    queue_index: u16,
) !UsedBufferPollSummary {
    return ring.pollUsedBuffers(queue_index);
}

pub fn usedBufferPollHasNewChains(summary: UsedBufferPollSummary) bool {
    return summary.has_newly_used_chains;
}

pub fn usedBufferPollSettled(summary: UsedBufferPollSummary) bool {
    return summary.outstanding_chain_count == 0 and !summary.has_newly_used_chains;
}

test "phase10 virtio ring used-buffer-poll wrapper keeps empty queues settled" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(0, 8, .split, true, false);

    const summary = try summarizeUsedBufferPoll(&ring, 0);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, 0), summary.queue_index);
    try std.testing.expectEqual(@as(u16, 0), summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 0), summary.newly_used_chain_count);
    try std.testing.expectEqual(@as(u16, 0), summary.outstanding_chain_count);
    try std.testing.expect(!usedBufferPollHasNewChains(summary));
    try std.testing.expect(usedBufferPollSettled(summary));
}

test "phase10 virtio ring used-buffer-poll wrapper exposes newly used chains before the follow-up poll settles" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(3, 8, .packed_ring, true, true);

    inline for (0..3) |_| {
        try ring.publishDescriptorChain(3);
    }
    _ = try ring.prepareKick(3);
    try ring.recordUsedChains(3, 2);

    var summary = try summarizeUsedBufferPoll(&ring, 3);
    try std.testing.expectEqual(@as(u16, 2), summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 2), summary.newly_used_chain_count);
    try std.testing.expectEqual(@as(u16, 1), summary.outstanding_chain_count);
    try std.testing.expect(usedBufferPollHasNewChains(summary));
    try std.testing.expect(!usedBufferPollSettled(summary));

    summary = try summarizeUsedBufferPoll(&ring, 3);
    try std.testing.expectEqual(@as(u16, 2), summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 2), summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 0), summary.newly_used_chain_count);
    try std.testing.expectEqual(@as(u16, 1), summary.outstanding_chain_count);
    try std.testing.expect(!usedBufferPollHasNewChains(summary));
    try std.testing.expect(!usedBufferPollSettled(summary));
}

test "phase10 virtio ring used-buffer-poll wrapper settles once all used chains are observed" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(5, 8, .split, false, false);

    inline for (0..2) |_| {
        try ring.publishDescriptorChain(5);
    }
    _ = try ring.prepareKick(5);
    try ring.recordUsedChains(5, 2);

    const first = try summarizeUsedBufferPoll(&ring, 5);
    try std.testing.expectEqual(@as(u16, 2), first.newly_used_chain_count);
    try std.testing.expectEqual(@as(u16, 0), first.outstanding_chain_count);
    try std.testing.expect(usedBufferPollHasNewChains(first));
    try std.testing.expect(!usedBufferPollSettled(first));

    const second = try summarizeUsedBufferPoll(&ring, 5);
    try std.testing.expectEqual(@as(u16, 0), second.newly_used_chain_count);
    try std.testing.expectEqual(@as(u16, 0), second.outstanding_chain_count);
    try std.testing.expect(!usedBufferPollHasNewChains(second));
    try std.testing.expect(usedBufferPollSettled(second));
}
