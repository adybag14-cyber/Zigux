const std = @import("std");
const virtio_ring = @import("virtio_ring");

test "phase10 virtio ring broken-queue coverage kicks published work before used accounting and keeps notification history visible" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(3, 8, .split, true, false);
    try ring.disableCallback(3);
    try ring.publishDescriptorChain(3);
    const first_kick = try ring.prepareKick(3);
    try std.testing.expect(first_kick.needs_kick);
    try std.testing.expectEqual(@as(u16, 1), first_kick.num_added);
    try std.testing.expectEqual(@as(usize, 1), first_kick.notification_count);
    try ring.recordUsedChains(3, 1);
    const broken_summary = try ring.markBroken(3);
    try std.testing.expect(broken_summary.broken);
    try std.testing.expect(!broken_summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 1), broken_summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), broken_summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 0), broken_summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), broken_summary.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 1), broken_summary.pending_used_chain_count);
    try std.testing.expectError(error.QueueBroken, ring.publishDescriptorChain(3));
    try std.testing.expectError(error.QueueBroken, ring.prepareKick(3));
    try std.testing.expectError(error.QueueBroken, ring.pollUsedBuffers(3));
    try std.testing.expectError(error.QueueBroken, ring.enableCallback(3));
    try std.testing.expectError(error.QueueBroken, ring.enableCallbackDelayed(3));
    try std.testing.expectError(error.QueueResetWhileBroken, ring.resetQueue(3));
    const summary_while_broken = try ring.notificationSummary(3);
    try std.testing.expectEqual(@as(u16, 0), summary_while_broken.num_added);
    try std.testing.expectEqual(@as(usize, 1), summary_while_broken.notification_count);
    const cleared_summary = try ring.clearBroken(3);
    try std.testing.expect(!cleared_summary.broken);
    try std.testing.expect(!cleared_summary.callback_enabled);
    try ring.publishDescriptorChain(3);
    const second_kick = try ring.prepareKick(3);
    try std.testing.expect(second_kick.needs_kick);
    try std.testing.expectEqual(@as(u16, 1), second_kick.num_added);
    try std.testing.expectEqual(@as(usize, 2), second_kick.notification_count);
}

test "phase10 virtio ring broken queues reject used accounting so clearBroken cannot hide outstanding debt" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(4, 8, .packed_ring, true, false);
    try ring.publishDescriptorChain(4);
    _ = try ring.prepareKick(4);

    const broken = try ring.markBroken(4);
    try std.testing.expect(broken.broken);
    try std.testing.expectEqual(@as(u16, 1), broken.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), broken.pending_used_chain_count);

    try std.testing.expectError(error.QueueBroken, ring.recordUsedChains(4, 1));

    const summary_while_broken = try ring.brokenQueueSummary(4);
    try std.testing.expect(summary_while_broken.broken);
    try std.testing.expectEqual(@as(u16, 1), summary_while_broken.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), summary_while_broken.pending_used_chain_count);

    const cleared = try ring.clearBroken(4);
    try std.testing.expect(!cleared.broken);
    try std.testing.expectEqual(@as(u16, 1), cleared.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), cleared.pending_used_chain_count);

    const readiness = try ring.queueResetReadinessSummary(4);
    try std.testing.expect(!readiness.reset_ready);
    try std.testing.expectEqualStrings("outstanding_chains", @tagName(readiness.blocker.?));
    try std.testing.expectEqual(@as(u16, 1), readiness.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), readiness.pending_used_chain_count);
}

test "phase10 virtio ring clearBroken exposes the next reset blocker across unpublished outstanding and unpolled debt" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(4, 8, .split, true, false);
    try ring.defineQueue(5, 8, .packed_ring, true, false);
    try ring.defineQueue(6, 8, .split, true, false);

    try ring.publishDescriptorChain(4);
    try ring.publishDescriptorChain(4);
    _ = try ring.markBroken(4);
    const cleared_unpublished = try ring.clearBroken(4);
    try std.testing.expect(!cleared_unpublished.broken);
    try std.testing.expectEqual(@as(u16, 2), cleared_unpublished.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 2), cleared_unpublished.outstanding_chain_count);
    var readiness = try ring.queueResetReadinessSummary(4);
    try std.testing.expect(!readiness.reset_ready);
    try std.testing.expectEqualStrings("unpublished_chains", @tagName(readiness.blocker.?));
    try std.testing.expectEqual(@as(u16, 2), readiness.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 2), readiness.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), readiness.pending_used_chain_count);

    try ring.publishDescriptorChain(5);
    _ = try ring.prepareKick(5);
    _ = try ring.markBroken(5);
    const cleared_outstanding = try ring.clearBroken(5);
    try std.testing.expect(!cleared_outstanding.broken);
    try std.testing.expectEqual(@as(u16, 0), cleared_outstanding.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 1), cleared_outstanding.outstanding_chain_count);
    readiness = try ring.queueResetReadinessSummary(5);
    try std.testing.expect(!readiness.reset_ready);
    try std.testing.expectEqualStrings("outstanding_chains", @tagName(readiness.blocker.?));
    try std.testing.expectEqual(@as(u16, 0), readiness.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 1), readiness.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), readiness.pending_used_chain_count);

    try ring.publishDescriptorChain(6);
    _ = try ring.prepareKick(6);
    try ring.recordUsedChains(6, 1);
    _ = try ring.markBroken(6);
    const cleared_unpolled = try ring.clearBroken(6);
    try std.testing.expect(!cleared_unpolled.broken);
    try std.testing.expectEqual(@as(u16, 0), cleared_unpolled.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 0), cleared_unpolled.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 1), cleared_unpolled.pending_used_chain_count);
    readiness = try ring.queueResetReadinessSummary(6);
    try std.testing.expect(!readiness.reset_ready);
    try std.testing.expectEqualStrings("unpolled_used_chains", @tagName(readiness.blocker.?));
    try std.testing.expectEqual(@as(u16, 0), readiness.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 0), readiness.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 1), readiness.pending_used_chain_count);
}
