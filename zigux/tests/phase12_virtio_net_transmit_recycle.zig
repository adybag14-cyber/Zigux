const std = @import("std");
const virtio_net_transmit_recycle = @import("virtio_net_transmit_recycle");

test "phase12 virtio net transmit recycle summary stays anchored to virtio_net.c" {
    const summary = try virtio_net_transmit_recycle.summarizeTransmitRecycle(.{
        .in_flight_descriptors = 4,
        .free_descriptors_before = 1,
        .completed_descriptors = 2,
        .wake_threshold = 3,
        .queue_stopped = true,
    });

    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, 4), summary.in_flight_descriptors);
    try std.testing.expectEqual(@as(u16, 2), summary.completed_descriptors);
    try std.testing.expectEqual(@as(u16, 2), summary.recycled_descriptors);
    try std.testing.expectEqual(@as(u16, 1), summary.free_descriptors_before);
    try std.testing.expectEqual(@as(u16, 3), summary.free_descriptors_after);
    try std.testing.expectEqual(@as(u16, 2), summary.remaining_in_flight_descriptors);
    try std.testing.expectEqual(@as(u16, 3), summary.wake_threshold);
    try std.testing.expect(summary.queue_was_stopped);
    try std.testing.expect(summary.reaches_wake_threshold);
    try std.testing.expect(summary.frees_completed_buffers);
    try std.testing.expect(summary.wakes_transmit_queue);
    try std.testing.expect(!summary.keeps_queue_stopped);
    try std.testing.expectEqual(
        virtio_net_transmit_recycle.RecycleDisposition.wake_queue,
        summary.disposition,
    );
}

test "phase12 virtio net transmit recycle keeps a stopped queue parked below the wake threshold" {
    const summary = try virtio_net_transmit_recycle.summarizeTransmitRecycle(.{
        .in_flight_descriptors = 5,
        .free_descriptors_before = 0,
        .completed_descriptors = 1,
        .wake_threshold = 4,
        .queue_stopped = true,
    });

    try std.testing.expectEqual(@as(u16, 1), summary.free_descriptors_after);
    try std.testing.expectEqual(@as(u16, 4), summary.remaining_in_flight_descriptors);
    try std.testing.expect(!summary.reaches_wake_threshold);
    try std.testing.expect(summary.frees_completed_buffers);
    try std.testing.expect(!summary.wakes_transmit_queue);
    try std.testing.expect(summary.keeps_queue_stopped);
    try std.testing.expectEqual(
        virtio_net_transmit_recycle.RecycleDisposition.keep_stopped,
        summary.disposition,
    );
}

test "phase12 virtio net transmit recycle does not wake a stopped queue without reclaimed descriptors" {
    const summary = try virtio_net_transmit_recycle.summarizeTransmitRecycle(.{
        .in_flight_descriptors = 3,
        .free_descriptors_before = 4,
        .completed_descriptors = 0,
        .wake_threshold = 2,
        .queue_stopped = true,
    });

    try std.testing.expectEqual(@as(u16, 4), summary.free_descriptors_after);
    try std.testing.expectEqual(@as(u16, 3), summary.remaining_in_flight_descriptors);
    try std.testing.expect(summary.reaches_wake_threshold);
    try std.testing.expect(!summary.frees_completed_buffers);
    try std.testing.expect(!summary.wakes_transmit_queue);
    try std.testing.expect(summary.keeps_queue_stopped);
    try std.testing.expectEqual(
        virtio_net_transmit_recycle.RecycleDisposition.keep_stopped,
        summary.disposition,
    );
}

test "phase12 virtio net transmit recycle keeps running queues running even when recycle frees enough descriptors" {
    const summary = try virtio_net_transmit_recycle.summarizeTransmitRecycle(.{
        .in_flight_descriptors = 3,
        .free_descriptors_before = 1,
        .completed_descriptors = 2,
        .wake_threshold = 2,
        .queue_stopped = false,
    });

    try std.testing.expectEqual(@as(u16, 3), summary.free_descriptors_after);
    try std.testing.expectEqual(@as(u16, 1), summary.remaining_in_flight_descriptors);
    try std.testing.expect(summary.reaches_wake_threshold);
    try std.testing.expect(summary.frees_completed_buffers);
    try std.testing.expect(!summary.wakes_transmit_queue);
    try std.testing.expect(!summary.keeps_queue_stopped);
    try std.testing.expectEqual(
        virtio_net_transmit_recycle.RecycleDisposition.keep_running,
        summary.disposition,
    );
}

test "phase12 virtio net transmit recycle rejects impossible completion counts" {
    try std.testing.expectError(
        error.CompletedDescriptorOverflow,
        virtio_net_transmit_recycle.summarizeTransmitRecycle(.{
            .in_flight_descriptors = 1,
            .free_descriptors_before = 0,
            .completed_descriptors = 2,
            .wake_threshold = 1,
            .queue_stopped = true,
        }),
    );
}

test "phase12 virtio net transmit recycle fails closed when the free-descriptor count would overflow" {
    try std.testing.expectError(
        error.QueueCountOverflow,
        virtio_net_transmit_recycle.summarizeTransmitRecycle(.{
            .in_flight_descriptors = 1,
            .free_descriptors_before = std.math.maxInt(u16),
            .completed_descriptors = 1,
            .wake_threshold = 1,
            .queue_stopped = true,
        }),
    );
}
