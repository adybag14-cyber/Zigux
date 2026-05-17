const std = @import("std");
const virtio_ring = @import("virtio_ring");

test "phase10 virtio ring reset reuse stays blocked until queue-local reset prerequisites clear and then replays from a clean queue state" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(2, 8, .packed_ring, true, true);

    var readiness = try ring.queueResetReadinessSummary(2);
    try std.testing.expect(readiness.reset_ready);
    try std.testing.expect(readiness.blocker == null);

    try ring.publishDescriptorChain(2);
    readiness = try ring.queueResetReadinessSummary(2);
    try std.testing.expect(!readiness.reset_ready);
    try std.testing.expectEqualStrings("unpublished_chains", @tagName(readiness.blocker.?));
    try std.testing.expectEqual(@as(u16, 1), readiness.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 1), readiness.outstanding_chain_count);

    const first_kick = try ring.prepareKick(2);
    try std.testing.expect(first_kick.needs_kick);
    try std.testing.expectEqual(@as(usize, 1), first_kick.notification_count);

    readiness = try ring.queueResetReadinessSummary(2);
    try std.testing.expect(!readiness.reset_ready);
    try std.testing.expectEqualStrings("outstanding_chains", @tagName(readiness.blocker.?));
    try std.testing.expectEqual(@as(u16, 0), readiness.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 1), readiness.outstanding_chain_count);

    try ring.recordUsedChains(2, 1);
    readiness = try ring.queueResetReadinessSummary(2);
    try std.testing.expect(!readiness.reset_ready);
    try std.testing.expectEqualStrings("unpolled_used_chains", @tagName(readiness.blocker.?));
    try std.testing.expectEqual(@as(u16, 1), readiness.pending_used_chain_count);

    const poll = try ring.pollUsedBuffers(2);
    try std.testing.expect(poll.has_newly_used_chains);
    try std.testing.expectEqual(@as(u16, 1), poll.newly_used_chain_count);

    readiness = try ring.queueResetReadinessSummary(2);
    try std.testing.expect(readiness.reset_ready);
    try std.testing.expect(readiness.blocker == null);

    const reset = try ring.resetQueue(2);
    try std.testing.expectEqual(virtio_ring.QueueLayout.packed_ring, reset.layout);
    try std.testing.expect(reset.callback_enabled);
    try std.testing.expectEqual(@as(u16, 0), reset.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 0), reset.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), reset.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 0), reset.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), reset.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 0), reset.pending_used_chain_count);
    try std.testing.expectEqual(@as(usize, 0), reset.notification_count);

    const after_reset = try ring.notificationSummary(2);
    try std.testing.expectEqual(@as(u16, 0), after_reset.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 0), after_reset.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), after_reset.num_added);
    try std.testing.expectEqual(@as(usize, 0), after_reset.notification_count);
    try std.testing.expect(!after_reset.needs_kick);

    try ring.publishDescriptorChain(2);
    const kick_after_reset = try ring.prepareKick(2);
    try std.testing.expect(kick_after_reset.needs_kick);
    try std.testing.expectEqual(@as(u16, 1), kick_after_reset.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 1), kick_after_reset.outstanding_chain_count);
    try std.testing.expectEqual(@as(usize, 1), kick_after_reset.notification_count);
}
