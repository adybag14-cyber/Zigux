const std = @import("std");
const virtio_ring = @import("virtio_ring");

pub const DelayedCallbackSummary = virtio_ring.DelayedCallbackSummary;
pub const BrokenQueueSummary = virtio_ring.BrokenQueueSummary;
pub const QueueResetReadinessSummary = virtio_ring.QueueResetReadinessSummary;

pub fn summarizeDelayedCallback(
    ring: *virtio_ring.VirtioRingLab,
    queue_index: u16,
) !DelayedCallbackSummary {
    return ring.enableCallbackDelayed(queue_index);
}

pub fn summarizeBrokenQueue(
    ring: *const virtio_ring.VirtioRingLab,
    queue_index: u16,
) !BrokenQueueSummary {
    return ring.brokenQueueSummary(queue_index);
}

pub fn summarizeResetReadiness(
    ring: *const virtio_ring.VirtioRingLab,
    queue_index: u16,
) !QueueResetReadinessSummary {
    return ring.queueResetReadinessSummary(queue_index);
}

pub fn queueNeedsResetPoll(summary: QueueResetReadinessSummary) bool {
    return summary.pending_used_chain_count != 0;
}

pub fn queueHasBrokenCallbackFence(summary: BrokenQueueSummary) bool {
    return summary.broken and !summary.callback_enabled;
}

pub fn delayedCallbackBudgetExhausted(summary: DelayedCallbackSummary) bool {
    return summary.pending_used_chain_count > summary.delay_budget_count;
}

test "phase10 virtio ring verify keeps delayed callback wrapper thresholds explicit" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(4, 8, .split, true, false);

    try ring.publishDescriptorChain(4);
    try ring.publishDescriptorChain(4);
    try ring.publishDescriptorChain(4);
    try ring.publishDescriptorChain(4);
    _ = try ring.prepareKick(4);

    try ring.recordUsedChains(4, 2);
    var summary = try summarizeDelayedCallback(&ring, 4);
    try std.testing.expect(summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 2), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 1), summary.delay_budget_count);
    try std.testing.expectEqual(@as(u16, 2), summary.pending_used_chain_count);
    try std.testing.expectEqual(@as(u16, 3), summary.delayed_event_target_idx);
    try std.testing.expect(summary.should_poll);
    try std.testing.expect(delayedCallbackBudgetExhausted(summary));

    const poll = try ring.pollUsedBuffers(4);
    try std.testing.expectEqual(@as(u16, 2), poll.newly_used_chain_count);

    summary = try summarizeDelayedCallback(&ring, 4);
    try std.testing.expectEqual(@as(u16, 0), summary.pending_used_chain_count);
    try std.testing.expect(!summary.should_poll);
    try std.testing.expect(!delayedCallbackBudgetExhausted(summary));
}

test "phase10 virtio ring verify keeps broken queue fences visible until clear" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(5, 8, .packed_ring, false, true);

    try ring.publishDescriptorChain(5);
    try ring.publishDescriptorChain(5);
    _ = try ring.prepareKick(5);
    try ring.recordUsedChains(5, 1);

    _ = try ring.markBroken(5);
    var broken = try summarizeBrokenQueue(&ring, 5);
    try std.testing.expect(queueHasBrokenCallbackFence(broken));
    try std.testing.expectEqual(@as(u16, 1), broken.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 1), broken.pending_used_chain_count);
    try std.testing.expectError(error.QueueBroken, ring.pollUsedBuffers(5));

    _ = try ring.clearBroken(5);
    broken = try summarizeBrokenQueue(&ring, 5);
    try std.testing.expect(!broken.broken);
    try std.testing.expect(!queueHasBrokenCallbackFence(broken));
    try std.testing.expectEqual(@as(u16, 1), broken.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 1), broken.pending_used_chain_count);

    const poll = try ring.pollUsedBuffers(5);
    try std.testing.expectEqual(@as(u16, 1), poll.newly_used_chain_count);
}

test "phase10 virtio ring verify keeps reset-readiness blockers ordered through queue-local replay" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(6, 8, .packed_ring, true, true);

    var readiness = try summarizeResetReadiness(&ring, 6);
    try std.testing.expect(readiness.reset_ready);
    try std.testing.expect(readiness.blocker == null);
    try std.testing.expect(!queueNeedsResetPoll(readiness));

    try ring.publishDescriptorChain(6);
    readiness = try summarizeResetReadiness(&ring, 6);
    try std.testing.expectEqualStrings("unpublished_chains", @tagName(readiness.blocker.?));

    _ = try ring.prepareKick(6);
    readiness = try summarizeResetReadiness(&ring, 6);
    try std.testing.expectEqualStrings("outstanding_chains", @tagName(readiness.blocker.?));

    try ring.recordUsedChains(6, 1);
    readiness = try summarizeResetReadiness(&ring, 6);
    try std.testing.expectEqualStrings("unpolled_used_chains", @tagName(readiness.blocker.?));
    try std.testing.expect(queueNeedsResetPoll(readiness));

    _ = try ring.pollUsedBuffers(6);
    readiness = try summarizeResetReadiness(&ring, 6);
    try std.testing.expect(readiness.reset_ready);
    try std.testing.expect(readiness.blocker == null);
    try std.testing.expect(!queueNeedsResetPoll(readiness));
}
