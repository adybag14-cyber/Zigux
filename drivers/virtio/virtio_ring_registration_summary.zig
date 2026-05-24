const std = @import("std");
const virtio_ring = @import("virtio_ring");

pub const QueueRegistrationSummary = virtio_ring.QueueRegistrationSummary;

pub fn summarizeQueueRegistration(
    ring: *const virtio_ring.VirtioRingLab,
    queue_index: u16,
) !QueueRegistrationSummary {
    return ring.queueRegistrationSummary(queue_index);
}

pub fn summarizeRegisteredQueueCount(ring: *const virtio_ring.VirtioRingLab) usize {
    return ring.registeredQueueCount();
}

pub fn queueDefinitionDisciplineStable(
    summary: QueueRegistrationSummary,
    expected_registered_queue_count: usize,
) bool {
    return summary.registered_queue_count == expected_registered_queue_count;
}

test "phase10 virtio ring registration-summary wrapper keeps definition discipline explicit" {
    var ring = virtio_ring.VirtioRingLab{};
    try std.testing.expectEqual(@as(usize, 0), summarizeRegisteredQueueCount(&ring));
    try std.testing.expectError(error.QueueNotDefined, summarizeQueueRegistration(&ring, 0));

    try std.testing.expectError(error.EmptyDescriptorCount, ring.defineQueue(0, 0, .split, true, false));
    try std.testing.expectEqual(@as(usize, 0), summarizeRegisteredQueueCount(&ring));
    try std.testing.expectError(
        error.DescriptorCountMustBePowerOfTwo,
        ring.defineQueue(0, 6, .split, true, false),
    );
    try std.testing.expectEqual(@as(usize, 0), summarizeRegisteredQueueCount(&ring));
    try std.testing.expectError(
        error.QueueIndexOutOfRange,
        ring.defineQueue(virtio_ring.queue_capacity, 8, .split, true, false),
    );
    try std.testing.expectEqual(@as(usize, 0), summarizeRegisteredQueueCount(&ring));

    try ring.defineQueue(0, 8, .split, true, false);
    var summary = try summarizeQueueRegistration(&ring, 0);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, 0), summary.queue_index);
    try std.testing.expectEqual(@as(u16, 8), summary.descriptor_count);
    try std.testing.expectEqual(virtio_ring.QueueLayout.split, summary.layout);
    try std.testing.expect(summary.uses_event_idx);
    try std.testing.expect(!summary.uses_indirect_descriptors);
    try std.testing.expect(queueDefinitionDisciplineStable(summary, 1));
    try std.testing.expectEqual(@as(usize, 1), summarizeRegisteredQueueCount(&ring));

    try ring.defineQueue(2, 16, .packed_ring, false, true);
    summary = try summarizeQueueRegistration(&ring, 2);
    try std.testing.expectEqual(@as(u16, 2), summary.queue_index);
    try std.testing.expectEqual(@as(u16, 16), summary.descriptor_count);
    try std.testing.expectEqual(virtio_ring.QueueLayout.packed_ring, summary.layout);
    try std.testing.expect(!summary.uses_event_idx);
    try std.testing.expect(summary.uses_indirect_descriptors);
    try std.testing.expect(queueDefinitionDisciplineStable(summary, 2));
    try std.testing.expectEqual(@as(usize, 2), summarizeRegisteredQueueCount(&ring));

    try std.testing.expectError(error.QueueAlreadyDefined, ring.defineQueue(2, 16, .packed_ring, false, true));
    try std.testing.expectEqual(@as(usize, 2), summarizeRegisteredQueueCount(&ring));
    try std.testing.expectError(error.QueueNotDefined, summarizeQueueRegistration(&ring, 1));
}

test "phase10 virtio ring registration-summary wrapper stays queue-local across noncontiguous queue definitions" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(1, 8, .split, false, false);
    try ring.defineQueue(7, 32, .packed_ring, true, true);

    const first = try summarizeQueueRegistration(&ring, 1);
    try std.testing.expectEqual(@as(u16, 1), first.queue_index);
    try std.testing.expectEqual(@as(u16, 8), first.descriptor_count);
    try std.testing.expectEqual(virtio_ring.QueueLayout.split, first.layout);
    try std.testing.expect(!first.uses_event_idx);
    try std.testing.expect(!first.uses_indirect_descriptors);
    try std.testing.expect(queueDefinitionDisciplineStable(first, 2));

    const last = try summarizeQueueRegistration(&ring, 7);
    try std.testing.expectEqual(@as(u16, 7), last.queue_index);
    try std.testing.expectEqual(@as(u16, 32), last.descriptor_count);
    try std.testing.expectEqual(virtio_ring.QueueLayout.packed_ring, last.layout);
    try std.testing.expect(last.uses_event_idx);
    try std.testing.expect(last.uses_indirect_descriptors);
    try std.testing.expect(queueDefinitionDisciplineStable(last, 2));
    try std.testing.expectEqual(@as(usize, 2), summarizeRegisteredQueueCount(&ring));
}
