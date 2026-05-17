const std = @import("std");

pub const WaitClass = enum {
    nonblocking,
    bounded,
    indefinite,
};

pub const PollOutcome = enum {
    ready,
    timeout,
    interrupted,
    failed,
};

pub const PollReturnDisposition = enum {
    ready_count,
    timed_out,
    interrupted,
    wait_failed,
    buffer_state_failed,
    processing_failed,
};

pub const BufferObservation = struct {
    ready: bool = false,
    error_code: ?i32 = null,
};

pub const WaitObservation = union(enum) {
    timed_out,
    interrupted,
    ready_events: usize,
    failed: i32,
};

pub const ReadyBufferCursor = struct {
    start_index: usize,
    next_scan_index: usize,
    ready_index: ?usize,
    skipped_nonready_count: usize,
};

pub const ReadyBufferSummary = struct {
    ready_count: usize,
    first_ready_index: ?usize,
    first_error: ?i32,
};

pub const ProcessRecordObservation = struct {
    result: i32 = 0,
    records_processed: usize = 0,
};

pub const ProcessRecordSummary = struct {
    attempted_count: usize,
    completed_count: usize,
    processed_record_count: usize,
    first_error_index: ?usize,
    first_error: ?i32,
};

pub const PollSummary = struct {
    wait_class: WaitClass,
    outcome: PollOutcome,
    observed_ready_events: usize,
    ready_count: usize,
    first_ready_index: ?usize,
    first_error: ?i32,
};

pub const PollExecutionSummary = struct {
    poll: PollSummary,
    attempted_ready_buffer_count: usize,
    completed_ready_buffer_count: usize,
    processed_record_count: usize,
    first_process_error_index: ?usize,
    first_process_error_ready_index: ?usize,
    first_process_error: ?i32,
};

pub const PollExecutionResult = struct {
    execution: PollExecutionSummary,
    return_value: i32,
    disposition: PollReturnDisposition,
};

pub const BufferFdLookupDisposition = enum {
    found_fd,
    invalid_index,
    missing_fd,
};

pub const BufferFdLookupSummary = struct {
    slot_count: usize,
    requested_index: usize,
    fd: ?i32,
    disposition: BufferFdLookupDisposition,
};

pub const BufferWindowObservation = struct {
    mapped_size: usize = 0,
};

pub const BufferWindowLookupDisposition = enum {
    found_window,
    invalid_index,
    missing_window,
};

pub const BufferWindowLookupSummary = struct {
    slot_count: usize,
    requested_index: usize,
    mapped_size: ?usize,
    disposition: BufferWindowLookupDisposition,
};

pub const PollError = error{
    InvalidTimeout,
    ReadyCountExceedsObservedEvents,
    ReadyEventsMissingReadyBuffer,
    TimeoutObservationHasReadyBuffer,
    InterruptedObservationHasReadyBuffer,
    FailedObservationHasBufferState,
    ReadyBufferProcessingExceedsReadyCount,
    ReadyBufferProcessingExceedsObservedEvents,
    NonReadyWaitHasProcessedRecords,
    InconsistentProcessingFailureSummary,
    InconsistentProcessingAccountingSummary,
    WaitResultDisagreesWithExecutionOutcome,
    WaitResultDisagreesWithReadyEventCount,
    WaitResultDisagreesWithFailureCode,
};

fn hasAnyBufferState(summary: ReadyBufferSummary) bool {
    return summary.ready_count != 0 or summary.first_error != null;
}

fn hasConsistentProcessFailure(summary: PollExecutionSummary) bool {
    return (summary.first_process_error_index == null) == (summary.first_process_error == null) and
        (summary.first_process_error_index == null) == (summary.first_process_error_ready_index == null);
}

