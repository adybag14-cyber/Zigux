const std = @import("std");

const cpu_mask = @import("cpu_mask.zig");
const logging = @import("logging.zig");
const online_cpu_routing = @import("online_cpu_routing.zig");
const perf_buffer_poll = @import("perf_buffer_poll.zig");
const pin_path = @import("pin_path.zig");
const type_names = @import("type_names.zig");

fn expectHasDecl(comptime Module: type, comptime decl_name: []const u8) !void {
    try std.testing.expect(@hasDecl(Module, decl_name));
}

const CpuMaskReaderContext = struct {
    input: []const u8,
    cursor: usize = 0,
};

fn readCpuMaskChunks(context: ?*anyopaque, buffer: []u8) anyerror!?usize {
    const typed_context: *CpuMaskReaderContext = @ptrCast(@alignCast(context.?));
    if (typed_context.cursor >= typed_context.input.len) return null;

    const remaining = typed_context.input.len - typed_context.cursor;
    const count = @min(buffer.len, remaining);
    @memcpy(buffer[0..count], typed_context.input[typed_context.cursor .. typed_context.cursor + count]);
    typed_context.cursor += count;
    return count;
}

fn readZeroCpuMaskChunks(context: ?*anyopaque, buffer: []u8) anyerror!?usize {
    _ = context;
    _ = buffer;
    return 0;
}

fn readTooManyCpuMaskChunks(context: ?*anyopaque, buffer: []u8) anyerror!?usize {
    _ = context;
    return buffer.len + 1;
}

test "materialized tools/lib/bpf Zigux segments compile together and keep their focused tests live" {
    std.testing.refAllDecls(cpu_mask);
    std.testing.refAllDecls(logging);
    std.testing.refAllDecls(online_cpu_routing);
    std.testing.refAllDecls(perf_buffer_poll);
    std.testing.refAllDecls(pin_path);
    std.testing.refAllDecls(type_names);
}

