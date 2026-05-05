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

test "phase10 virtio ring records queue shape metadata for split and packed layouts" {
    var ring = virtio_ring.VirtioRingLab{};

    try ring.defineQueue(1, 16, .split, true, false);
    try ring.defineQueue(2, 32, .packed_ring, false, true);

    const split_shape = try ring.queueShapeSummary(1);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", split_shape.anchor);
    try std.testing.expectEqual(@as(u16, 16), split_shape.descriptor_count);
    try std.testing.expectEqual(virtio_ring.QueueLayout.split, split_shape.layout);
    try std.testing.expect(split_shape.uses_event_idx);
    try std.testing.expect(!split_shape.uses_indirect_descriptors);

    const packed_shape = try ring.queueShapeSummary(2);
    try std.testing.expectEqual(virtio_ring.QueueLayout.packed_ring, packed_shape.layout);
    try std.testing.expect(!packed_shape.uses_event_idx);
    try std.testing.expect(packed_shape.uses_indirect_descriptors);
}

test "phase10 virtio ring keeps avail and notify bookkeeping in memory only" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(3, 4, .split, true, false);

    try ring.publishDescriptorChain(3);
    try ring.publishDescriptorChain(3);

    var summary = try ring.notificationSummary(3);
    try std.testing.expectEqual(@as(u16, 2), summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 2), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 2), summary.num_added);
    try std.testing.expect(summary.needs_kick);
    try std.testing.expectEqual(@as(usize, 0), summary.notification_count);

    summary = try ring.prepareKick(3);
    try std.testing.expect(summary.needs_kick);
    try std.testing.expectEqual(@as(u16, 2), summary.num_added);
    try std.testing.expectEqual(@as(usize, 1), summary.notification_count);

    summary = try ring.notificationSummary(3);
    try std.testing.expectEqual(@as(u16, 0), summary.num_added);
    try std.testing.expect(!summary.needs_kick);
    try std.testing.expectEqual(@as(usize, 1), summary.notification_count);

    summary = try ring.prepareKick(3);
    try std.testing.expect(!summary.needs_kick);
    try std.testing.expectEqual(@as(usize, 1), summary.notification_count);
}

test "phase10 virtio ring rejects queue overflow and used batches beyond outstanding chains" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(4, 2, .packed_ring, false, true);

    try ring.publishDescriptorChain(4);
    try ring.publishDescriptorChain(4);
    try std.testing.expectError(error.QueueFull, ring.publishDescriptorChain(4));

    try std.testing.expectError(error.EmptyUsedBatch, ring.recordUsedChains(4, 0));
    try std.testing.expectError(error.UsedBatchExceedsOutstanding, ring.recordUsedChains(4, 3));

    try ring.recordUsedChains(4, 1);
    const summary = try ring.notificationSummary(4);
    try std.testing.expectEqual(@as(u16, 1), summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 1), summary.outstanding_chain_count);
}

test "phase10 virtio ring polls newly used buffers without transport callbacks" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(5, 8, .split, true, false);

    var poll_summary = try ring.pollUsedBuffers(5);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", poll_summary.anchor);
    try std.testing.expectEqual(@as(u16, 0), poll_summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), poll_summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 0), poll_summary.newly_used_chain_count);
    try std.testing.expectEqual(@as(u16, 0), poll_summary.outstanding_chain_count);
    try std.testing.expect(!poll_summary.has_newly_used_chains);

    try ring.publishDescriptorChain(5);
    try ring.publishDescriptorChain(5);
    try ring.recordUsedChains(5, 1);

    poll_summary = try ring.pollUsedBuffers(5);
    try std.testing.expectEqual(@as(u16, 1), poll_summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), poll_summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 1), poll_summary.newly_used_chain_count);
    try std.testing.expectEqual(@as(u16, 1), poll_summary.outstanding_chain_count);
    try std.testing.expect(poll_summary.has_newly_used_chains);

    poll_summary = try ring.pollUsedBuffers(5);
    try std.testing.expectEqual(@as(u16, 1), poll_summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 1), poll_summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 0), poll_summary.newly_used_chain_count);
    try std.testing.expectEqual(@as(u16, 1), poll_summary.outstanding_chain_count);
    try std.testing.expect(!poll_summary.has_newly_used_chains);

    try ring.recordUsedChains(5, 1);
    poll_summary = try ring.pollUsedBuffers(5);
    try std.testing.expectEqual(@as(u16, 2), poll_summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 1), poll_summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 1), poll_summary.newly_used_chain_count);
    try std.testing.expectEqual(@as(u16, 0), poll_summary.outstanding_chain_count);
    try std.testing.expect(poll_summary.has_newly_used_chains);
}

test "phase10 virtio ring re-enables callbacks and reports whether polling is still needed" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(6, 8, .split, true, false);

    try ring.disableCallback(6);
    try ring.publishDescriptorChain(6);
    try ring.recordUsedChains(6, 1);

    var enable_summary = try ring.enableCallback(6);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", enable_summary.anchor);
    try std.testing.expectEqual(@as(u16, 6), enable_summary.queue_index);
    try std.testing.expect(enable_summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 1), enable_summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), enable_summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 1), enable_summary.pending_used_chain_count);
    try std.testing.expect(enable_summary.should_poll);

    _ = try ring.pollUsedBuffers(6);
    try ring.disableCallback(6);

    enable_summary = try ring.enableCallback(6);
    try std.testing.expect(enable_summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 1), enable_summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 1), enable_summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 0), enable_summary.pending_used_chain_count);
    try std.testing.expect(!enable_summary.should_poll);
}

