const std = @import("std");

pub const default_wake_threshold: u16 = 2;
pub const default_recycle_budget: u16 = std.math.maxInt(u16);

pub const RecycleDisposition = enum {
    keep_running,
    keep_stopped,
    wake_queue,
};

pub const TransmitRecycleRequest = struct {
    in_flight_descriptors: u16,
    free_descriptors_before: u16,
    completed_descriptors: u16,
    recycle_budget: u16 = default_recycle_budget,
    wake_threshold: u16 = default_wake_threshold,
    queue_stopped: bool = false,
};

pub const TransmitRecycleSummary = struct {
    anchor: []const u8,
    in_flight_descriptors: u16,
    completed_descriptors: u16,
    recycled_descriptors: u16,
    completion_backlog_after: u16,
    free_descriptors_before: u16,
    free_descriptors_after: u16,
    remaining_in_flight_descriptors: u16,
    wake_threshold: u16,
    queue_was_stopped: bool,
    reaches_wake_threshold: bool,
    frees_completed_buffers: bool,
    requires_followup_recycle: bool,
    wakes_transmit_queue: bool,
    keeps_queue_stopped: bool,
    disposition: RecycleDisposition,
};

pub fn summarizeTransmitRecycle(request: TransmitRecycleRequest) !TransmitRecycleSummary {
    if (request.completed_descriptors > request.in_flight_descriptors) {
        return error.CompletedDescriptorOverflow;
    }

    const recycled_descriptors = @min(request.completed_descriptors, request.recycle_budget);
    const completion_backlog_after = request.completed_descriptors - recycled_descriptors;
    const free_descriptors_after = try checkedAddU16(
        request.free_descriptors_before,
        recycled_descriptors,
    );
    const remaining_in_flight_descriptors = request.in_flight_descriptors - recycled_descriptors;
    const frees_completed_buffers = recycled_descriptors > 0;
    const requires_followup_recycle = completion_backlog_after > 0;
    const reaches_wake_threshold = free_descriptors_after >= request.wake_threshold;
    const wakes_transmit_queue = request.queue_stopped and
        frees_completed_buffers and
        reaches_wake_threshold and
        !requires_followup_recycle;
    const keeps_queue_stopped = request.queue_stopped and !wakes_transmit_queue;

    return .{
        .anchor = "drivers/net/virtio_net.c",
        .in_flight_descriptors = request.in_flight_descriptors,
        .completed_descriptors = request.completed_descriptors,
        .recycled_descriptors = recycled_descriptors,
        .completion_backlog_after = completion_backlog_after,
        .free_descriptors_before = request.free_descriptors_before,
        .free_descriptors_after = free_descriptors_after,
        .remaining_in_flight_descriptors = remaining_in_flight_descriptors,
        .wake_threshold = request.wake_threshold,
        .queue_was_stopped = request.queue_stopped,
        .reaches_wake_threshold = reaches_wake_threshold,
        .frees_completed_buffers = frees_completed_buffers,
        .requires_followup_recycle = requires_followup_recycle,
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

test "summarizeTransmitRecycle wakes a stopped queue only after the bounded recycle clears the backlog" {
    const summary = try summarizeTransmitRecycle(.{
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
    try std.testing.expectEqual(@as(u16, 0), summary.completion_backlog_after);
    try std.testing.expectEqual(@as(u16, 1), summary.free_descriptors_before);
    try std.testing.expectEqual(@as(u16, 3), summary.free_descriptors_after);
    try std.testing.expectEqual(@as(u16, 2), summary.remaining_in_flight_descriptors);
    try std.testing.expectEqual(@as(u16, 3), summary.wake_threshold);
    try std.testing.expect(summary.queue_was_stopped);
    try std.testing.expect(summary.reaches_wake_threshold);
    try std.testing.expect(summary.frees_completed_buffers);
    try std.testing.expect(!summary.requires_followup_recycle);
    try std.testing.expect(summary.wakes_transmit_queue);
    try std.testing.expect(!summary.keeps_queue_stopped);
    try std.testing.expectEqual(RecycleDisposition.wake_queue, summary.disposition);
}

test "summarizeTransmitRecycle keeps a stopped queue parked while a bounded poll leaves completions behind" {
    const summary = try summarizeTransmitRecycle(.{
        .in_flight_descriptors = 8,
        .free_descriptors_before = 1,
        .completed_descriptors = 4,
        .recycle_budget = 2,
        .wake_threshold = 3,
        .queue_stopped = true,
    });

    try std.testing.expectEqual(@as(u16, 4), summary.completed_descriptors);
    try std.testing.expectEqual(@as(u16, 2), summary.recycled_descriptors);
    try std.testing.expectEqual(@as(u16, 2), summary.completion_backlog_after);
    try std.testing.expectEqual(@as(u16, 3), summary.free_descriptors_after);
    try std.testing.expectEqual(@as(u16, 6), summary.remaining_in_flight_descriptors);
    try std.testing.expect(summary.reaches_wake_threshold);
    try std.testing.expect(summary.frees_completed_buffers);
    try std.testing.expect(summary.requires_followup_recycle);
    try std.testing.expect(!summary.wakes_transmit_queue);
    try std.testing.expect(summary.keeps_queue_stopped);
    try std.testing.expectEqual(RecycleDisposition.keep_stopped, summary.disposition);
}

test "summarizeTransmitRecycle keeps a stopped queue parked below the wake threshold" {
    const summary = try summarizeTransmitRecycle(.{
        .in_flight_descriptors = 5,
        .free_descriptors_before = 0,
        .completed_descriptors = 1,
        .wake_threshold = 4,
        .queue_stopped = true,
    });

    try std.testing.expectEqual(@as(u16, 1), summary.recycled_descriptors);
    try std.testing.expectEqual(@as(u16, 0), summary.completion_backlog_after);
    try std.testing.expectEqual(@as(u16, 1), summary.free_descriptors_after);
    try std.testing.expectEqual(@as(u16, 4), summary.remaining_in_flight_descriptors);
    try std.testing.expect(!summary.reaches_wake_threshold);
    try std.testing.expect(summary.frees_completed_buffers);
    try std.testing.expect(!summary.requires_followup_recycle);
    try std.testing.expect(!summary.wakes_transmit_queue);
    try std.testing.expect(summary.keeps_queue_stopped);
    try std.testing.expectEqual(RecycleDisposition.keep_stopped, summary.disposition);
}

test "summarizeTransmitRecycle does not wake a stopped queue without reclaimed descriptors" {
    const summary = try summarizeTransmitRecycle(.{
        .in_flight_descriptors = 3,
        .free_descriptors_before = 2,
        .completed_descriptors = 0,
        .wake_threshold = 2,
        .queue_stopped = true,
    });

    try std.testing.expectEqual(@as(u16, 0), summary.recycled_descriptors);
    try std.testing.expectEqual(@as(u16, 0), summary.completion_backlog_after);
    try std.testing.expectEqual(@as(u16, 2), summary.free_descriptors_after);
    try std.testing.expectEqual(@as(u16, 3), summary.remaining_in_flight_descriptors);
    try std.testing.expect(summary.queue_was_stopped);
    try std.testing.expect(summary.reaches_wake_threshold);
    try std.testing.expect(!summary.frees_completed_buffers);
    try std.testing.expect(!summary.requires_followup_recycle);
    try std.testing.expect(!summary.wakes_transmit_queue);
    try std.testing.expect(summary.keeps_queue_stopped);
    try std.testing.expectEqual(RecycleDisposition.keep_stopped, summary.disposition);
}

test "summarizeTransmitRecycle keeps running queues running even when recycle frees enough descriptors" {
    const summary = try summarizeTransmitRecycle(.{
        .in_flight_descriptors = 3,
        .free_descriptors_before = 1,
        .completed_descriptors = 2,
        .wake_threshold = 2,
        .queue_stopped = false,
    });

    try std.testing.expectEqual(@as(u16, 2), summary.recycled_descriptors);
    try std.testing.expectEqual(@as(u16, 0), summary.completion_backlog_after);
    try std.testing.expectEqual(@as(u16, 3), summary.free_descriptors_after);
    try std.testing.expectEqual(@as(u16, 1), summary.remaining_in_flight_descriptors);
    try std.testing.expect(summary.reaches_wake_threshold);
    try std.testing.expect(summary.frees_completed_buffers);
    try std.testing.expect(!summary.requires_followup_recycle);
    try std.testing.expect(!summary.wakes_transmit_queue);
    try std.testing.expect(!summary.keeps_queue_stopped);
    try std.testing.expectEqual(RecycleDisposition.keep_running, summary.disposition);
}

test "summarizeTransmitRecycle rejects impossible completion counts" {
    try std.testing.expectError(
        error.CompletedDescriptorOverflow,
        summarizeTransmitRecycle(.{
            .in_flight_descriptors = 1,
            .free_descriptors_before = 0,
            .completed_descriptors = 2,
            .wake_threshold = 1,
            .queue_stopped = true,
        }),
    );
}

test "summarizeTransmitRecycle fails closed when the free-descriptor count would overflow" {
    try std.testing.expectError(
        error.QueueCountOverflow,
        summarizeTransmitRecycle(.{
            .in_flight_descriptors = 1,
            .free_descriptors_before = std.math.maxInt(u16),
            .completed_descriptors = 1,
            .wake_threshold = 1,
            .queue_stopped = true,
        }),
    );
}