fn hasConsistentProcessAccounting(summary: PollExecutionSummary) bool {
    return switch (summary.poll.outcome) {
        .timeout, .interrupted, .failed => summary.attempted_ready_buffer_count == 0 and
            summary.completed_ready_buffer_count == 0 and
            summary.processed_record_count == 0 and
            summary.first_process_error_index == null and
            summary.first_process_error_ready_index == null and
            summary.first_process_error == null,
        .ready => blk: {
            if (summary.poll.ready_count == 0) break :blk false;
            if (summary.poll.first_ready_index == null) break :blk false;
            if (summary.poll.observed_ready_events == 0) break :blk false;
            if (summary.attempted_ready_buffer_count == 0) break :blk false;
            if (summary.attempted_ready_buffer_count > summary.poll.ready_count) break :blk false;
            if (summary.attempted_ready_buffer_count > summary.poll.observed_ready_events) break :blk false;
            if (summary.completed_ready_buffer_count > summary.attempted_ready_buffer_count) break :blk false;
            if (summary.completed_ready_buffer_count == 0 and summary.processed_record_count != 0) break :blk false;

            if (summary.first_process_error_index) |index| {
                break :blk summary.first_process_error != null and
                    summary.first_process_error_ready_index != null and
                    summary.completed_ready_buffer_count < summary.attempted_ready_buffer_count and
                    summary.attempted_ready_buffer_count == index + 1 and
                    index == summary.completed_ready_buffer_count;
            }

            break :blk summary.first_process_error == null and
                summary.first_process_error_ready_index == null and
                summary.completed_ready_buffer_count == summary.attempted_ready_buffer_count;
        },
    };
}

pub fn classifyObservedWaitResult(wait_result: i32) WaitObservation {
    if (wait_result == 0) return .timed_out;
    if (wait_result > 0) return .{ .ready_events = @intCast(wait_result) };
    if (wait_result == -@as(i32, @intFromEnum(std.os.linux.E.INTR))) return .interrupted;
    return .{ .failed = wait_result };
}

pub fn classifyWaitClass(timeout_ms: i32) PollError!WaitClass {
    return switch (timeout_ms) {
        -1 => .indefinite,
        0 => .nonblocking,
        1...std.math.maxInt(i32) => .bounded,
        else => PollError.InvalidTimeout,
    };
}

pub fn advanceReadyBufferCursor(
    buffers: []const BufferObservation,
    start_index: usize,
) ReadyBufferCursor {
    if (start_index >= buffers.len) {
        return .{
            .start_index = start_index,
            .next_scan_index = buffers.len,
            .ready_index = null,
            .skipped_nonready_count = 0,
        };
    }

    var index = start_index;
    while (index < buffers.len) : (index += 1) {
        if (buffers[index].ready) {
            return .{
                .start_index = start_index,
                .next_scan_index = index + 1,
                .ready_index = index,
                .skipped_nonready_count = index - start_index,
            };
        }
    }

    return .{
        .start_index = start_index,
        .next_scan_index = buffers.len,
        .ready_index = null,
        .skipped_nonready_count = buffers.len - start_index,
    };
}

pub fn resolveReadyBufferAttemptIndex(
    buffers: []const BufferObservation,
    attempt_index: usize,
) ?usize {
    var next_scan_index: usize = 0;
    var remaining = attempt_index;

    while (next_scan_index < buffers.len) {
        const cursor = advanceReadyBufferCursor(buffers, next_scan_index);
        const ready_index = cursor.ready_index orelse return null;
        if (remaining == 0) return ready_index;
        remaining -= 1;
        next_scan_index = cursor.next_scan_index;
    }

    return null;
}

pub fn summarizeReadyBuffers(buffers: []const BufferObservation) ReadyBufferSummary {
    const cursor = advanceReadyBufferCursor(buffers, 0);
    var ready_count: usize = 0;
    var first_ready_index = cursor.ready_index;
    var first_error: ?i32 = null;

    for (buffers, 0..) |buffer, index| {
        if (buffer.ready) {
            ready_count += 1;
            if (first_ready_index == null) first_ready_index = index;
        }
        if (first_error == null and buffer.error_code != null) {
            first_error = buffer.error_code;
        }
    }

    return .{
        .ready_count = ready_count,
        .first_ready_index = first_ready_index,
        .first_error = first_error,
    };
}

pub fn summarizeProcessRecords(observations: []const ProcessRecordObservation) ProcessRecordSummary {
    var completed_count: usize = 0;
    var processed_record_count: usize = 0;

    for (observations, 0..) |observation, index| {
        if (observation.result != 0) {
            return .{
                .attempted_count = index + 1,
                .completed_count = completed_count,
                .processed_record_count = processed_record_count,
                .first_error_index = index,
                .first_error = observation.result,
            };
        }

        completed_count += 1;
        processed_record_count += observation.records_processed;
    }

    return .{
        .attempted_count = observations.len,
        .completed_count = completed_count,
        .processed_record_count = processed_record_count,
        .first_error_index = null,
        .first_error = null,
    };
}

