const std = @import("std");
const virtio_ring = @import("virtio_ring");

pub const DelayedCallbackSummary = virtio_ring.DelayedCallbackSummary;

pub fn summarizeDelayedCallback(
    ring: *virtio_ring.VirtioRingLab,
    queue_index: u16,
) !DelayedCallbackSummary {
    return ring.enableCallbackDelayed(queue_index);
}

pub fn delayedCallbackShouldPoll(summary: DelayedCallbackSummary) bool {
    return summary.should_poll;
}

pub fn delayedCallbackBudgetExhausted(summary: DelayedCallbackSummary) bool {
    return summary.pending_used_chain_count > summary.delay_budget_count;
}

pub fn delayedCallbackSettled(summary: DelayedCallbackSummary) bool {
    return summary.settled;
}

pub fn delayedCallbackTargetWraps(summary: DelayedCallbackSummary) bool {
    return summary.delayed_event_target_wraps;
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

    for (0..5) |_| {
        try ring.publishDescriptorChain(queue_index);
    }
    _ = try ring.prepareKick(queue_index);
    try ring.recordUsedChains(queue_index, 5);
    _ = try ring.pollUsedBuffers(queue_index);
}

test "phase10 virtio ring delayed-callback wrapper keeps empty queues settled" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(0, 8, .split, true, false);

    const summary = try summarizeDelayedCallback(&ring, 0);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, 0), summary.queue_index);
    try std.testing.expect(summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 0), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), summary.delay_budget_count);
    try std.testing.expectEqual(@as(u16, 0), summary.delayed_event_target_idx);
    try std.testing.expectEqual(@as(u16, 0), summary.pending_used_chain_count);
    try std.testing.expect(!delayedCallbackTargetWraps(summary));
    try std.testing.expect(!delayedCallbackShouldPoll(summary));
    try std.testing.expect(!delayedCallbackBudgetExhausted(summary));
    try std.testing.expect(delayedCallbackSettled(summary));
}

test "phase10 virtio ring delayed-callback wrapper exposes threshold pressure before follow-up poll" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(7, 8, .packed_ring, true, true);

    try ring.publishDescriptorChain(7);
    try ring.publishDescriptorChain(7);
    try ring.publishDescriptorChain(7);
    try ring.publishDescriptorChain(7);
    _ = try ring.prepareKick(7);

    try ring.recordUsedChains(7, 2);
    var summary = try summarizeDelayedCallback(&ring, 7);
    try std.testing.expect(summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 2), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 1), summary.delay_budget_count);
    try std.testing.expectEqual(@as(u16, 3), summary.delayed_event_target_idx);
    try std.testing.expectEqual(@as(u16, 2), summary.pending_used_chain_count);
    try std.testing.expect(!delayedCallbackTargetWraps(summary));
    try std.testing.expect(delayedCallbackShouldPoll(summary));
    try std.testing.expect(delayedCallbackBudgetExhausted(summary));
    try std.testing.expect(!delayedCallbackSettled(summary));

    const poll = try ring.pollUsedBuffers(7);
    try std.testing.expectEqual(@as(u16, 2), poll.newly_used_chain_count);

    summary = try summarizeDelayedCallback(&ring, 7);
    try std.testing.expect(summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 2), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 1), summary.delay_budget_count);
    try std.testing.expectEqual(@as(u16, 3), summary.delayed_event_target_idx);
    try std.testing.expectEqual(@as(u16, 0), summary.pending_used_chain_count);
    try std.testing.expect(!delayedCallbackTargetWraps(summary));
    try std.testing.expect(!delayedCallbackShouldPoll(summary));
    try std.testing.expect(!delayedCallbackBudgetExhausted(summary));
    try std.testing.expect(delayedCallbackSettled(summary));
}

test "phase10 virtio ring delayed-callback wrapper reports wraparound targets near used-index rollover" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(6, 8, .packed_ring, true, true);
    try advanceUsedIndexNearWrap(&ring, 6);

    try ring.publishDescriptorChain(6);
    try ring.publishDescriptorChain(6);
    try ring.publishDescriptorChain(6);
    try ring.publishDescriptorChain(6);
    _ = try ring.prepareKick(6);
    try ring.recordUsedChains(6, 2);

    var summary = try summarizeDelayedCallback(&ring, 6);
    try std.testing.expectEqual(@as(u16, 65535), summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 65533), summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 2), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 1), summary.delay_budget_count);
    try std.testing.expectEqual(@as(u16, 0), summary.delayed_event_target_idx);
    try std.testing.expectEqual(@as(u16, 2), summary.pending_used_chain_count);
    try std.testing.expect(delayedCallbackTargetWraps(summary));
    try std.testing.expect(delayedCallbackShouldPoll(summary));
    try std.testing.expect(delayedCallbackBudgetExhausted(summary));
    try std.testing.expect(!delayedCallbackSettled(summary));

    const poll = try ring.pollUsedBuffers(6);
    try std.testing.expectEqual(@as(u16, 2), poll.newly_used_chain_count);

    summary = try summarizeDelayedCallback(&ring, 6);
    try std.testing.expectEqual(@as(u16, 65535), summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 65535), summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 2), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 1), summary.delay_budget_count);
    try std.testing.expectEqual(@as(u16, 0), summary.delayed_event_target_idx);
    try std.testing.expectEqual(@as(u16, 0), summary.pending_used_chain_count);
    try std.testing.expect(delayedCallbackTargetWraps(summary));
    try std.testing.expect(!delayedCallbackShouldPoll(summary));
    try std.testing.expect(!delayedCallbackBudgetExhausted(summary));
    try std.testing.expect(delayedCallbackSettled(summary));
}

test "phase10 virtio ring delayed-callback wrapper fences broken queues" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(5, 8, .split, false, false);
    _ = try ring.markBroken(5);

    try std.testing.expectError(error.QueueBroken, summarizeDelayedCallback(&ring, 5));
}
