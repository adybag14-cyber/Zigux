const std = @import("std");

const perf_buffer_poll = @import("perf_buffer_poll.zig");
const ready_buffer_fd_lookup = @import("ready_buffer_fd_lookup.zig");

test "phase8 ready-buffer fd helper entrypoints stay explicit" {
    try std.testing.expect(@hasDecl(ready_buffer_fd_lookup, "ReadyBufferFdLookupError"));
    try std.testing.expect(@hasDecl(ready_buffer_fd_lookup, "ReadyBufferFdLookupDisposition"));
    try std.testing.expect(@hasDecl(ready_buffer_fd_lookup, "ReadyBufferFdLookupSummary"));
    try std.testing.expect(@hasDecl(ready_buffer_fd_lookup, "summarizeReadyBufferFdLookupAtAttempt"));
    try std.testing.expect(@hasDecl(ready_buffer_fd_lookup, "resolveReadyBufferFdLookup"));
    try std.testing.expect(@hasDecl(ready_buffer_fd_lookup, "resolveReadyBufferFdAtAttempt"));
    try std.testing.expect(@hasDecl(ready_buffer_fd_lookup, "resolveReadyBufferFdLookupReturn"));
    try std.testing.expect(@hasDecl(ready_buffer_fd_lookup, "resolveReadyBufferFdLookupReturnAtAttempt"));
}

test "phase8 ready-buffer fd helpers keep typed summary outputs stable" {
    const buffers = [_]perf_buffer_poll.BufferObservation{
        .{},
        .{ .ready = true },
        .{},
        .{ .ready = true },
    };
    const buffer_fds = [_]?i32{ null, 9, null, 21 };

    const first = ready_buffer_fd_lookup.summarizeReadyBufferFdLookupAtAttempt(&buffers, &buffer_fds, 0);
    try std.testing.expectEqual(
        ready_buffer_fd_lookup.ReadyBufferFdLookupDisposition.found_fd,
        first.disposition,
    );
    try std.testing.expectEqual(@as(?usize, 1), first.ready_index);
    try std.testing.expectEqual(@as(?i32, 9), first.fd);

    const second = ready_buffer_fd_lookup.summarizeReadyBufferFdLookupAtAttempt(&buffers, &buffer_fds, 1);
    try std.testing.expectEqual(
        ready_buffer_fd_lookup.ReadyBufferFdLookupDisposition.found_fd,
        second.disposition,
    );
    try std.testing.expectEqual(@as(?usize, 3), second.ready_index);
    try std.testing.expectEqual(@as(?i32, 21), second.fd);

    const missing = ready_buffer_fd_lookup.summarizeReadyBufferFdLookupAtAttempt(&buffers, &buffer_fds, 2);
    try std.testing.expectEqual(
        ready_buffer_fd_lookup.ReadyBufferFdLookupDisposition.missing_ready_buffer,
        missing.disposition,
    );
    try std.testing.expectEqual(@as(?usize, null), missing.ready_index);
    try std.testing.expectEqual(@as(?i32, null), missing.fd);
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
        try ready_buffer_fd_lookup.resolveReadyBufferFdAtAttempt(&buffers, &buffer_fds, 0),
    );
    try std.testing.expectEqual(
        @as(i32, 21),
        try ready_buffer_fd_lookup.resolveReadyBufferFdAtAttempt(&buffers, &buffer_fds, 1),
    );
    try std.testing.expectError(
        error.MissingReadyBuffer,
        ready_buffer_fd_lookup.resolveReadyBufferFdAtAttempt(&buffers, &buffer_fds, 2),
    );

    const short_fds = [_]?i32{ null, 9 };
    try std.testing.expectError(
        error.InvalidIndex,
        ready_buffer_fd_lookup.resolveReadyBufferFdAtAttempt(&buffers, &short_fds, 1),
    );

    const missing_fd = [_]?i32{ null, 9, null, null };
    try std.testing.expectError(
        error.MissingFd,
        ready_buffer_fd_lookup.resolveReadyBufferFdAtAttempt(&buffers, &missing_fd, 1),
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
        ready_buffer_fd_lookup.resolveReadyBufferFdLookupReturnAtAttempt(&buffers, &buffer_fds, 0),
    );
    try std.testing.expectEqual(
        @as(i32, 21),
        ready_buffer_fd_lookup.resolveReadyBufferFdLookupReturnAtAttempt(&buffers, &buffer_fds, 1),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        ready_buffer_fd_lookup.resolveReadyBufferFdLookupReturnAtAttempt(&buffers, &buffer_fds, 2),
    );

    const short_fds = [_]?i32{ null, 9 };
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        ready_buffer_fd_lookup.resolveReadyBufferFdLookupReturnAtAttempt(&buffers, &short_fds, 1),
    );

    const missing_fd = [_]?i32{ null, 9, null, null };
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        ready_buffer_fd_lookup.resolveReadyBufferFdLookupReturnAtAttempt(&buffers, &missing_fd, 1),
    );
}