pub fn summarizePoll(
    timeout_ms: i32,
    observation: WaitObservation,
    buffers: []const BufferObservation,
) PollError!PollSummary {
    const wait_class = try classifyWaitClass(timeout_ms);
    const ready = summarizeReadyBuffers(buffers);

    return switch (observation) {
        .timed_out => {
            if (hasAnyBufferState(ready)) return PollError.TimeoutObservationHasReadyBuffer;
            return .{
                .wait_class = wait_class,
                .outcome = .timeout,
                .observed_ready_events = 0,
                .ready_count = 0,
                .first_ready_index = null,
                .first_error = null,
            };
        },
        .interrupted => {
            if (hasAnyBufferState(ready)) return PollError.InterruptedObservationHasReadyBuffer;
            return .{
                .wait_class = wait_class,
                .outcome = .interrupted,
                .observed_ready_events = 0,
                .ready_count = 0,
                .first_ready_index = null,
                .first_error = null,
            };
        },
        .failed => |err_code| {
            if (hasAnyBufferState(ready)) return PollError.FailedObservationHasBufferState;
            return .{
                .wait_class = wait_class,
                .outcome = .failed,
                .observed_ready_events = 0,
                .ready_count = 0,
                .first_ready_index = null,
                .first_error = err_code,
            };
        },
        .ready_events => |observed_ready_events| blk: {
            if (ready.ready_count > observed_ready_events) {
                return PollError.ReadyCountExceedsObservedEvents;
            }
            if (ready.ready_count == 0) {
                if (ready.first_error != null) {
                    break :blk .{
                        .wait_class = wait_class,
                        .outcome = .failed,
                        .observed_ready_events = observed_ready_events,
                        .ready_count = 0,
                        .first_ready_index = null,
                        .first_error = ready.first_error,
                    };
                }
                return PollError.ReadyEventsMissingReadyBuffer;
            }
            break :blk .{
                .wait_class = wait_class,
                .outcome = .ready,
                .observed_ready_events = observed_ready_events,
                .ready_count = ready.ready_count,
                .first_ready_index = ready.first_ready_index,
                .first_error = ready.first_error,
            };
        },
    };
}

pub fn summarizePollFromWaitResult(
    timeout_ms: i32,
    wait_result: i32,
    buffers: []const BufferObservation,
) PollError!PollSummary {
    return summarizePoll(timeout_ms, classifyObservedWaitResult(wait_result), buffers);
}

pub fn summarizePollExecution(
    timeout_ms: i32,
    observation: WaitObservation,
    buffers: []const BufferObservation,
    process_observations: []const ProcessRecordObservation,
) PollError!PollExecutionSummary {
    const poll = try summarizePoll(timeout_ms, observation, buffers);
    const process = summarizeProcessRecords(process_observations);
    const first_process_error_ready_index = if (process.first_error_index) |index|
        resolveReadyBufferAttemptIndex(buffers, index)
    else
        null;

    switch (poll.outcome) {
        .ready => {
            if (process.attempted_count > poll.observed_ready_events) {
                return PollError.ReadyBufferProcessingExceedsObservedEvents;
            }
            if (process.attempted_count > poll.ready_count) {
                return PollError.ReadyBufferProcessingExceedsReadyCount;
            }
            if (process.first_error_index != null and first_process_error_ready_index == null) {
                return PollError.ReadyBufferProcessingExceedsReadyCount;
            }
        },
        .timeout, .interrupted, .failed => {
            if (process.attempted_count != 0) {
                return PollError.NonReadyWaitHasProcessedRecords;
            }
        },
    }

    return .{
        .poll = poll,
        .attempted_ready_buffer_count = process.attempted_count,
        .completed_ready_buffer_count = process.completed_count,
        .processed_record_count = process.processed_record_count,
        .first_process_error_index = process.first_error_index,
        .first_process_error_ready_index = first_process_error_ready_index,
        .first_process_error = process.first_error,
    };
}

pub fn summarizePollExecutionFromWaitResult(
    timeout_ms: i32,
    wait_result: i32,
    buffers: []const BufferObservation,
    process_observations: []const ProcessRecordObservation,
) PollError!PollExecutionSummary {
    return summarizePollExecution(
        timeout_ms,
        classifyObservedWaitResult(wait_result),
        buffers,
        process_observations,
    );
}