test "materialized tools/lib/bpf Zigux segments keep their current bounded entrypoints explicit" {
    try expectHasDecl(cpu_mask, "CpuMask");
    try expectHasDecl(cpu_mask, "PossibleCpuSummary");
    try expectHasDecl(cpu_mask, "ParseCpuMaskError");
    try expectHasDecl(cpu_mask, "ChunkReader");
    try expectHasDecl(cpu_mask, "parseCpuMaskString");
    try expectHasDecl(cpu_mask, "parseCpuMaskFromReader");
    try expectHasDecl(cpu_mask, "summarizePossibleCpus");
    try expectHasDecl(cpu_mask, "summarizePossibleCpusFromReader");
    try expectHasDecl(cpu_mask, "countPossibleCpus");
    try expectHasDecl(cpu_mask, "isOnlineCpuEligible");
    try expectHasDecl(cpu_mask, "derivePerfBufferAutoCpuCount");
    try expectHasDecl(cpu_mask, "derivePerfBufferAutoCpuCountFromReader");

    try expectHasDecl(logging, "parseLogLevelSetting");
    try expectHasDecl(logging, "shouldLog");
    try expectHasDecl(logging, "shouldLogWithEnv");
    try expectHasDecl(logging, "formatUnrecognizedLogLevel");
    try expectHasDecl(logging, "libbpfMajorVersion");
    try expectHasDecl(logging, "libbpfMinorVersion");
    try expectHasDecl(logging, "libbpfVersionString");
    try expectHasDecl(logging, "libbpfErrorCode");
    try expectHasDecl(logging, "libbpfErrorMessage");
    try expectHasDecl(logging, "formatLibbpfError");

    try expectHasDecl(online_cpu_routing, "OnlineCpuCursor");
    try expectHasDecl(online_cpu_routing, "OnlineCpuRouteAttemptDisposition");
    try expectHasDecl(online_cpu_routing, "OnlineCpuRouteAttemptSummary");
    try expectHasDecl(online_cpu_routing, "OnlineCpuRoutingDisposition");
    try expectHasDecl(online_cpu_routing, "OnlineCpuRoutingSummary");
    try expectHasDecl(online_cpu_routing, "advanceOnlineCpuCursor");
    try expectHasDecl(online_cpu_routing, "summarizeNextOnlineCpuRoute");
    try expectHasDecl(online_cpu_routing, "summarizeOnlineCpuRouting");

    try expectHasDecl(perf_buffer_poll, "classifyObservedWaitResult");
    try expectHasDecl(perf_buffer_poll, "classifyWaitClass");
    try expectHasDecl(perf_buffer_poll, "advanceReadyBufferCursor");
    try expectHasDecl(perf_buffer_poll, "resolveReadyBufferAttemptIndex");
    try expectHasDecl(perf_buffer_poll, "summarizeReadyBufferAttemptLookup");
    try expectHasDecl(perf_buffer_poll, "resolveReadyBufferAttemptLookup");
    try expectHasDecl(perf_buffer_poll, "resolveReadyBufferAttemptAtIndex");
    try expectHasDecl(perf_buffer_poll, "resolveReadyBufferAttemptIndexReturn");
    try expectHasDecl(perf_buffer_poll, "resolveReadyBufferAttemptLookupReturn");
    try expectHasDecl(perf_buffer_poll, "summarizeReadyBuffers");
    try expectHasDecl(perf_buffer_poll, "summarizeProcessRecords");
    try expectHasDecl(perf_buffer_poll, "summarizePoll");
    try expectHasDecl(perf_buffer_poll, "summarizePollFromWaitResult");
    try expectHasDecl(perf_buffer_poll, "summarizePollExecution");
    try expectHasDecl(perf_buffer_poll, "summarizePollExecutionFromWaitResult");
    try expectHasDecl(perf_buffer_poll, "summarizePollExecutionResultFromWaitResult");
    try expectHasDecl(perf_buffer_poll, "resolvePollExecutionResultFromWaitResult");
    try expectHasDecl(perf_buffer_poll, "summarizeBufferFdLookup");
    try expectHasDecl(perf_buffer_poll, "resolveBufferFdAtIndex");
    try expectHasDecl(perf_buffer_poll, "resolveBufferFd");
    try expectHasDecl(perf_buffer_poll, "resolveBufferFdLookupReturn");
    try expectHasDecl(perf_buffer_poll, "resolveBufferFdLookupReturnAtIndex");
    try expectHasDecl(perf_buffer_poll, "summarizeBufferWindowLookup");
    try expectHasDecl(perf_buffer_poll, "resolveBufferWindowMappedSizeAtIndex");
    try expectHasDecl(perf_buffer_poll, "resolveBufferWindowMappedSize");
    try expectHasDecl(perf_buffer_poll, "resolveBufferWindowLookupReturn");
    try expectHasDecl(perf_buffer_poll, "resolveBufferWindowLookupReturnAtIndex");

    try expectHasDecl(pin_path, "pathnameConcat");
    try expectHasDecl(pin_path, "sanitizePinPath");
    try expectHasDecl(pin_path, "validatePinName");
    try expectHasDecl(pin_path, "validatePinRootPath");
    try expectHasDecl(pin_path, "buildMapPinPath");
    try expectHasDecl(pin_path, "buildValidatedMapPinPath");
    try expectHasDecl(pin_path, "buildSanitizedMapPinPath");
    try expectHasDecl(pin_path, "buildValidatedSanitizedMapPinPath");
    try expectHasDecl(pin_path, "buildProgramPinPath");
    try expectHasDecl(pin_path, "buildValidatedProgramPinPath");
    try expectHasDecl(pin_path, "buildSanitizedProgramPinPath");
    try expectHasDecl(pin_path, "buildValidatedSanitizedProgramPinPath");

    try expectHasDecl(type_names, "libbpfBpfAttachTypeStr");
    try expectHasDecl(type_names, "libbpfBpfMapTypeStr");
    try expectHasDecl(type_names, "libbpfBpfLinkTypeStr");
    try expectHasDecl(type_names, "libbpfBpfProgTypeStr");
    try expectHasDecl(type_names, "formatLibbpfBpfAttachType");
    try expectHasDecl(type_names, "formatLibbpfBpfMapType");
    try expectHasDecl(type_names, "formatLibbpfBpfLinkType");
    try expectHasDecl(type_names, "formatLibbpfBpfProgType");
}

test "materialized tools/lib/bpf Zigux segments keep direct return helpers explicit and stable" {
    const buffers = [_]perf_buffer_poll.BufferObservation{
        .{},
        .{ .ready = true },
        .{},
        .{ .ready = true },
    };
    try std.testing.expectEqual(@as(i32, 1), perf_buffer_poll.resolveReadyBufferAttemptIndexReturn(&buffers, 0));
    try std.testing.expectEqual(@as(i32, 3), perf_buffer_poll.resolveReadyBufferAttemptIndexReturn(&buffers, 1));
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        perf_buffer_poll.resolveReadyBufferAttemptIndexReturn(&buffers, 2),
    );

    const buffer_fds = [_]?i32{ 9, null, 21 };
    try std.testing.expectEqual(@as(i32, 21), perf_buffer_poll.resolveBufferFdLookupReturnAtIndex(&buffer_fds, 2));
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        perf_buffer_poll.resolveBufferFdLookupReturnAtIndex(&buffer_fds, 1),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        perf_buffer_poll.resolveBufferFdLookupReturnAtIndex(&buffer_fds, 4),
    );

    const buffer_windows = [_]?perf_buffer_poll.BufferWindowObservation{
        .{ .mapped_size = 4096 },
        null,
        .{ .mapped_size = 8192 },
    };
    try std.testing.expectEqual(@as(i32, 0), perf_buffer_poll.resolveBufferWindowLookupReturnAtIndex(&buffer_windows, 0));
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        perf_buffer_poll.resolveBufferWindowLookupReturnAtIndex(&buffer_windows, 1),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        perf_buffer_poll.resolveBufferWindowLookupReturnAtIndex(&buffer_windows, 4),
    );
}

