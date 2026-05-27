const std = @import("std");
const virtio_ring = @import("virtio_ring");

pub const CallbackEnableSummary = virtio_ring.CallbackEnableSummary;

pub fn summarizeCallbackEnable(
    ring: *virtio_ring.VirtioRingLab,
    queue_index: u16,
) !CallbackEnableSummary {
    return ring.enableCallback(queue_index);
}

pub fn callbackShouldPoll(summary: CallbackEnableSummary) bool {
    return summary.should_poll;
}

pub fn callbackObservedAllUsedChains(summary: CallbackEnableSummary) bool {
    return summary.pending_used_chain_count == 0;
}

test "phase10 virtio ring callback-enable wrapper keeps empty queues callback-ready" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(0, 8, .split, true, false);

    const summary = try summarizeCallbackEnable(&ring, 0);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, 0), summary.queue_index);
    try std.testing.expect(summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 0), summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 0), summary.pending_used_chain_count);
    try std.testing.expect(!callbackShouldPoll(summary));
    try std.testing.expect(callbackObservedAllUsedChains(summary));
}

test "phase10 virtio ring callback-enable wrapper exposes pending used chains before the follow-up poll" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(3, 8, .packed_ring, true, true);

    inline for (0..3) |_| {
        try ring.publishDescriptorChain(3);
    }
    _ = try ring.prepareKick(3);
    try ring.recordUsedChains(3, 2);
    try ring.disableCallback(3);

    var summary = try summarizeCallbackEnable(&ring, 3);
    try std.testing.expect(summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 2), summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 2), summary.pending_used_chain_count);
    try std.testing.expect(callbackShouldPoll(summary));
    try std.testing.expect(!callbackObservedAllUsedChains(summary));

    _ = try ring.pollUsedBuffers(3);

    summary = try summarizeCallbackEnable(&ring, 3);
    try std.testing.expect(summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 2), summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 2), summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 0), summary.pending_used_chain_count);
    try std.testing.expect(!callbackShouldPoll(summary));
    try std.testing.expect(callbackObservedAllUsedChains(summary));
}

test "phase10 virtio ring callback-enable wrapper fences broken queues" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(5, 8, .split, false, false);
    _ = try ring.markBroken(5);

    try std.testing.expectError(error.QueueBroken, summarizeCallbackEnable(&ring, 5));
}
