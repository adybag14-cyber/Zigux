const std = @import("std");
const perf_buffer_poll = @import("perf_buffer_poll");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readWorkspaceFile(allocator: std.mem.Allocator, path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(limit),
    );
}

test "phase 8 perf-buffer poll docs keep the bounded wait-result helper explicit" {
    const note = try readWorkspaceFile(
        std.testing.allocator,
        "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(note);

    try expectContains(note, "perf_buffer__poll(timeout_ms)");
    try expectContains(note, "wait-result classification");
    try expectContains(note, "normalized negative errno-or-ready-count wait results");
    try expectContains(note, "ordered ready-buffer cursor traversal");
    try expectContains(note, "ready-buffer bookkeeping");
    try expectContains(note, "ordered `perf_buffer__process_records()` pass");
    try expectContains(note, "cumulative processed-record count");
    try expectContains(note, "first failing ready buffer");
    try expectContains(note, "final return-path choice between a successful ready count and the first processing failure");
    try expectContains(note, "bounded buffer-fd lookup and errno shaping");
    try expectContains(note, "bounded buffer-window lookup and mapped-size passthrough");
    try expectContains(note, "`perf_buffer__buffer_fd(buf_idx)` slot lookup classification");
    try expectContains(note, "`perf_buffer__buffer(buf_idx, &buf, &buf_size)` slot lookup classification");
    try expectContains(note, "ready-buffer processing attempts cannot exceed the helper-counted ready buffers");
    try expectContains(note, "ready-buffer processing attempts cannot exceed observed ready events");
    try expectContains(note, "non-ready wait observations cannot claim record processing");
    try expectContains(note, "reject impossible post-wait buffer state combinations");
    try expectContains(note, "no standalone timer helper");
    try expectContains(note, "no standalone clockevent helper");
}

test "phase 8 perf-buffer poll focused shard keeps the dedicated gate explicit" {
    const gate = try readWorkspaceFile(
        std.testing.allocator,
        "scripts/zigux/check-phase8-perf-buffer-poll-gate.py",
        32 * 1024,
    );
    defer std.testing.allocator.free(gate);

    try expectContains(gate, "scripts/zigux/check-phase8-perf-buffer-poll-gate.py");
    try expectContains(gate, "Documentation/zigux/phase8-perf-buffer-poll-slice.md");
    try expectContains(gate, "zigux/tests/phase8_perf_buffer_poll.zig");
    try expectContains(gate, "zigux/tests/phase8_perf_buffer_poll_only_build.zig");
    try expectContains(gate, "make -C zigux phase8-perf-buffer-poll-test");
    try expectContains(gate, "\"ready-buffer processing attempts cannot exceed the helper-counted ready buffers\"");
    try expectContains(gate, "phase 8 perf-buffer poll focused shard keeps the dedicated gate explicit");
    try expectContains(
        gate,
        "phase 8 perf-buffer poll helper keeps buffer-state-only ready events explicit below routing parity",
    );
    try expectContains(
        gate,
        "phase 8 perf-buffer poll helper rejects inconsistent processing accounting summaries before return shaping",
    );
}

test "phase 8 perf-buffer poll helper keeps ready-buffer cursor traversal explicit" {
    const buffers = [_]perf_buffer_poll.BufferObservation{
        .{},
        .{ .error_code = -32 },
        .{ .ready = true },
        .{},
        .{ .ready = true, .error_code = -11 },
    };

    const first = perf_buffer_poll.advanceReadyBufferCursor(&buffers, 0);
    try std.testing.expectEqual(@as(usize, 0), first.start_index);
    try std.testing.expectEqual(@as(?usize, 2), first.ready_index);
    try std.testing.expectEqual(@as(usize, 3), first.next_scan_index);
    try std.testing.expectEqual(@as(usize, 2), first.skipped_nonready_count);

    const second = perf_buffer_poll.advanceReadyBufferCursor(&buffers, first.next_scan_index);
    try std.testing.expectEqual(@as(usize, 3), second.start_index);
    try std.testing.expectEqual(@as(?usize, 4), second.ready_index);
    try std.testing.expectEqual(@as(usize, 5), second.next_scan_index);
    try std.testing.expectEqual(@as(usize, 1), second.skipped_nonready_count);

    const exhausted = perf_buffer_poll.advanceReadyBufferCursor(&buffers, second.next_scan_index);
    try std.testing.expectEqual(@as(?usize, null), exhausted.ready_index);
    try std.testing.expectEqual(@as(usize, 5), exhausted.next_scan_index);
    try std.testing.expectEqual(@as(usize, 0), exhausted.skipped_nonready_count);

    const past_end = perf_buffer_poll.advanceReadyBufferCursor(&buffers, 9);
    try std.testing.expectEqual(@as(?usize, null), past_end.ready_index);
    try std.testing.expectEqual(@as(usize, 5), past_end.next_scan_index);
    try std.testing.expectEqual(@as(usize, 0), past_end.skipped_nonready_count);
}

test "phase 8 perf-buffer poll helper keeps the final return-path bookkeeping below routing parity" {
    const success = try perf_buffer_poll.summarizePollExecutionResultFromWaitResult(12, 3, &.{
        .{ .ready = true },
        .{ .ready = true },
        .{ .error_code = -32 },
    }, &.{
        .{ .records_processed = 4 },
        .{ .records_processed = 2 },
    });
    try std.testing.expectEqual(perf_buffer_poll.PollReturnDisposition.ready_count, success.disposition);
    try std.testing.expectEqual(@as(i32, 3), success.return_value);
    try std.testing.expectEqual(@as(usize, 6), success.execution.processed_record_count);

    const processing_failure = try perf_buffer_poll.summarizePollExecutionResultFromWaitResult(12, 3, &.{
        .{ .ready = true },
        .{ .ready = true },
        .{ .error_code = -32 },
    }, &.{
        .{ .records_processed = 4 },
        .{ .result = -11 },
    });
    try std.testing.expectEqual(
        perf_buffer_poll.PollReturnDisposition.processing_failed,
        processing_failure.disposition,
    );
    try std.testing.expectEqual(@as(i32, -11), processing_failure.return_value);
    try std.testing.expectEqual(@as(?usize, 1), processing_failure.execution.first_process_error_index);
}

test "phase 8 perf-buffer poll helper keeps buffer-state-only ready events explicit below routing parity" {
    const result = try perf_buffer_poll.summarizePollExecutionResultFromWaitResult(
        5,
        2,
        &.{
            .{ .error_code = -22 },
            .{ .error_code = -32 },
        },
        &.{},
    );
    try std.testing.expectEqual(perf_buffer_poll.PollOutcome.failed, result.execution.poll.outcome);
    try std.testing.expectEqual(
        perf_buffer_poll.PollReturnDisposition.buffer_state_failed,
        result.disposition,
    );
    try std.testing.expectEqual(@as(i32, -22), result.return_value);
}

test "phase 8 perf-buffer poll helper rejects inconsistent processing-failure bookkeeping before return shaping" {
    const missing_error = perf_buffer_poll.PollExecutionSummary{
        .poll = .{
            .wait_class = .bounded,
            .outcome = .ready,
            .observed_ready_events = 2,
            .ready_count = 2,
            .first_ready_index = 0,
            .first_error = null,
        },
        .attempted_ready_buffer_count = 1,
        .completed_ready_buffer_count = 0,
        .processed_record_count = 0,
        .first_process_error_index = 0,
        .first_process_error = null,
    };
    try std.testing.expectError(
        perf_buffer_poll.PollError.InconsistentProcessingFailureSummary,
        perf_buffer_poll.resolvePollExecutionResultFromWaitResult(2, missing_error),
    );

    const missing_index = perf_buffer_poll.PollExecutionSummary{
        .poll = .{
            .wait_class = .bounded,
            .outcome = .ready,
            .observed_ready_events = 2,
            .ready_count = 2,
            .first_ready_index = 0,
            .first_error = null,
        },
        .attempted_ready_buffer_count = 1,
        .completed_ready_buffer_count = 0,
        .processed_record_count = 0,
        .first_process_error_index = null,
        .first_process_error = -11,
    };
    try std.testing.expectError(
        perf_buffer_poll.PollError.InconsistentProcessingFailureSummary,
        perf_buffer_poll.resolvePollExecutionResultFromWaitResult(2, missing_index),
    );
}

test "phase 8 perf-buffer poll helper rejects inconsistent processing accounting summaries before return shaping" {
    const too_many_attempts = perf_buffer_poll.PollExecutionSummary{
        .poll = .{
            .wait_class = .bounded,
            .outcome = .ready,
            .observed_ready_events = 2,
            .ready_count = 1,
            .first_ready_index = 0,
            .first_error = null,
        },
        .attempted_ready_buffer_count = 2,
        .completed_ready_buffer_count = 1,
        .processed_record_count = 4,
        .first_process_error_index = 1,
        .first_process_error = -11,
    };
    try std.testing.expectError(
        perf_buffer_poll.PollError.InconsistentProcessingAccountingSummary,
        perf_buffer_poll.resolvePollExecutionResultFromWaitResult(2, too_many_attempts),
    );

    const failed_with_processing = perf_buffer_poll.PollExecutionSummary{
        .poll = .{
            .wait_class = .bounded,
            .outcome = .failed,
            .observed_ready_events = 0,
            .ready_count = 0,
            .first_ready_index = null,
            .first_error = -5,
        },
        .attempted_ready_buffer_count = 1,
        .completed_ready_buffer_count = 1,
        .processed_record_count = 2,
        .first_process_error_index = null,
        .first_process_error = null,
    };
    try std.testing.expectError(
        perf_buffer_poll.PollError.InconsistentProcessingAccountingSummary,
        perf_buffer_poll.resolvePollExecutionResultFromWaitResult(-5, failed_with_processing),
    );
}

test "phase 8 perf-buffer poll helper keeps ready-buffer processing budget failures explicit" {
    try std.testing.expectError(
        perf_buffer_poll.PollError.ReadyBufferProcessingExceedsObservedEvents,
        perf_buffer_poll.summarizePollExecution(
            5,
            .{ .ready_events = 1 },
            &.{.{ .ready = true }},
            &.{
                .{ .records_processed = 1 },
                .{ .records_processed = 2 },
            },
        ),
    );

    try std.testing.expectError(
        perf_buffer_poll.PollError.ReadyBufferProcessingExceedsReadyCount,
        perf_buffer_poll.summarizePollExecution(
            5,
            .{ .ready_events = 3 },
            &.{
                .{ .ready = true },
                .{},
                .{ .error_code = -32 },
            },
            &.{
                .{ .records_processed = 1 },
                .{ .records_processed = 2 },
            },
        ),
    );
}

test "phase 8 perf-buffer poll helper keeps buffer-fd lookup returns compact and errno-shaped" {
    const buffer_fds = [_]?i32{ 9, null, 21 };

    const found = perf_buffer_poll.summarizeBufferFdLookup(&buffer_fds, 2);
    try std.testing.expectEqual(perf_buffer_poll.BufferFdLookupDisposition.found_fd, found.disposition);
    try std.testing.expectEqual(@as(i32, 21), perf_buffer_poll.resolveBufferFdLookupReturn(found));

    const missing = perf_buffer_poll.summarizeBufferFdLookup(&buffer_fds, 1);
    try std.testing.expectEqual(perf_buffer_poll.BufferFdLookupDisposition.missing_fd, missing.disposition);
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        perf_buffer_poll.resolveBufferFdLookupReturn(missing),
    );

    const invalid = perf_buffer_poll.summarizeBufferFdLookup(&buffer_fds, 4);
    try std.testing.expectEqual(perf_buffer_poll.BufferFdLookupDisposition.invalid_index, invalid.disposition);
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        perf_buffer_poll.resolveBufferFdLookupReturn(invalid),
    );
}

