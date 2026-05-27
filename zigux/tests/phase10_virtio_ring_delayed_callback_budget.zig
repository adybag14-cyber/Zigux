const std = @import("std");
const virtio_ring = @import("virtio_ring");

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

test "phase10 virtio ring delayed callback budget stays bounded to queue-local replay state" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(7, 8, .packed_ring, true, true);

    try ring.publishDescriptorChain(7);
    try ring.publishDescriptorChain(7);
    try ring.publishDescriptorChain(7);
    try ring.publishDescriptorChain(7);
    _ = try ring.prepareKick(7);

    try ring.recordUsedChains(7, 2);
    var summary = try ring.enableCallbackDelayed(7);
    try std.testing.expect(summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 2), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 1), summary.delay_budget_count);
    try std.testing.expectEqual(@as(u16, 2), summary.pending_used_chain_count);
    try std.testing.expectEqual(@as(u16, 3), summary.delayed_event_target_idx);
    try std.testing.expect(!summary.delayed_event_target_wraps);
    try std.testing.expect(summary.should_poll);
    try std.testing.expect(!summary.settled);

    const poll = try ring.pollUsedBuffers(7);
    try std.testing.expectEqual(@as(u16, 2), poll.newly_used_chain_count);

    summary = try ring.enableCallbackDelayed(7);
    try std.testing.expect(summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 2), summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 2), summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 2), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 1), summary.delay_budget_count);
    try std.testing.expectEqual(@as(u16, 3), summary.delayed_event_target_idx);
    try std.testing.expect(!summary.delayed_event_target_wraps);
    try std.testing.expectEqual(@as(u16, 0), summary.pending_used_chain_count);
    try std.testing.expect(!summary.should_poll);
    try std.testing.expect(summary.settled);

    try ring.disableCallback(7);
    summary = try ring.enableCallbackDelayed(7);
    try std.testing.expect(summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 2), summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 2), summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 2), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 1), summary.delay_budget_count);
    try std.testing.expectEqual(@as(u16, 3), summary.delayed_event_target_idx);
    try std.testing.expect(!summary.delayed_event_target_wraps);
    try std.testing.expectEqual(@as(u16, 0), summary.pending_used_chain_count);
    try std.testing.expect(!summary.should_poll);
    try std.testing.expect(summary.settled);

    try ring.recordUsedChains(7, 1);
    summary = try ring.enableCallbackDelayed(7);
    try std.testing.expect(summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 3), summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 2), summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 1), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), summary.delay_budget_count);
    try std.testing.expectEqual(@as(u16, 3), summary.delayed_event_target_idx);
    try std.testing.expect(!summary.delayed_event_target_wraps);
    try std.testing.expectEqual(@as(u16, 1), summary.pending_used_chain_count);
    try std.testing.expect(summary.should_poll);
    try std.testing.expect(!summary.settled);

    _ = try ring.markBroken(7);
    try std.testing.expectError(error.QueueBroken, ring.enableCallbackDelayed(7));
}

test "phase10 virtio ring delayed callback budget stays settled when pending used chains exactly match the delay threshold" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(5, 8, .packed_ring, true, true);

    inline for (0..8) |_| {
        try ring.publishDescriptorChain(5);
    }
    _ = try ring.prepareKick(5);

    try ring.recordUsedChains(5, 2);
    var summary = try ring.enableCallbackDelayed(5);
    try std.testing.expect(summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 6), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 4), summary.delay_budget_count);
    try std.testing.expectEqual(@as(u16, 2), summary.pending_used_chain_count);
    try std.testing.expectEqual(@as(u16, 6), summary.delayed_event_target_idx);
    try std.testing.expect(!summary.delayed_event_target_wraps);
    try std.testing.expect(!summary.should_poll);
    try std.testing.expect(!summary.settled);

    try ring.recordUsedChains(5, 2);
    summary = try ring.enableCallbackDelayed(5);
    try std.testing.expect(summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 4), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 3), summary.delay_budget_count);
    try std.testing.expectEqual(@as(u16, 4), summary.pending_used_chain_count);
    try std.testing.expectEqual(@as(u16, 7), summary.delayed_event_target_idx);
    try std.testing.expect(!summary.delayed_event_target_wraps);
    try std.testing.expect(summary.should_poll);
    try std.testing.expect(!summary.settled);

    const poll = try ring.pollUsedBuffers(5);
    try std.testing.expectEqual(@as(u16, 4), poll.newly_used_chain_count);
    try std.testing.expectEqual(@as(u16, 4), poll.outstanding_chain_count);

    summary = try ring.enableCallbackDelayed(5);
    try std.testing.expect(summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 4), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 3), summary.delay_budget_count);
    try std.testing.expectEqual(@as(u16, 0), summary.pending_used_chain_count);
    try std.testing.expectEqual(@as(u16, 7), summary.delayed_event_target_idx);
    try std.testing.expect(!summary.delayed_event_target_wraps);
    try std.testing.expect(!summary.should_poll);
    try std.testing.expect(summary.settled);
}

test "phase10 virtio ring delayed callback budget reports wraparound targets when used indices approach u16 rollover" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(6, 8, .packed_ring, true, true);
    try advanceUsedIndexNearWrap(&ring, 6);

    try ring.publishDescriptorChain(6);
    try ring.publishDescriptorChain(6);
    try ring.publishDescriptorChain(6);
    try ring.publishDescriptorChain(6);
    _ = try ring.prepareKick(6);
    try ring.recordUsedChains(6, 2);

    var summary = try ring.enableCallbackDelayed(6);
    try std.testing.expect(summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 65535), summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 65533), summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 2), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 1), summary.delay_budget_count);
    try std.testing.expectEqual(@as(u16, 0), summary.delayed_event_target_idx);
    try std.testing.expect(summary.delayed_event_target_wraps);
    try std.testing.expectEqual(@as(u16, 2), summary.pending_used_chain_count);
    try std.testing.expect(summary.should_poll);
    try std.testing.expect(!summary.settled);

    const poll = try ring.pollUsedBuffers(6);
    try std.testing.expectEqual(@as(u16, 2), poll.newly_used_chain_count);
    try std.testing.expectEqual(@as(u16, 2), poll.outstanding_chain_count);

    summary = try ring.enableCallbackDelayed(6);
    try std.testing.expectEqual(@as(u16, 65535), summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 65535), summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 2), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 1), summary.delay_budget_count);
    try std.testing.expectEqual(@as(u16, 0), summary.delayed_event_target_idx);
    try std.testing.expect(summary.delayed_event_target_wraps);
    try std.testing.expectEqual(@as(u16, 0), summary.pending_used_chain_count);
    try std.testing.expect(!summary.should_poll);
    try std.testing.expect(summary.settled);
}
