const std = @import("std");

pub const default_wake_threshold: u16 = 2;

pub const RecycleDisposition = enum {
    keep_running,
    keep_stopped,
    wake_queue,
};

pub const CompletedOwnershipDisposition = enum {
    device_retained,
    driver_free_list,
};

pub const TransmitRecycleRequest = struct {
    in_flight_descriptors: u16,
    free_descriptors_before: u16,
    completed_descriptors: u16,
    wake_threshold: u16 = default_wake_threshold,
    queue_stopped: bool = false,
};

pub const TransmitRecycleSummary = struct {
    anchor: []const u8,
    in_flight_descriptors: u16,
    completed_descriptors: u16,
    recycled_descriptors: u16,
    free_descriptors_before: u16,
    free_descriptors_after: u16,
    remaining_in_flight_descriptors: u16,
    wake_threshold: u16,
    queue_was_stopped: bool,
    reaches_wake_threshold: bool,
    frees_completed_buffers: bool,
    returns_completed_ownership_to_driver: bool,
    completed_ownership_after_recycle: CompletedOwnershipDisposition,
    wakes_transmit_queue: bool,
    keeps_queue_stopped: bool,
    disposition: RecycleDisposition,
};

pub fn summarizeTransmitRecycle(request: TransmitRecycleRequest) !TransmitRecycleSummary {
    if (request.completed_descriptors > request.in_flight_descriptors) {
        return error.CompletedDescriptorOverflow;
    }
    if (request.queue_stopped and request.wake_threshold == 0) {
        return error.StoppedQueueWakeThresholdMissing;
    }

    const free_descriptors_after = try checkedAddU16(
        request.free_descriptors_before,
        request.completed_descriptors,
    );

    const remaining_in_flight_descriptors =
        request.in_flight_descriptors - request.completed_descriptors;
    const frees_completed_buffers = request.completed_descriptors > 0;
    const reaches_wake_threshold = free_descriptors_after >= request.wake_threshold;
    const wakes_transmit_queue =
        request.queue_stopped and frees_completed_buffers and reaches_wake_threshold;
    const keeps_queue_stopped = request.queue_stopped and !wakes_transmit_queue;
    const completed_ownership_after_recycle: CompletedOwnershipDisposition =
        if (frees_completed_buffers) .driver_free_list else .device_retained;

    return .{
        .anchor = "drivers/net/virtio_net.c",
        .in_flight_descriptors = request.in_flight_descriptors,
        .completed_descriptors = request.completed_descriptors,
        .recycled_descriptors = request.completed_descriptors,
        .free_descriptors_before = request.free_descriptors_before,
        .free_descriptors_after = free_descriptors_after,
        .remaining_in_flight_descriptors = remaining_in_flight_descriptors,
        .wake_threshold = request.wake_threshold,
        .queue_was_stopped = request.queue_stopped,
        .reaches_wake_threshold = reaches_wake_threshold,
        .frees_completed_buffers = frees_completed_buffers,
        .returns_completed_ownership_to_driver = frees_completed_buffers,
        .completed_ownership_after_recycle = completed_ownership_after_recycle,
        .wakes_transmit_queue = wakes_transmit_queue,
        .keeps_queue_stopped = keeps_queue_stopped,
        .disposition = if (wakes_transmit_queue)
            .wake_queue
        else if (request.queue_stopped)
            .keep_stopped
        else
            .keep_running,
    };
}

fn checkedAddU16(lhs: u16, rhs: u16) !u16 {
    const value = @as(u32, lhs) + rhs;
    return std.math.cast(u16, value) orelse error.QueueCountOverflow;
}

test "summarizeTransmitRecycle keeps a stopped queue stopped below the wake threshold" {
    const summary = try summarizeTransmitRecycle(.{
        .in_flight_descriptors = 6,
        .free_descriptors_before = 1,
        .completed_descriptors = 0,
        .queue_stopped = true,
    });

    try std.testing.expectEqual(@as(u16, 6), summary.remaining_in_flight_descriptors);
    try std.testing.expectEqual(@as(u16, 1), summary.free_descriptors_after);
    try std.testing.expect(!summary.frees_completed_buffers);
    try std.testing.expect(!summary.returns_completed_ownership_to_driver);
    try std.testing.expectEqual(
        CompletedOwnershipDisposition.device_retained,
        summary.completed_ownership_after_recycle,
    );
    try std.testing.expect(!summary.reaches_wake_threshold);
    try std.testing.expect(!summary.wakes_transmit_queue);
    try std.testing.expect(summary.keeps_queue_stopped);
    try std.testing.expectEqual(RecycleDisposition.keep_stopped, summary.disposition);
}