test "phase 8 perf-buffer poll helper keeps empty buffer-fd tables invalid and errno-shaped" {
    const summary = perf_buffer_poll.summarizeBufferFdLookup(&.{}, 0);
    try std.testing.expectEqual(perf_buffer_poll.BufferFdLookupDisposition.invalid_index, summary.disposition);
    try std.testing.expectEqual(@as(usize, 0), summary.slot_count);
    try std.testing.expectEqual(@as(usize, 0), summary.requested_index);
    try std.testing.expectEqual(@as(?i32, null), summary.fd);
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        perf_buffer_poll.resolveBufferFdLookupReturn(summary),
    );
}

test "phase 8 perf-buffer poll helper keeps buffer-window lookup returns compact and mapped-size-shaped" {
    const buffer_windows = [_]?perf_buffer_poll.BufferWindowObservation{
        .{ .mapped_size = 4096 },
        null,
        .{ .mapped_size = 8192 },
    };

    const found = perf_buffer_poll.summarizeBufferWindowLookup(&buffer_windows, 2);
    try std.testing.expectEqual(
        perf_buffer_poll.BufferWindowLookupDisposition.found_window,
        found.disposition,
    );
    try std.testing.expectEqual(@as(?usize, 8192), found.mapped_size);
    try std.testing.expectEqual(
        @as(i32, 0),
        perf_buffer_poll.resolveBufferWindowLookupReturn(found),
    );

    const missing = perf_buffer_poll.summarizeBufferWindowLookup(&buffer_windows, 1);
    try std.testing.expectEqual(
        perf_buffer_poll.BufferWindowLookupDisposition.missing_window,
        missing.disposition,
    );
    try std.testing.expectEqual(@as(?usize, null), missing.mapped_size);
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        perf_buffer_poll.resolveBufferWindowLookupReturn(missing),
    );

    const invalid = perf_buffer_poll.summarizeBufferWindowLookup(&buffer_windows, 4);
    try std.testing.expectEqual(
        perf_buffer_poll.BufferWindowLookupDisposition.invalid_index,
        invalid.disposition,
    );
    try std.testing.expectEqual(@as(?usize, null), invalid.mapped_size);
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        perf_buffer_poll.resolveBufferWindowLookupReturn(invalid),
    );
}

