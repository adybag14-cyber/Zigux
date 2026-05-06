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
    try expectContains(note, "successful ready count");
    try expectContains(note, "first processing failure");
    try expectContains(note, "ready-buffer processing attempts cannot exceed observed ready events");
    try expectContains(note, "non-ready wait observations cannot claim record processing");
    try expectContains(note, "reject impossible post-wait buffer state combinations");
    try expectContains(note, "no standalone timer helper");
    try expectContains(note, "no standalone clockevent helper");
}

test "phase 8 perf-buffer poll helper stays wired into focused and shared Phase 8 builds" {
    const focused_build_file = try readWorkspaceFile(
        std.testing.allocator,
        "zigux/tests/phase8_perf_buffer_poll_only_build.zig",
        16 * 1024,
    );
    defer std.testing.allocator.free(focused_build_file);

    const shared_build_file = try readWorkspaceFile(
        std.testing.allocator,
        "zigux/tests/phase8_build.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(shared_build_file);

    try expectContains(focused_build_file, "phase8_perf_buffer_poll.zig");
    try expectContains(focused_build_file, "phase8-perf-buffer-poll-tests");
    try expectContains(focused_build_file, "Run focused Phase 8 perf-buffer poll tests");

    try expectContains(shared_build_file, "../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig");
    try expectContains(shared_build_file, "phase8_perf_buffer_poll.zig");
    try expectContains(shared_build_file, "phase8-perf-buffer-poll-tests");
}

test "phase 8 perf-buffer poll helper keeps observed wait outcomes compact" {
    const buffers = [_]perf_buffer_poll.BufferObservation{
        .{ .ready = true },
        .{},
        .{ .error_code = -5 },
    };

    const summary = try perf_buffer_poll.summarizePoll(12, .{ .ready_events = 2 }, &buffers);
    try std.testing.expectEqual(perf_buffer_poll.WaitClass.bounded, summary.wait_class);
    try std.testing.expectEqual(perf_buffer_poll.PollOutcome.ready, summary.outcome);
    try std.testing.expectEqual(@as(usize, 1), summary.ready_count);
    try std.testing.expectEqual(@as(?i32, -5), summary.first_error);
}

test "phase 8 perf-buffer poll helper normalizes observed wait results before summarizing buffers" {
    const ready = perf_buffer_poll.classifyObservedWaitResult(2);
    try std.testing.expectEqualDeep(
        perf_buffer_poll.WaitObservation{ .ready_events = 2 },
        ready,
    );
    try std.testing.expectEqualDeep(
        perf_buffer_poll.WaitObservation.interrupted,
        perf_buffer_poll.classifyObservedWaitResult(-@as(i32, @intFromEnum(std.os.linux.E.INTR))),
    );
    try std.testing.expectEqualDeep(
        perf_buffer_poll.WaitObservation{ .failed = -5 },
        perf_buffer_poll.classifyObservedWaitResult(-5),
    );
}

test "phase 8 perf-buffer poll helper rejects more ready buffers than the observed wait result" {
    try std.testing.expectError(
        perf_buffer_poll.PollError.ReadyCountExceedsObservedEvents,
        perf_buffer_poll.summarizePoll(5, .{ .ready_events = 1 }, &.{
            .{ .ready = true },
            .{ .ready = true },
        }),
    );
    try std.testing.expectError(
        perf_buffer_poll.PollError.ReadyCountExceedsObservedEvents,
        perf_buffer_poll.summarizePollFromWaitResult(5, 1, &.{
            .{ .ready = true },
            .{ .ready = true },
        }),
    );
}

test "phase 8 perf-buffer poll helper rejects observed ready counts beyond available buffer observations" {
    try std.testing.expectError(
        perf_buffer_poll.PollError.ObservedReadyEventsExceedBufferObservationCount,
        perf_buffer_poll.summarizePoll(5, .{ .ready_events = 2 }, &.{.{ .ready = true }}),
    );
    try std.testing.expectError(
        perf_buffer_poll.PollError.ObservedReadyEventsExceedBufferObservationCount,
        perf_buffer_poll.summarizePollFromWaitResult(5, 2, &.{.{ .ready = true }}),
    );
}

test "phase 8 perf-buffer poll helper keeps ready-buffer processing fail-fast below epoll parity" {
    const failure = perf_buffer_poll.summarizeProcessRecords(&.{
        .{ .records_processed = 5 },
        .{ .result = -11 },
        .{ .result = -32, .records_processed = 9 },
    });
    try std.testing.expectEqual(@as(usize, 2), failure.attempted_count);
    try std.testing.expectEqual(@as(usize, 1), failure.completed_count);
    try std.testing.expectEqual(@as(usize, 5), failure.processed_record_count);
    try std.testing.expectEqual(@as(?usize, 1), failure.first_error_index);
    try std.testing.expectEqual(@as(?i32, -11), failure.first_error);

    const success = perf_buffer_poll.summarizeProcessRecords(&.{
        .{ .records_processed = 2 },
        .{ .records_processed = 3 },
    });
    try std.testing.expectEqual(@as(usize, 2), success.attempted_count);
    try std.testing.expectEqual(@as(usize, 2), success.completed_count);
    try std.testing.expectEqual(@as(usize, 5), success.processed_record_count);
    try std.testing.expectEqual(@as(?usize, null), success.first_error_index);
    try std.testing.expectEqual(@as(?i32, null), success.first_error);
}

test "phase 8 perf-buffer poll helper keeps execution bookkeeping aligned with the observed ready-event budget" {
    const summary = try perf_buffer_poll.summarizePollExecution(12, .{ .ready_events = 3 }, &.{
        .{ .ready = true },
        .{ .ready = true },
        .{ .error_code = -32 },
    }, &.{
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

test "phase 8 perf-buffer poll helper keeps the final return-path choice explicit" {
    const successful = try perf_buffer_poll.summarizePollExecutionResultFromWaitResult(12, 3, &.{
        .{ .ready = true },
        .{ .ready = true },
        .{ .error_code = -32 },
    }, &.{
        .{ .records_processed = 4 },
        .{ .records_processed = 2 },
    });
    try std.testing.expectEqual(perf_buffer_poll.PollReturnDisposition.ready_count, successful.disposition);
    try std.testing.expectEqual(@as(i32, 3), successful.return_value);

    const failed = try perf_buffer_poll.resolvePollExecutionResultFromWaitResult(12, 3, &.{
        .{ .ready = true },
        .{ .ready = true },
        .{ .error_code = -32 },
    }, &.{
        .{ .records_processed = 4 },
        .{ .result = -11 },
    });
    try std.testing.expectEqual(perf_buffer_poll.PollReturnDisposition.processing_error, failed.disposition);
    try std.testing.expectEqual(@as(i32, -11), failed.return_value);
}

test "phase 8 perf-buffer poll helper rejects processing beyond counted ready buffers" {
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

test "phase 8 perf-buffer poll helper rejects impossible post-wait record processing" {
    try std.testing.expectError(
        perf_buffer_poll.PollError.NonReadyWaitHasProcessedRecords,
        perf_buffer_poll.summarizePollExecution(0, .timed_out, &.{}, &.{.{ .records_processed = 1 }}),
    );
    try std.testing.expectError(
        perf_buffer_poll.PollError.ReadyBufferProcessingExceedsReadyCount,
        perf_buffer_poll.summarizePollExecution(5, .{ .ready_events = 1 }, &.{.{ .ready = true }}, &.{
            .{ .records_processed = 1 },
            .{ .records_processed = 2 },
        }),
    );
}

test "phase 8 perf-buffer poll helper rejects impossible post-wait buffer state" {
    try std.testing.expectError(
        perf_buffer_poll.PollError.TimeoutObservationHasReadyBuffer,
        perf_buffer_poll.summarizePoll(0, .timed_out, &.{.{ .error_code = -11 }}),
    );
    try std.testing.expectError(
        perf_buffer_poll.PollError.InterruptedObservationHasReadyBuffer,
        perf_buffer_poll.summarizePoll(-1, .interrupted, &.{.{ .ready = true }}),
    );
    try std.testing.expectError(
        perf_buffer_poll.PollError.FailedObservationHasBufferState,
        perf_buffer_poll.summarizePoll(5, .{ .failed = -22 }, &.{.{ .error_code = -22 }}),
    );
}
