const std = @import("std");
const virtio_ring = @import("virtio_ring");

test "phase10 virtio ring descriptor stays anchored to virtio_ring.c" {
    const descriptor = virtio_ring.VirtioRingLab.descriptor();

    try std.testing.expectEqualStrings("virtio_ring_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_lab_validation);
    try std.testing.expect(!descriptor.touches_transport_mmio);
    try std.testing.expect(!descriptor.touches_dma_paths);
}

test "phase10 virtio ring validates queue bounds before any transport work" {
    var ring = virtio_ring.VirtioRingLab{};

    try std.testing.expectError(error.EmptyDescriptorCount, ring.defineQueue(0, 0, .split, false, false));
    try std.testing.expectError(error.DescriptorCountMustBePowerOfTwo, ring.defineQueue(0, 3, .split, false, false));
    try std.testing.expectError(error.DescriptorCountTooLarge, ring.defineQueue(0, virtio_ring.max_descriptor_count + 1, .split, false, false));
    try std.testing.expectError(error.QueueIndexOutOfRange, ring.defineQueue(virtio_ring.queue_capacity, 8, .split, false, false));

    try ring.defineQueue(0, 8, .split, true, false);
    try std.testing.expectEqual(@as(usize, 1), ring.registeredQueueCount());
    try std.testing.expectError(error.QueueAlreadyDefined, ring.defineQueue(0, 8, .packed_ring, false, true));
}

test "phase10 virtio ring refuses reset while unpublished outstanding or unpolled work remains" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(1, 8, .split, true, false);

    try ring.publishDescriptorChain(1);
    try std.testing.expectError(error.QueueResetHasUnpublishedChains, ring.resetQueue(1));

    _ = try ring.prepareKick(1);
    try std.testing.expectError(error.QueueResetHasOutstandingChains, ring.resetQueue(1));

    try ring.recordUsedChains(1, 1);
    try std.testing.expectError(error.QueueResetHasUnpolledUsedChains, ring.resetQueue(1));
}

test "phase10 virtio ring reset clears queue bookkeeping but preserves queue shape for reuse" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(2, 16, .packed_ring, false, true);

    try ring.publishDescriptorChain(2);
    _ = try ring.prepareKick(2);
    try ring.recordUsedChains(2, 1);
    _ = try ring.pollUsedBuffers(2);
    try ring.disableCallback(2);

    const reset_summary = try ring.resetQueue(2);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", reset_summary.anchor);
    try std.testing.expectEqual(@as(u16, 2), reset_summary.queue_index);
    try std.testing.expectEqual(@as(u16, 16), reset_summary.descriptor_count);
    try std.testing.expectEqual(virtio_ring.QueueLayout.packed_ring, reset_summary.layout);
    try std.testing.expect(!reset_summary.uses_event_idx);
    try std.testing.expect(reset_summary.uses_indirect_descriptors);
    try std.testing.expect(reset_summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 0), reset_summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 0), reset_summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), reset_summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 0), reset_summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), reset_summary.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 0), reset_summary.pending_used_chain_count);
    try std.testing.expectEqual(@as(usize, 0), reset_summary.notification_count);

    const shape_summary = try ring.queueShapeSummary(2);
    try std.testing.expectEqual(@as(u16, 16), shape_summary.descriptor_count);
    try std.testing.expectEqual(virtio_ring.QueueLayout.packed_ring, shape_summary.layout);
    try std.testing.expect(shape_summary.uses_indirect_descriptors);

    const notification_summary = try ring.notificationSummary(2);
    try std.testing.expectEqual(@as(u16, 0), notification_summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 0), notification_summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), notification_summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), notification_summary.num_added);
    try std.testing.expectEqual(@as(usize, 0), notification_summary.notification_count);
    try std.testing.expect(!notification_summary.needs_kick);

    try ring.publishDescriptorChain(2);
    const kick_summary = try ring.prepareKick(2);
    try std.testing.expect(kick_summary.needs_kick);
    try std.testing.expectEqual(@as(u16, 1), kick_summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(usize, 1), kick_summary.notification_count);
}

