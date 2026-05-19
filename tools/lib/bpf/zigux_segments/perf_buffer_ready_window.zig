const std = @import("std");
const perf_buffer_poll = @import("perf_buffer_poll.zig");

pub const ReadyBufferWindowLookupError =
    perf_buffer_poll.ReadyBufferAttemptLookupError || perf_buffer_poll.BufferWindowLookupError;

pub fn resolveReadyBufferWindowMappedSizeAtAttempt(
    buffers: []const perf_buffer_poll.BufferObservation,
    buffer_windows: []const ?perf_buffer_poll.BufferWindowObservation,
    attempt_index: usize,
) ReadyBufferWindowLookupError!usize {
    const buffer_index = try perf_buffer_poll.resolveReadyBufferAttemptAtIndex(buffers, attempt_index);
    return perf_buffer_poll.resolveBufferWindowMappedSizeAtIndex(buffer_windows, buffer_index);
}

pub fn resolveReadyBufferWindowLookupReturnAtAttempt(
    buffers: []const perf_buffer_poll.BufferObservation,
    buffer_windows: []const ?perf_buffer_poll.BufferWindowObservation,
    attempt_index: usize,
) i32 {
    const buffer_index = perf_buffer_poll.resolveReadyBufferAttemptIndex(buffers, attempt_index) orelse
        return -@as(i32, @intFromEnum(std.os.linux.E.NOENT));
    return perf_buffer_poll.resolveBufferWindowLookupReturnAtIndex(buffer_windows, buffer_index);
}

test "phase8 perf-buffer ready-window helper resolves ready-buffer windows without manual slot plumbing" {
    const buffers = [_]perf_buffer_poll.BufferObservation{
        .{},
        .{ .ready = true },
        .{},
        .{ .ready = true },
    };
    const buffer_windows = [_]?perf_buffer_poll.BufferWindowObservation{
        null,
        .{ .mapped_size = 4096 },
        null,
        .{ .mapped_size = 8192 },
    };

    try std.testing.expectEqual(
        @as(usize, 4096),
        try resolveReadyBufferWindowMappedSizeAtAttempt(&buffers, &buffer_windows, 0),
    );
    try std.testing.expectEqual(
        @as(usize, 8192),
        try resolveReadyBufferWindowMappedSizeAtAttempt(&buffers, &buffer_windows, 1),
    );
    try std.testing.expectError(
        error.MissingReadyBuffer,
        resolveReadyBufferWindowMappedSizeAtAttempt(&buffers, &buffer_windows, 2),
    );

    const short_windows = [_]?perf_buffer_poll.BufferWindowObservation{
        null,
        .{ .mapped_size = 4096 },
    };
    try std.testing.expectError(
        error.InvalidIndex,
        resolveReadyBufferWindowMappedSizeAtAttempt(&buffers, &short_windows, 1),
    );

    const missing_window = [_]?perf_buffer_poll.BufferWindowObservation{
        null,
        .{ .mapped_size = 4096 },
        null,
        null,
    };
    try std.testing.expectError(
        error.MissingWindow,
        resolveReadyBufferWindowMappedSizeAtAttempt(&buffers, &missing_window, 1),
    );
}

test "phase8 perf-buffer ready-window helper keeps ready-buffer window returns errno-shaped" {
    const buffers = [_]perf_buffer_poll.BufferObservation{
        .{},
        .{ .ready = true },
        .{},
        .{ .ready = true },
    };
    const buffer_windows = [_]?perf_buffer_poll.BufferWindowObservation{
        null,
        .{ .mapped_size = 4096 },
        null,
        .{ .mapped_size = 8192 },
    };

    try std.testing.expectEqual(
        @as(i32, 0),
        resolveReadyBufferWindowLookupReturnAtAttempt(&buffers, &buffer_windows, 0),
    );
    try std.testing.expectEqual(
        @as(i32, 0),
        resolveReadyBufferWindowLookupReturnAtAttempt(&buffers, &buffer_windows, 1),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        resolveReadyBufferWindowLookupReturnAtAttempt(&buffers, &buffer_windows, 2),
    );

    const short_windows = [_]?perf_buffer_poll.BufferWindowObservation{
        null,
        .{ .mapped_size = 4096 },
    };
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        resolveReadyBufferWindowLookupReturnAtAttempt(&buffers, &short_windows, 1),
    );

    const missing_window = [_]?perf_buffer_poll.BufferWindowObservation{
        null,
        .{ .mapped_size = 4096 },
        null,
        null,
    };
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        resolveReadyBufferWindowLookupReturnAtAttempt(&buffers, &missing_window, 1),
    );
}