test "materialized tools/lib/bpf Zigux segments keep stable perf-buffer summary outputs explicit" {
    const ready_buffers = [_]perf_buffer_poll.BufferObservation{
        .{},
        .{ .ready = true },
        .{ .error_code = -32 },
        .{ .ready = true },
    };
    try std.testing.expectEqualDeep(
        perf_buffer_poll.ReadyBufferSummary{
            .ready_count = 2,
            .first_ready_index = 1,
            .first_error = -32,
        },
        perf_buffer_poll.summarizeReadyBuffers(&ready_buffers),
    );
    try std.testing.expectEqualDeep(
        perf_buffer_poll.PollSummary{
            .wait_class = .bounded,
            .outcome = .ready,
            .observed_ready_events = 3,
            .ready_count = 2,
            .first_ready_index = 1,
            .first_error = -32,
        },
        try perf_buffer_poll.summarizePollFromWaitResult(12, 3, &ready_buffers),
    );

    const process_observations = [_]perf_buffer_poll.ProcessRecordObservation{
        .{ .records_processed = 4 },
        .{ .result = -11 },
    };
    try std.testing.expectEqualDeep(
        perf_buffer_poll.ProcessRecordSummary{
            .attempted_count = 2,
            .completed_count = 1,
            .processed_record_count = 4,
            .first_error_index = 1,
            .first_error = -11,
        },
        perf_buffer_poll.summarizeProcessRecords(&process_observations),
    );

    const execution_buffers = [_]perf_buffer_poll.BufferObservation{
        .{},
        .{ .ready = true },
        .{},
        .{ .ready = true },
    };
    const execution = try perf_buffer_poll.summarizePollExecutionFromWaitResult(
        12,
        2,
        &execution_buffers,
        &process_observations,
    );
    try std.testing.expectEqualDeep(
        perf_buffer_poll.PollExecutionSummary{
            .poll = .{
                .wait_class = .bounded,
                .outcome = .ready,
                .observed_ready_events = 2,
                .ready_count = 2,
                .first_ready_index = 1,
                .first_error = null,
            },
            .attempted_ready_buffer_count = 2,
            .completed_ready_buffer_count = 1,
            .processed_record_count = 4,
            .first_process_error_index = 1,
            .first_process_error_ready_index = 3,
            .first_process_error = -11,
        },
        execution,
    );
    try std.testing.expectEqualDeep(
        perf_buffer_poll.PollExecutionResult{
            .execution = execution,
            .return_value = -11,
            .disposition = .processing_failed,
        },
        try perf_buffer_poll.summarizePollExecutionResultFromWaitResult(
            12,
            2,
            &execution_buffers,
            &process_observations,
        ),
    );

    const buffer_fds = [_]?i32{ 9, null, 21 };
    try std.testing.expectEqualDeep(
        perf_buffer_poll.BufferFdLookupSummary{
            .slot_count = 3,
            .requested_index = 2,
            .fd = 21,
            .disposition = .found_fd,
        },
        perf_buffer_poll.summarizeBufferFdLookup(&buffer_fds, 2),
    );

    const buffer_windows = [_]?perf_buffer_poll.BufferWindowObservation{
        .{ .mapped_size = 4096 },
        null,
        .{ .mapped_size = 8192 },
    };
    try std.testing.expectEqualDeep(
        perf_buffer_poll.BufferWindowLookupSummary{
            .slot_count = 3,
            .requested_index = 2,
            .mapped_size = 8192,
            .disposition = .found_window,
        },
        perf_buffer_poll.summarizeBufferWindowLookup(&buffer_windows, 2),
    );
}