test "phase10 virtio ring blocks publish, kick, poll, and callback snapshots while a queue is broken" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(3, 8, .split, true, false);

    try ring.disableCallback(3);
    try ring.publishDescriptorChain(3);
    try ring.recordUsedChains(3, 1);

    var broken_summary = try ring.markBroken(3);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", broken_summary.anchor);
    try std.testing.expectEqual(@as(u16, 3), broken_summary.queue_index);
    try std.testing.expect(broken_summary.broken);
    try std.testing.expect(!broken_summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 1), broken_summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), broken_summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 0), broken_summary.outstanding_chain_count);

    try std.testing.expectError(error.QueueBroken, ring.publishDescriptorChain(3));
    try std.testing.expectError(error.QueueBroken, ring.prepareKick(3));
    try std.testing.expectError(error.QueueBroken, ring.pollUsedBuffers(3));
    try std.testing.expectError(error.QueueBroken, ring.enableCallback(3));
    try std.testing.expectError(error.QueueBroken, ring.enableCallbackDelayed(3));
    try std.testing.expectError(error.QueueResetWhileBroken, ring.resetQueue(3));

    const summary_while_broken = try ring.notificationSummary(3);
    try std.testing.expectEqual(@as(u16, 1), summary_while_broken.num_added);
    try std.testing.expectEqual(@as(usize, 0), summary_while_broken.notification_count);

    broken_summary = try ring.clearBroken(3);
    try std.testing.expect(!broken_summary.broken);
    try std.testing.expect(!broken_summary.callback_enabled);

    try ring.publishDescriptorChain(3);
    const kick_summary = try ring.prepareKick(3);
    try std.testing.expect(kick_summary.needs_kick);
    try std.testing.expectEqual(@as(u16, 2), kick_summary.num_added);
    try std.testing.expectEqual(@as(usize, 1), kick_summary.notification_count);

    const poll_summary = try ring.pollUsedBuffers(3);
    try std.testing.expectEqual(@as(u16, 1), poll_summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), poll_summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 1), poll_summary.newly_used_chain_count);
    try std.testing.expectEqual(@as(u16, 1), poll_summary.outstanding_chain_count);
    try std.testing.expect(poll_summary.has_newly_used_chains);
}

test "phase10 virtio ring delayed callback pacing reports both thresholded and immediate poll cases" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(5, 8, .split, true, false);

    inline for (0..4) |_| {
        try ring.publishDescriptorChain(5);
    }
    _ = try ring.prepareKick(5);

    try ring.recordUsedChains(5, 1);
    try ring.disableCallback(5);

    var delayed = try ring.enableCallbackDelayed(5);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", delayed.anchor);
    try std.testing.expectEqual(@as(u16, 5), delayed.queue_index);
    try std.testing.expect(delayed.callback_enabled);
    try std.testing.expectEqual(@as(u16, 1), delayed.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), delayed.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 3), delayed.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 2), delayed.delay_budget_count);
    try std.testing.expectEqual(@as(u16, 3), delayed.delayed_event_target_idx);
    try std.testing.expectEqual(@as(u16, 1), delayed.pending_used_chain_count);
    try std.testing.expect(!delayed.should_poll);

    try ring.disableCallback(5);
    try ring.recordUsedChains(5, 2);

    delayed = try ring.enableCallbackDelayed(5);
    try std.testing.expect(delayed.callback_enabled);
    try std.testing.expectEqual(@as(u16, 3), delayed.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), delayed.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 1), delayed.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), delayed.delay_budget_count);
    try std.testing.expectEqual(@as(u16, 3), delayed.delayed_event_target_idx);
    try std.testing.expectEqual(@as(u16, 3), delayed.pending_used_chain_count);
    try std.testing.expect(delayed.should_poll);
}