test "phase 8 perf-buffer poll helper keeps empty buffer-window tables invalid and errno-shaped" {
    const summary = perf_buffer_poll.summarizeBufferWindowLookup(&.{}, 0);
    try std.testing.expectEqual(
        perf_buffer_poll.BufferWindowLookupDisposition.invalid_index,
        summary.disposition,
    );
    try std.testing.expectEqual(@as(usize, 0), summary.slot_count);
    try std.testing.expectEqual(@as(usize, 0), summary.requested_index);
    try std.testing.expectEqual(@as(?usize, null), summary.mapped_size);
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        perf_buffer_poll.resolveBufferWindowLookupReturn(summary),
    );
}

test "phase 8 perf-buffer poll helper keeps impossible post-wait buffer states rejected" {
    try std.testing.expectError(
        perf_buffer_poll.PollError.TimeoutObservationHasReadyBuffer,
        perf_buffer_poll.summarizePoll(0, .timed_out, &.{.{ .error_code = -5 }}),
    );
    try std.testing.expectError(
        perf_buffer_poll.PollError.InterruptedObservationHasReadyBuffer,
        perf_buffer_poll.summarizePoll(-1, .interrupted, &.{.{ .ready = true }}),
    );
    try std.testing.expectError(
        perf_buffer_poll.PollError.FailedObservationHasBufferState,
        perf_buffer_poll.summarizePoll(5, .{ .failed = -11 }, &.{.{ .error_code = -32 }}),
    );
}

test "resolvePollExecutionResultFromWaitResult rejects mismatched wait-result and execution summaries" {
    const ready_execution = try perf_buffer_poll.summarizePollExecutionFromWaitResult(
        12,
        2,
        &.{ .{ .ready = true }, .{ .ready = true } },
        &.{.{ .records_processed = 1 }},
    );
    try std.testing.expectError(
        perf_buffer_poll.PollError.WaitResultDisagreesWithExecutionOutcome,
        perf_buffer_poll.resolvePollExecutionResultFromWaitResult(0, ready_execution),
    );
    try std.testing.expectError(
        perf_buffer_poll.PollError.WaitResultDisagreesWithReadyEventCount,
        perf_buffer_poll.resolvePollExecutionResultFromWaitResult(3, ready_execution),
    );

    const failed_execution = try perf_buffer_poll.summarizePollExecutionFromWaitResult(5, -5, &.{}, &.{});
    try std.testing.expectError(
        perf_buffer_poll.PollError.WaitResultDisagreesWithFailureCode,
        perf_buffer_poll.resolvePollExecutionResultFromWaitResult(-9, failed_execution),
    );
}