test "materialized tools/lib/bpf Zigux segments keep stable perf-buffer wait and cursor helpers explicit" {
    try std.testing.expectEqualDeep(
        perf_buffer_poll.WaitObservation.timed_out,
        perf_buffer_poll.classifyObservedWaitResult(0),
    );
    try std.testing.expectEqualDeep(
        perf_buffer_poll.WaitObservation.interrupted,
        perf_buffer_poll.classifyObservedWaitResult(-@as(i32, @intFromEnum(std.os.linux.E.INTR))),
    );
    try std.testing.expectEqualDeep(
        perf_buffer_poll.WaitObservation{ .ready_events = 3 },
        perf_buffer_poll.classifyObservedWaitResult(3),
    );
    try std.testing.expectEqualDeep(
        perf_buffer_poll.WaitObservation{ .failed = -22 },
        perf_buffer_poll.classifyObservedWaitResult(-22),
    );

    try std.testing.expectEqual(perf_buffer_poll.WaitClass.nonblocking, try perf_buffer_poll.classifyWaitClass(0));
    try std.testing.expectEqual(perf_buffer_poll.WaitClass.bounded, try perf_buffer_poll.classifyWaitClass(12));
    try std.testing.expectEqual(perf_buffer_poll.WaitClass.indefinite, try perf_buffer_poll.classifyWaitClass(-1));
    try std.testing.expectError(error.InvalidTimeout, perf_buffer_poll.classifyWaitClass(-2));

    const buffers = [_]perf_buffer_poll.BufferObservation{
        .{},
        .{},
        .{ .ready = true },
        .{},
        .{ .ready = true },
    };
    try std.testing.expectEqualDeep(
        perf_buffer_poll.ReadyBufferCursor{
            .start_index = 0,
            .next_scan_index = 3,
            .ready_index = 2,
            .skipped_nonready_count = 2,
        },
        perf_buffer_poll.advanceReadyBufferCursor(&buffers, 0),
    );
    try std.testing.expectEqualDeep(
        perf_buffer_poll.ReadyBufferCursor{
            .start_index = 3,
            .next_scan_index = 5,
            .ready_index = 4,
            .skipped_nonready_count = 1,
        },
        perf_buffer_poll.advanceReadyBufferCursor(&buffers, 3),
    );
    try std.testing.expectEqualDeep(
        perf_buffer_poll.ReadyBufferCursor{
            .start_index = 6,
            .next_scan_index = buffers.len,
            .ready_index = null,
            .skipped_nonready_count = 0,
        },
        perf_buffer_poll.advanceReadyBufferCursor(&buffers, 6),
    );
}

test "materialized tools/lib/bpf Zigux segments keep stable online-CPU routing helper outputs explicit" {
    const online_cpu_mask = [_]bool{ false, true, false, true, true };

    try std.testing.expectEqualDeep(
        online_cpu_routing.OnlineCpuCursor{
            .start_index = 0,
            .next_scan_index = 2,
            .cpu_index = 1,
            .skipped_offline_count = 1,
        },
        online_cpu_routing.advanceOnlineCpuCursor(&online_cpu_mask, 0),
    );

    try std.testing.expectEqualDeep(
        online_cpu_routing.OnlineCpuRouteAttemptSummary{
            .start_index = 0,
            .next_scan_index = 2,
            .cpu_index = 1,
            .buffer_index = 0,
            .buffer_fd = 11,
            .skipped_offline_count = 1,
            .disposition = .routed_cpu,
        },
        online_cpu_routing.summarizeNextOnlineCpuRoute(
            &online_cpu_mask,
            0,
            &.{ 11, 17, 29 },
            0,
        ),
    );
    try std.testing.expectEqualDeep(
        online_cpu_routing.OnlineCpuRouteAttemptSummary{
            .start_index = 2,
            .next_scan_index = 4,
            .cpu_index = 3,
            .buffer_index = 1,
            .buffer_fd = null,
            .skipped_offline_count = 1,
            .disposition = .missing_buffer_fd,
        },
        online_cpu_routing.summarizeNextOnlineCpuRoute(
            &online_cpu_mask,
            2,
            &.{ 11, null, 29 },
            1,
        ),
    );

    try std.testing.expectEqualDeep(
        online_cpu_routing.OnlineCpuRoutingSummary{
            .online_cpu_count = 3,
            .requested_cpu_count = 2,
            .selected_cpu_count = 2,
            .buffer_slot_count = 3,
            .routed_cpu_count = 2,
            .first_routed_cpu_index = 1,
            .next_online_cpu_index = 4,
            .missing_buffer_index = null,
            .disposition = .requested_subset,
        },
        online_cpu_routing.summarizeOnlineCpuRouting(
            &online_cpu_mask,
            2,
            &.{ 11, 17, 29 },
        ),
    );
    try std.testing.expectEqualDeep(
        online_cpu_routing.OnlineCpuRoutingSummary{
            .online_cpu_count = 3,
            .requested_cpu_count = 0,
            .selected_cpu_count = 3,
            .buffer_slot_count = 2,
            .routed_cpu_count = 2,
            .first_routed_cpu_index = 1,
            .next_online_cpu_index = 4,
            .missing_buffer_index = 2,
            .disposition = .missing_buffer_slot,
        },
        online_cpu_routing.summarizeOnlineCpuRouting(
            &online_cpu_mask,
            0,
            &.{ 11, 17 },
        ),
    );
}

