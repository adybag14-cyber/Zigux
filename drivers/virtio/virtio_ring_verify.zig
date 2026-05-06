const std = @import("std");
const testing = std.testing;
const virtio_ring = @import("virtio_ring.zig");

test "virtio ring reset readiness tracks unpublished, outstanding, and unpolled work" {
    var lab = virtio_ring.VirtioRingLab{};
    try lab.defineQueue(0, 8, .split, true, false);

    var readiness = try lab.queueResetReadinessSummary(0);
    try testing.expect(readiness.reset_ready);
    try testing.expectEqual(@as(?virtio_ring.QueueResetReadinessBlocker, null), readiness.blocker);

    try lab.publishDescriptorChain(0);
    readiness = try lab.queueResetReadinessSummary(0);
    try testing.expect(!readiness.reset_ready);
    try testing.expectEqual(virtio_ring.QueueResetReadinessBlocker.unpublished_chains, readiness.blocker.?);

    const notification = try lab.prepareKick(0);
    try testing.expect(notification.needs_kick);
    try testing.expectEqual(@as(u16, 0), notification.last_used_idx);

    readiness = try lab.queueResetReadinessSummary(0);
    try testing.expect(!readiness.reset_ready);
    try testing.expectEqual(virtio_ring.QueueResetReadinessBlocker.outstanding_chains, readiness.blocker.?);

    try lab.recordUsedChains(0, 1);
    readiness = try lab.queueResetReadinessSummary(0);
    try testing.expect(!readiness.reset_ready);
    try testing.expectEqual(virtio_ring.QueueResetReadinessBlocker.unpolled_used_chains, readiness.blocker.?);

    const poll = try lab.pollUsedBuffers(0);
    try testing.expect(poll.has_newly_used_chains);
    try testing.expectEqual(@as(u16, 1), poll.newly_used_chain_count);

    readiness = try lab.queueResetReadinessSummary(0);
    try testing.expect(readiness.reset_ready);
    try testing.expectEqual(@as(?virtio_ring.QueueResetReadinessBlocker, null), readiness.blocker);

    const reset = try lab.resetQueue(0);
    try testing.expectEqual(@as(u16, 8), reset.descriptor_count);
    try testing.expectEqual(@as(u16, 0), reset.avail_idx_shadow);
    try testing.expectEqual(@as(usize, 0), reset.notification_count);
}

test "virtio ring delayed callback summary reports poll pressure when used work outruns delay budget" {
    var lab = virtio_ring.VirtioRingLab{};
    try lab.defineQueue(2, 16, .packed_ring, false, true);

    inline for (0..8) |_| {
        try lab.publishDescriptorChain(2);
    }
    _ = try lab.prepareKick(2);
    try lab.recordUsedChains(2, 4);
    try lab.disableCallback(2);

    const delayed = try lab.enableCallbackDelayed(2);
    try testing.expect(delayed.callback_enabled);
    try testing.expectEqual(@as(u16, 4), delayed.pending_used_chain_count);
    try testing.expectEqual(@as(u16, 3), delayed.delay_budget_count);
    try testing.expectEqual(@as(u16, 7), delayed.delayed_event_target_idx);
    try testing.expect(delayed.should_poll);
}
