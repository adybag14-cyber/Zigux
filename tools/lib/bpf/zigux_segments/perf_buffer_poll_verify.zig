const std = @import("std");

const perf_buffer_poll = @import("perf_buffer_poll.zig");

test "phase8 perf-buffer poll helper entrypoints stay explicit" {
    try std.testing.expect(@hasDecl(perf_buffer_poll, "WaitClass"));
    try std.testing.expect(@hasDecl(perf_buffer_poll, "PollOutcome"));
    try std.testing.expect(@hasDecl(perf_buffer_poll, "PollReturnDisposition"));
    try std.testing.expect(@hasDecl(perf_buffer_poll, "BufferObservation"));
    try std.testing.expect(@hasDecl(perf_buffer_poll, "WaitObservation"));
    try std.testing.expect(@hasDecl(perf_buffer_poll, "ReadyBufferSummary"));
    try std.testing.expect(@hasDecl(perf_buffer_poll, "ProcessRecordObservation"));
    try std.testing.expect(@hasDecl(perf_buffer_poll, "ProcessRecordSummary"));
    try std.testing.expect(@hasDecl(perf_buffer_poll, "PollSummary"));
    try std.testing.expect(@hasDecl(perf_buffer_poll, "PollExecutionSummary"));
    try std.testing.expect(@hasDecl(perf_buffer_poll, "PollExecutionResult"));
    try std.testing.expect(@hasDecl(perf_buffer_poll, "PollError"));
    try std.testing.expect(@hasDecl(perf_buffer_poll, "classifyObservedWaitResult"));
    try std.testing.expect(@hasDecl(perf_buffer_poll, "classifyWaitClass"));
    try std.testing.expect(@hasDecl(perf_buffer_poll, "summarizeReadyBuffers"));
    try std.testing.expect(@hasDecl(perf_buffer_poll, "summarizeProcessRecords"));
    try std.testing.expect(@hasDecl(perf_buffer_poll, "summarizePoll"));
    try std.testing.expect(@hasDecl(perf_buffer_poll, "summarizePollFromWaitResult"));
    try std.testing.expect(@hasDecl(perf_buffer_poll, "summarizePollExecution"));
    try std.testing.expect(@hasDecl(perf_buffer_poll, "summarizePollExecutionFromWaitResult"));
    try std.testing.expect(@hasDecl(perf_buffer_poll, "resolvePollExecutionResultFromWaitResult"));
    try std.testing.expect(@hasDecl(perf_buffer_poll, "summarizePollExecutionResultFromWaitResult"));
}

test "phase8 perf-buffer poll keeps wait classification and buffer summaries stable" {
    try std.testing.expectEqual(
        perf_buffer_poll.WaitObservation.timed_out,
        perf_buffer_poll.classifyObservedWaitResult(0),
    );
    try std.testing.expectEqual(
        perf_buffer_poll.WaitObservation{ .ready_events = 3 },
        perf_buffer_poll.classifyObservedWaitResult(3),
    );
    try std.testing.expectEqual(
        perf_buffer_poll.WaitObservation.interrupted,
        perf_buffer_poll.classifyObservedWaitResult(-@as(i32, @intFromEnum(std.os.linux.E.INTR))),
    );
    try std.testing.expectEqual(
        perf_buffer_poll.WaitObservation{ .failed = -19 },
        perf_buffer_poll.classifyObservedWaitResult(-19),
    );

    try std.testing.expectEqual(
        perf_buffer_poll.WaitClass.nonblocking,
        try perf_buffer_poll.classifyWaitClass(0),
    );
    try std.testing.expectEqual(
        perf_buffer_poll.WaitClass.indefinite,
        try perf_buffer_poll.classifyWaitClass(-1),
    );
    try std.testing.expectEqual(
        perf_buffer_poll.WaitClass.bounded,
        try perf_buffer_poll.classifyWaitClass(12),
    );
    try std.testing.expectError(
        perf_buffer_poll.PollError.InvalidTimeout,
        perf_buffer_poll.classifyWaitClass(-2),
    );

    const ready_summary = perf_buffer_poll.summarizeReadyBuffers(&.{
        .{ .ready = true },
        .{},
        .{ .ready = true, .error_code = -5 },
    });
    try std.testing.expectEqual(@as(usize, 2), ready_summary.ready_count);
    try std.testing.expectEqual(@as(?usize, 0), ready_summary.first_ready_index);
    try std.testing.expectEqual(@as(?i32, -5), ready_summary.first_error);

    const process_summary = perf_buffer_poll.summarizeProcessRecords(&.{
        .{ .records_processed = 4 },
        .{ .records_processed = 2 },
        .{ .result = -11 },
    });
    try std.testing.expectEqual(@as(usize, 3), process_summary.attempted_count);
    try std.testing.expectEqual(@as(usize, 2), process_summary.completed_count);
    try std.testing.expectEqual(@as(usize, 6), process_summary.processed_record_count);
    try std.testing.expectEqual(@as(?usize, 2), process_summary.first_error_index);
    try std.testing.expectEqual(@as(?i32, -11), process_summary.first_error);
}

