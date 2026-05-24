const std = @import("std");
const virtio_ring = @import("virtio_ring");

test "phase10 virtio ring reset reuse stays blocked until queue-local reset prerequisites clear and then replays from a clean queue state" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(2, 8, .packed_ring, true, true);

    var publish = try ring.queuePublishReadinessSummary(2);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", publish.anchor);
    try std.testing.expect(publish.publish_ready);
    try std.testing.expect(publish.blocker == null);
    try std.testing.expectEqual(@as(u16, 8), publish.available_descriptor_count);
    try std.testing.expectEqual(@as(u16, 0), publish.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 0), publish.outstanding_chain_count);

    var readiness = try ring.queueResetReadinessSummary(2);
    try std.testing.expect(readiness.reset_ready);
    try std.testing.expect(readiness.blocker == null);

    try ring.publishDescriptorChain(2);
    publish = try ring.queuePublishReadinessSummary(2);
    try std.testing.expect(publish.publish_ready);
    try std.testing.expect(publish.blocker == null);
    try std.testing.expectEqual(@as(u16, 1), publish.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 1), publish.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 1), publish.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 7), publish.available_descriptor_count);

    readiness = try ring.queueResetReadinessSummary(2);
    try std.testing.expect(!readiness.reset_ready);
    try std.testing.expectEqualStrings("unpublished_chains", @tagName(readiness.blocker.?));
    try std.testing.expectEqual(@as(u16, 1), readiness.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 1), readiness.outstanding_chain_count);

    const first_kick = try ring.prepareKick(2);
    try std.testing.expect(first_kick.needs_kick);
    try std.testing.expectEqual(@as(usize, 1), first_kick.notification_count);

    publish = try ring.queuePublishReadinessSummary(2);
    try std.testing.expect(publish.publish_ready);
    try std.testing.expect(publish.blocker == null);
    try std.testing.expectEqual(@as(u16, 1), publish.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), publish.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 7), publish.available_descriptor_count);

    readiness = try ring.queueResetReadinessSummary(2);
    try std.testing.expect(!readiness.reset_ready);
    try std.testing.expectEqualStrings("outstanding_chains", @tagName(readiness.blocker.?));
    try std.testing.expectEqual(@as(u16, 0), readiness.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 1), readiness.outstanding_chain_count);

    try ring.recordUsedChains(2, 1);
    publish = try ring.queuePublishReadinessSummary(2);
    try std.testing.expect(publish.publish_ready);
    try std.testing.expect(publish.blocker == null);
    try std.testing.expectEqual(@as(u16, 0), publish.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 8), publish.available_descriptor_count);

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

    publish = try ring.queuePublishReadinessSummary(2);
    try std.testing.expect(publish.publish_ready);
    try std.testing.expect(publish.blocker == null);
    try std.testing.expectEqual(@as(u16, 0), publish.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 0), publish.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), publish.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 8), publish.available_descriptor_count);

    const after_reset = try ring.notificationSummary(2);
    try std.testing.expectEqual(@as(u16, 0), after_reset.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 0), after_reset.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), after_reset.num_added);
    try std.testing.expectEqual(@as(usize, 0), after_reset.notification_count);
    try std.testing.expect(!after_reset.needs_kick);

    try ring.publishDescriptorChain(2);
    publish = try ring.queuePublishReadinessSummary(2);
    try std.testing.expect(publish.publish_ready);
    try std.testing.expect(publish.blocker == null);
    try std.testing.expectEqual(@as(u16, 1), publish.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 1), publish.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 7), publish.available_descriptor_count);

    const kick_after_reset = try ring.prepareKick(2);
    try std.testing.expect(kick_after_reset.needs_kick);
    try std.testing.expectEqual(@as(u16, 1), kick_after_reset.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 1), kick_after_reset.outstanding_chain_count);
    try std.testing.expectEqual(@as(usize, 1), kick_after_reset.notification_count);

    publish = try ring.queuePublishReadinessSummary(2);
    try std.testing.expect(publish.publish_ready);
    try std.testing.expect(publish.blocker == null);
    try std.testing.expectEqual(@as(u16, 1), publish.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), publish.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 7), publish.available_descriptor_count);
}

