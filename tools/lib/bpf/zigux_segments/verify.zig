const std = @import("std");

const logging = @import("logging.zig");
const perf_buffer_poll = @import("perf_buffer_poll.zig");
const pin_path = @import("pin_path.zig");
const type_names = @import("type_names.zig");

fn expectHasDecl(comptime Module: type, comptime decl_name: []const u8) !void {
    try std.testing.expect(@hasDecl(Module, decl_name));
}

test "materialized tools/lib/bpf Zigux segments compile together and keep their focused tests live" {
    std.testing.refAllDecls(logging);
    std.testing.refAllDecls(perf_buffer_poll);
    std.testing.refAllDecls(pin_path);
    std.testing.refAllDecls(type_names);
}

test "materialized tools/lib/bpf Zigux segments keep their current bounded entrypoints explicit" {
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

test "materialized tools/lib/bpf Zigux segments keep stable pin-path helper outputs explicit" {
    var buffer: [128]u8 = undefined;

    try std.testing.expectEqualStrings(
        "/sys/fs/bpf/stats_map",
        try pin_path.buildMapPinPath(buffer[0..], null, "stats_map"),
    );
    try std.testing.expectEqualStrings(
        "/tmp/bpf.v1/stats.map",
        try pin_path.buildValidatedMapPinPath(buffer[0..], "/tmp/bpf.v1", "stats.map"),
    );
    try std.testing.expectEqualStrings(
        "/sys/fs/bpf/xdp_dispatch_v1",
        try pin_path.buildValidatedSanitizedProgramPinPath(buffer[0..], null, "xdp_dispatch.v1"),
    );
    try std.testing.expectError(
        error.InvalidName,
        pin_path.buildValidatedProgramPinPath(buffer[0..], null, "xdp/dispatch"),
    );
    try std.testing.expectError(
        error.InvalidRootPath,
        pin_path.buildValidatedSanitizedProgramPinPath(buffer[0..], "tmp/bpf", "xdp_dispatch.v1"),
    );
}
