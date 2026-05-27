const std = @import("std");
const virtio_ring = @import("virtio_ring");

pub const QueueResetReadinessSummary = virtio_ring.QueueResetReadinessSummary;

pub fn summarizeResetReadiness(
    ring: *const virtio_ring.VirtioRingLab,
    queue_index: u16,
) !QueueResetReadinessSummary {
    return ring.queueResetReadinessSummary(queue_index);
}

pub fn queueCanReset(summary: QueueResetReadinessSummary) bool {
    return summary.reset_ready;
}

pub fn queueNeedsUsedPoll(summary: QueueResetReadinessSummary) bool {
    return summary.pending_used_chain_count != 0;
}

pub fn queueHasResetDebt(summary: QueueResetReadinessSummary) bool {
    return summary.unpublished_chain_count != 0 or
        summary.outstanding_chain_count != 0 or
        summary.pending_used_chain_count != 0;
}

fn advanceUsedIndexNearWrap(ring: *virtio_ring.VirtioRingLab, queue_index: u16) !void {
    for (0..8191) |_| {
        for (0..8) |_| {
            try ring.publishDescriptorChain(queue_index);
        }
        _ = try ring.prepareKick(queue_index);
        try ring.recordUsedChains(queue_index, 8);
        _ = try ring.pollUsedBuffers(queue_index);
    }

    for (0..7) |_| {
        try ring.publishDescriptorChain(queue_index);
    }
    _ = try ring.prepareKick(queue_index);
    try ring.recordUsedChains(queue_index, 7);
    _ = try ring.pollUsedBuffers(queue_index);
}

test "phase10 virtio ring reset-readiness wrapper keeps empty queues resettable" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(0, 8, .split, true, false);

    const summary = try summarizeResetReadiness(&ring, 0);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, 0), summary.queue_index);
    try std.testing.expect(summary.callback_enabled);
    try std.testing.expect(!summary.broken);
    try std.testing.expectEqual(@as(u16, 0), summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 0), summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 0), summary.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 0), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), summary.pending_used_chain_count);
    try std.testing.expect(summary.blocker == null);
    try std.testing.expect(queueCanReset(summary));
    try std.testing.expect(!queueNeedsUsedPoll(summary));
    try std.testing.expect(!queueHasResetDebt(summary));
}

test "phase10 virtio ring reset-readiness wrapper orders unpublished then outstanding debt" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(1, 8, .packed_ring, true, true);

    try ring.publishDescriptorChain(1);
    try ring.publishDescriptorChain(1);

    var summary = try summarizeResetReadiness(&ring, 1);
    try std.testing.expectEqualStrings("unpublished_chains", @tagName(summary.blocker.?));
    try std.testing.expectEqual(@as(u16, 2), summary.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 2), summary.outstanding_chain_count);
    try std.testing.expect(!queueCanReset(summary));
    try std.testing.expect(queueHasResetDebt(summary));

    const kick = try ring.prepareKick(1);
    try std.testing.expect(kick.needs_kick);

    summary = try summarizeResetReadiness(&ring, 1);
    try std.testing.expectEqualStrings("outstanding_chains", @tagName(summary.blocker.?));
    try std.testing.expectEqual(@as(u16, 0), summary.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 2), summary.outstanding_chain_count);
    try std.testing.expect(!queueCanReset(summary));
    try std.testing.expect(queueHasResetDebt(summary));
}

test "phase10 virtio ring reset-readiness wrapper exposes used-poll debt before reset clears" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(2, 8, .split, true, false);

    try ring.publishDescriptorChain(2);
    _ = try ring.prepareKick(2);
    try ring.recordUsedChains(2, 1);

    var summary = try summarizeResetReadiness(&ring, 2);
    try std.testing.expectEqualStrings("unpolled_used_chains", @tagName(summary.blocker.?));
    try std.testing.expectEqual(@as(u16, 1), summary.pending_used_chain_count);
    try std.testing.expect(!queueCanReset(summary));
    try std.testing.expect(queueNeedsUsedPoll(summary));
    try std.testing.expect(queueHasResetDebt(summary));

    const poll = try ring.pollUsedBuffers(2);
    try std.testing.expectEqual(@as(u16, 1), poll.newly_used_chain_count);

    summary = try summarizeResetReadiness(&ring, 2);
    try std.testing.expect(summary.blocker == null);
    try std.testing.expect(queueCanReset(summary));
    try std.testing.expect(!queueNeedsUsedPoll(summary));
    try std.testing.expect(!queueHasResetDebt(summary));
}

test "phase10 virtio ring reset-readiness wrapper keeps used-poll debt explicit across used-index rollover" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(6, 8, .split, true, false);
    try advanceUsedIndexNearWrap(&ring, 6);

    try ring.publishDescriptorChain(6);
    _ = try ring.prepareKick(6);
    try ring.recordUsedChains(6, 1);

    var summary = try summarizeResetReadiness(&ring, 6);
    try std.testing.expectEqual(@as(u16, 0), summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, std.math.maxInt(u16)), summary.last_polled_used_idx);
    try std.testing.expectEqualStrings("unpolled_used_chains", @tagName(summary.blocker.?));
    try std.testing.expectEqual(@as(u16, 1), summary.pending_used_chain_count);
    try std.testing.expect(!queueCanReset(summary));
    try std.testing.expect(queueNeedsUsedPoll(summary));
    try std.testing.expect(queueHasResetDebt(summary));

    const poll = try ring.pollUsedBuffers(6);
    try std.testing.expectEqual(@as(u16, 0), poll.last_used_idx);
    try std.testing.expectEqual(@as(u16, std.math.maxInt(u16)), poll.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 1), poll.newly_used_chain_count);
    try std.testing.expectEqual(@as(u16, 0), poll.outstanding_chain_count);
    try std.testing.expect(poll.has_newly_used_chains);

    summary = try summarizeResetReadiness(&ring, 6);
    try std.testing.expectEqual(@as(u16, 0), summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), summary.last_polled_used_idx);
    try std.testing.expect(summary.blocker == null);
    try std.testing.expect(queueCanReset(summary));
    try std.testing.expect(!queueNeedsUsedPoll(summary));
    try std.testing.expect(!queueHasResetDebt(summary));
}

test "phase10 virtio ring reset-readiness wrapper keeps broken queues fenced until clearBroken" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(3, 8, .split, false, false);

    try ring.publishDescriptorChain(3);
    _ = try ring.markBroken(3);

    var summary = try summarizeResetReadiness(&ring, 3);
    try std.testing.expect(summary.broken);
    try std.testing.expect(!summary.callback_enabled);
    try std.testing.expectEqualStrings("queue_broken", @tagName(summary.blocker.?));
    try std.testing.expect(!queueCanReset(summary));
    try std.testing.expect(queueHasResetDebt(summary));

    _ = try ring.clearBroken(3);
    summary = try summarizeResetReadiness(&ring, 3);
    try std.testing.expect(!summary.broken);
    try std.testing.expectEqualStrings("unpublished_chains", @tagName(summary.blocker.?));
    try std.testing.expect(!queueCanReset(summary));
    try std.testing.expect(queueHasResetDebt(summary));
}
