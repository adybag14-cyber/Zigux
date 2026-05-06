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

pub const BufferFdObservation = struct {
    fd: ?i32 = null,
};

pub const BufferFdLookup = union(enum) {
    buffer_fd: i32,
    invalid_index,
    missing_buffer_fd,
};

pub const BufferFdDisposition = enum {
    buffer_fd,
    invalid_index,
    missing_buffer_fd,
};

pub const BufferFdResult = struct {
    disposition: BufferFdDisposition,
    return_value: i32,
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
    first_process_error: ?i32,
};

pub const PollReturnDisposition = enum {
    ready_count,
    interrupted_error,
    wait_error,
    processing_error,
};

pub const PollExecutionResult = struct {
    execution: PollExecutionSummary,
    disposition: PollReturnDisposition,
    return_value: i32,
};

pub const PollError = error{
    InvalidTimeout,
    ObservedReadyEventsExceedBufferObservationCount,
    ReadyCountExceedsObservedEvents,
    ReadyEventsMissingReadyBuffer,
    TimeoutObservationHasReadyBuffer,
    InterruptedObservationHasReadyBuffer,
    FailedObservationHasBufferState,
    ReadyBufferProcessingExceedsReadyCount,
    ReadyBufferProcessingExceedsObservedEvents,
    NonReadyWaitHasProcessedRecords,
    FailedWaitMissingError,
};

fn hasAnyBufferState(summary: ReadyBufferSummary) bool {
    return summary.ready_count != 0 or summary.first_error != null;
}