pub fn resolvePollExecutionResultFromWaitResult(
    wait_result: i32,
    execution: PollExecutionSummary,
) PollError!PollExecutionResult {
    if (!hasConsistentProcessFailure(execution)) {
        return PollError.InconsistentProcessingFailureSummary;
    }
    if (!hasConsistentProcessAccounting(execution)) {
        return PollError.InconsistentProcessingAccountingSummary;
    }

    return switch (classifyObservedWaitResult(wait_result)) {
        .timed_out => {
            if (execution.poll.outcome != .timeout) {
                return PollError.WaitResultDisagreesWithExecutionOutcome;
            }
            return .{
                .execution = execution,
                .return_value = 0,
                .disposition = .timed_out,
            };
        },
        .interrupted => {
            if (execution.poll.outcome != .interrupted) {
                return PollError.WaitResultDisagreesWithExecutionOutcome;
            }
            return .{
                .execution = execution,
                .return_value = wait_result,
                .disposition = .interrupted,
            };
        },
        .failed => |err_code| {
            if (execution.poll.outcome != .failed) {
                return PollError.WaitResultDisagreesWithExecutionOutcome;
            }
            if (execution.poll.first_error != err_code) {
                return PollError.WaitResultDisagreesWithFailureCode;
            }
            return .{
                .execution = execution,
                .return_value = err_code,
                .disposition = .wait_failed,
            };
        },
        .ready_events => |ready_events| {
            if (execution.poll.observed_ready_events != ready_events) {
                return PollError.WaitResultDisagreesWithReadyEventCount;
            }

            return switch (execution.poll.outcome) {
                .ready => .{
                    .execution = execution,
                    .return_value = execution.first_process_error orelse wait_result,
                    .disposition = if (execution.first_process_error == null) .ready_count else .processing_failed,
                },
                .failed => .{
                    .execution = execution,
                    .return_value = execution.poll.first_error.?,
                    .disposition = .buffer_state_failed,
                },
                .timeout, .interrupted => PollError.WaitResultDisagreesWithExecutionOutcome,
            };
        },
    };
}

pub fn summarizePollExecutionResultFromWaitResult(
    timeout_ms: i32,
    wait_result: i32,
    buffers: []const BufferObservation,
    process_observations: []const ProcessRecordObservation,
) PollError!PollExecutionResult {
    return resolvePollExecutionResultFromWaitResult(
        wait_result,
        try summarizePollExecutionFromWaitResult(
            timeout_ms,
            wait_result,
            buffers,
            process_observations,
        ),
    );
}

pub fn summarizeBufferFdLookup(
    buffer_fds: []const ?i32,
    buffer_index: usize,
) BufferFdLookupSummary {
    if (buffer_index >= buffer_fds.len) {
        return .{
            .slot_count = buffer_fds.len,
            .requested_index = buffer_index,
            .fd = null,
            .disposition = .invalid_index,
        };
    }

    return if (buffer_fds[buffer_index]) |fd| .{
        .slot_count = buffer_fds.len,
        .requested_index = buffer_index,
        .fd = fd,
        .disposition = .found_fd,
    } else .{
        .slot_count = buffer_fds.len,
        .requested_index = buffer_index,
        .fd = null,
        .disposition = .missing_fd,
    };
}

pub fn resolveBufferFdLookupReturn(summary: BufferFdLookupSummary) i32 {
    return switch (summary.disposition) {
        .found_fd => summary.fd.?,
        .invalid_index => -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        .missing_fd => -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
    };
}

pub fn summarizeBufferWindowLookup(
    buffer_windows: []const ?BufferWindowObservation,
    buffer_index: usize,
) BufferWindowLookupSummary {
    if (buffer_index >= buffer_windows.len) {
        return .{
            .slot_count = buffer_windows.len,
            .requested_index = buffer_index,
            .mapped_size = null,
            .disposition = .invalid_index,
        };
    }

    return if (buffer_windows[buffer_index]) |window| .{
        .slot_count = buffer_windows.len,
        .requested_index = buffer_index,
        .mapped_size = window.mapped_size,
        .disposition = .found_window,
    } else .{
        .slot_count = buffer_windows.len,
        .requested_index = buffer_index,
        .mapped_size = null,
        .disposition = .missing_window,
    };
}

pub fn resolveBufferWindowLookupReturn(summary: BufferWindowLookupSummary) i32 {
    return switch (summary.disposition) {
        .found_window => 0,
        .invalid_index => -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        .missing_window => -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
    };
}

