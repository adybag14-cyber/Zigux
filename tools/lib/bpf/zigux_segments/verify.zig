const std = @import("std");

const cpu_mask = @import("cpu_mask.zig");
const logging = @import("logging.zig");
const online_cpu_routing = @import("online_cpu_routing.zig");
const online_cpu_routing_verify = @import("online_cpu_routing_verify.zig");
const perf_buffer_poll = @import("perf_buffer_poll.zig");
const perf_buffer_ready_window = @import("perf_buffer_ready_window.zig");
const pin_path = @import("pin_path.zig");
const ready_buffer_fd_verify = @import("ready_buffer_fd_verify.zig");
const ready_buffer_window_verify = @import("ready_buffer_window_verify.zig");
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
    std.testing.refAllDecls(online_cpu_routing_verify);
    std.testing.refAllDecls(perf_buffer_poll);
    std.testing.refAllDecls(perf_buffer_ready_window);
    std.testing.refAllDecls(pin_path);
    std.testing.refAllDecls(ready_buffer_fd_verify);
    std.testing.refAllDecls(ready_buffer_window_verify);
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
    try expectHasDecl(cpu_mask, "summarizePossibleCpusFromString");
    try expectHasDecl(cpu_mask, "summarizePossibleCpusFromReader");
    try expectHasDecl(cpu_mask, "countPossibleCpus");
    try expectHasDecl(cpu_mask, "isOnlineCpuEligible");
    try expectHasDecl(cpu_mask, "derivePerfBufferAutoCpuCount");
    try expectHasDecl(cpu_mask, "derivePerfBufferAutoCpuCountFromString");
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
    try expectHasDecl(online_cpu_routing, "OnlineCpuRouteBufferFdError");
    try expectHasDecl(online_cpu_routing, "OnlineCpuRouteCpuIndexError");
    try expectHasDecl(online_cpu_routing, "OnlineCpuRoutingDisposition");
    try expectHasDecl(online_cpu_routing, "OnlineCpuRoutingSummary");
    try expectHasDecl(online_cpu_routing, "advanceOnlineCpuCursor");
    try expectHasDecl(online_cpu_routing, "summarizeNextOnlineCpuRoute");
    try expectHasDecl(online_cpu_routing, "summarizeOnlineCpuRouting");
    try expectHasDecl(online_cpu_routing, "resolveNextOnlineCpuRouteCpuIndex");
    try expectHasDecl(online_cpu_routing, "resolveNextOnlineCpuRouteCpuIndexAtIndex");
    try expectHasDecl(online_cpu_routing, "resolveNextOnlineCpuRouteCpuIndexReturn");
    try expectHasDecl(online_cpu_routing, "resolveNextOnlineCpuRouteCpuIndexReturnAtIndex");
    try expectHasDecl(online_cpu_routing, "resolveNextOnlineCpuRouteBufferFd");
    try expectHasDecl(online_cpu_routing, "resolveNextOnlineCpuRouteBufferFdAtIndex");
    try expectHasDecl(online_cpu_routing, "resolveNextOnlineCpuRouteBufferFdReturn");
    try expectHasDecl(online_cpu_routing, "resolveNextOnlineCpuRouteBufferFdReturnAtIndex");

    try expectHasDecl(perf_buffer_poll, "WaitClass");
    try expectHasDecl(perf_buffer_poll, "PollOutcome");
    try expectHasDecl(perf_buffer_poll, "PollReturnDisposition");
    try expectHasDecl(perf_buffer_poll, "BufferObservation");
    try expectHasDecl(perf_buffer_poll, "WaitObservation");
    try expectHasDecl(perf_buffer_poll, "ReadyBufferCursor");
    try expectHasDecl(perf_buffer_poll, "ReadyBufferSummary");
    try expectHasDecl(perf_buffer_poll, "ReadyBufferAttemptLookupDisposition");
    try expectHasDecl(perf_buffer_poll, "ReadyBufferAttemptLookupSummary");
    try expectHasDecl(perf_buffer_poll, "ReadyBufferAttemptLookupError");
    try expectHasDecl(perf_buffer_poll, "ProcessRecordObservation");
    try expectHasDecl(perf_buffer_poll, "ProcessRecordSummary");
    try expectHasDecl(perf_buffer_poll, "PollSummary");
    try expectHasDecl(perf_buffer_poll, "PollExecutionSummary");
    try expectHasDecl(perf_buffer_poll, "PollExecutionResult");
    try expectHasDecl(perf_buffer_poll, "BufferFdLookupDisposition");
    try expectHasDecl(perf_buffer_poll, "BufferFdLookupSummary");
    try expectHasDecl(perf_buffer_poll, "BufferFdLookupError");
    try expectHasDecl(perf_buffer_poll, "ReadyBufferFdLookupError");
    try expectHasDecl(perf_buffer_poll, "BufferWindowObservation");
    try expectHasDecl(perf_buffer_poll, "BufferWindowLookupDisposition");
    try expectHasDecl(perf_buffer_poll, "BufferWindowLookupSummary");
    try expectHasDecl(perf_buffer_poll, "BufferWindowLookupError");
    try expectHasDecl(perf_buffer_poll, "PollError");
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
    try expectHasDecl(perf_buffer_poll, "resolveReadyBufferFdAtAttempt");
    try expectHasDecl(perf_buffer_poll, "resolveReadyBufferFdLookupReturnAtAttempt");
    try expectHasDecl(perf_buffer_poll, "summarizeBufferWindowLookup");
    try expectHasDecl(perf_buffer_poll, "resolveBufferWindowMappedSizeAtIndex");
    try expectHasDecl(perf_buffer_poll, "resolveBufferWindowMappedSize");
    try expectHasDecl(perf_buffer_poll, "resolveBufferWindowLookupReturn");
    try expectHasDecl(perf_buffer_poll, "resolveBufferWindowLookupReturnAtIndex");

    try expectHasDecl(perf_buffer_ready_window, "ReadyBufferWindowLookupError");
    try expectHasDecl(perf_buffer_ready_window, "resolveReadyBufferWindowMappedSizeAtAttempt");
    try expectHasDecl(perf_buffer_ready_window, "resolveReadyBufferWindowMappedSizeReturnAtAttempt");
    try expectHasDecl(perf_buffer_ready_window, "resolveReadyBufferWindowLookupReturnAtAttempt");

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

