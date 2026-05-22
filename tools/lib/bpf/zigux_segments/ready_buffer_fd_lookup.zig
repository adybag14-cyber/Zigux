const std = @import("std");
const perf_buffer_poll = @import("perf_buffer_poll.zig");

pub const ReadyBufferFdLookupError =
    perf_buffer_poll.ReadyBufferAttemptLookupError || perf_buffer_poll.BufferFdLookupError;

pub const ReadyBufferFdLookupDisposition = enum {
    found_fd,
    missing_ready_buffer,
    invalid_index,
    missing_fd,
};

pub const ReadyBufferFdLookupSummary = struct {
    requested_attempt_index: usize,
    ready_index: ?usize,
    slot_count: usize,
    fd: ?i32,
    disposition: ReadyBufferFdLookupDisposition,
};

pub fn summarizeReadyBufferFdLookupAtAttempt(
    buffers: []const perf_buffer_poll.BufferObservation,
    buffer_fds: []const ?i32,
    attempt_index: usize,
) ReadyBufferFdLookupSummary {
    const ready_lookup = perf_buffer_poll.summarizeReadyBufferAttemptLookup(buffers, attempt_index);
    const ready_index = ready_lookup.ready_index orelse return .{
        .requested_attempt_index = attempt_index,
        .ready_index = null,
        .slot_count = buffer_fds.len,
        .fd = null,
        .disposition = .missing_ready_buffer,
    };

    const fd_lookup = perf_buffer_poll.summarizeBufferFdLookup(buffer_fds, ready_index);
    return .{
        .requested_attempt_index = attempt_index,
        .ready_index = ready_index,
        .slot_count = fd_lookup.slot_count,
        .fd = fd_lookup.fd,
        .disposition = switch (fd_lookup.disposition) {
            .found_fd => .found_fd,
            .invalid_index => .invalid_index,
            .missing_fd => .missing_fd,
        },
    };
}

pub fn resolveReadyBufferFdLookup(
    summary: ReadyBufferFdLookupSummary,
) ReadyBufferFdLookupError!i32 {
    return switch (summary.disposition) {
        .found_fd => summary.fd.?,
        .missing_ready_buffer => error.MissingReadyBuffer,
        .invalid_index => error.InvalidIndex,
        .missing_fd => error.MissingFd,
    };
}

pub fn resolveReadyBufferFdAtAttempt(
    buffers: []const perf_buffer_poll.BufferObservation,
    buffer_fds: []const ?i32,
    attempt_index: usize,
) ReadyBufferFdLookupError!i32 {
    return resolveReadyBufferFdLookup(
        summarizeReadyBufferFdLookupAtAttempt(buffers, buffer_fds, attempt_index),
    );
}

pub fn resolveReadyBufferFdLookupReturn(summary: ReadyBufferFdLookupSummary) i32 {
    return switch (summary.disposition) {
        .found_fd => summary.fd.?,
        .missing_ready_buffer => -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        .invalid_index => -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        .missing_fd => -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
    };
}

pub fn resolveReadyBufferFdLookupReturnAtAttempt(
    buffers: []const perf_buffer_poll.BufferObservation,
    buffer_fds: []const ?i32,
    attempt_index: usize,
) i32 {
    return resolveReadyBufferFdLookupReturn(
        summarizeReadyBufferFdLookupAtAttempt(buffers, buffer_fds, attempt_index),
    );
}

test "phase8 ready-buffer fd lookup helper keeps typed lookup summaries stable" {
    const buffers = [_]perf_buffer_poll.BufferObservation{
        .{},
        .{ .ready = true },
        .{},
        .{ .ready = true },
    };
    const buffer_fds = [_]?i32{ null, 9, null, 21 };

    const found = summarizeReadyBufferFdLookupAtAttempt(&buffers, &buffer_fds, 1);
    try std.testing.expectEqual(ReadyBufferFdLookupDisposition.found_fd, found.disposition);
    try std.testing.expectEqual(@as(usize, 1), found.requested_attempt_index);
    try std.testing.expectEqual(@as(?usize, 3), found.ready_index);
    try std.testing.expectEqual(@as(usize, 4), found.slot_count);
    try std.testing.expectEqual(@as(?i32, 21), found.fd);

    const missing_ready = summarizeReadyBufferFdLookupAtAttempt(&buffers, &buffer_fds, 2);
    try std.testing.expectEqual(
        ReadyBufferFdLookupDisposition.missing_ready_buffer,
        missing_ready.disposition,
    );
    try std.testing.expectEqual(@as(?usize, null), missing_ready.ready_index);
    try std.testing.expectEqual(@as(usize, 4), missing_ready.slot_count);
    try std.testing.expectEqual(@as(?i32, null), missing_ready.fd);
}

test "phase8 ready-buffer fd lookup helper resolves typed lookups without manual slot plumbing" {
    const buffers = [_]perf_buffer_poll.BufferObservation{
        .{},
        .{ .ready = true },
        .{},
        .{ .ready = true },
    };
    const buffer_fds = [_]?i32{ null, 9, null, 21 };

    try std.testing.expectEqual(
        @as(i32, 9),
        try resolveReadyBufferFdLookup(
            summarizeReadyBufferFdLookupAtAttempt(&buffers, &buffer_fds, 0),
        ),
    );
    try std.testing.expectError(
        error.MissingReadyBuffer,
        resolveReadyBufferFdLookup(
            summarizeReadyBufferFdLookupAtAttempt(&buffers, &buffer_fds, 2),
        ),
    );

    const short_fds = [_]?i32{ null, 9 };
    try std.testing.expectError(
        error.InvalidIndex,
        resolveReadyBufferFdLookup(
            summarizeReadyBufferFdLookupAtAttempt(&buffers, &short_fds, 1),
        ),
    );

    const missing_fd = [_]?i32{ null, 9, null, null };
    try std.testing.expectError(
        error.MissingFd,
        resolveReadyBufferFdLookup(
            summarizeReadyBufferFdLookupAtAttempt(&buffers, &missing_fd, 1),
        ),
    );
}

test "phase8 ready-buffer fd lookup helper keeps errno-shaped outputs stable" {
    const buffers = [_]perf_buffer_poll.BufferObservation{
        .{},
        .{ .ready = true },
        .{},
        .{ .ready = true },
    };
    const buffer_fds = [_]?i32{ null, 9, null, 21 };

    try std.testing.expectEqual(
        @as(i32, 9),
        resolveReadyBufferFdLookupReturnAtAttempt(&buffers, &buffer_fds, 0),
    );
    try std.testing.expectEqual(
        @as(i32, 21),
        resolveReadyBufferFdLookupReturnAtAttempt(&buffers, &buffer_fds, 1),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        resolveReadyBufferFdLookupReturnAtAttempt(&buffers, &buffer_fds, 2),
    );

    const short_fds = [_]?i32{ null, 9 };
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        resolveReadyBufferFdLookupReturnAtAttempt(&buffers, &short_fds, 1),
    );

    const missing_fd = [_]?i32{ null, 9, null, null };
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        resolveReadyBufferFdLookupReturnAtAttempt(&buffers, &missing_fd, 1),
    );
}
