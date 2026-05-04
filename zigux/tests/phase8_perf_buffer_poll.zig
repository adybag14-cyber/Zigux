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
    try expectContains(note, "ready-buffer bookkeeping");
    try expectContains(note, "ordered `perf_buffer__process_records()` pass");
    try expectContains(note, "cumulative processed-record count");
    try expectContains(note, "first failing ready buffer");
    try expectContains(note, "final poll return keeps successful ready counts and first processing failures explicit");
    try expectContains(note, "ready-buffer processing attempts cannot exceed observed ready events");
    try expectContains(note, "non-ready wait observations cannot claim record processing");
    try expectContains(note, "reject impossible post-wait buffer state combinations");
    try expectContains(note, "no standalone timer helper");
    try expectContains(note, "no standalone clockevent helper");
}

test "phase 8 perf-buffer poll helper stays wired into focused and shared Phase 8 builds" {
    const focused_build = try readWorkspaceFile(
        std.testing.allocator,
        "zigux/tests/phase8_perf_buffer_poll_only_build.zig",
        16 * 1024,
    );
    defer std.testing.allocator.free(focused_build);
    try expectContains(focused_build, "../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig");
    try expectContains(focused_build, "phase8_perf_buffer_poll.zig");
    try expectContains(focused_build, "phase8-perf-buffer-poll-tests");
    try expectContains(focused_build, "Run focused Phase 8 perf-buffer poll tests");

    const shared_build = try readWorkspaceFile(
        std.testing.allocator,
        "zigux/tests/phase8_build.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(shared_build);
    try expectContains(shared_build, "../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig");
    try expectContains(shared_build, "phase8_perf_buffer_poll.zig");
    try expectContains(shared_build, "phase8-perf-buffer-poll-tests");

    const makefile = try readWorkspaceFile(
        std.testing.allocator,
        "zigux/Makefile",
        32 * 1024,
    );
    defer std.testing.allocator.free(makefile);
    try expectContains(makefile, "phase8-perf-buffer-poll-test:");
    try expectContains(
        makefile,
        "$(ZIG) build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all",
    );
    try expectContains(
        makefile,
        "phase8: phase8-validate phase8-exec-cmd-test phase8-help-test phase8-kallsyms-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test phase8-test",
    );
}

test "phase 8 perf-buffer poll helper keeps execution bookkeeping aligned with the observed ready-event budget" {
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

test "phase 8 perf-buffer poll helper rejects impossible post-wait record processing" {
    try std.testing.expectError(
        perf_buffer_poll.PollError.NonReadyWaitHasProcessedRecords,
        perf_buffer_poll.summarizePollExecution(0, .timed_out, &.{}, &.{.{ .records_processed = 1 }}),
    );
    try std.testing.expectError(
        perf_buffer_poll.PollError.NonReadyWaitHasProcessedRecords,
        perf_buffer_poll.summarizePollExecution(-1, .interrupted, &.{}, &.{.{ .records_processed = 1 }}),
    );
    try std.testing.expectError(
        perf_buffer_poll.PollError.ReadyBufferProcessingExceedsObservedEvents,
        perf_buffer_poll.summarizePollExecution(5, .{ .ready_events = 1 }, &.{.{ .ready = true }}, &.{
            .{ .records_processed = 1 },
            .{ .records_processed = 2 },
        }),
    );
}

test "classifyWaitClass keeps perf_buffer__poll timeout classes explicit" {
    try std.testing.expectEqual(perf_buffer_poll.WaitClass.indefinite, try perf_buffer_poll.classifyWaitClass(-1));
    try std.testing.expectEqual(perf_buffer_poll.WaitClass.nonblocking, try perf_buffer_poll.classifyWaitClass(0));
    try std.testing.expectEqual(perf_buffer_poll.WaitClass.bounded, try perf_buffer_poll.classifyWaitClass(25));
    try std.testing.expectError(perf_buffer_poll.PollError.InvalidTimeout, perf_buffer_poll.classifyWaitClass(-2));
}

test "classifyObservedWaitResult keeps normalized wait outcomes compact before buffer bookkeeping" {
    try std.testing.expectEqualDeep(perf_buffer_poll.WaitObservation.timed_out, perf_buffer_poll.classifyObservedWaitResult(0));
    try std.testing.expectEqualDeep(perf_buffer_poll.WaitObservation{ .ready_events = 3 }, perf_buffer_poll.classifyObservedWaitResult(3));
    try std.testing.expectEqualDeep(
        perf_buffer_poll.WaitObservation.interrupted,
        perf_buffer_poll.classifyObservedWaitResult(-@as(i32, @intFromEnum(std.os.linux.E.INTR))),
    );
    try std.testing.expectEqualDeep(perf_buffer_poll.WaitObservation{ .failed = -5 }, perf_buffer_poll.classifyObservedWaitResult(-5));
}

test "summarizeReadyBuffers counts ready buffers and preserves the first error" {
    const buffers = [_]perf_buffer_poll.BufferObservation{
        .{},
        .{ .ready = true },
        .{ .error_code = -11 },
        .{ .ready = true, .error_code = -32 },
    };
    const summary = perf_buffer_poll.summarizeReadyBuffers(&buffers);

    try std.testing.expectEqual(@as(usize, 2), summary.ready_count);
    try std.testing.expectEqual(@as(?usize, 1), summary.first_ready_index);
    try std.testing.expectEqual(@as(?i32, -11), summary.first_error);
}

test "summarizeProcessRecords keeps perf_buffer__process_records fail-fast ordering and processed record totals explicit" {
    const failure = perf_buffer_poll.summarizeProcessRecords(&.{
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

    const success = perf_buffer_poll.summarizeProcessRecords(&.{
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

test "summarizeConsumeExecution keeps already-open buffer traversal fail-fast while skipping absent slots" {
    const summary = perf_buffer_poll.summarizeConsumeExecution(&.{
        .{ .present = true, .process = .{ .records_processed = 4 } },
        .{ .present = false },
        .{ .present = true, .process = .{ .result = -11 } },
        .{ .present = true, .process = .{ .records_processed = 9 } },
    });

    try std.testing.expectEqual(@as(usize, 4), summary.slot_count);
    try std.testing.expectEqual(@as(usize, 2), summary.attempted_present_buffer_count);
    try std.testing.expectEqual(@as(usize, 1), summary.completed_present_buffer_count);
    try std.testing.expectEqual(@as(usize, 4), summary.processed_record_count);
    try std.testing.expectEqual(@as(?usize, 2), summary.first_error_slot_index);
    try std.testing.expectEqual(@as(?i32, -11), summary.first_error);
}

test "summarizeConsumeExecutionResult keeps success and first processing failure explicit" {
    const success = perf_buffer_poll.summarizeConsumeExecutionResult(&.{
        .{ .present = false },
        .{ .present = true, .process = .{ .records_processed = 1 } },
        .{ .present = true, .process = .{ .records_processed = 2 } },
    });
    try std.testing.expectEqual(perf_buffer_poll.ConsumeReturnDisposition.success, success.disposition);
    try std.testing.expectEqual(@as(i32, 0), success.return_value);
    try std.testing.expectEqual(@as(usize, 2), success.execution.completed_present_buffer_count);
    try std.testing.expectEqual(@as(usize, 3), success.execution.processed_record_count);

    const failure = perf_buffer_poll.summarizeConsumeExecutionResult(&.{
        .{ .present = true, .process = .{ .records_processed = 5 } },
        .{ .present = true, .process = .{ .result = -32 } },
    });
    try std.testing.expectEqual(perf_buffer_poll.ConsumeReturnDisposition.processing_failed, failure.disposition);
    try std.testing.expectEqual(@as(i32, -32), failure.return_value);
    try std.testing.expectEqual(@as(?usize, 1), failure.execution.first_error_slot_index);
}

test "summarizePoll keeps bounded ready observations compact and reviewable" {
    const buffers = [_]perf_buffer_poll.BufferObservation{
        .{ .ready = true },
        .{ .error_code = -32 },
        .{ .ready = true },
    };
    const summary = try perf_buffer_poll.summarizePoll(10, .{ .ready_events = 3 }, &buffers);

    try std.testing.expectEqual(perf_buffer_poll.WaitClass.bounded, summary.wait_class);
    try std.testing.expectEqual(perf_buffer_poll.PollOutcome.ready, summary.outcome);
    try std.testing.expectEqual(@as(usize, 3), summary.observed_ready_events);
    try std.testing.expectEqual(@as(usize, 2), summary.ready_count);
    try std.testing.expectEqual(@as(?usize, 0), summary.first_ready_index);
    try std.testing.expectEqual(@as(?i32, -32), summary.first_error);
}

test "summarizePollFromWaitResult keeps raw wait-result normalization coupled to the bounded buffer summary" {
    const buffers = [_]perf_buffer_poll.BufferObservation{
        .{ .ready = true },
        .{ .error_code = -32 },
        .{ .ready = true },
    };
    const summary = try perf_buffer_poll.summarizePollFromWaitResult(10, 3, &buffers);

    try std.testing.expectEqual(perf_buffer_poll.WaitClass.bounded, summary.wait_class);
    try std.testing.expectEqual(perf_buffer_poll.PollOutcome.ready, summary.outcome);
    try std.testing.expectEqual(@as(usize, 3), summary.observed_ready_events);
    try std.testing.expectEqual(@as(usize, 2), summary.ready_count);
    try std.testing.expectEqual(@as(?usize, 0), summary.first_ready_index);
    try std.testing.expectEqual(@as(?i32, -32), summary.first_error);
}

test "summarizePoll keeps timeout interruption and missing-ready mismatches explicit" {
    const idle_buffers = [_]perf_buffer_poll.BufferObservation{ .{}, .{} };
    const timeout_summary = try perf_buffer_poll.summarizePoll(0, .timed_out, &idle_buffers);
    try std.testing.expectEqual(perf_buffer_poll.WaitClass.nonblocking, timeout_summary.wait_class);
    try std.testing.expectEqual(perf_buffer_poll.PollOutcome.timeout, timeout_summary.outcome);

    const interrupted_summary = try perf_buffer_poll.summarizePoll(-1, .interrupted, &idle_buffers);
    try std.testing.expectEqual(perf_buffer_poll.WaitClass.indefinite, interrupted_summary.wait_class);
    try std.testing.expectEqual(perf_buffer_poll.PollOutcome.interrupted, interrupted_summary.outcome);

    const error_only = [_]perf_buffer_poll.BufferObservation{.{ .error_code = -22 }};
    const failed_summary = try perf_buffer_poll.summarizePoll(5, .{ .ready_events = 1 }, &error_only);
    try std.testing.expectEqual(perf_buffer_poll.PollOutcome.failed, failed_summary.outcome);
    try std.testing.expectEqual(@as(?i32, -22), failed_summary.first_error);

    try std.testing.expectError(
        perf_buffer_poll.PollError.ReadyEventsMissingReadyBuffer,
        perf_buffer_poll.summarizePoll(5, .{ .ready_events = 1 }, &idle_buffers),
    );
}

test "summarizePollExecution keeps ready-buffer processing inside the observed epoll budget" {
    const buffers = [_]perf_buffer_poll.BufferObservation{
        .{ .ready = true },
        .{ .ready = true },
        .{ .error_code = -32 },
    };
    const summary = try perf_buffer_poll.summarizePollExecution(12, .{ .ready_events = 3 }, &buffers, &.{
        .{ .records_processed = 4 },
        .{ .result = -11 },
        .{ .records_processed = 9 },
    });

    try std.testing.expectEqual(perf_buffer_poll.PollOutcome.ready, summary.poll.outcome);
    try std.testing.expectEqual(@as(usize, 2), summary.attempted_ready_buffer_count);
    try std.testing.expectEqual(@as(usize, 1), summary.completed_ready_buffer_count);
    try std.testing.expectEqual(@as(usize, 4), summary.processed_record_count);
    try std.testing.expectEqual(@as(?usize, 1), summary.first_process_error_index);
    try std.testing.expectEqual(@as(?i32, -11), summary.first_process_error);
}

test "summarizePollExecutionFromWaitResult keeps raw wait-result normalization coupled to execution bookkeeping" {
    const buffers = [_]perf_buffer_poll.BufferObservation{
        .{ .ready = true },
        .{ .ready = true },
        .{ .error_code = -32 },
    };
    const summary = try perf_buffer_poll.summarizePollExecutionFromWaitResult(12, 3, &buffers, &.{
        .{ .records_processed = 4 },
        .{ .result = -11 },
        .{ .records_processed = 9 },
    });

    try std.testing.expectEqual(perf_buffer_poll.PollOutcome.ready, summary.poll.outcome);
    try std.testing.expectEqual(@as(usize, 2), summary.attempted_ready_buffer_count);
    try std.testing.expectEqual(@as(usize, 1), summary.completed_ready_buffer_count);
    try std.testing.expectEqual(@as(usize, 4), summary.processed_record_count);
    try std.testing.expectEqual(@as(?usize, 1), summary.first_process_error_index);
    try std.testing.expectEqual(@as(?i32, -11), summary.first_process_error);
}

test "resolvePollExecutionResultFromWaitResult keeps the final ready-count return and first processing failure explicit" {
    const success = try perf_buffer_poll.resolvePollExecutionResultFromWaitResult(3, try perf_buffer_poll.summarizePollExecutionFromWaitResult(
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
    try std.testing.expectEqual(perf_buffer_poll.PollReturnDisposition.ready_count, success.disposition);
    try std.testing.expectEqual(@as(i32, 3), success.return_value);

    const processing_failure = try perf_buffer_poll.resolvePollExecutionResultFromWaitResult(3, try perf_buffer_poll.summarizePollExecutionFromWaitResult(
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
    try std.testing.expectEqual(perf_buffer_poll.PollReturnDisposition.processing_failed, processing_failure.disposition);
    try std.testing.expectEqual(@as(i32, -11), processing_failure.return_value);
}

test "summarizePollExecutionResultFromWaitResult keeps timeout interrupt and wait failure returns aligned" {
    const timed_out = try perf_buffer_poll.summarizePollExecutionResultFromWaitResult(0, 0, &.{}, &.{});
    try std.testing.expectEqual(perf_buffer_poll.PollReturnDisposition.timed_out, timed_out.disposition);
    try std.testing.expectEqual(@as(i32, 0), timed_out.return_value);

    const interrupted = try perf_buffer_poll.summarizePollExecutionResultFromWaitResult(
        -1,
        -@as(i32, @intFromEnum(std.os.linux.E.INTR)),
        &.{},
        &.{},
    );
    try std.testing.expectEqual(perf_buffer_poll.PollReturnDisposition.interrupted, interrupted.disposition);
    try std.testing.expectEqual(-@as(i32, @intFromEnum(std.os.linux.E.INTR)), interrupted.return_value);

    const failed = try perf_buffer_poll.summarizePollExecutionResultFromWaitResult(5, -5, &.{}, &.{});
    try std.testing.expectEqual(perf_buffer_poll.PollReturnDisposition.wait_failed, failed.disposition);
    try std.testing.expectEqual(@as(i32, -5), failed.return_value);
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

test "summarizePollExecution rejects impossible processing outside the live perf_buffer__poll wait result" {
    try std.testing.expectError(
        perf_buffer_poll.PollError.NonReadyWaitHasProcessedRecords,
        perf_buffer_poll.summarizePollExecution(0, .timed_out, &.{}, &.{.{ .records_processed = 1 }}),
    );
    try std.testing.expectError(
        perf_buffer_poll.PollError.NonReadyWaitHasProcessedRecords,
        perf_buffer_poll.summarizePollExecution(-1, .interrupted, &.{}, &.{.{ .records_processed = 1 }}),
    );
    try std.testing.expectError(
        perf_buffer_poll.PollError.ReadyBufferProcessingExceedsObservedEvents,
        perf_buffer_poll.summarizePollExecution(5, .{ .ready_events = 1 }, &.{.{ .ready = true }}, &.{
            .{ .records_processed = 1 },
            .{ .records_processed = 2 },
        }),
    );
}

test "summarizePollExecution rejects processing more ready buffers than the helper counted as ready" {
    try std.testing.expectError(
        perf_buffer_poll.PollError.ReadyBufferProcessingExceedsReadyCount,
        perf_buffer_poll.summarizePollExecution(5, .{ .ready_events = 3 }, &.{
            .{ .ready = true },
            .{},
            .{ .error_code = -32 },
        }, &.{
            .{ .records_processed = 1 },
            .{ .records_processed = 2 },
        }),
    );
}

test "summarizePoll rejects impossible buffer state for timeout interrupt and failed wait results" {
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
