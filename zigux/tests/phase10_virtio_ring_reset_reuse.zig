const std = @import("std");
const virtio_ring = @import("virtio_ring");

test "phase10 virtio ring explicit clear plus drained reset keeps queue reuse honest" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(2, 8, .packed_ring, true, true);

    const broken_summary = try ring.markBroken(2);
    try std.testing.expect(broken_summary.broken);
    try std.testing.expect(!broken_summary.callback_enabled);
    try std.testing.expectError(error.QueueBroken, ring.publishDescriptorChain(2));

    var readiness = try ring.queueResetReadinessSummary(2);
    try std.testing.expect(!readiness.reset_ready);
    try std.testing.expectEqual(virtio_ring.QueueResetReadinessBlocker.queue_broken, readiness.blocker.?);

    const cleared_summary = try ring.clearBroken(2);
    try std.testing.expect(!cleared_summary.broken);
    try std.testing.expect(!cleared_summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 0), cleared_summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), cleared_summary.pending_used_chain_count);
    try std.testing.expectEqual(@as(u16, 0), cleared_summary.unpublished_chain_count);

    readiness = try ring.queueResetReadinessSummary(2);
    try std.testing.expect(readiness.reset_ready);
    try std.testing.expectEqual(@as(?virtio_ring.QueueResetReadinessBlocker, null), readiness.blocker);

    const reset_summary = try ring.resetQueue(2);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", reset_summary.anchor);
    try std.testing.expect(reset_summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 0), reset_summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 0), reset_summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), reset_summary.pending_used_chain_count);

    const final_broken_summary = try ring.brokenQueueSummary(2);
    try std.testing.expect(!final_broken_summary.broken);
    try std.testing.expect(final_broken_summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 0), final_broken_summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), final_broken_summary.pending_used_chain_count);
    try std.testing.expectEqual(@as(u16, 0), final_broken_summary.unpublished_chain_count);

    try ring.publishDescriptorChain(2);
    const notification_summary = try ring.notificationSummary(2);
    try std.testing.expectEqual(@as(u16, 1), notification_summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 1), notification_summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 1), notification_summary.num_added);
}
