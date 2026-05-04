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