test "materialized tools/lib/bpf Zigux segments keep typed direct and summary lookup helpers explicit and stable" {
    const buffers = [_]perf_buffer_poll.BufferObservation{
        .{},
        .{ .ready = true },
        .{},
        .{ .ready = true },
    };
    try std.testing.expectEqual(@as(usize, 1), try perf_buffer_poll.resolveReadyBufferAttemptAtIndex(&buffers, 0));
    try std.testing.expectEqual(@as(usize, 3), try perf_buffer_poll.resolveReadyBufferAttemptAtIndex(&buffers, 1));
    try std.testing.expectError(error.MissingReadyBuffer, perf_buffer_poll.resolveReadyBufferAttemptAtIndex(&buffers, 2));

    const buffer_fds = [_]?i32{ 9, null, 21 };
    try std.testing.expectEqual(@as(i32, 21), try perf_buffer_poll.resolveBufferFdAtIndex(&buffer_fds, 2));
    try std.testing.expectError(error.MissingFd, perf_buffer_poll.resolveBufferFdAtIndex(&buffer_fds, 1));
    try std.testing.expectError(error.InvalidIndex, perf_buffer_poll.resolveBufferFdAtIndex(&buffer_fds, 4));
    try std.testing.expectEqual(
        @as(i32, 21),
        try perf_buffer_poll.resolveBufferFd(
            perf_buffer_poll.summarizeBufferFdLookup(&buffer_fds, 2),
        ),
    );
    try std.testing.expectError(
        error.MissingFd,
        perf_buffer_poll.resolveBufferFd(
            perf_buffer_poll.summarizeBufferFdLookup(&buffer_fds, 1),
        ),
    );
    try std.testing.expectError(
        error.InvalidIndex,
        perf_buffer_poll.resolveBufferFd(
            perf_buffer_poll.summarizeBufferFdLookup(&buffer_fds, 4),
        ),
    );

    const buffer_windows = [_]?perf_buffer_poll.BufferWindowObservation{
        .{ .mapped_size = 4096 },
        null,
        .{ .mapped_size = 8192 },
    };
    try std.testing.expectEqual(@as(usize, 8192), try perf_buffer_poll.resolveBufferWindowMappedSizeAtIndex(&buffer_windows, 2));
    try std.testing.expectError(error.MissingWindow, perf_buffer_poll.resolveBufferWindowMappedSizeAtIndex(&buffer_windows, 1));
    try std.testing.expectError(error.InvalidIndex, perf_buffer_poll.resolveBufferWindowMappedSizeAtIndex(&buffer_windows, 4));
    try std.testing.expectEqual(
        @as(usize, 8192),
        try perf_buffer_poll.resolveBufferWindowMappedSize(
            perf_buffer_poll.summarizeBufferWindowLookup(&buffer_windows, 2),
        ),
    );
    try std.testing.expectError(
        error.MissingWindow,
        perf_buffer_poll.resolveBufferWindowMappedSize(
            perf_buffer_poll.summarizeBufferWindowLookup(&buffer_windows, 1),
        ),
    );
    try std.testing.expectError(
        error.InvalidIndex,
        perf_buffer_poll.resolveBufferWindowMappedSize(
            perf_buffer_poll.summarizeBufferWindowLookup(&buffer_windows, 4),
        ),
    );
}

