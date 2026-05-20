const std = @import("std");

const online_cpu_routing = @import("../../tools/lib/bpf/zigux_segments/online_cpu_routing.zig");
const perf_buffer_poll = @import("../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig");

fn expectHasDecl(comptime Module: type, comptime decl_name: []const u8) !void {
    try std.testing.expect(@hasDecl(Module, decl_name));
}

test "phase8 libbpf routing alias witness keeps typed route surfaces explicit" {
    try expectHasDecl(online_cpu_routing, "OnlineCpuRouteAttemptSummary");
    try expectHasDecl(online_cpu_routing, "OnlineCpuRouteBufferFdError");
    try expectHasDecl(online_cpu_routing, "OnlineCpuRouteCpuIndexError");
    try expectHasDecl(online_cpu_routing, "OnlineCpuRoutingSummary");
    try expectHasDecl(online_cpu_routing, "resolveNextOnlineCpuRouteCpuIndex");
    try expectHasDecl(online_cpu_routing, "resolveNextOnlineCpuRouteCpuIndexAtIndex");
    try expectHasDecl(online_cpu_routing, "resolveNextOnlineCpuRouteCpuIndexReturn");
    try expectHasDecl(online_cpu_routing, "resolveNextOnlineCpuRouteCpuIndexReturnAtIndex");
    try expectHasDecl(online_cpu_routing, "resolveNextOnlineCpuRouteBufferFd");
    try expectHasDecl(online_cpu_routing, "resolveNextOnlineCpuRouteBufferFdAtIndex");
    try expectHasDecl(online_cpu_routing, "resolveNextOnlineCpuRouteBufferFdReturn");
    try expectHasDecl(online_cpu_routing, "resolveNextOnlineCpuRouteBufferFdReturnAtIndex");

    try expectHasDecl(perf_buffer_poll, "ReadyBufferAttemptLookupSummary");
    try expectHasDecl(perf_buffer_poll, "ReadyBufferAttemptLookupError");
    try expectHasDecl(perf_buffer_poll, "BufferFdLookupSummary");
    try expectHasDecl(perf_buffer_poll, "BufferFdLookupError");
    try expectHasDecl(perf_buffer_poll, "ReadyBufferFdLookupError");
    try expectHasDecl(perf_buffer_poll, "BufferWindowLookupSummary");
    try expectHasDecl(perf_buffer_poll, "BufferWindowLookupError");
    try expectHasDecl(perf_buffer_poll, "PollExecutionResult");
    try expectHasDecl(perf_buffer_poll, "PollError");
}

test "phase8 libbpf routing alias witness keeps typed and errno-shaped route helpers aligned" {
    const online_cpu_mask = [_]bool{ false, true, false, true, true };

    const routed = online_cpu_routing.summarizeNextOnlineCpuRoute(
        &online_cpu_mask,
        0,
        &.{ 11, 17, 29 },
        0,
    );
    try std.testing.expectEqual(@as(usize, 1), try online_cpu_routing.resolveNextOnlineCpuRouteCpuIndex(routed));
    try std.testing.expectEqual(@as(i32, 1), online_cpu_routing.resolveNextOnlineCpuRouteCpuIndexReturn(routed));
    try std.testing.expectEqual(@as(i32, 11), try online_cpu_routing.resolveNextOnlineCpuRouteBufferFd(routed));
    try std.testing.expectEqual(@as(i32, 11), online_cpu_routing.resolveNextOnlineCpuRouteBufferFdReturn(routed));

    const missing_fd = online_cpu_routing.summarizeNextOnlineCpuRoute(
        &online_cpu_mask,
        2,
        &.{ 11, null, 29 },
        1,
    );
    try std.testing.expectError(
        error.MissingBufferFd,
        online_cpu_routing.resolveNextOnlineCpuRouteCpuIndex(missing_fd),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        online_cpu_routing.resolveNextOnlineCpuRouteCpuIndexReturn(missing_fd),
    );
    try std.testing.expectError(
        error.MissingBufferFd,
        online_cpu_routing.resolveNextOnlineCpuRouteBufferFd(missing_fd),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        online_cpu_routing.resolveNextOnlineCpuRouteBufferFdReturn(missing_fd),
    );

    const missing_slot = online_cpu_routing.summarizeNextOnlineCpuRoute(
        &online_cpu_mask,
        4,
        &.{ 11, 17 },
        2,
    );
    try std.testing.expectError(
        error.MissingBufferSlot,
        online_cpu_routing.resolveNextOnlineCpuRouteCpuIndex(missing_slot),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        online_cpu_routing.resolveNextOnlineCpuRouteCpuIndexReturn(missing_slot),
    );
    try std.testing.expectError(
        error.MissingBufferSlot,
        online_cpu_routing.resolveNextOnlineCpuRouteBufferFd(missing_slot),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        online_cpu_routing.resolveNextOnlineCpuRouteBufferFdReturn(missing_slot),
    );

    const exhausted = online_cpu_routing.summarizeNextOnlineCpuRoute(
        &online_cpu_mask,
        online_cpu_mask.len,
        &.{ 11, 17, 29 },
        3,
    );
    try std.testing.expectError(
        error.NoMoreOnlineCpu,
        online_cpu_routing.resolveNextOnlineCpuRouteCpuIndex(exhausted),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        online_cpu_routing.resolveNextOnlineCpuRouteCpuIndexReturn(exhausted),
    );
    try std.testing.expectError(
        error.NoMoreOnlineCpu,
        online_cpu_routing.resolveNextOnlineCpuRouteBufferFd(exhausted),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        online_cpu_routing.resolveNextOnlineCpuRouteBufferFdReturn(exhausted),
    );
}

test "phase8 libbpf routing alias witness keeps lookup and routing summaries stable together" {
    const buffers = [_]perf_buffer_poll.BufferObservation{
        .{},
        .{ .ready = true },
        .{},
        .{ .ready = true },
    };
    const ready_buffer_fds = [_]?i32{ null, 11, null, 17 };

    try std.testing.expectEqual(
        @as(i32, 11),
        try perf_buffer_poll.resolveReadyBufferFdAtAttempt(&buffers, &ready_buffer_fds, 0),
    );
    try std.testing.expectEqual(
        @as(i32, 17),
        try perf_buffer_poll.resolveReadyBufferFdAtAttempt(&buffers, &ready_buffer_fds, 1),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        perf_buffer_poll.resolveReadyBufferFdLookupReturnAtAttempt(&buffers, &ready_buffer_fds, 2),
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
            &.{ false, true, false, true, true },
            2,
            &.{ 11, 17, 29 },
        ),
    );
    try std.testing.expectEqualDeep(
        online_cpu_routing.OnlineCpuRoutingSummary{
            .online_cpu_count = 3,
            .requested_cpu_count = 0,
            .selected_cpu_count = 3,
            .buffer_slot_count = 3,
            .routed_cpu_count = 1,
            .first_routed_cpu_index = 1,
            .next_online_cpu_index = 3,
            .missing_buffer_index = 1,
            .disposition = .missing_buffer_fd,
        },
        online_cpu_routing.summarizeOnlineCpuRouting(
            &.{ false, true, false, true, true },
            0,
            &.{ 11, null, 29 },
        ),
    );
}
