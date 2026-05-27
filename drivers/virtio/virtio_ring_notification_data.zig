const std = @import("std");
const virtio_ring = @import("virtio_ring");

pub const NotificationDataSummary = virtio_ring.NotificationDataSummary;

pub fn summarizeNotificationData(
    ring: *const virtio_ring.VirtioRingLab,
    queue_index: u16,
) !NotificationDataSummary {
    return ring.notificationDataSummary(queue_index);
}

pub fn notificationDataUsesWrapBit(summary: NotificationDataSummary) bool {
    return (summary.encoded_next & virtio_ring.packed_notification_wrap_bit) != 0;
}

pub fn queueIndexMatchesNotificationData(summary: NotificationDataSummary) bool {
    return @as(u16, @truncate(summary.notification_data)) == summary.queue_index;
}

pub fn nextAvailStateMatchesEncoding(summary: NotificationDataSummary) bool {
    const encoded_index = summary.encoded_next & ~virtio_ring.packed_notification_wrap_bit;
    return encoded_index == summary.next_avail_idx and
        notificationDataUsesWrapBit(summary) == summary.next_avail_wrap_counter;
}

fn advancePackedAvailIndexNearWrap(ring: *virtio_ring.VirtioRingLab, queue_index: u16) !void {
    for (0..8191) |_| {
        for (0..8) |_| {
            try ring.publishDescriptorChain(queue_index);
        }
        _ = try ring.prepareKick(queue_index);
        try ring.recordUsedChains(queue_index, 8);
        _ = try ring.pollUsedBuffers(queue_index);
    }

    for (0..7) |_| {
        try ring.publishDescriptorChain(queue_index);
    }
}

test "phase10 virtio ring notification-data wrapper keeps split queue state explicit" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(1, 8, .split, true, false);

    try ring.publishDescriptorChain(1);
    try ring.publishDescriptorChain(1);

    const summary = try summarizeNotificationData(&ring, 1);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, 1), summary.queue_index);
    try std.testing.expectEqual(virtio_ring.QueueLayout.split, summary.layout);
    try std.testing.expectEqual(@as(u16, 8), summary.descriptor_count);
    try std.testing.expectEqual(@as(u16, 2), summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 2), summary.next_avail_idx);
    try std.testing.expect(!summary.next_avail_wrap_counter);
    try std.testing.expectEqual(@as(u16, 2), summary.encoded_next);
    try std.testing.expectEqual(@as(u32, 0x0002_0001), summary.notification_data);
    try std.testing.expect(!notificationDataUsesWrapBit(summary));
    try std.testing.expect(queueIndexMatchesNotificationData(summary));
    try std.testing.expect(nextAvailStateMatchesEncoding(summary));
}

test "phase10 virtio ring notification-data wrapper keeps packed wrap-bit rollover explicit" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(2, 8, .packed_ring, false, true);

    inline for (0..8) |_| {
        try ring.publishDescriptorChain(2);
    }
    _ = try ring.prepareKick(2);
    try ring.recordUsedChains(2, 8);
    _ = try ring.pollUsedBuffers(2);
    try ring.publishDescriptorChain(2);

    const summary = try summarizeNotificationData(&ring, 2);
    try std.testing.expectEqual(virtio_ring.QueueLayout.packed_ring, summary.layout);
    try std.testing.expectEqual(@as(u16, 8), summary.descriptor_count);
    try std.testing.expectEqual(@as(u16, 9), summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 1), summary.next_avail_idx);
    try std.testing.expect(summary.next_avail_wrap_counter);
    try std.testing.expectEqual(
        @as(u16, virtio_ring.packed_notification_wrap_bit | 1),
        summary.encoded_next,
    );
    try std.testing.expectEqual(@as(u32, 0x8001_0002), summary.notification_data);
    try std.testing.expect(notificationDataUsesWrapBit(summary));
    try std.testing.expect(queueIndexMatchesNotificationData(summary));
    try std.testing.expect(nextAvailStateMatchesEncoding(summary));
}

test "phase10 virtio ring notification-data wrapper preserves packed wrap encoding across u16 rollover" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(4, 8, .packed_ring, true, false);
    try advancePackedAvailIndexNearWrap(&ring, 4);

    var summary = try summarizeNotificationData(&ring, 4);
    try std.testing.expectEqual(@as(u16, std.math.maxInt(u16)), summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 7), summary.next_avail_idx);
    try std.testing.expect(summary.next_avail_wrap_counter);
    try std.testing.expectEqual(
        @as(u16, virtio_ring.packed_notification_wrap_bit | 7),
        summary.encoded_next,
    );
    try std.testing.expectEqual(@as(u32, 0x8007_0004), summary.notification_data);
    try std.testing.expect(notificationDataUsesWrapBit(summary));
    try std.testing.expect(queueIndexMatchesNotificationData(summary));
    try std.testing.expect(nextAvailStateMatchesEncoding(summary));

    try ring.publishDescriptorChain(4);
    summary = try summarizeNotificationData(&ring, 4);
    try std.testing.expectEqual(@as(u16, 0), summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 0), summary.next_avail_idx);
    try std.testing.expect(!summary.next_avail_wrap_counter);
    try std.testing.expectEqual(@as(u16, 0), summary.encoded_next);
    try std.testing.expectEqual(@as(u32, 4), summary.notification_data);
    try std.testing.expect(!notificationDataUsesWrapBit(summary));
    try std.testing.expect(queueIndexMatchesNotificationData(summary));
    try std.testing.expect(nextAvailStateMatchesEncoding(summary));
}

test "phase10 virtio ring notification-data wrapper clears packed wrap state after reset" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(3, 8, .packed_ring, true, false);

    inline for (0..8) |_| {
        try ring.publishDescriptorChain(3);
    }
    _ = try ring.prepareKick(3);
    try ring.recordUsedChains(3, 8);
    _ = try ring.pollUsedBuffers(3);
    try ring.publishDescriptorChain(3);
    _ = try ring.prepareKick(3);
    try ring.recordUsedChains(3, 1);
    _ = try ring.pollUsedBuffers(3);
    _ = try ring.resetQueue(3);

    const summary = try summarizeNotificationData(&ring, 3);
    try std.testing.expectEqual(@as(u16, 0), summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 0), summary.next_avail_idx);
    try std.testing.expect(!summary.next_avail_wrap_counter);
    try std.testing.expectEqual(@as(u16, 0), summary.encoded_next);
    try std.testing.expectEqual(@as(u32, 3), summary.notification_data);
    try std.testing.expect(!notificationDataUsesWrapBit(summary));
    try std.testing.expect(queueIndexMatchesNotificationData(summary));
    try std.testing.expect(nextAvailStateMatchesEncoding(summary));
}