test "materialized tools/lib/bpf Zigux segments keep stable logging helper outputs explicit" {
    try std.testing.expectEqualDeep(
        logging.ParsedLogLevel{ .min_level = .debug, .recognized = true },
        logging.parseLogLevelSetting("DEBUG"),
    );
    try std.testing.expectEqualDeep(
        logging.ParsedLogLevel{ .min_level = .info, .recognized = false },
        logging.parseLogLevelSetting("chatty"),
    );
    try std.testing.expectEqualDeep(
        logging.ParsedLogLevel{ .min_level = .info, .recognized = true },
        logging.parseLogLevelSetting(null),
    );
    try std.testing.expect(logging.shouldLogWithEnv(.debug, "debug"));
    try std.testing.expect(!logging.shouldLogWithEnv(.debug, null));

    var warning_buffer: [128]u8 = undefined;
    try std.testing.expectEqualStrings(
        "libbpf: unrecognized 'LIBBPF_LOG_LEVEL' envvar value: 'chatty', should be one of 'warn', 'debug', or 'info'.\n",
        try logging.formatUnrecognizedLogLevel(warning_buffer[0..], "chatty"),
    );

    var version_buffer: [16]u8 = undefined;
    try std.testing.expectEqual(@as(u32, 1), logging.libbpfMajorVersion());
    try std.testing.expectEqual(@as(u32, 7), logging.libbpfMinorVersion());
    try std.testing.expectEqualStrings("v1.7", try logging.libbpfVersionString(version_buffer[0..]));

    var error_buffer: [40]u8 = undefined;
    try std.testing.expectEqual(
        @as(u32, @intFromEnum(logging.LibbpfErrno.verify)),
        logging.libbpfErrorCode(-@intFromEnum(logging.LibbpfErrno.verify)),
    );
    try std.testing.expectEqualStrings(
        "Kernel verifier blocks program loading",
        logging.libbpfErrorMessage(-@intFromEnum(logging.LibbpfErrno.verify)).?,
    );
    try std.testing.expectEqualStrings(
        "Something wrong in libelf",
        try logging.formatLibbpfError(
            error_buffer[0..],
            -@as(i32, @intFromEnum(logging.LibbpfErrno.libelf)),
        ),
    );
    try std.testing.expectEqualStrings(
        "Kernel verifier blocks program loading",
        try logging.formatLibbpfError(
            error_buffer[0..],
            -@as(i32, @intFromEnum(logging.LibbpfErrno.verify)),
        ),
    );
    try std.testing.expectEqualStrings(
        "Incorrect netlink message parsing",
        try logging.formatLibbpfError(
            error_buffer[0..],
            -@as(i32, @intFromEnum(logging.LibbpfErrno.nlparse)),
        ),
    );
    try std.testing.expectEqualStrings(
        "Unknown libbpf error 4999",
        try logging.formatLibbpfError(error_buffer[0..], -4999),
    );
    try std.testing.expectEqualStrings(
        "Unknown libbpf error 2147483648",
        try logging.formatLibbpfError(error_buffer[0..], std.math.minInt(i32)),
    );
}

test "materialized tools/lib/bpf Zigux segments keep stable libbpf type-name outputs explicit" {
    try std.testing.expectEqualStrings("ringbuf", type_names.libbpfBpfMapTypeStr(27).?);
    try std.testing.expect(type_names.libbpfBpfMapTypeStr(99) == null);
    try std.testing.expectEqualStrings("perf_event", type_names.libbpfBpfAttachTypeStr(41).?);
    try std.testing.expectEqualStrings("sockmap", type_names.libbpfBpfLinkTypeStr(14).?);
    try std.testing.expectEqualStrings("netfilter", type_names.libbpfBpfProgTypeStr(32).?);

    var map_buffer: [32]u8 = undefined;
    var attach_buffer: [40]u8 = undefined;
    var link_buffer: [32]u8 = undefined;
    var prog_buffer: [32]u8 = undefined;

    try std.testing.expectEqualStrings("ringbuf", try type_names.formatLibbpfBpfMapType(map_buffer[0..], 27));
    try std.testing.expectEqualStrings("unknown_map_type(35)", try type_names.formatLibbpfBpfMapType(map_buffer[0..], 35));
    try std.testing.expectEqualStrings("unknown_map_type(99)", try type_names.formatLibbpfBpfMapType(map_buffer[0..], 99));
    try std.testing.expectEqualStrings("perf_event", try type_names.formatLibbpfBpfAttachType(attach_buffer[0..], 41));
    try std.testing.expectEqualStrings("unknown_attach_type(59)", try type_names.formatLibbpfBpfAttachType(attach_buffer[0..], 59));
    try std.testing.expectEqualStrings("sockmap", try type_names.formatLibbpfBpfLinkType(link_buffer[0..], 14));
    try std.testing.expectEqualStrings("unknown_link_type(15)", try type_names.formatLibbpfBpfLinkType(link_buffer[0..], 15));
    try std.testing.expectEqualStrings("netfilter", try type_names.formatLibbpfBpfProgType(prog_buffer[0..], 32));
    try std.testing.expectEqualStrings("unknown_prog_type(33)", try type_names.formatLibbpfBpfProgType(prog_buffer[0..], 33));
}

