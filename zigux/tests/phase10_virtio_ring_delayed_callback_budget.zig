const std = @import("std");
const virtio_ring = @import("virtio_ring");

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
    try std.testing.expect(summary.should_poll);

    const poll = try ring.pollUsedBuffers(7);
    try std.testing.expectEqual(@as(u16, 2), poll.newly_used_chain_count);

    summary = try ring.enableCallbackDelayed(7);
    try std.testing.expect(summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 2), summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 2), summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 2), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 1), summary.delay_budget_count);
    try std.testing.expectEqual(@as(u16, 3), summary.delayed_event_target_idx);
    try std.testing.expectEqual(@as(u16, 0), summary.pending_used_chain_count);
    try std.testing.expect(!summary.should_poll);

    try ring.disableCallback(7);
    summary = try ring.enableCallbackDelayed(7);
    try std.testing.expect(summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 2), summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 2), summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 2), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 1), summary.delay_budget_count);
    try std.testing.expectEqual(@as(u16, 3), summary.delayed_event_target_idx);
    try std.testing.expectEqual(@as(u16, 0), summary.pending_used_chain_count);
    try std.testing.expect(!summary.should_poll);

    _ = try ring.markBroken(7);
    try std.testing.expectError(error.QueueBroken, ring.enableCallbackDelayed(7));
}