test "phase10 virtio ring reset reuse refuses broken queues until the broken fence is cleared" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(3, 8, .split, true, false);

    _ = try ring.markBroken(3);

    var readiness = try ring.queueResetReadinessSummary(3);
    try std.testing.expect(!readiness.reset_ready);
    try std.testing.expect(readiness.broken);
    try std.testing.expect(!readiness.callback_enabled);
    try std.testing.expectEqualStrings("queue_broken", @tagName(readiness.blocker.?));
    try std.testing.expectEqual(@as(u16, 0), readiness.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 0), readiness.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), readiness.pending_used_chain_count);

    try std.testing.expectError(error.QueueResetWhileBroken, ring.resetQueue(3));

    const cleared = try ring.clearBroken(3);
    try std.testing.expect(!cleared.broken);
    try std.testing.expect(!cleared.callback_enabled);
    try std.testing.expectEqual(@as(u16, 0), cleared.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), cleared.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 0), cleared.pending_used_chain_count);

    readiness = try ring.queueResetReadinessSummary(3);
    try std.testing.expect(readiness.reset_ready);
    try std.testing.expect(!readiness.broken);
    try std.testing.expect(readiness.blocker == null);

    const reset = try ring.resetQueue(3);
    try std.testing.expectEqual(virtio_ring.QueueLayout.split, reset.layout);
    try std.testing.expect(reset.callback_enabled);
    try std.testing.expectEqual(@as(u16, 0), reset.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 0), reset.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), reset.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 0), reset.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), reset.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 0), reset.pending_used_chain_count);
}

test "phase10 virtio ring reset reuse clears packed notification wrap state after rollover" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(4, 8, .packed_ring, true, false);

    inline for (0..8) |_| {
        try ring.publishDescriptorChain(4);
    }
    _ = try ring.prepareKick(4);
    try ring.recordUsedChains(4, 8);
    _ = try ring.pollUsedBuffers(4);
    try ring.publishDescriptorChain(4);

    var notification_data = try ring.notificationDataSummary(4);
    try std.testing.expectEqual(@as(u16, 9), notification_data.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 1), notification_data.next_avail_idx);
    try std.testing.expect(notification_data.next_avail_wrap_counter);
    try std.testing.expectEqual(
        @as(u16, virtio_ring.packed_notification_wrap_bit | 1),
        notification_data.encoded_next,
    );
    try std.testing.expectEqual(@as(u32, 0x8001_0004), notification_data.notification_data);

    var readiness = try ring.queueResetReadinessSummary(4);
    try std.testing.expectEqualStrings("unpublished_chains", @tagName(readiness.blocker.?));
    _ = try ring.prepareKick(4);
    readiness = try ring.queueResetReadinessSummary(4);
    try std.testing.expectEqualStrings("outstanding_chains", @tagName(readiness.blocker.?));

    try ring.recordUsedChains(4, 1);
    readiness = try ring.queueResetReadinessSummary(4);
    try std.testing.expectEqualStrings("unpolled_used_chains", @tagName(readiness.blocker.?));
    _ = try ring.pollUsedBuffers(4);

    const reset = try ring.resetQueue(4);
    try std.testing.expectEqual(virtio_ring.QueueLayout.packed_ring, reset.layout);
    try std.testing.expectEqual(@as(u16, 0), reset.avail_idx_shadow);
    try std.testing.expectEqual(@as(usize, 0), reset.notification_count);

    notification_data = try ring.notificationDataSummary(4);
    try std.testing.expectEqual(@as(u16, 0), notification_data.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 0), notification_data.next_avail_idx);
    try std.testing.expect(!notification_data.next_avail_wrap_counter);
    try std.testing.expectEqual(@as(u16, 0), notification_data.encoded_next);
    try std.testing.expectEqual(@as(u32, 4), notification_data.notification_data);
}