test "phase8 perf-buffer poll keeps poll summaries stable across timeout ready and error-only paths" {
    const timeout_summary = try perf_buffer_poll.summarizePoll(0, .timed_out, &.{});
    try std.testing.expectEqual(perf_buffer_poll.WaitClass.nonblocking, timeout_summary.wait_class);
    try std.testing.expectEqual(perf_buffer_poll.PollOutcome.timeout, timeout_summary.outcome);
    try std.testing.expectEqual(@as(usize, 0), timeout_summary.observed_ready_events);
    try std.testing.expectEqual(@as(usize, 0), timeout_summary.ready_count);
    try std.testing.expectEqual(@as(?usize, null), timeout_summary.first_ready_index);
    try std.testing.expectEqual(@as(?i32, null), timeout_summary.first_error);

    const ready_summary = try perf_buffer_poll.summarizePollFromWaitResult(
        12,
        2,
        &.{ .{ .ready = true }, .{ .ready = true }, .{} },
    );
    try std.testing.expectEqual(perf_buffer_poll.WaitClass.bounded, ready_summary.wait_class);
    try std.testing.expectEqual(perf_buffer_poll.PollOutcome.ready, ready_summary.outcome);
    try std.testing.expectEqual(@as(usize, 2), ready_summary.observed_ready_events);
    try std.testing.expectEqual(@as(usize, 2), ready_summary.ready_count);
    try std.testing.expectEqual(@as(?usize, 0), ready_summary.first_ready_index);
    try std.testing.expectEqual(@as(?i32, null), ready_summary.first_error);

    const failed_summary = try perf_buffer_poll.summarizePollFromWaitResult(
        12,
        2,
        &.{ .{ .error_code = -105 }, .{} },
    );
    try std.testing.expectEqual(perf_buffer_poll.PollOutcome.failed, failed_summary.outcome);
    try std.testing.expectEqual(@as(usize, 2), failed_summary.observed_ready_events);
    try std.testing.expectEqual(@as(usize, 0), failed_summary.ready_count);
    try std.testing.expectEqual(@as(?usize, null), failed_summary.first_ready_index);
    try std.testing.expectEqual(@as(?i32, -105), failed_summary.first_error);
}

