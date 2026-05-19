const std = @import("std");
const virtio_ring = @import("virtio_ring");

test "phase10 virtio ring notification-data replay keeps split and packed next-avail state explicit" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(1, 8, .split, true, false);
    try ring.defineQueue(2, 8, .packed_ring, false, true);

    try ring.publishDescriptorChain(1);
    try ring.publishDescriptorChain(1);
    const split_summary = try ring.notificationDataSummary(1);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", split_summary.anchor);
    try std.testing.expectEqual(@as(u16, 1), split_summary.queue_index);
    try std.testing.expectEqual(virtio_ring.QueueLayout.split, split_summary.layout);
    try std.testing.expectEqual(@as(u16, 2), split_summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 2), split_summary.next_avail_idx);
    try std.testing.expect(!split_summary.next_avail_wrap_counter);
    try std.testing.expectEqual(@as(u16, 2), split_summary.encoded_next);
    try std.testing.expectEqual(@as(u32, 0x0002_0001), split_summary.notification_data);

    inline for (0..8) |_| {
        try ring.publishDescriptorChain(2);
    }
    _ = try ring.prepareKick(2);
    try ring.recordUsedChains(2, 8);
    _ = try ring.pollUsedBuffers(2);
    try ring.publishDescriptorChain(2);

    const packed_summary = try ring.notificationDataSummary(2);
    try std.testing.expectEqual(virtio_ring.QueueLayout.packed_ring, packed_summary.layout);
    try std.testing.expectEqual(@as(u16, 9), packed_summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 1), packed_summary.next_avail_idx);
    try std.testing.expect(packed_summary.next_avail_wrap_counter);
    try std.testing.expectEqual(
        @as(u16, virtio_ring.packed_notification_wrap_bit | 1),
        packed_summary.encoded_next,
    );
    try std.testing.expectEqual(@as(u32, 0x8001_0002), packed_summary.notification_data);
}

test "phase10 virtio ring reset-readiness replay orders blockers before a clean queue reset" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(5, 8, .packed_ring, true, true);

    var readiness = try ring.queueResetReadinessSummary(5);
    try std.testing.expect(readiness.reset_ready);
    try std.testing.expect(readiness.blocker == null);

    try ring.publishDescriptorChain(5);
    readiness = try ring.queueResetReadinessSummary(5);
    try std.testing.expect(!readiness.reset_ready);
    try std.testing.expectEqualStrings("unpublished_chains", @tagName(readiness.blocker.?));
    try std.testing.expectEqual(@as(u16, 1), readiness.unpublished_chain_count);

    const kick = try ring.prepareKick(5);
    try std.testing.expect(kick.needs_kick);
    try std.testing.expectEqual(@as(usize, 1), kick.notification_count);

    readiness = try ring.queueResetReadinessSummary(5);
    try std.testing.expect(!readiness.reset_ready);
    try std.testing.expectEqualStrings("outstanding_chains", @tagName(readiness.blocker.?));
    try std.testing.expectEqual(@as(u16, 1), readiness.outstanding_chain_count);

    try ring.recordUsedChains(5, 1);
    readiness = try ring.queueResetReadinessSummary(5);
    try std.testing.expect(!readiness.reset_ready);
    try std.testing.expectEqualStrings("unpolled_used_chains", @tagName(readiness.blocker.?));
    try std.testing.expectEqual(@as(u16, 1), readiness.pending_used_chain_count);

    const poll = try ring.pollUsedBuffers(5);
    try std.testing.expect(poll.has_newly_used_chains);
    try std.testing.expectEqual(@as(u16, 1), poll.newly_used_chain_count);

    readiness = try ring.queueResetReadinessSummary(5);
    try std.testing.expect(readiness.reset_ready);
    try std.testing.expect(readiness.blocker == null);

    const reset = try ring.resetQueue(5);
    try std.testing.expectEqual(virtio_ring.QueueLayout.packed_ring, reset.layout);
    try std.testing.expect(reset.callback_enabled);
    try std.testing.expectEqual(@as(u16, 0), reset.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 0), reset.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), reset.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 0), reset.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), reset.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 0), reset.pending_used_chain_count);
    try std.testing.expectEqual(@as(usize, 0), reset.notification_count);
}