test "materialized tools/lib/bpf Zigux segments keep stable cpu-mask helper outputs explicit" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    var parsed = try cpu_mask.parseCpuMaskString(allocator, "0-2, 4\n");
    defer parsed.deinit(allocator);

    try std.testing.expectEqual(@as(usize, 4), parsed.countSet());
    try std.testing.expectEqualSlices(bool, &[_]bool{ true, true, true, false, true }, parsed.values);

    const summary = cpu_mask.summarizePossibleCpus(parsed.values);
    try std.testing.expectEqual(@as(usize, 5), summary.mask_bit_len);
    try std.testing.expectEqual(@as(usize, 4), summary.possible_cpu_count);
    try std.testing.expectEqual(@as(?usize, 4), summary.highest_cpu_index);
    try std.testing.expect(cpu_mask.isOnlineCpuEligible(parsed.values, 2));
    try std.testing.expect(!cpu_mask.isOnlineCpuEligible(parsed.values, 3));
    try std.testing.expectEqual(@as(usize, 4), summary.deriveAutoCpuCount(0));
    try std.testing.expectEqual(@as(usize, 2), cpu_mask.derivePerfBufferAutoCpuCount(summary.possible_cpu_count, 2));
    try std.testing.expectEqual(@as(usize, 4), cpu_mask.derivePerfBufferAutoCpuCount(summary.possible_cpu_count, 99));

    var scratch: [3]u8 = undefined;
    var reader_context = CpuMaskReaderContext{ .input = "1,3-4\n" };
    const reader = cpu_mask.ChunkReader{
        .context = &reader_context,
        .readFn = readCpuMaskChunks,
    };
    const reader_summary = try cpu_mask.summarizePossibleCpusFromReader(allocator, scratch[0..], reader);
    try std.testing.expectEqual(@as(usize, 5), reader_summary.mask_bit_len);
    try std.testing.expectEqual(@as(usize, 3), reader_summary.possible_cpu_count);
    try std.testing.expectEqual(@as(?usize, 4), reader_summary.highest_cpu_index);

    var spaced_plus = try cpu_mask.parseCpuMaskString(allocator, " +0, 2- 3\n");
    defer spaced_plus.deinit(allocator);
    try std.testing.expectEqualSlices(bool, &[_]bool{ true, false, true, true }, spaced_plus.values);
    try std.testing.expectEqual(@as(usize, 3), cpu_mask.countPossibleCpus(spaced_plus.values));

    const empty_summary = cpu_mask.summarizePossibleCpus(&.{});
    try std.testing.expectEqual(@as(usize, 0), empty_summary.mask_bit_len);
    try std.testing.expectEqual(@as(usize, 0), empty_summary.possible_cpu_count);
    try std.testing.expectEqual(@as(?usize, null), empty_summary.highest_cpu_index);
    try std.testing.expectEqual(@as(usize, 0), empty_summary.deriveAutoCpuCount(3));

    var auto_context = CpuMaskReaderContext{ .input = "0-1,4\n" };
    const auto_reader = cpu_mask.ChunkReader{
        .context = &auto_context,
        .readFn = readCpuMaskChunks,
    };
    try std.testing.expectEqual(
        @as(usize, 3),
        try cpu_mask.derivePerfBufferAutoCpuCountFromReader(allocator, scratch[0..], auto_reader, 0),
    );

    var clamped_auto_context = CpuMaskReaderContext{ .input = "2-4\n" };
    const clamped_auto_reader = cpu_mask.ChunkReader{
        .context = &clamped_auto_context,
        .readFn = readCpuMaskChunks,
    };
    try std.testing.expectEqual(
        @as(usize, 3),
        try cpu_mask.derivePerfBufferAutoCpuCountFromReader(allocator, scratch[0..], clamped_auto_reader, 9),
    );

    try std.testing.expectError(error.InvalidCpuRange, cpu_mask.parseCpuMaskString(allocator, "4-2"));

    const empty_reader = cpu_mask.ChunkReader{
        .context = null,
        .readFn = readZeroCpuMaskChunks,
    };
    try std.testing.expectError(
        error.EmptyReadBuffer,
        cpu_mask.parseCpuMaskFromReader(allocator, scratch[0..0], empty_reader),
    );
    try std.testing.expectError(
        error.EmptyReadChunk,
        cpu_mask.parseCpuMaskFromReader(allocator, scratch[0..], empty_reader),
    );

    const invalid_count_reader = cpu_mask.ChunkReader{
        .context = null,
        .readFn = readTooManyCpuMaskChunks,
    };
    try std.testing.expectError(
        error.InvalidReadCount,
        cpu_mask.parseCpuMaskFromReader(allocator, scratch[0..], invalid_count_reader),
    );
}