test "phase8 perf-buffer poll keeps execution summaries and returns stable" {
    const execution = try perf_buffer_poll.summarizePollExecutionFromWaitResult(
        12,
        2,
        &.{ .{}, .{ .ready = true }, .{}, .{ .ready = true } },
        &.{ .{ .records_processed = 4 }, .{ .result = -11 } },
    );
    try std.testing.expectEqual(perf_buffer_poll.PollOutcome.ready, execution.poll.outcome);
    try std.testing.expectEqual(@as(usize, 2), execution.poll.ready_count);
    try std.testing.expectEqual(@as(usize, 2), execution.attempted_ready_buffer_count);
    try std.testing.expectEqual(@as(usize, 1), execution.completed_ready_buffer_count);
    try std.testing.expectEqual(@as(usize, 4), execution.processed_record_count);
    try std.testing.expectEqual(@as(?usize, 1), execution.first_process_error_index);
    try std.testing.expectEqual(@as(?usize, 3), execution.first_process_error_ready_index);
    try std.testing.expectEqual(@as(?i32, -11), execution.first_process_error);

    const success = try perf_buffer_poll.summarizePollExecutionResultFromWaitResult(
        12,
        3,
        &.{ .{ .ready = true }, .{ .ready = true }, .{ .error_code = -32 } },
        &.{ .{ .records_processed = 4 }, .{ .records_processed = 2 } },
    );
    try std.testing.expectEqual(perf_buffer_poll.PollReturnDisposition.ready_count, success.disposition);
    try std.testing.expectEqual(@as(i32, 3), success.return_value);
    try std.testing.expectEqual(@as(usize, 6), success.execution.processed_record_count);

    const failure = try perf_buffer_poll.summarizePollExecutionResultFromWaitResult(
        12,
        2,
        &.{ .{}, .{ .ready = true }, .{}, .{ .ready = true } },
        &.{ .{ .records_processed = 4 }, .{ .result = -11 } },
    );
    try std.testing.expectEqual(perf_buffer_poll.PollReturnDisposition.processing_failed, failure.disposition);
    try std.testing.expectEqual(@as(i32, -11), failure.return_value);
    try std.testing.expectEqual(@as(?usize, 3), failure.execution.first_process_error_ready_index);

    const buffer_state_failure = try perf_buffer_poll.summarizePollExecutionResultFromWaitResult(
        12,
        2,
        &.{ .{ .error_code = -105 }, .{} },
        &.{},
    );
    try std.testing.expectEqual(
        perf_buffer_poll.PollReturnDisposition.buffer_state_failed,
        buffer_state_failure.disposition,
    );
    try std.testing.expectEqual(@as(i32, -105), buffer_state_failure.return_value);
}

test "phase8 perf-buffer poll rejects impossible hand-built summaries and mismatched ready waits" {
    const impossible_timeout = perf_buffer_poll.PollExecutionSummary{
        .poll = .{
            .wait_class = .nonblocking,
            .outcome = .timeout,
            .observed_ready_events = 1,
            .ready_count = 0,
            .first_ready_index = null,
            .first_error = null,
        },
        .attempted_ready_buffer_count = 0,
        .completed_ready_buffer_count = 0,
        .processed_record_count = 0,
        .first_process_error_index = null,
        .first_process_error_ready_index = null,
        .first_process_error = null,
    };
    try std.testing.expectError(
        perf_buffer_poll.PollError.InconsistentPollSummary,
        perf_buffer_poll.resolvePollExecutionResultFromWaitResult(0, impossible_timeout),
    );

    try std.testing.expectError(
        perf_buffer_poll.PollError.ReadyBufferProcessingFallsShortOfReadyCount,
        perf_buffer_poll.summarizePollExecutionResultFromWaitResult(
            12,
            2,
            &.{ .{ .ready = true }, .{ .ready = true } },
            &.{.{ .records_processed = 1 }},
        ),
    );

    const ready_execution = try perf_buffer_poll.summarizePollExecutionFromWaitResult(
        12,
        2,
        &.{ .{ .ready = true }, .{ .ready = true } },
        &.{ .{ .records_processed = 1 }, .{ .records_processed = 1 } },
    );
    try std.testing.expectError(
        perf_buffer_poll.PollError.WaitResultDisagreesWithExecutionOutcome,
        perf_buffer_poll.resolvePollExecutionResultFromWaitResult(0, ready_execution),
    );
    try std.testing.expectError(
        perf_buffer_poll.PollError.WaitResultDisagreesWithReadyEventCount,
        perf_buffer_poll.resolvePollExecutionResultFromWaitResult(3, ready_execution),
    );
}