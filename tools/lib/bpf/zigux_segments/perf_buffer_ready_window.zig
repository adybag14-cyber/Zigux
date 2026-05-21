const std = @import("std");
const perf_buffer_poll = @import("perf_buffer_poll.zig");

pub const ReadyBufferWindowLookupError =
    perf_buffer_poll.ReadyBufferAttemptLookupError || perf_buffer_poll.BufferWindowLookupError;

pub const ReadyBufferWindowLookupDisposition = enum {
    found_window,
    missing_ready_buffer,
    invalid_index,
    missing_window,
};

pub const ReadyBufferWindowLookupSummary = struct {
    requested_attempt_index: usize,
    ready_index: ?usize,
    slot_count: usize,
    mapped_size: ?usize,
    disposition: ReadyBufferWindowLookupDisposition,
};

pub fn summarizeReadyBufferWindowLookupAtAttempt(
    buffers: []const perf_buffer_poll.BufferObservation,
    buffer_windows: []const ?perf_buffer_poll.BufferWindowObservation,
    attempt_index: usize,
) ReadyBufferWindowLookupSummary {
    const ready_lookup = perf_buffer_poll.summarizeReadyBufferAttemptLookup(buffers, attempt_index);
    const ready_index = ready_lookup.ready_index orelse return .{
        .requested_attempt_index = attempt_index,
        .ready_index = null,
        .slot_count = buffer_windows.len,
        .mapped_size = null,
        .disposition = .missing_ready_buffer,
    };

    const window_lookup = perf_buffer_poll.summarizeBufferWindowLookup(buffer_windows, ready_index);
    return .{
        .requested_attempt_index = attempt_index,
        .ready_index = ready_index,
        .slot_count = window_lookup.slot_count,
        .mapped_size = window_lookup.mapped_size,
        .disposition = switch (window_lookup.disposition) {
            .found_window => .found_window,
            .invalid_index => .invalid_index,
            .missing_window => .missing_window,
        },
    };
}

pub fn resolveReadyBufferWindowLookup(
    summary: ReadyBufferWindowLookupSummary,
) ReadyBufferWindowLookupError!usize {
    return switch (summary.disposition) {
        .found_window => summary.mapped_size.?,
        .missing_ready_buffer => error.MissingReadyBuffer,
        .invalid_index => error.InvalidIndex,
        .missing_window => error.MissingWindow,
    };
}

pub fn resolveReadyBufferWindowMappedSizeAtAttempt(
    buffers: []const perf_buffer_poll.BufferObservation,
    buffer_windows: []const ?perf_buffer_poll.BufferWindowObservation,
    attempt_index: usize,
) ReadyBufferWindowLookupError!usize {
    return resolveReadyBufferWindowLookup(
        summarizeReadyBufferWindowLookupAtAttempt(buffers, buffer_windows, attempt_index),
    );
}

pub fn resolveReadyBufferWindowMappedSizeReturn(
    summary: ReadyBufferWindowLookupSummary,
) i32 {
    const mapped_size = resolveReadyBufferWindowLookup(summary) catch |err| return switch (err) {
        error.MissingReadyBuffer => -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        error.InvalidIndex => -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        error.MissingWindow => -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
    };
    return std.math.cast(i32, mapped_size) orelse
        -@as(i32, @intFromEnum(std.os.linux.E.OVERFLOW));
}

pub fn resolveReadyBufferWindowMappedSizeReturnAtAttempt(
    buffers: []const perf_buffer_poll.BufferObservation,
    buffer_windows: []const ?perf_buffer_poll.BufferWindowObservation,
    attempt_index: usize,
) i32 {
    return resolveReadyBufferWindowMappedSizeReturn(
        summarizeReadyBufferWindowLookupAtAttempt(buffers, buffer_windows, attempt_index),
    );
}

pub fn resolveReadyBufferWindowLookupReturn(
    summary: ReadyBufferWindowLookupSummary,
) i32 {
    return switch (summary.disposition) {
        .found_window => 0,
        .missing_ready_buffer => -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        .invalid_index => -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        .missing_window => -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
    };
}