test "summarizeTransmitRecycle wakes a stopped queue once completions reach the threshold" {
    const summary = try summarizeTransmitRecycle(.{
        .in_flight_descriptors = 5,
        .free_descriptors_before = 1,
        .completed_descriptors = 2,
        .queue_stopped = true,
    });

    try std.testing.expectEqual(@as(u16, 3), summary.remaining_in_flight_descriptors);
    try std.testing.expectEqual(@as(u16, 3), summary.free_descriptors_after);
    try std.testing.expect(summary.frees_completed_buffers);
    try std.testing.expect(summary.returns_completed_ownership_to_driver);
    try std.testing.expectEqual(
        CompletedOwnershipDisposition.driver_free_list,
        summary.completed_ownership_after_recycle,
    );
    try std.testing.expect(summary.reaches_wake_threshold);
    try std.testing.expect(summary.wakes_transmit_queue);
    try std.testing.expect(!summary.keeps_queue_stopped);
    try std.testing.expectEqual(RecycleDisposition.wake_queue, summary.disposition);
}

test "summarizeTransmitRecycle wakes a stopped queue when new completions arrive after the wake budget was already restored" {
    const summary = try summarizeTransmitRecycle(.{
        .in_flight_descriptors = 4,
        .free_descriptors_before = 3,
        .completed_descriptors = 1,
        .wake_threshold = 2,
        .queue_stopped = true,
    });

    try std.testing.expectEqual(@as(u16, 3), summary.remaining_in_flight_descriptors);
    try std.testing.expectEqual(@as(u16, 4), summary.free_descriptors_after);
    try std.testing.expect(summary.frees_completed_buffers);
    try std.testing.expect(summary.returns_completed_ownership_to_driver);
    try std.testing.expectEqual(
        CompletedOwnershipDisposition.driver_free_list,
        summary.completed_ownership_after_recycle,
    );
    try std.testing.expect(summary.reaches_wake_threshold);
    try std.testing.expect(summary.wakes_transmit_queue);
    try std.testing.expect(!summary.keeps_queue_stopped);
    try std.testing.expectEqual(RecycleDisposition.wake_queue, summary.disposition);
}

test "summarizeTransmitRecycle keeps a running queue running even above threshold" {
    const summary = try summarizeTransmitRecycle(.{
        .in_flight_descriptors = 8,
        .free_descriptors_before = 0,
        .completed_descriptors = 4,
        .queue_stopped = false,
    });

    try std.testing.expectEqual(@as(u16, 4), summary.remaining_in_flight_descriptors);
    try std.testing.expectEqual(@as(u16, 4), summary.free_descriptors_after);
    try std.testing.expect(summary.frees_completed_buffers);
    try std.testing.expect(summary.returns_completed_ownership_to_driver);
    try std.testing.expectEqual(
        CompletedOwnershipDisposition.driver_free_list,
        summary.completed_ownership_after_recycle,
    );
    try std.testing.expect(summary.reaches_wake_threshold);
    try std.testing.expect(!summary.wakes_transmit_queue);
    try std.testing.expect(!summary.keeps_queue_stopped);
    try std.testing.expectEqual(RecycleDisposition.keep_running, summary.disposition);
}

test "summarizeTransmitRecycle rejects completion counts larger than the in-flight set" {
    try std.testing.expectError(error.CompletedDescriptorOverflow, summarizeTransmitRecycle(.{
        .in_flight_descriptors = 3,
        .free_descriptors_before = 1,
        .completed_descriptors = 4,
        .queue_stopped = true,
    }));
}

test "summarizeTransmitRecycle rejects zero wake thresholds for stopped queues" {
    try std.testing.expectError(error.StoppedQueueWakeThresholdMissing, summarizeTransmitRecycle(.{
        .in_flight_descriptors = 1,
        .free_descriptors_before = 0,
        .completed_descriptors = 0,
        .wake_threshold = 0,
        .queue_stopped = true,
    }));
}

test "summarizeTransmitRecycle rejects descriptor-count overflow after recycling" {
    try std.testing.expectError(error.QueueCountOverflow, summarizeTransmitRecycle(.{
        .in_flight_descriptors = 1,
        .free_descriptors_before = std.math.maxInt(u16),
        .completed_descriptors = 1,
        .queue_stopped = true,
    }));
}