test "phase10 virtio ring delays callbacks until most outstanding buffers are consumed" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(7, 8, .split, true, false);

    try ring.disableCallback(7);
    try ring.publishDescriptorChain(7);
    try ring.publishDescriptorChain(7);
    try ring.publishDescriptorChain(7);
    try ring.publishDescriptorChain(7);
    try ring.recordUsedChains(7, 1);

    var delayed_summary = try ring.enableCallbackDelayed(7);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", delayed_summary.anchor);
    try std.testing.expectEqual(@as(u16, 7), delayed_summary.queue_index);
    try std.testing.expect(delayed_summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 1), delayed_summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), delayed_summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 3), delayed_summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 2), delayed_summary.delay_budget_count);
    try std.testing.expectEqual(@as(u16, 3), delayed_summary.delayed_event_target_idx);
    try std.testing.expectEqual(@as(u16, 1), delayed_summary.pending_used_chain_count);
    try std.testing.expect(!delayed_summary.should_poll);

    _ = try ring.pollUsedBuffers(7);
    try ring.disableCallback(7);
    try ring.recordUsedChains(7, 3);

    delayed_summary = try ring.enableCallbackDelayed(7);
    try std.testing.expect(delayed_summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 4), delayed_summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 1), delayed_summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 0), delayed_summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), delayed_summary.delay_budget_count);
    try std.testing.expectEqual(@as(u16, 4), delayed_summary.delayed_event_target_idx);
    try std.testing.expectEqual(@as(u16, 3), delayed_summary.pending_used_chain_count);
    try std.testing.expect(delayed_summary.should_poll);
}

test "phase10 virtio ring blocks poll and callback snapshots while a queue is broken" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(1, 8, .split, true, false);

    try ring.disableCallback(1);
    try ring.publishDescriptorChain(1);
    try ring.recordUsedChains(1, 1);

    var broken_summary = try ring.markBroken(1);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", broken_summary.anchor);
    try std.testing.expectEqual(@as(u16, 1), broken_summary.queue_index);
    try std.testing.expect(broken_summary.broken);
    try std.testing.expect(!broken_summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 1), broken_summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), broken_summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 0), broken_summary.outstanding_chain_count);

    try std.testing.expectError(error.QueueBroken, ring.pollUsedBuffers(1));
    try std.testing.expectError(error.QueueBroken, ring.enableCallback(1));
    try std.testing.expectError(error.QueueBroken, ring.enableCallbackDelayed(1));

    broken_summary = try ring.clearBroken(1);
    try std.testing.expect(!broken_summary.broken);
    try std.testing.expect(!broken_summary.callback_enabled);

    const poll_summary = try ring.pollUsedBuffers(1);
    try std.testing.expectEqual(@as(u16, 1), poll_summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), poll_summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 1), poll_summary.newly_used_chain_count);
    try std.testing.expectEqual(@as(u16, 0), poll_summary.outstanding_chain_count);
    try std.testing.expect(poll_summary.has_newly_used_chains);
}

test "phase10 virtio ring wraps avail used and poll bookkeeping at u16 boundaries" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(0, 1, .split, true, false);

    var iteration: usize = 0;
    while (iteration < std.math.maxInt(u16)) : (iteration += 1) {
        try ring.publishDescriptorChain(0);
        _ = try ring.prepareKick(0);
        try ring.recordUsedChains(0, 1);
        _ = try ring.pollUsedBuffers(0);
    }

    try ring.publishDescriptorChain(0);
    _ = try ring.prepareKick(0);
    try ring.recordUsedChains(0, 1);

    var poll_summary = try ring.pollUsedBuffers(0);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", poll_summary.anchor);
    try std.testing.expectEqual(@as(u16, 0), poll_summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, std.math.maxInt(u16)), poll_summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 1), poll_summary.newly_used_chain_count);
    try std.testing.expectEqual(@as(u16, 0), poll_summary.outstanding_chain_count);
    try std.testing.expect(poll_summary.has_newly_used_chains);

    try ring.publishDescriptorChain(0);
    _ = try ring.prepareKick(0);
    try ring.recordUsedChains(0, 1);

    poll_summary = try ring.pollUsedBuffers(0);
    try std.testing.expectEqual(@as(u16, 1), poll_summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), poll_summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 1), poll_summary.newly_used_chain_count);
    try std.testing.expectEqual(@as(u16, 0), poll_summary.outstanding_chain_count);
    try std.testing.expect(poll_summary.has_newly_used_chains);

    const summary = try ring.notificationSummary(0);
    try std.testing.expectEqual(@as(u16, 1), summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 1), summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), summary.num_added);
    try std.testing.expectEqual(@as(usize, std.math.maxInt(u16) + 2), summary.notification_count);
    try std.testing.expect(!summary.needs_kick);
}
