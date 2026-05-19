const std = @import("std");
const perf_buffer_poll = @import("perf_buffer_poll");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readWorkspaceFile(
    allocator: std.mem.Allocator,
    path: []const u8,
    limit: usize,
) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(limit),
    );
}

test "phase 8 perf-buffer poll tests README keeps the current direct-readback packet explicit" {
    const note = try readWorkspaceFile(
        std.testing.allocator,
        "zigux/tests/README.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(note);

    try expectContains(note, "current direct-readback Phase 8 anchors:");
    try expectContains(note, "`scripts/zigux/check-phase8-tests-readme-alignment.py`");
    try expectContains(note, "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`");
    try expectContains(note, "`zigux/tests/phase8_perf_buffer_poll.zig`");
    try expectContains(note, "`tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`");
    try expectContains(
        note,
        "current mixed-source file-path-handle bridge companions also remain reviewable on current `master` through the public tree and aligned reminder packet:",
    );
    try expectContains(
        note,
        "`Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`",
    );
    try expectContains(note, "`Documentation/zigux/phase8-file-path-handle-bridge-slice.md`");
    try expectContains(note, "`scripts/zigux/validate-phase8.py`");
    try expectContains(note, "`tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`");
    try expectContains(note, "`zigux/tests/phase8_file_path_handle_bridge.zig`");
    try expectContains(note, "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`");
    try expectContains(note, "`zigux/tests/phase8_build.zig`");
    try expectContains(note, "`make -C zigux phase8-file-path-handle-bridge-test`");
    try expectContains(
        note,
        "repo-reality warning for the broader remaining Phase 8 tooling packet:",
    );
    try expectContains(note, "`Documentation/zigux/phase8-tooling-lane-sequencing.md`");
    try expectContains(note, "`Documentation/zigux/phase8-help-slice.md`");
    try expectContains(note, "`Documentation/zigux/phase8-kallsyms-slice.md`");
    try expectContains(note, "`Documentation/zigux/phase8-libbpf-segment-survey.md`");
    try expectContains(note, "`zigux/tests/phase8_perf_buffer_poll_only_build.zig`");
    try expectContains(note, "`zigux/tests/phase8_libbpf_segments.zig`");
    try expectContains(note, "`zigux/Makefile`");
    try expectContains(
        note,
        "keep the narrower current Phase 8 reminder tied to the directly readable tests-readme checker plus the surviving perf-buffer poll checker, helper, and focused test packet, while also keeping the landed mixed-source file-path-handle bridge packet visible through the shared bridge-boundary survey, bridge slice, validator entrypoint, focused bridge proof, and helper-local replay instead of treating that same-lane bridge surface as missing current-master evidence",
    );
}

test "phase 8 perf-buffer poll scripts README keeps the surviving bridge packet explicit" {
    const note = try readWorkspaceFile(
        std.testing.allocator,
        "scripts/zigux/README.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(note);

    try expectContains(
        note,
        "Phase 8 flow - the current userspace-adjacent tooling reminder should stay anchored to the surviving perf-buffer poll packet together with the mixed-source file-path-handle bridge packet and its shipped validator and make routes, instead of reconstructing older help, kallsyms, or broader shared-bridge claims from paths that current `master` still does not serve directly",
    );
    try expectContains(note, "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`");
    try expectContains(
        note,
        "`zigux/tests/phase8_perf_buffer_poll.zig` remains the surviving direct Phase 8 replay surface",
    );
    try expectContains(
        note,
        "keep the current Phase 8 follow-through tied to the surviving perf-buffer-poll gate, the tests-root Phase 8 summary, the shipped file-path-handle bridge validator and helper packet, and the live shared build evidence instead of widening back into exec-cmd, help, kallsyms, or broader libbpf segment wording from older route names alone",
    );
}

test "phase 8 perf-buffer poll helper keeps direct ready-buffer attempt wrappers aligned" {
    const buffers = [_]perf_buffer_poll.BufferObservation{
        .{},
        .{ .ready = true },
        .{},
        .{ .ready = true },
    };

    try std.testing.expectEqual(
        @as(usize, 1),
        try perf_buffer_poll.resolveReadyBufferAttemptAtIndex(&buffers, 0),
    );
    try std.testing.expectEqual(
        @as(usize, 3),
        try perf_buffer_poll.resolveReadyBufferAttemptAtIndex(&buffers, 1),
    );
    try std.testing.expectError(
        error.MissingReadyBuffer,
        perf_buffer_poll.resolveReadyBufferAttemptAtIndex(&buffers, 2),
    );

    try std.testing.expectEqual(
        @as(i32, 1),
        perf_buffer_poll.resolveReadyBufferAttemptIndexReturn(&buffers, 0),
    );
    try std.testing.expectEqual(
        @as(i32, 3),
        perf_buffer_poll.resolveReadyBufferAttemptIndexReturn(&buffers, 1),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        perf_buffer_poll.resolveReadyBufferAttemptIndexReturn(&buffers, 2),
    );
}

test "phase 8 perf-buffer poll helper keeps the final return-path bookkeeping below routing parity" {
    const success = try perf_buffer_poll.summarizePollExecutionResultFromWaitResult(
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
    try std.testing.expectEqual(
        perf_buffer_poll.PollReturnDisposition.ready_count,
        success.disposition,
    );
    try std.testing.expectEqual(@as(i32, 3), success.return_value);
    try std.testing.expectEqual(@as(usize, 6), success.execution.processed_record_count);

    const processing_failure = try perf_buffer_poll.summarizePollExecutionResultFromWaitResult(
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
    );
    try std.testing.expectEqual(
        perf_buffer_poll.PollReturnDisposition.processing_failed,
        processing_failure.disposition,
    );
    try std.testing.expectEqual(@as(i32, -11), processing_failure.return_value);
    try std.testing.expectEqual(
        @as(?usize, 1),
        processing_failure.execution.first_process_error_index,
    );
    try std.testing.expectEqual(
        @as(?usize, 1),
        processing_failure.execution.first_process_error_ready_index,
    );
}

test "phase 8 perf-buffer poll helper rejects ready waits without processing attempts" {
    try std.testing.expectError(
        perf_buffer_poll.PollError.InconsistentProcessingAccountingSummary,
        perf_buffer_poll.summarizePollExecutionResultFromWaitResult(
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

test "phase 8 perf-buffer poll helper rejects successful waits that stop before every ready buffer is processed" {
    try std.testing.expectError(
        perf_buffer_poll.PollError.ReadyBufferProcessingFallsShortOfReadyCount,
        perf_buffer_poll.summarizePollExecutionResultFromWaitResult(
            12,
            2,
            &.{
                .{ .ready = true },
                .{ .ready = true },
            },
            &.{
                .{ .records_processed = 4 },
            },
        ),
    );
}

test "phase 8 perf-buffer poll rejects impossible post-wait buffer states" {
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

test "phase 8 perf-buffer poll helper keeps buffer-fd lookup returns compact and errno-shaped" {
    const buffer_fds = [_]?i32{ 9, null, 21 };

    const found = perf_buffer_poll.summarizeBufferFdLookup(&buffer_fds, 2);
    try std.testing.expectEqual(
        perf_buffer_poll.BufferFdLookupDisposition.found_fd,
        found.disposition,
    );
    try std.testing.expectEqual(@as(i32, 21), perf_buffer_poll.resolveBufferFdLookupReturn(found));

    const missing = perf_buffer_poll.summarizeBufferFdLookup(&buffer_fds, 1);
    try std.testing.expectEqual(
        perf_buffer_poll.BufferFdLookupDisposition.missing_fd,
        missing.disposition,
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        perf_buffer_poll.resolveBufferFdLookupReturn(missing),
    );

    const invalid = perf_buffer_poll.summarizeBufferFdLookup(&buffer_fds, 4);
    try std.testing.expectEqual(
        perf_buffer_poll.BufferFdLookupDisposition.invalid_index,
        invalid.disposition,
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        perf_buffer_poll.resolveBufferFdLookupReturn(invalid),
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
    try std.testing.expectEqual(@as(usize, 8192), try perf_buffer_poll.resolveBufferWindowMappedSize(found));
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
    try std.testing.expectError(error.MissingWindow, perf_buffer_poll.resolveBufferWindowMappedSize(missing));
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
    try std.testing.expectError(error.InvalidIndex, perf_buffer_poll.resolveBufferWindowMappedSize(invalid));
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        perf_buffer_poll.resolveBufferWindowLookupReturn(invalid),
    );
}

test "phase 8 perf-buffer poll helper resolves direct fd and mapped-window lookups without summary plumbing" {
    const buffer_fds = [_]?i32{ 9, null, 21 };

    try std.testing.expectEqual(@as(i32, 21), try perf_buffer_poll.resolveBufferFdAtIndex(&buffer_fds, 2));
    try std.testing.expectError(error.MissingFd, perf_buffer_poll.resolveBufferFdAtIndex(&buffer_fds, 1));
    try std.testing.expectError(error.InvalidIndex, perf_buffer_poll.resolveBufferFdAtIndex(&buffer_fds, 4));

    const buffer_windows = [_]?perf_buffer_poll.BufferWindowObservation{
        .{ .mapped_size = 4096 },
        null,
        .{ .mapped_size = 8192 },
    };

    try std.testing.expectEqual(
        @as(usize, 8192),
        try perf_buffer_poll.resolveBufferWindowMappedSizeAtIndex(&buffer_windows, 2),
    );
    try std.testing.expectError(
        error.MissingWindow,
        perf_buffer_poll.resolveBufferWindowMappedSizeAtIndex(&buffer_windows, 1),
    );
    try std.testing.expectError(
        error.InvalidIndex,
        perf_buffer_poll.resolveBufferWindowMappedSizeAtIndex(&buffer_windows, 4),
    );
}

test "resolvePollExecutionResultFromWaitResult rejects mismatched wait-result and execution summaries" {
    const resolvePollExecutionResultFromWaitResult =
        perf_buffer_poll.resolvePollExecutionResultFromWaitResult;
    // _ = resolvePollExecutionResultFromWaitResult;

    const ready_execution = try perf_buffer_poll.summarizePollExecutionFromWaitResult(
        12,
        2,
        &.{
            .{ .ready = true },
            .{ .ready = true },
        },
        &.{
            .{ .records_processed = 1 },
            .{ .records_processed = 1 },
        },
    );
    try std.testing.expectError(
        perf_buffer_poll.PollError.WaitResultDisagreesWithExecutionOutcome,
        resolvePollExecutionResultFromWaitResult(0, ready_execution),
    );
    try std.testing.expectError(
        perf_buffer_poll.PollError.WaitResultDisagreesWithReadyEventCount,
        resolvePollExecutionResultFromWaitResult(3, ready_execution),
    );

    const failed_execution = try perf_buffer_poll.summarizePollExecutionFromWaitResult(
        5,
        -5,
        &.{},
        &.{},
    );
    try std.testing.expectError(
        perf_buffer_poll.PollError.WaitResultDisagreesWithFailureCode,
        resolvePollExecutionResultFromWaitResult(-9, failed_execution),
    );
}