test "phase8 perf-buffer poll resolves ready-buffer attempt ordinals back to slot indexes" {
    const buffers = [_]BufferObservation{
        .{},
        .{ .ready = true },
        .{},
        .{ .ready = true },
        .{},
    };

    try std.testing.expectEqual(@as(?usize, 1), resolveReadyBufferAttemptIndex(&buffers, 0));
    try std.testing.expectEqual(@as(?usize, 3), resolveReadyBufferAttemptIndex(&buffers, 1));
    try std.testing.expectEqual(@as(?usize, null), resolveReadyBufferAttemptIndex(&buffers, 2));
}

test "phase8 perf-buffer poll keeps ready-count return semantics and process totals separate" {
    const success = try summarizePollExecutionResultFromWaitResult(
        12,
        3,
        &.{
            .{ .ready = true },
            .{ .ready = true },
            .{ .error_code = -32 },
        },
        &.{
            .{ .records_processed = 4 },
            .{ .records_processed = 2 },
        },
    );
    try std.testing.expectEqual(PollReturnDisposition.ready_count, success.disposition);
    try std.testing.expectEqual(@as(i32, 3), success.return_value);
    try std.testing.expectEqual(@as(usize, 6), success.execution.processed_record_count);
}

test "phase8 perf-buffer poll keeps the first processing failure tied to the ready-buffer slot" {
    const failure = try summarizePollExecutionResultFromWaitResult(
        12,
        2,
        &.{
            .{},
            .{ .ready = true },
            .{},
            .{ .ready = true },
        },
        &.{
            .{ .records_processed = 4 },
            .{ .result = -11 },
        },
    );

    try std.testing.expectEqual(PollReturnDisposition.processing_failed, failure.disposition);
    try std.testing.expectEqual(@as(?usize, 1), failure.execution.first_process_error_index);
    try std.testing.expectEqual(@as(?usize, 3), failure.execution.first_process_error_ready_index);
    try std.testing.expectEqual(@as(i32, -11), failure.return_value);
}

test "phase8 perf-buffer poll rejects ready waits without processing attempts" {
    try std.testing.expectError(
        PollError.InconsistentProcessingAccountingSummary,
        summarizePollExecutionResultFromWaitResult(
            12,
            2,
            &.{
                .{ .ready = true },
                .{ .ready = true },
            },
            &.{},
        ),
    );
}

test "phase8 perf-buffer poll keeps buffer lookup returns errno-shaped" {
    const buffer_fds = [_]?i32{ 9, null, 21 };
    try std.testing.expectEqual(
        @as(i32, 21),
        resolveBufferFdLookupReturn(summarizeBufferFdLookup(&buffer_fds, 2)),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        resolveBufferFdLookupReturn(summarizeBufferFdLookup(&buffer_fds, 1)),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        resolveBufferFdLookupReturn(summarizeBufferFdLookup(&buffer_fds, 4)),
    );

    const buffer_windows = [_]?BufferWindowObservation{
        .{ .mapped_size = 4096 },
        null,
        .{ .mapped_size = 8192 },
    };
    try std.testing.expectEqual(
        @as(i32, 0),
        resolveBufferWindowLookupReturn(summarizeBufferWindowLookup(&buffer_windows, 0)),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        resolveBufferWindowLookupReturn(summarizeBufferWindowLookup(&buffer_windows, 1)),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        resolveBufferWindowLookupReturn(summarizeBufferWindowLookup(&buffer_windows, 4)),
    );
}

test "phase8 perf-buffer poll rejects impossible post-wait buffer states" {
    try std.testing.expectError(
        PollError.TimeoutObservationHasReadyBuffer,
        summarizePoll(0, .timed_out, &.{.{ .error_code = -5 }}),
    );
    try std.testing.expectError(
        PollError.InterruptedObservationHasReadyBuffer,
        summarizePoll(-1, .interrupted, &.{.{ .ready = true }}),
    );
    try std.testing.expectError(
        PollError.FailedObservationHasBufferState,
        summarizePoll(5, .{ .failed = -11 }, &.{.{ .error_code = -32 }}),
    );
}

test "phase8 perf-buffer poll rejects mismatched wait-result replays" {
    const ready_execution = try summarizePollExecutionFromWaitResult(
        12,
        2,
        &.{
            .{ .ready = true },
            .{ .ready = true },
        },
        &.{
            .{ .records_processed = 1 },
        },
    );
    try std.testing.expectError(
        PollError.WaitResultDisagreesWithExecutionOutcome,
        resolvePollExecutionResultFromWaitResult(0, ready_execution),
    );
    try std.testing.expectError(
        PollError.WaitResultDisagreesWithReadyEventCount,
        resolvePollExecutionResultFromWaitResult(3, ready_execution),
    );
}
