const std = @import("std");

const perf_buffer_poll = @import("perf_buffer_poll.zig");

test "phase8 ready-buffer attempt helper entrypoints stay explicit" {
    try std.testing.expect(@hasDecl(perf_buffer_poll, "ReadyBufferAttemptLookupDisposition"));
    try std.testing.expect(@hasDecl(perf_buffer_poll, "ReadyBufferAttemptLookupSummary"));
    try std.testing.expect(@hasDecl(perf_buffer_poll, "ReadyBufferAttemptLookupError"));
    try std.testing.expect(@hasDecl(perf_buffer_poll, "resolveReadyBufferAttemptIndex"));
    try std.testing.expect(@hasDecl(perf_buffer_poll, "summarizeReadyBufferAttemptLookup"));
    try std.testing.expect(@hasDecl(perf_buffer_poll, "resolveReadyBufferAttemptLookup"));
    try std.testing.expect(@hasDecl(perf_buffer_poll, "resolveReadyBufferAttemptAtIndex"));
    try std.testing.expect(@hasDecl(perf_buffer_poll, "resolveReadyBufferAttemptIndexReturn"));
    try std.testing.expect(@hasDecl(perf_buffer_poll, "resolveReadyBufferAttemptLookupReturn"));
}

test "phase8 ready-buffer attempt helpers keep typed summary outputs stable" {
    const buffers = [_]perf_buffer_poll.BufferObservation{
        .{},
        .{ .ready = true },
        .{},
        .{ .ready = true },
    };

    const first = perf_buffer_poll.summarizeReadyBufferAttemptLookup(&buffers, 0);
    try std.testing.expectEqual(
        perf_buffer_poll.ReadyBufferAttemptLookupDisposition.found_ready_index,
        first.disposition,
    );
    try std.testing.expectEqual(@as(usize, 2), first.ready_count);
    try std.testing.expectEqual(@as(?usize, 1), first.ready_index);
    try std.testing.expectEqual(
        @as(usize, 1),
        try perf_buffer_poll.resolveReadyBufferAttemptLookup(first),
    );

    const second = perf_buffer_poll.summarizeReadyBufferAttemptLookup(&buffers, 1);
    try std.testing.expectEqual(
        perf_buffer_poll.ReadyBufferAttemptLookupDisposition.found_ready_index,
        second.disposition,
    );
    try std.testing.expectEqual(@as(usize, 2), second.ready_count);
    try std.testing.expectEqual(@as(?usize, 3), second.ready_index);
    try std.testing.expectEqual(
        @as(usize, 3),
        try perf_buffer_poll.resolveReadyBufferAttemptLookup(second),
    );

    const missing = perf_buffer_poll.summarizeReadyBufferAttemptLookup(&buffers, 2);
    try std.testing.expectEqual(
        perf_buffer_poll.ReadyBufferAttemptLookupDisposition.missing_ready_index,
        missing.disposition,
    );
    try std.testing.expectEqual(@as(usize, 2), missing.ready_count);
    try std.testing.expectEqual(@as(?usize, null), missing.ready_index);
    try std.testing.expectError(
        error.MissingReadyBuffer,
        perf_buffer_poll.resolveReadyBufferAttemptLookup(missing),
    );
}

test "phase8 ready-buffer attempt helpers keep typed index lookups stable" {
    const buffers = [_]perf_buffer_poll.BufferObservation{
        .{},
        .{ .ready = true },
        .{},
        .{ .ready = true },
    };

    try std.testing.expectEqual(@as(?usize, 1), perf_buffer_poll.resolveReadyBufferAttemptIndex(&buffers, 0));
    try std.testing.expectEqual(@as(?usize, 3), perf_buffer_poll.resolveReadyBufferAttemptIndex(&buffers, 1));
    try std.testing.expectEqual(@as(?usize, null), perf_buffer_poll.resolveReadyBufferAttemptIndex(&buffers, 2));

    try std.testing.expectEqual(
        @as(usize, 1),
        try perf_buffer_poll.resolveReadyBufferAttemptAtIndex(&buffers, 0),
    );
    try std.testing.expectEqual(
        @as(usize, 3),
        try perf_buffer_poll.resolveReadyBufferAttemptAtIndex(&buffers, 1),
    );
    try std.testing.expectError(
        error.MissingReadyBuffer,
        perf_buffer_poll.resolveReadyBufferAttemptAtIndex(&buffers, 2),
    );
}

test "phase8 ready-buffer attempt helpers keep errno-shaped outputs stable" {
    const buffers = [_]perf_buffer_poll.BufferObservation{
        .{},
        .{ .ready = true },
        .{},
        .{ .ready = true },
    };

    try std.testing.expectEqual(
        @as(i32, 1),
        perf_buffer_poll.resolveReadyBufferAttemptLookupReturn(
            perf_buffer_poll.summarizeReadyBufferAttemptLookup(&buffers, 0),
        ),
    );
    try std.testing.expectEqual(
        @as(i32, 3),
        perf_buffer_poll.resolveReadyBufferAttemptLookupReturn(
            perf_buffer_poll.summarizeReadyBufferAttemptLookup(&buffers, 1),
        ),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        perf_buffer_poll.resolveReadyBufferAttemptLookupReturn(
            perf_buffer_poll.summarizeReadyBufferAttemptLookup(&buffers, 2),
        ),
    );

    try std.testing.expectEqual(@as(i32, 1), perf_buffer_poll.resolveReadyBufferAttemptIndexReturn(&buffers, 0));
    try std.testing.expectEqual(@as(i32, 3), perf_buffer_poll.resolveReadyBufferAttemptIndexReturn(&buffers, 1));
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        perf_buffer_poll.resolveReadyBufferAttemptIndexReturn(&buffers, 2),
    );

    const impossible = perf_buffer_poll.ReadyBufferAttemptLookupSummary{
        .requested_attempt_index = 0,
        .ready_index = @as(usize, std.math.maxInt(i32)) + 1,
        .ready_count = 1,
        .disposition = .found_ready_index,
    };
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.OVERFLOW)),
        perf_buffer_poll.resolveReadyBufferAttemptLookupReturn(impossible),
    );
}
