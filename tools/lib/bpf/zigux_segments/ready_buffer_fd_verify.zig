const std = @import("std");

const perf_buffer_poll = @import("perf_buffer_poll.zig");

test "phase8 ready-buffer fd helper entrypoints stay explicit" {
    try std.testing.expect(@hasDecl(perf_buffer_poll, "ReadyBufferFdLookupError"));
    try std.testing.expect(@hasDecl(perf_buffer_poll, "resolveReadyBufferFdAtAttempt"));
    try std.testing.expect(@hasDecl(perf_buffer_poll, "resolveReadyBufferFdLookupReturnAtAttempt"));
}

test "phase8 ready-buffer fd helpers keep typed outputs stable" {
    const buffers = [_]perf_buffer_poll.BufferObservation{
        .{},
        .{ .ready = true },
        .{},
        .{ .ready = true },
    };
    const buffer_fds = [_]?i32{ null, 9, null, 21 };

    try std.testing.expectEqual(
        @as(i32, 9),
        try perf_buffer_poll.resolveReadyBufferFdAtAttempt(&buffers, &buffer_fds, 0),
    );
    try std.testing.expectEqual(
        @as(i32, 21),
        try perf_buffer_poll.resolveReadyBufferFdAtAttempt(&buffers, &buffer_fds, 1),
    );
    try std.testing.expectError(
        error.MissingReadyBuffer,
        perf_buffer_poll.resolveReadyBufferFdAtAttempt(&buffers, &buffer_fds, 2),
    );

    const short_fds = [_]?i32{ null, 9 };
    try std.testing.expectError(
        error.InvalidIndex,
        perf_buffer_poll.resolveReadyBufferFdAtAttempt(&buffers, &short_fds, 1),
    );

    const missing_fd = [_]?i32{ null, 9, null, null };
    try std.testing.expectError(
        error.MissingFd,
        perf_buffer_poll.resolveReadyBufferFdAtAttempt(&buffers, &missing_fd, 1),
    );
}

test "phase8 ready-buffer fd helpers keep errno-shaped outputs stable" {
    const buffers = [_]perf_buffer_poll.BufferObservation{
        .{},
        .{ .ready = true },
        .{},
        .{ .ready = true },
    };
    const buffer_fds = [_]?i32{ null, 9, null, 21 };

    try std.testing.expectEqual(
        @as(i32, 9),
        perf_buffer_poll.resolveReadyBufferFdLookupReturnAtAttempt(&buffers, &buffer_fds, 0),
    );
    try std.testing.expectEqual(
        @as(i32, 21),
        perf_buffer_poll.resolveReadyBufferFdLookupReturnAtAttempt(&buffers, &buffer_fds, 1),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        perf_buffer_poll.resolveReadyBufferFdLookupReturnAtAttempt(&buffers, &buffer_fds, 2),
    );

    const short_fds = [_]?i32{ null, 9 };
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        perf_buffer_poll.resolveReadyBufferFdLookupReturnAtAttempt(&buffers, &short_fds, 1),
    );

    const missing_fd = [_]?i32{ null, 9, null, null };
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        perf_buffer_poll.resolveReadyBufferFdLookupReturnAtAttempt(&buffers, &missing_fd, 1),
    );
}
