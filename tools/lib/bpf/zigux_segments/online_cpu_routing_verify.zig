const std = @import("std");
const online_cpu_routing = @import("online_cpu_routing.zig");

test "phase8 online-cpu route helpers keep typed cpu-index wrappers stable" {
    const found = online_cpu_routing.summarizeNextOnlineCpuRoute(
        &.{ false, true, false, true },
        0,
        &.{ 11, 17 },
        0,
    );
    try std.testing.expectEqual(
        @as(usize, 1),
        try online_cpu_routing.resolveNextOnlineCpuRouteCpuIndex(found),
    );

    const missing_slot = online_cpu_routing.summarizeNextOnlineCpuRoute(
        &.{ true, false, true },
        2,
        &.{11},
        1,
    );
    try std.testing.expectError(
        error.MissingBufferSlot,
        online_cpu_routing.resolveNextOnlineCpuRouteCpuIndex(missing_slot),
    );

    const missing_fd = online_cpu_routing.summarizeNextOnlineCpuRoute(
        &.{ true, false, true },
        2,
        &.{ 11, null, 29 },
        1,
    );
    try std.testing.expectError(
        error.MissingBufferFd,
        online_cpu_routing.resolveNextOnlineCpuRouteCpuIndex(missing_fd),
    );

    const exhausted = online_cpu_routing.summarizeNextOnlineCpuRoute(
        &.{ false, true },
        2,
        &.{11},
        1,
    );
    try std.testing.expectError(
        error.NoMoreOnlineCpu,
        online_cpu_routing.resolveNextOnlineCpuRouteCpuIndex(exhausted),
    );
}

test "phase8 online-cpu route helpers keep errno-shaped cpu-index wrappers stable" {
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
}

test "phase8 online-cpu route helpers keep typed buffer-fd wrappers stable" {
    const found = online_cpu_routing.summarizeNextOnlineCpuRoute(
        &.{ false, true, false, true },
        0,
        &.{ 11, 17 },
        0,
    );
    try std.testing.expectEqual(
        @as(i32, 11),
        try online_cpu_routing.resolveNextOnlineCpuRouteBufferFd(found),
    );
    try std.testing.expectEqual(
        @as(i32, 17),
        try online_cpu_routing.resolveNextOnlineCpuRouteBufferFdAtIndex(
            &.{ false, true, false, true },
            2,
            &.{ 11, 17 },
            1,
        ),
    );

    const missing_slot = online_cpu_routing.summarizeNextOnlineCpuRoute(
        &.{ true, false, true },
        2,
        &.{11},
        1,
    );
    try std.testing.expectError(
        error.MissingBufferSlot,
        online_cpu_routing.resolveNextOnlineCpuRouteBufferFd(missing_slot),
    );

    const missing_fd = online_cpu_routing.summarizeNextOnlineCpuRoute(
        &.{ true, false, true },
        2,
        &.{ 11, null, 29 },
        1,
    );
    try std.testing.expectError(
        error.MissingBufferFd,
        online_cpu_routing.resolveNextOnlineCpuRouteBufferFd(missing_fd),
    );

    const exhausted = online_cpu_routing.summarizeNextOnlineCpuRoute(
        &.{ false, true },
        2,
        &.{11},
        1,
    );
    try std.testing.expectError(
        error.NoMoreOnlineCpu,
        online_cpu_routing.resolveNextOnlineCpuRouteBufferFd(exhausted),
    );
}

test "phase8 online-cpu route helpers keep errno-shaped buffer-fd wrappers stable" {
    const found = online_cpu_routing.summarizeNextOnlineCpuRoute(
        &.{ false, true, false, true },
        0,
        &.{ 11, 17 },
        0,
    );
    try std.testing.expectEqual(
        @as(i32, 11),
        online_cpu_routing.resolveNextOnlineCpuRouteBufferFdReturn(found),
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

test "phase8 online-cpu route helpers fail closed when a hand-built CPU index exceeds i32" {
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