pub fn classifyObservedWaitResult(wait_result: i32) WaitObservation {
    if (wait_result == 0) {
        return .timed_out;
    }
    if (wait_result > 0) {
        return .{ .ready_events = @intCast(wait_result) };
    }
    if (wait_result == -@as(i32, @intFromEnum(std.os.linux.E.INTR))) {
        return .interrupted;
    }

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

pub fn summarizeReadyBuffers(buffers: []const BufferObservation) ReadyBufferSummary {
    var ready_count: usize = 0;
    var first_ready_index: ?usize = null;
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

pub fn lookupBufferFd(buffers: []const BufferFdObservation, buffer_index: usize) BufferFdLookup {
    if (buffer_index >= buffers.len) {
        return .invalid_index;
    }

    const fd = buffers[buffer_index].fd orelse return .missing_buffer_fd;
    return .{ .buffer_fd = fd };
}

pub fn resolveBufferFdResult(lookup: BufferFdLookup) BufferFdResult {
    return switch (lookup) {
        .buffer_fd => |fd| .{
            .disposition = .buffer_fd,
            .return_value = fd,
        },
        .invalid_index => .{
            .disposition = .invalid_index,
            .return_value = -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        },
        .missing_buffer_fd => .{
            .disposition = .missing_buffer_fd,
            .return_value = -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        },
    };
}

pub fn resolveBufferFdResultFromSlots(
    buffers: []const BufferFdObservation,
    buffer_index: usize,
) BufferFdResult {
    return resolveBufferFdResult(lookupBufferFd(buffers, buffer_index));
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
            if (observed_ready_events > buffers.len) {
                return PollError.ObservedReadyEventsExceedBufferObservationCount;
            }
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

    switch (poll.outcome) {
        .ready => {
            if (process.attempted_count > poll.ready_count) {
                return PollError.ReadyBufferProcessingExceedsReadyCount;
            }
            if (process.attempted_count > poll.observed_ready_events) {
                return PollError.ReadyBufferProcessingExceedsObservedEvents;
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

pub fn resolvePollExecutionResult(execution: PollExecutionSummary) PollError!PollExecutionResult {
    return switch (execution.poll.outcome) {
        .ready => {
            if (execution.first_process_error) |err| {
                return .{
                    .execution = execution,
                    .disposition = .processing_error,
                    .return_value = err,
                };
            }

            return .{
                .execution = execution,
                .disposition = .ready_count,
                .return_value = @intCast(execution.poll.observed_ready_events),
            };
        },
        .timeout => .{
            .execution = execution,
            .disposition = .ready_count,
            .return_value = 0,
        },
        .interrupted => .{
            .execution = execution,
            .disposition = .interrupted_error,
            .return_value = -@as(i32, @intFromEnum(std.os.linux.E.INTR)),
        },
        .failed => {
            const err = execution.poll.first_error orelse return PollError.FailedWaitMissingError;
            return .{
                .execution = execution,
                .disposition = .wait_error,
                .return_value = err,
            };
        },
    };
}

pub fn resolvePollExecutionResultFromWaitResult(
    timeout_ms: i32,
    wait_result: i32,
    buffers: []const BufferObservation,
    process_observations: []const ProcessRecordObservation,
) PollError!PollExecutionResult {
    return resolvePollExecutionResult(try summarizePollExecutionFromWaitResult(
        timeout_ms,
        wait_result,
        buffers,
        process_observations,
    ));
}

pub fn summarizePollExecutionResultFromWaitResult(
    timeout_ms: i32,
    wait_result: i32,
    buffers: []const BufferObservation,
    process_observations: []const ProcessRecordObservation,
) PollError!PollExecutionResult {
    return resolvePollExecutionResultFromWaitResult(
        timeout_ms,
        wait_result,
        buffers,
        process_observations,
    );
}

test "classifyWaitClass keeps perf_buffer__poll timeout classes explicit" {
    try std.testing.expectEqual(WaitClass.indefinite, try classifyWaitClass(-1));
    try std.testing.expectEqual(WaitClass.nonblocking, try classifyWaitClass(0));
    try std.testing.expectEqual(WaitClass.bounded, try classifyWaitClass(25));
    try std.testing.expectError(PollError.InvalidTimeout, classifyWaitClass(-2));
}

test "classifyObservedWaitResult keeps normalized wait outcomes compact before buffer bookkeeping" {
    try std.testing.expectEqualDeep(WaitObservation.timed_out, classifyObservedWaitResult(0));
    try std.testing.expectEqualDeep(WaitObservation{ .ready_events = 3 }, classifyObservedWaitResult(3));
    try std.testing.expectEqualDeep(
        WaitObservation.interrupted,
        classifyObservedWaitResult(-@as(i32, @intFromEnum(std.os.linux.E.INTR))),
    );
    try std.testing.expectEqualDeep(WaitObservation{ .failed = -5 }, classifyObservedWaitResult(-5));
}

test "summarizeReadyBuffers counts ready buffers and preserves the first error" {
    const buffers = [_]BufferObservation{
        .{},
        .{ .ready = true },
        .{ .error_code = -11 },
        .{ .ready = true, .error_code = -32 },
    };
    const summary = summarizeReadyBuffers(&buffers);

    try std.testing.expectEqual(@as(usize, 2), summary.ready_count);
    try std.testing.expectEqual(@as(?usize, 1), summary.first_ready_index);
    try std.testing.expectEqual(@as(?i32, -11), summary.first_error);
}

test "lookupBufferFd keeps perf_buffer__buffer_fd slot selection explicit" {
    const buffers = [_]BufferFdObservation{
        .{ .fd = 17 },
        .{},
        .{ .fd = 42 },
    };

    try std.testing.expectEqualDeep(
        BufferFdLookup{ .buffer_fd = 17 },
        lookupBufferFd(&buffers, 0),
    );
    try std.testing.expectEqualDeep(BufferFdLookup.missing_buffer_fd, lookupBufferFd(&buffers, 1));
    try std.testing.expectEqualDeep(BufferFdLookup.invalid_index, lookupBufferFd(&buffers, 3));
}

test "resolveBufferFdResult keeps perf_buffer__buffer_fd return shaping explicit" {
    const buffers = [_]BufferFdObservation{
        .{ .fd = 17 },
        .{},
        .{ .fd = 42 },
    };

    const success = resolveBufferFdResultFromSlots(&buffers, 2);
    try std.testing.expectEqual(BufferFdDisposition.buffer_fd, success.disposition);
    try std.testing.expectEqual(@as(i32, 42), success.return_value);

    const missing = resolveBufferFdResultFromSlots(&buffers, 1);
    try std.testing.expectEqual(BufferFdDisposition.missing_buffer_fd, missing.disposition);
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        missing.return_value,
    );

    const invalid = resolveBufferFdResultFromSlots(&buffers, 4);
    try std.testing.expectEqual(BufferFdDisposition.invalid_index, invalid.disposition);
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        invalid.return_value,
    );
}

test "summarizePoll keeps bounded ready observations compact and reviewable" {
    const buffers = [_]BufferObservation{
        .{ .ready = true },
        .{ .error_code = -32 },
        .{ .ready = true },
    };
    const summary = try summarizePoll(10, .{ .ready_events = 3 }, &buffers);

    try std.testing.expectEqual(WaitClass.bounded, summary.wait_class);
    try std.testing.expectEqual(PollOutcome.ready, summary.outcome);
    try std.testing.expectEqual(@as(usize, 3), summary.observed_ready_events);
    try std.testing.expectEqual(@as(usize, 2), summary.ready_count);
    try std.testing.expectEqual(@as(?usize, 0), summary.first_ready_index);
    try std.testing.expectEqual(@as(?i32, -32), summary.first_error);
}

test "summarizePollFromWaitResult keeps raw wait-result normalization coupled to the bounded buffer summary" {
    const buffers = [_]BufferObservation{
        .{ .ready = true },
        .{ .error_code = -32 },
        .{ .ready = true },
    };
    const summary = try summarizePollFromWaitResult(10, 3, &buffers);

    try std.testing.expectEqual(WaitClass.bounded, summary.wait_class);
    try std.testing.expectEqual(PollOutcome.ready, summary.outcome);
    try std.testing.expectEqual(@as(usize, 3), summary.observed_ready_events);
    try std.testing.expectEqual(@as(usize, 2), summary.ready_count);
    try std.testing.expectEqual(@as(?usize, 0), summary.first_ready_index);
    try std.testing.expectEqual(@as(?i32, -32), summary.first_error);
}

test "summarizePoll rejects more observed ready events than buffer observations" {
    try std.testing.expectError(
        PollError.ObservedReadyEventsExceedBufferObservationCount,
        summarizePoll(5, .{ .ready_events = 2 }, &.{.{ .ready = true }}),
    );
    try std.testing.expectError(
        PollError.ObservedReadyEventsExceedBufferObservationCount,
        summarizePollFromWaitResult(5, 2, &.{.{ .ready = true }}),
    );
}

test "summarizePoll keeps timeout interruption and missing-ready mismatches explicit" {
    const idle_buffers = [_]BufferObservation{ .{}, .{} };
    const timeout_summary = try summarizePoll(0, .timed_out, &idle_buffers);
    try std.testing.expectEqual(WaitClass.nonblocking, timeout_summary.wait_class);
    try std.testing.expectEqual(PollOutcome.timeout, timeout_summary.outcome);

    const interrupted_summary = try summarizePoll(-1, .interrupted, &idle_buffers);
    try std.testing.expectEqual(WaitClass.indefinite, interrupted_summary.wait_class);
    try std.testing.expectEqual(PollOutcome.interrupted, interrupted_summary.outcome);

    const error_only = [_]BufferObservation{.{ .error_code = -22 }};
    const failed_summary = try summarizePoll(5, .{ .ready_events = 1 }, &error_only);
    try std.testing.expectEqual(PollOutcome.failed, failed_summary.outcome);
    try std.testing.expectEqual(@as(?i32, -22), failed_summary.first_error);

    try std.testing.expectError(
        PollError.ReadyEventsMissingReadyBuffer,
        summarizePoll(5, .{ .ready_events = 1 }, &idle_buffers),
    );
}

test "summarizeProcessRecords keeps perf_buffer__process_records fail-fast ordering and processed record totals explicit" {
    const failure = summarizeProcessRecords(&.{
        .{ .records_processed = 4 },
        .{ .records_processed = 3 },
        .{ .result = -22 },
        .{ .result = -5, .records_processed = 9 },
    });
    try std.testing.expectEqual(@as(usize, 3), failure.attempted_count);
    try std.testing.expectEqual(@as(usize, 2), failure.completed_count);
    try std.testing.expectEqual(@as(usize, 7), failure.processed_record_count);
    try std.testing.expectEqual(@as(?usize, 2), failure.first_error_index);
    try std.testing.expectEqual(@as(?i32, -22), failure.first_error);

    const success = summarizeProcessRecords(&.{
        .{ .records_processed = 1 },
        .{ .records_processed = 2 },
        .{ .records_processed = 3 },
    });
    try std.testing.expectEqual(@as(usize, 3), success.attempted_count);
    try std.testing.expectEqual(@as(usize, 3), success.completed_count);
    try std.testing.expectEqual(@as(usize, 6), success.processed_record_count);
    try std.testing.expectEqual(@as(?usize, null), success.first_error_index);
    try std.testing.expectEqual(@as(?i32, null), success.first_error);
}

test "summarizePollExecution keeps ready-buffer processing inside the observed epoll budget" {
    const buffers = [_]BufferObservation{
        .{ .ready = true },
        .{ .ready = true },
        .{ .error_code = -32 },
    };
    const summary = try summarizePollExecution(12, .{ .ready_events = 3 }, &buffers, &.{
        .{ .records_processed = 4 },
        .{ .result = -11 },
        .{ .records_processed = 9 },
    });

    try std.testing.expectEqual(PollOutcome.ready, summary.poll.outcome);
    try std.testing.expectEqual(@as(usize, 2), summary.attempted_ready_buffer_count);
    try std.testing.expectEqual(@as(usize, 1), summary.completed_ready_buffer_count);
    try std.testing.expectEqual(@as(usize, 4), summary.processed_record_count);
    try std.testing.expectEqual(@as(?usize, 1), summary.first_process_error_index);
    try std.testing.expectEqual(@as(?i32, -11), summary.first_process_error);
}

test "summarizePollExecution rejects process attempts beyond counted ready buffers" {
    try std.testing.expectError(
        PollError.ReadyBufferProcessingExceedsReadyCount,
        summarizePollExecution(5, .{ .ready_events = 3 }, &.{
            .{ .ready = true },
            .{},
            .{ .error_code = -32 },
        }, &.{
            .{ .records_processed = 1 },
            .{ .records_processed = 2 },
        }),
    );
}

test "summarizePollExecutionFromWaitResult keeps raw wait-result normalization coupled to execution bookkeeping" {
    const buffers = [_]BufferObservation{
        .{ .ready = true },
        .{ .ready = true },
        .{ .error_code = -32 },
    };
    const summary = try summarizePollExecutionFromWaitResult(12, 3, &buffers, &.{
        .{ .records_processed = 4 },
        .{ .result = -11 },
        .{ .records_processed = 9 },
    });

    try std.testing.expectEqual(PollOutcome.ready, summary.poll.outcome);
    try std.testing.expectEqual(@as(usize, 2), summary.attempted_ready_buffer_count);
    try std.testing.expectEqual(@as(usize, 1), summary.completed_ready_buffer_count);
    try std.testing.expectEqual(@as(usize, 4), summary.processed_record_count);
    try std.testing.expectEqual(@as(?usize, 1), summary.first_process_error_index);
    try std.testing.expectEqual(@as(?i32, -11), summary.first_process_error);
}

test "resolvePollExecutionResult keeps perf_buffer__poll return-path choices explicit" {
    const successful_execution = try summarizePollExecution(12, .{ .ready_events = 3 }, &.{
        .{ .ready = true },
        .{ .ready = true },
        .{ .error_code = -32 },
    }, &.{
        .{ .records_processed = 4 },
        .{ .records_processed = 2 },
    });
    const successful_result = try resolvePollExecutionResult(successful_execution);
    try std.testing.expectEqual(PollReturnDisposition.ready_count, successful_result.disposition);
    try std.testing.expectEqual(@as(i32, 3), successful_result.return_value);

    const failed_execution = try summarizePollExecution(12, .{ .ready_events = 3 }, &.{
        .{ .ready = true },
        .{ .ready = true },
        .{ .error_code = -32 },
    }, &.{
        .{ .records_processed = 4 },
        .{ .result = -11 },
    });
    const failed_result = try resolvePollExecutionResult(failed_execution);
    try std.testing.expectEqual(PollReturnDisposition.processing_error, failed_result.disposition);
    try std.testing.expectEqual(@as(i32, -11), failed_result.return_value);
}

test "summarizePollExecutionResultFromWaitResult keeps ready-count versus first-processing-failure return rules explicit" {
    const successful_result = try summarizePollExecutionResultFromWaitResult(12, 3, &.{
        .{ .ready = true },
        .{ .ready = true },
        .{ .error_code = -32 },
    }, &.{
        .{ .records_processed = 4 },
        .{ .records_processed = 2 },
    });
    try std.testing.expectEqual(PollReturnDisposition.ready_count, successful_result.disposition);
    try std.testing.expectEqual(@as(i32, 3), successful_result.return_value);

    const failed_result = try summarizePollExecutionResultFromWaitResult(12, 3, &.{
        .{ .ready = true },
        .{ .ready = true },
        .{ .error_code = -32 },
    }, &.{
        .{ .records_processed = 4 },
        .{ .result = -11 },
    });
    try std.testing.expectEqual(PollReturnDisposition.processing_error, failed_result.disposition);
    try std.testing.expectEqual(@as(i32, -11), failed_result.return_value);
}

test "summarizePollExecution rejects impossible processing outside the live perf_buffer__poll wait result" {
    try std.testing.expectError(
        PollError.NonReadyWaitHasProcessedRecords,
        summarizePollExecution(0, .timed_out, &.{}, &.{.{ .records_processed = 1 }}),
    );
    try std.testing.expectError(
        PollError.NonReadyWaitHasProcessedRecords,
        summarizePollExecution(-1, .interrupted, &.{}, &.{.{ .records_processed = 1 }}),
    );
    try std.testing.expectError(
        PollError.ReadyBufferProcessingExceedsReadyCount,
        summarizePollExecution(5, .{ .ready_events = 1 }, &.{.{ .ready = true }}, &.{
            .{ .records_processed = 1 },
            .{ .records_processed = 2 },
        }),
    );
}

test "resolvePollExecutionResult keeps interrupted and failed wait outcomes explicit" {
    const interrupted_result = try resolvePollExecutionResult(try summarizePollExecution(
        -1,
        .interrupted,
        &.{},
        &.{},
    ));
    try std.testing.expectEqual(PollReturnDisposition.interrupted_error, interrupted_result.disposition);
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INTR)),
        interrupted_result.return_value,
    );

    const failed_result = try resolvePollExecutionResult(try summarizePollExecution(
        5,
        .{ .failed = -22 },
        &.{},
        &.{},
    ));
    try std.testing.expectEqual(PollReturnDisposition.wait_error, failed_result.disposition);
    try std.testing.expectEqual(@as(i32, -22), failed_result.return_value);

    try std.testing.expectError(
        PollError.FailedWaitMissingError,
        resolvePollExecutionResult(.{
            .poll = .{
                .wait_class = .bounded,
                .outcome = .failed,
                .observed_ready_events = 0,
                .ready_count = 0,
                .first_ready_index = null,
                .first_error = null,
            },
            .attempted_ready_buffer_count = 0,
            .completed_ready_buffer_count = 0,
            .processed_record_count = 0,
            .first_process_error_index = null,
            .first_process_error = null,
        }),
    );
}

test "summarizePoll rejects impossible buffer state for timeout interrupt and failed wait results" {
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
