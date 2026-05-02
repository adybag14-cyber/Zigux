const std = @import("std");
const virtio_ring = @import("virtio_ring");

test "phase10 virtio ring drained reset clears the broken flag so the queue can be reused" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(2, 8, .packed_ring, true, true);

    _ = try ring.breakQueue(2);
    try std.testing.expectError(error.QueueBroken, ring.publishDescriptorChain(2));

    const guard_summary = try ring.resetGuardSummary(2);
    try std.testing.expect(guard_summary.reset_allowed);

    const reset_summary = try ring.resetQueue(2);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", reset_summary.anchor);
    try std.testing.expect(reset_summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 0), reset_summary.avail_idx_shadow);

    const broken_summary = try ring.brokenSummary(2);
    try std.testing.expect(!broken_summary.broken);
    try std.testing.expectEqual(@as(u16, 0), broken_summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), broken_summary.pending_used_chain_count);
    try std.testing.expectEqual(@as(u16, 0), broken_summary.unpublished_chain_count);

    try ring.publishDescriptorChain(2);
    const notification_summary = try ring.notificationSummary(2);
    try std.testing.expectEqual(@as(u16, 1), notification_summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 1), notification_summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 1), notification_summary.num_added);
}

test "phase10 virtio ring drained reset restores callback bookkeeping to a clean reuse baseline" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(3, 8, .split, true, false);

    _ = try ring.disableCallback(3);
    try ring.publishDescriptorChain(3);
    _ = try ring.prepareKick(3);
    try ring.recordUsedChains(3, 1);
    _ = try ring.pollUsedBuffers(3);
    _ = try ring.breakQueue(3);

    const reset_summary = try ring.resetQueue(3);
    try std.testing.expect(reset_summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 0), reset_summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), reset_summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(usize, 0), reset_summary.notification_count);

    var disable_summary = try ring.disableCallback(3);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", disable_summary.anchor);
    try std.testing.expectEqual(@as(u16, 3), disable_summary.queue_index);
    try std.testing.expect(!disable_summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 0), disable_summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), disable_summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 0), disable_summary.pending_used_chain_count);
    try std.testing.expect(!disable_summary.should_poll);

    const prepare_summary = try ring.enableCallbackPrepare(3);
    try std.testing.expect(prepare_summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 0), prepare_summary.last_used_idx_snapshot);

    const poll_summary = try ring.pollAfterEnable(3, prepare_summary.last_used_idx_snapshot);
    try std.testing.expectEqual(@as(u16, 0), poll_summary.last_used_idx_snapshot);
    try std.testing.expectEqual(@as(u16, 0), poll_summary.current_last_used_idx);
    try std.testing.expect(!poll_summary.has_used_buffers_since_prepare);

    const delayed_summary = try ring.enableCallbackDelayed(3);
    try std.testing.expect(delayed_summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 0), delayed_summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), delayed_summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 0), delayed_summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), delayed_summary.delay_budget_count);
    try std.testing.expectEqual(@as(u16, 0), delayed_summary.delayed_event_target_idx);
    try std.testing.expectEqual(@as(u16, 0), delayed_summary.pending_used_chain_count);
    try std.testing.expect(!delayed_summary.should_poll);

    disable_summary = try ring.disableCallback(3);
    try std.testing.expectEqual(@as(u16, 0), disable_summary.pending_used_chain_count);
    try std.testing.expect(!disable_summary.should_poll);
}