test "phase10 virtio ring callback re-enable reports pending used work and settles after poll" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(6, 8, .split, true, false);

    inline for (0..3) |_| {
        try ring.publishDescriptorChain(6);
    }
    const kick_summary = try ring.prepareKick(6);
    try std.testing.expect(kick_summary.needs_kick);
    try std.testing.expectEqual(@as(u16, 3), kick_summary.num_added);
    try std.testing.expectEqual(@as(usize, 1), kick_summary.notification_count);

    try ring.recordUsedChains(6, 2);
    try ring.disableCallback(6);

    var callback_summary = try ring.enableCallback(6);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", callback_summary.anchor);
    try std.testing.expectEqual(@as(u16, 6), callback_summary.queue_index);
    try std.testing.expect(callback_summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 2), callback_summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), callback_summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 2), callback_summary.pending_used_chain_count);
    try std.testing.expect(callback_summary.should_poll);

    const poll_summary = try ring.pollUsedBuffers(6);
    try std.testing.expectEqual(@as(u16, 2), poll_summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), poll_summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 2), poll_summary.newly_used_chain_count);
    try std.testing.expectEqual(@as(u16, 1), poll_summary.outstanding_chain_count);
    try std.testing.expect(poll_summary.has_newly_used_chains);

    callback_summary = try ring.enableCallback(6);
    try std.testing.expect(callback_summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 2), callback_summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 2), callback_summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 0), callback_summary.pending_used_chain_count);
    try std.testing.expect(!callback_summary.should_poll);
}

test "phase10 virtio ring reset-readiness preflight reports the current queue blocker" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(4, 8, .split, true, false);

    var summary = try ring.queueResetReadinessSummary(4);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, 4), summary.queue_index);
    try std.testing.expect(summary.callback_enabled);
    try std.testing.expect(!summary.broken);
    try std.testing.expectEqual(@as(u16, 0), summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 0), summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 0), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), summary.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 0), summary.pending_used_chain_count);
    try std.testing.expect(summary.reset_ready);
    try std.testing.expectEqual(@as(?virtio_ring.QueueResetReadinessBlocker, null), summary.blocker);

    try ring.publishDescriptorChain(4);
    summary = try ring.queueResetReadinessSummary(4);
    try std.testing.expect(!summary.reset_ready);
    try std.testing.expectEqual(@as(u16, 1), summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 1), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 1), summary.unpublished_chain_count);
    try std.testing.expectEqual(virtio_ring.QueueResetReadinessBlocker.unpublished_chains, summary.blocker.?);

    _ = try ring.prepareKick(4);
    summary = try ring.queueResetReadinessSummary(4);
    try std.testing.expect(!summary.reset_ready);
    try std.testing.expectEqual(@as(u16, 1), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), summary.unpublished_chain_count);
    try std.testing.expectEqual(virtio_ring.QueueResetReadinessBlocker.outstanding_chains, summary.blocker.?);

    try ring.recordUsedChains(4, 1);
    summary = try ring.queueResetReadinessSummary(4);
    try std.testing.expect(!summary.reset_ready);
    try std.testing.expectEqual(@as(u16, 1), summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 1), summary.pending_used_chain_count);
    try std.testing.expectEqual(virtio_ring.QueueResetReadinessBlocker.unpolled_used_chains, summary.blocker.?);

    _ = try ring.pollUsedBuffers(4);
    summary = try ring.queueResetReadinessSummary(4);
    try std.testing.expect(summary.reset_ready);
    try std.testing.expectEqual(@as(u16, 0), summary.pending_used_chain_count);
    try std.testing.expectEqual(@as(?virtio_ring.QueueResetReadinessBlocker, null), summary.blocker);

    _ = try ring.markBroken(4);
    summary = try ring.queueResetReadinessSummary(4);
    try std.testing.expect(!summary.callback_enabled);
    try std.testing.expect(summary.broken);
    try std.testing.expect(!summary.reset_ready);
    try std.testing.expectEqual(virtio_ring.QueueResetReadinessBlocker.queue_broken, summary.blocker.?);
}
