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