test "materialized tools/lib/bpf Zigux segments keep stable pin-path helper outputs explicit" {
    var buffer: [128]u8 = undefined;

    try std.testing.expectEqualStrings(
        "/sys/fs/bpf/stats_map",
        try pin_path.buildMapPinPath(buffer[0..], null, "stats_map"),
    );
    try std.testing.expectEqualStrings(
        "/custom/root/stats_map",
        try pin_path.buildMapPinPath(buffer[0..], "/custom/root", "stats_map"),
    );
    try std.testing.expectEqualStrings(
        "/tmp/bpf.v1/stats.map",
        try pin_path.buildValidatedMapPinPath(buffer[0..], "/tmp/bpf.v1", "stats.map"),
    );
    try std.testing.expectEqualStrings(
        "/cache_map",
        try pin_path.buildSanitizedMapPinPath(buffer[0..], "/", "cache.map"),
    );
    try std.testing.expectEqualStrings(
        "/sys/fs/bpf/metrics_v1",
        try pin_path.buildValidatedSanitizedMapPinPath(buffer[0..], null, "metrics.v1"),
    );
    try std.testing.expectEqualStrings(
        "/tmp/bpf.v1/xdp_dispatch",
        try pin_path.buildValidatedProgramPinPath(buffer[0..], "/tmp/bpf.v1", "xdp_dispatch"),
    );
    try std.testing.expectEqualStrings(
        "/tmp/bpf.v1/xdp_dispatch_v1",
        try pin_path.buildSanitizedProgramPinPath(buffer[0..], "/tmp/bpf.v1", "xdp_dispatch.v1"),
    );
    try std.testing.expectEqualStrings(
        "/sys/fs/bpf/xdp_dispatch_v1",
        try pin_path.buildValidatedSanitizedProgramPinPath(buffer[0..], null, "xdp_dispatch.v1"),
    );
    try std.testing.expectEqualStrings(
        "/root_map",
        try pin_path.pathnameConcat(buffer[0..], "/", "root_map"),
    );
    try std.testing.expectError(
        error.InvalidName,
        pin_path.buildValidatedProgramPinPath(buffer[0..], null, "xdp/dispatch"),
    );
    try std.testing.expectError(
        error.InvalidRootPath,
        pin_path.buildValidatedMapPinPath(buffer[0..], "/tmp/bpf/", "stats.map"),
    );
    try std.testing.expectError(
        error.InvalidRootPath,
        pin_path.buildValidatedSanitizedProgramPinPath(buffer[0..], "tmp/bpf", "xdp_dispatch.v1"),
    );

    var short_buffer: [16]u8 = undefined;
    try std.testing.expectError(
        error.NameTooLong,
        pin_path.buildProgramPinPath(short_buffer[0..], "/custom/root", "very_long_program_name"),
    );
}

test "materialized tools/lib/bpf Zigux segments keep direct pin-path sanitizer and validator outputs explicit" {
    var sanitized_path = [_]u8{ '/', 't', 'm', 'p', '/', 'b', 'p', 'f', '.', 'v', '1', '/', 'c', 'a', 'c', 'h', 'e', '.', 'm', 'a', 'p' };
    pin_path.sanitizePinPath(sanitized_path[0..]);
    try std.testing.expectEqualStrings("/tmp/bpf_v1/cache_map", sanitized_path[0..]);

    try pin_path.validatePinName("stats_map");
    try std.testing.expectError(error.EmptyName, pin_path.validatePinName(""));
    try std.testing.expectError(error.InvalidName, pin_path.validatePinName("stats/map"));
    try std.testing.expectError(error.InvalidName, pin_path.validatePinName("stats\x00map"));

    try pin_path.validatePinRootPath("/sys/fs/bpf");
    try std.testing.expectError(error.InvalidRootPath, pin_path.validatePinRootPath("relative/root"));
    try std.testing.expectError(error.InvalidRootPath, pin_path.validatePinRootPath("/sys/fs/bpf/"));
    try std.testing.expectError(error.InvalidRootPath, pin_path.validatePinRootPath("/tmp/bpf\x00tmp"));

    var buffer: [128]u8 = undefined;
    try std.testing.expectEqualStrings(
        "/tmp/bpf.v1.2/cache_map",
        try pin_path.buildSanitizedMapPinPath(buffer[0..], "/tmp/bpf.v1.2", "cache.map"),
    );
    try std.testing.expectEqualStrings(
        "/tmp/bpf.v1/metrics_v1",
        try pin_path.buildValidatedSanitizedMapPinPath(buffer[0..], "/tmp/bpf.v1", "metrics.v1"),
    );
    try std.testing.expectEqualStrings(
        "/tmp/bpf.v1/xdp_dispatch_v1",
        try pin_path.buildSanitizedProgramPinPath(buffer[0..], "/tmp/bpf.v1", "xdp_dispatch.v1"),
    );
}
