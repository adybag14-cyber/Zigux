const std = @import("std");
const virtio_ring = @import("../../drivers/virtio/virtio_ring.zig");

test "phase10 virtio ring registration replay keeps noncontiguous queue registration counts explicit" {
    var ring = virtio_ring.VirtioRingLab{};

    try std.testing.expectEqual(@as(usize, 0), ring.registeredQueueCount());
    try std.testing.expectError(error.QueueNotDefined, ring.queueRegistrationSummary(6));

    try ring.defineQueue(1, 8, .split, true, false);
    try ring.defineQueue(6, 32, .packed_ring, false, true);

    const split_summary = try ring.queueRegistrationSummary(1);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", split_summary.anchor);
    try std.testing.expectEqual(@as(u16, 1), split_summary.queue_index);
    try std.testing.expectEqual(@as(u16, 8), split_summary.descriptor_count);
    try std.testing.expectEqual(virtio_ring.QueueLayout.split, split_summary.layout);
    try std.testing.expect(split_summary.uses_event_idx);
    try std.testing.expect(!split_summary.uses_indirect_descriptors);
    try std.testing.expectEqual(@as(usize, 2), split_summary.registered_queue_count);

    const packed_summary = try ring.queueRegistrationSummary(6);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", packed_summary.anchor);
    try std.testing.expectEqual(@as(u16, 6), packed_summary.queue_index);
    try std.testing.expectEqual(@as(u16, 32), packed_summary.descriptor_count);
    try std.testing.expectEqual(virtio_ring.QueueLayout.packed_ring, packed_summary.layout);
    try std.testing.expect(!packed_summary.uses_event_idx);
    try std.testing.expect(packed_summary.uses_indirect_descriptors);
    try std.testing.expectEqual(@as(usize, 2), packed_summary.registered_queue_count);
    try std.testing.expectEqual(@as(usize, 2), ring.registeredQueueCount());
}

test "phase10 virtio ring registration replay keeps failed definitions from inflating queue counts" {
    var ring = virtio_ring.VirtioRingLab{};

    try std.testing.expectError(error.EmptyDescriptorCount, ring.defineQueue(0, 0, .split, true, false));
    try std.testing.expectError(
        error.DescriptorCountMustBePowerOfTwo,
        ring.defineQueue(2, 6, .split, true, false),
    );
    try std.testing.expectError(
        error.QueueIndexOutOfRange,
        ring.defineQueue(virtio_ring.queue_capacity, 8, .split, false, false),
    );
    try std.testing.expectEqual(@as(usize, 0), ring.registeredQueueCount());

    try ring.defineQueue(3, 16, .packed_ring, true, true);
    try std.testing.expectEqual(@as(usize, 1), ring.registeredQueueCount());
    try std.testing.expectError(error.QueueAlreadyDefined, ring.defineQueue(3, 16, .packed_ring, true, true));

    const summary = try ring.queueRegistrationSummary(3);
    try std.testing.expectEqual(@as(u16, 3), summary.queue_index);
    try std.testing.expectEqual(@as(u16, 16), summary.descriptor_count);
    try std.testing.expectEqual(virtio_ring.QueueLayout.packed_ring, summary.layout);
    try std.testing.expect(summary.uses_event_idx);
    try std.testing.expect(summary.uses_indirect_descriptors);
    try std.testing.expectEqual(@as(usize, 1), summary.registered_queue_count);
    try std.testing.expectError(error.QueueNotDefined, ring.queueRegistrationSummary(4));
}

test "phase10 virtio ring registration replay preserves queue definitions across queue-local reset" {
    var ring = virtio_ring.VirtioRingLab{};

    try ring.defineQueue(4, 16, .packed_ring, true, true);
    try ring.publishDescriptorChain(4);
    try ring.publishDescriptorChain(4);
    _ = try ring.prepareKick(4);
    try ring.recordUsedChains(4, 2);
    _ = try ring.pollUsedBuffers(4);

    const reset = try ring.resetQueue(4);
    try std.testing.expectEqual(@as(u16, 4), reset.queue_index);
    try std.testing.expectEqual(@as(u16, 16), reset.descriptor_count);
    try std.testing.expectEqual(virtio_ring.QueueLayout.packed_ring, reset.layout);
    try std.testing.expect(reset.uses_event_idx);
    try std.testing.expect(reset.uses_indirect_descriptors);
    try std.testing.expectEqual(@as(u16, 0), reset.avail_idx_shadow);
    try std.testing.expectEqual(@as(usize, 0), reset.notification_count);

    const summary = try ring.queueRegistrationSummary(4);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, 4), summary.queue_index);
    try std.testing.expectEqual(@as(u16, 16), summary.descriptor_count);
    try std.testing.expectEqual(virtio_ring.QueueLayout.packed_ring, summary.layout);
    try std.testing.expect(summary.uses_event_idx);
    try std.testing.expect(summary.uses_indirect_descriptors);
    try std.testing.expectEqual(@as(usize, 1), summary.registered_queue_count);
    try std.testing.expectEqual(@as(usize, 1), ring.registeredQueueCount());
}

test "phase10 virtio ring registration replay keeps queue definitions stable across broken-queue fencing and recovery" {
    var ring = virtio_ring.VirtioRingLab{};

    try ring.defineQueue(1, 8, .split, false, false);
    try ring.defineQueue(5, 32, .packed_ring, true, true);
    try ring.publishDescriptorChain(5);

    const broken = try ring.markBroken(5);
    try std.testing.expect(broken.broken);
    try std.testing.expect(!broken.callback_enabled);

    var summary = try ring.queueRegistrationSummary(5);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, 5), summary.queue_index);
    try std.testing.expectEqual(@as(u16, 32), summary.descriptor_count);
    try std.testing.expectEqual(virtio_ring.QueueLayout.packed_ring, summary.layout);
    try std.testing.expect(summary.uses_event_idx);
    try std.testing.expect(summary.uses_indirect_descriptors);
    try std.testing.expectEqual(@as(usize, 2), summary.registered_queue_count);
    try std.testing.expectEqual(@as(usize, 2), ring.registeredQueueCount());

    const cleared = try ring.clearBroken(5);
    try std.testing.expect(!cleared.broken);

    summary = try ring.queueRegistrationSummary(5);
    try std.testing.expectEqual(@as(u16, 5), summary.queue_index);
    try std.testing.expectEqual(@as(u16, 32), summary.descriptor_count);
    try std.testing.expectEqual(virtio_ring.QueueLayout.packed_ring, summary.layout);
    try std.testing.expect(summary.uses_event_idx);
    try std.testing.expect(summary.uses_indirect_descriptors);
    try std.testing.expectEqual(@as(usize, 2), summary.registered_queue_count);
    try std.testing.expectEqual(@as(usize, 2), ring.registeredQueueCount());

    const neighbor = try ring.queueRegistrationSummary(1);
    try std.testing.expectEqual(@as(u16, 1), neighbor.queue_index);
    try std.testing.expectEqual(@as(u16, 8), neighbor.descriptor_count);
    try std.testing.expectEqual(virtio_ring.QueueLayout.split, neighbor.layout);
    try std.testing.expect(!neighbor.uses_event_idx);
    try std.testing.expect(!neighbor.uses_indirect_descriptors);
    try std.testing.expectEqual(@as(usize, 2), neighbor.registered_queue_count);
}