test "materialized tools/lib/bpf Zigux segments keep stable online-CPU route-cpu wrappers explicit" {
    const routed = online_cpu_routing.summarizeNextOnlineCpuRoute(
        &.{ false, true, false, true },
        0,
        &.{ 11, 17 },
        0,
    );
    try std.testing.expectEqual(
        @as(usize, 1),
        try online_cpu_routing.resolveNextOnlineCpuRouteCpuIndex(routed),
    );
    try std.testing.expectEqual(
        @as(i32, 1),
        online_cpu_routing.resolveNextOnlineCpuRouteCpuIndexReturnAtIndex(
            &.{ false, true, false, true },
            0,
            &.{ 11, 17 },
            0,
        ),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        online_cpu_routing.resolveNextOnlineCpuRouteCpuIndexReturnAtIndex(
            &.{ true, false, true },
            2,
            &.{11},
            1,
        ),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        online_cpu_routing.resolveNextOnlineCpuRouteCpuIndexReturnAtIndex(
            &.{ true, false, true },
            2,
            &.{ 11, null, 29 },
            1,
        ),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        online_cpu_routing.resolveNextOnlineCpuRouteCpuIndexReturnAtIndex(
            &.{ false, true },
            2,
            &.{11},
            1,
        ),
    );

    const impossible = online_cpu_routing.OnlineCpuRouteAttemptSummary{
        .start_index = 0,
        .next_scan_index = 0,
        .cpu_index = @as(usize, std.math.maxInt(i32)) + 1,
        .buffer_index = 0,
        .buffer_fd = 11,
        .skipped_offline_count = 0,
        .disposition = .routed_cpu,
    };
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.OVERFLOW)),
        online_cpu_routing.resolveNextOnlineCpuRouteCpuIndexReturn(impossible),
    );
}

test "materialized tools/lib/bpf Zigux segments keep stable online-CPU route-fd wrappers explicit" {
    const routed = online_cpu_routing.summarizeNextOnlineCpuRoute(
        &.{ false, true, false, true },
        0,
        &.{ 11, 17 },
        0,
    );
    try std.testing.expectEqual(
        @as(i32, 11),
        try online_cpu_routing.resolveNextOnlineCpuRouteBufferFd(routed),
    );
    try std.testing.expectEqual(
        @as(i32, 17),
        online_cpu_routing.resolveNextOnlineCpuRouteBufferFdReturnAtIndex(
            &.{ false, true, false, true },
            2,
            &.{ 11, 17 },
            1,
        ),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        online_cpu_routing.resolveNextOnlineCpuRouteBufferFdReturnAtIndex(
            &.{ true, false, true },
            2,
            &.{11},
            1,
        ),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        online_cpu_routing.resolveNextOnlineCpuRouteBufferFdReturnAtIndex(
            &.{ true, false, true },
            2,
            &.{ 11, null, 29 },
            1,
        ),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        online_cpu_routing.resolveNextOnlineCpuRouteBufferFdReturnAtIndex(
            &.{ false, true },
            2,
            &.{11},
            1,
        ),
    );
}
