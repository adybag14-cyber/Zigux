const std = @import("std");

const perf_buffer_poll = @import("perf_buffer_poll.zig");
const perf_buffer_ready_window = @import("perf_buffer_ready_window.zig");

test "phase8 ready-buffer window helper entrypoints stay explicit" {
    try std.testing.expect(@hasDecl(perf_buffer_ready_window, "ReadyBufferWindowLookupError"));
    try std.testing.expect(@hasDecl(perf_buffer_ready_window, "resolveReadyBufferWindowMappedSizeAtAttempt"));
    try std.testing.expect(@hasDecl(perf_buffer_ready_window, "resolveReadyBufferWindowMappedSizeReturnAtAttempt"));
    try std.testing.expect(@hasDecl(perf_buffer_ready_window, "resolveReadyBufferWindowLookupReturnAtAttempt"));
}

test "phase8 ready-buffer window helpers keep typed outputs stable" {
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
        try perf_buffer_ready_window.resolveReadyBufferWindowMappedSizeAtAttempt(&buffers, &buffer_windows, 0),
    );
    try std.testing.expectEqual(
        @as(usize, 8192),
        try perf_buffer_ready_window.resolveReadyBufferWindowMappedSizeAtAttempt(&buffers, &buffer_windows, 1),
    );
    try std.testing.expectError(
        error.MissingReadyBuffer,
        perf_buffer_ready_window.resolveReadyBufferWindowMappedSizeAtAttempt(&buffers, &buffer_windows, 2),
    );

    const short_windows = [_]?perf_buffer_poll.BufferWindowObservation{
        null,
        .{ .mapped_size = 4096 },
    };
    try std.testing.expectError(
        error.InvalidIndex,
        perf_buffer_ready_window.resolveReadyBufferWindowMappedSizeAtAttempt(&buffers, &short_windows, 1),
    );

    const missing_window = [_]?perf_buffer_poll.BufferWindowObservation{
        null,
        .{ .mapped_size = 4096 },
        null,
        null,
    };
    try std.testing.expectError(
        error.MissingWindow,
        perf_buffer_ready_window.resolveReadyBufferWindowMappedSizeAtAttempt(&buffers, &missing_window, 1),
    );
}

test "phase8 ready-buffer window helpers keep errno-shaped outputs stable" {
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
        @as(i32, 4096),
        perf_buffer_ready_window.resolveReadyBufferWindowMappedSizeReturnAtAttempt(&buffers, &buffer_windows, 0),
    );
    try std.testing.expectEqual(
        @as(i32, 8192),
        perf_buffer_ready_window.resolveReadyBufferWindowMappedSizeReturnAtAttempt(&buffers, &buffer_windows, 1),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        perf_buffer_ready_window.resolveReadyBufferWindowMappedSizeReturnAtAttempt(&buffers, &buffer_windows, 2),
    );

    const short_windows = [_]?perf_buffer_poll.BufferWindowObservation{
        null,
        .{ .mapped_size = 4096 },
    };
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        perf_buffer_ready_window.resolveReadyBufferWindowMappedSizeReturnAtAttempt(&buffers, &short_windows, 1),
    );

    const missing_window = [_]?perf_buffer_poll.BufferWindowObservation{
        null,
        .{ .mapped_size = 4096 },
        null,
        null,
    };
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        perf_buffer_ready_window.resolveReadyBufferWindowMappedSizeReturnAtAttempt(&buffers, &missing_window, 1),
    );

    const overflow_windows = [_]?perf_buffer_poll.BufferWindowObservation{
        null,
        .{ .mapped_size = @as(usize, std.math.maxInt(i32)) + 1 },
    };
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.OVERFLOW)),
        perf_buffer_ready_window.resolveReadyBufferWindowMappedSizeReturnAtAttempt(&buffers, &overflow_windows, 0),
    );
}

test "phase8 ready-buffer window helpers keep lookup-return outputs stable" {
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
        perf_buffer_ready_window.resolveReadyBufferWindowLookupReturnAtAttempt(&buffers, &buffer_windows, 0),
    );
    try std.testing.expectEqual(
        @as(i32, 0),
        perf_buffer_ready_window.resolveReadyBufferWindowLookupReturnAtAttempt(&buffers, &buffer_windows, 1),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        perf_buffer_ready_window.resolveReadyBufferWindowLookupReturnAtAttempt(&buffers, &buffer_windows, 2),
    );

    const short_windows = [_]?perf_buffer_poll.BufferWindowObservation{
        null,
        .{ .mapped_size = 4096 },
    };
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        perf_buffer_ready_window.resolveReadyBufferWindowLookupReturnAtAttempt(&buffers, &short_windows, 1),
    );

    const missing_window = [_]?perf_buffer_poll.BufferWindowObservation{
        null,
        .{ .mapped_size = 4096 },
        null,
        null,
    };
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        perf_buffer_ready_window.resolveReadyBufferWindowLookupReturnAtAttempt(&buffers, &missing_window, 1),
    );
}