pub fn resolveReadyBufferWindowLookupReturnAtAttempt(
    buffers: []const perf_buffer_poll.BufferObservation,
    buffer_windows: []const ?perf_buffer_poll.BufferWindowObservation,
    attempt_index: usize,
) i32 {
    return resolveReadyBufferWindowLookupReturn(
        summarizeReadyBufferWindowLookupAtAttempt(buffers, buffer_windows, attempt_index),
    );
}

test "phase8 perf-buffer ready-window helper keeps typed lookup summaries explicit" {
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

    const found = summarizeReadyBufferWindowLookupAtAttempt(&buffers, &buffer_windows, 1);
    try std.testing.expectEqual(ReadyBufferWindowLookupDisposition.found_window, found.disposition);
    try std.testing.expectEqual(@as(usize, 1), found.requested_attempt_index);
    try std.testing.expectEqual(@as(?usize, 3), found.ready_index);
    try std.testing.expectEqual(@as(usize, 4), found.slot_count);
    try std.testing.expectEqual(@as(?usize, 8192), found.mapped_size);

    const missing_ready = summarizeReadyBufferWindowLookupAtAttempt(&buffers, &buffer_windows, 2);
    try std.testing.expectEqual(
        ReadyBufferWindowLookupDisposition.missing_ready_buffer,
        missing_ready.disposition,
    );
    try std.testing.expectEqual(@as(?usize, null), missing_ready.ready_index);
    try std.testing.expectEqual(@as(usize, 4), missing_ready.slot_count);
    try std.testing.expectEqual(@as(?usize, null), missing_ready.mapped_size);
}

test "phase8 perf-buffer ready-window helper resolves summary lookups without manual slot plumbing" {
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
        try resolveReadyBufferWindowLookup(
            summarizeReadyBufferWindowLookupAtAttempt(&buffers, &buffer_windows, 0),
        ),
    );
    try std.testing.expectError(
        error.MissingReadyBuffer,
        resolveReadyBufferWindowLookup(
            summarizeReadyBufferWindowLookupAtAttempt(&buffers, &buffer_windows, 2),
        ),
    );

    const short_windows = [_]?perf_buffer_poll.BufferWindowObservation{
        null,
        .{ .mapped_size = 4096 },
    };
    try std.testing.expectError(
        error.InvalidIndex,
        resolveReadyBufferWindowLookup(
            summarizeReadyBufferWindowLookupAtAttempt(&buffers, &short_windows, 1),
        ),
    );

    const missing_window = [_]?perf_buffer_poll.BufferWindowObservation{
        null,
        .{ .mapped_size = 4096 },
        null,
        null,
    };
    try std.testing.expectError(
        error.MissingWindow,
        resolveReadyBufferWindowLookup(
            summarizeReadyBufferWindowLookupAtAttempt(&buffers, &missing_window, 1),
        ),
    );
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

test "phase8 perf-buffer ready-window helper keeps mapped-size returns errno-shaped and overflow-aware" {
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
        resolveReadyBufferWindowMappedSizeReturnAtAttempt(&buffers, &buffer_windows, 0),
    );
    try std.testing.expectEqual(
        @as(i32, 8192),
        resolveReadyBufferWindowMappedSizeReturnAtAttempt(&buffers, &buffer_windows, 1),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        resolveReadyBufferWindowMappedSizeReturnAtAttempt(&buffers, &buffer_windows, 2),
    );

    const short_windows = [_]?perf_buffer_poll.BufferWindowObservation{
        null,
        .{ .mapped_size = 4096 },
    };
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        resolveReadyBufferWindowMappedSizeReturnAtAttempt(&buffers, &short_windows, 1),
    );

    const missing_window = [_]?perf_buffer_poll.BufferWindowObservation{
        null,
        .{ .mapped_size = 4096 },
        null,
        null,
    };
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        resolveReadyBufferWindowMappedSizeReturnAtAttempt(&buffers, &missing_window, 1),
    );

    const overflow_windows = [_]?perf_buffer_poll.BufferWindowObservation{
        null,
        .{ .mapped_size = @as(usize, std.math.maxInt(i32)) + 1 },
    };
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.OVERFLOW)),
        resolveReadyBufferWindowMappedSizeReturnAtAttempt(&buffers, &overflow_windows, 0),
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
