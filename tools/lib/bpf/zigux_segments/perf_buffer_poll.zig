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

pub const ReadyBufferSummary = struct {
    ready_count: usize,
    first_ready_index: ?usize,
    first_error: ?i32,
};

pub const ReadyBufferCursor = struct {
    start_index: usize,
    next_scan_index: usize,
    ready_index: ?usize,
    skipped_nonready_count: usize,
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
    WaitResultDisagreesWithExecutionOutcome,
    WaitResultDisagreesWithReadyEventCount,
    WaitResultDisagreesWithFailureCode,
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

    switch (poll.outcome) {
        .ready => {
            if (process.attempted_count > poll.observed_ready_events) {
                return PollError.ReadyBufferProcessingExceedsObservedEvents;
            }
            if (process.attempted_count > poll.ready_count) {
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

test "advanceReadyBufferCursor keeps ordered ready-buffer traversal explicit" {
    const buffers = [_]BufferObservation{
        .{},
        .{ .error_code = -32 },
        .{ .ready = true },
        .{},
        .{ .ready = true, .error_code = -11 },
    };

    const first = advanceReadyBufferCursor(&buffers, 0);
    try std.testing.expectEqual(@as(usize, 0), first.start_index);
    try std.testing.expectEqual(@as(?usize, 2), first.ready_index);
    try std.testing.expectEqual(@as(usize, 3), first.next_scan_index);
    try std.testing.expectEqual(@as(usize, 2), first.skipped_nonready_count);

    const second = advanceReadyBufferCursor(&buffers, first.next_scan_index);
    try std.testing.expectEqual(@as(usize, 3), second.start_index);
    try std.testing.expectEqual(@as(?usize, 4), second.ready_index);
    try std.testing.expectEqual(@as(usize, 5), second.next_scan_index);
    try std.testing.expectEqual(@as(usize, 1), second.skipped_nonready_count);

    const exhausted = advanceReadyBufferCursor(&buffers, second.next_scan_index);
    try std.testing.expectEqual(@as(?usize, null), exhausted.ready_index);
    try std.testing.expectEqual(@as(usize, 5), exhausted.next_scan_index);
    try std.testing.expectEqual(@as(usize, 0), exhausted.skipped_nonready_count);

    const past_end = advanceReadyBufferCursor(&buffers, 9);
    try std.testing.expectEqual(@as(?usize, null), past_end.ready_index);
    try std.testing.expectEqual(@as(usize, 5), past_end.next_scan_index);
    try std.testing.expectEqual(@as(usize, 0), past_end.skipped_nonready_count);
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

test "resolvePollExecutionResultFromWaitResult keeps the final ready-count return and first processing failure explicit" {
    const success = try resolvePollExecutionResultFromWaitResult(3, try summarizePollExecutionFromWaitResult(
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
    ));
    try std.testing.expectEqual(PollReturnDisposition.ready_count, success.disposition);
    try std.testing.expectEqual(@as(i32, 3), success.return_value);

    const processing_failure = try resolvePollExecutionResultFromWaitResult(3, try summarizePollExecutionFromWaitResult(
        12,
        3,
        &.{
            .{ .ready = true },
            .{ .ready = true },
            .{ .error_code = -32 },
        },
        &.{
            .{ .records_processed = 4 },
            .{ .result = -11 },
        },
    ));
    try std.testing.expectEqual(PollReturnDisposition.processing_failed, processing_failure.disposition);
    try std.testing.expectEqual(@as(i32, -11), processing_failure.return_value);
}

test "summarizePollExecutionResultFromWaitResult keeps buffer-state failures explicit when ready events surface only error buffers" {
    const result = try summarizePollExecutionResultFromWaitResult(
        5,
        2,
        &.{
            .{ .error_code = -22 },
            .{ .error_code = -32 },
        },
        &.{},
    );
    try std.testing.expectEqual(PollOutcome.failed, result.execution.poll.outcome);
    try std.testing.expectEqual(PollReturnDisposition.buffer_state_failed, result.disposition);
    try std.testing.expectEqual(@as(i32, -22), result.return_value);
}

test "summarizePollExecutionResultFromWaitResult keeps timeout interrupt and wait failure returns aligned" {
    const timed_out = try summarizePollExecutionResultFromWaitResult(0, 0, &.{}, &.{});
    try std.testing.expectEqual(PollReturnDisposition.timed_out, timed_out.disposition);
    try std.testing.expectEqual(@as(i32, 0), timed_out.return_value);

    const interrupted = try summarizePollExecutionResultFromWaitResult(
        -1,
        -@as(i32, @intFromEnum(std.os.linux.E.INTR)),
        &.{},
        &.{},
    );
    try std.testing.expectEqual(PollReturnDisposition.interrupted, interrupted.disposition);
    try std.testing.expectEqual(-@as(i32, @intFromEnum(std.os.linux.E.INTR)), interrupted.return_value);

    const failed = try summarizePollExecutionResultFromWaitResult(5, -5, &.{}, &.{});
    try std.testing.expectEqual(PollReturnDisposition.wait_failed, failed.disposition);
    try std.testing.expectEqual(@as(i32, -5), failed.return_value);
}

test "resolvePollExecutionResultFromWaitResult rejects mismatched wait-result and execution summaries" {
    const ready_execution = try summarizePollExecutionFromWaitResult(
        12,
        2,
        &.{ .{ .ready = true }, .{ .ready = true } },
        &.{ .{ .records_processed = 1 } },
    );
    try std.testing.expectError(
        PollError.WaitResultDisagreesWithExecutionOutcome,
        resolvePollExecutionResultFromWaitResult(0, ready_execution),
    );

    const failed_execution = try summarizePollExecutionFromWaitResult(5, -5, &.{}, &.{});
    try std.testing.expectError(
        PollError.WaitResultDisagreesWithFailureCode,
        resolvePollExecutionResultFromWaitResult(-9, failed_execution),
    );
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
        PollError.ReadyBufferProcessingExceedsObservedEvents,
        summarizePollExecution(5, .{ .ready_events = 1 }, &.{.{ .ready = true }}, &.{
            .{ .records_processed = 1 },
            .{ .records_processed = 2 },
        }),
    );
}

test "summarizePollExecution rejects processing more ready buffers than the helper counted as ready" {
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

test "summarizeBufferFdLookup keeps perf_buffer__buffer_fd slot classification compact and reviewable" {
    const buffer_fds = [_]?i32{ 11, null, 17 };

    const found = summarizeBufferFdLookup(&buffer_fds, 2);
    try std.testing.expectEqual(BufferFdLookupDisposition.found_fd, found.disposition);
    try std.testing.expectEqual(@as(usize, 3), found.slot_count);
    try std.testing.expectEqual(@as(usize, 2), found.requested_index);
    try std.testing.expectEqual(@as(?i32, 17), found.fd);

    const missing = summarizeBufferFdLookup(&buffer_fds, 1);
    try std.testing.expectEqual(BufferFdLookupDisposition.missing_fd, missing.disposition);
    try std.testing.expectEqual(@as(?i32, null), missing.fd);

    const invalid = summarizeBufferFdLookup(&buffer_fds, 4);
    try std.testing.expectEqual(BufferFdLookupDisposition.invalid_index, invalid.disposition);
    try std.testing.expectEqual(@as(?i32, null), invalid.fd);
}

test "resolveBufferFdLookupReturn keeps errno-shaped buffer-fd lookup returns explicit" {
    const buffer_fds = [_]?i32{ 11, null, 17 };

    try std.testing.expectEqual(
        @as(i32, 11),
        resolveBufferFdLookupReturn(summarizeBufferFdLookup(&buffer_fds, 0)),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        resolveBufferFdLookupReturn(summarizeBufferFdLookup(&buffer_fds, 1)),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        resolveBufferFdLookupReturn(summarizeBufferFdLookup(&buffer_fds, 5)),
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
