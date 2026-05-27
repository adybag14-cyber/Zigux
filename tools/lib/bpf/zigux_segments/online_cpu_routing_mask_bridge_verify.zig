const std = @import("std");
const bridge = @import("online_cpu_routing_mask_bridge.zig");
const online_cpu_routing = @import("online_cpu_routing.zig");

const ReaderContext = struct {
    input: []const u8,
    cursor: usize = 0,
};

const InjectedReadError = error{InjectedReadFailure};

fn readCpuMaskChunks(context: ?*anyopaque, buffer: []u8) anyerror!?usize {
    const typed_context: *ReaderContext = @ptrCast(@alignCast(context.?));
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

fn readInjectedCpuMaskError(context: ?*anyopaque, buffer: []u8) InjectedReadError!?usize {
    _ = context;
    _ = buffer;
    return error.InjectedReadFailure;
}

test "phase8 online-cpu routing mask bridge entrypoints stay explicit" {
    try std.testing.expect(@hasDecl(bridge, "ChunkReader"));
    try std.testing.expect(@hasDecl(bridge, "ParseCpuMaskError"));
    try std.testing.expect(@hasDecl(bridge, "OnlineCpuRouteAttemptSummary"));
    try std.testing.expect(@hasDecl(bridge, "OnlineCpuRouteBufferFdError"));
    try std.testing.expect(@hasDecl(bridge, "OnlineCpuRouteCpuIndexError"));
    try std.testing.expect(@hasDecl(bridge, "OnlineCpuRoutingSummary"));
    try std.testing.expect(@hasDecl(bridge, "summarizeNextOnlineCpuRouteFromString"));
    try std.testing.expect(@hasDecl(bridge, "summarizeNextOnlineCpuRouteFromReader"));
    try std.testing.expect(@hasDecl(bridge, "summarizeOnlineCpuRoutingFromString"));
    try std.testing.expect(@hasDecl(bridge, "summarizeOnlineCpuRoutingFromReader"));
    try std.testing.expect(@hasDecl(bridge, "resolveNextOnlineCpuRouteCpuIndexFromString"));
    try std.testing.expect(@hasDecl(bridge, "resolveNextOnlineCpuRouteCpuIndexFromReader"));
    try std.testing.expect(@hasDecl(bridge, "resolveNextOnlineCpuRouteCpuIndexReturnFromString"));
    try std.testing.expect(@hasDecl(bridge, "resolveNextOnlineCpuRouteCpuIndexReturnFromReader"));
    try std.testing.expect(@hasDecl(bridge, "resolveNextOnlineCpuRouteBufferFdFromString"));
    try std.testing.expect(@hasDecl(bridge, "resolveNextOnlineCpuRouteBufferFdFromReader"));
    try std.testing.expect(@hasDecl(bridge, "resolveNextOnlineCpuRouteBufferFdReturnFromString"));
    try std.testing.expect(@hasDecl(bridge, "resolveNextOnlineCpuRouteBufferFdReturnFromReader"));
}

test "phase8 online-cpu routing mask bridge keeps string-backed next-route summaries stable" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    const first = try bridge.summarizeNextOnlineCpuRouteFromString(
        allocator,
        "0-1,4\n",
        0,
        &.{ 11, 17, 21 },
        0,
    );
    try std.testing.expectEqual(
        online_cpu_routing.OnlineCpuRouteAttemptDisposition.routed_cpu,
        first.disposition,
    );
    try std.testing.expectEqual(@as(?usize, 0), first.cpu_index);
    try std.testing.expectEqual(@as(?i32, 11), first.buffer_fd);
    try std.testing.expectEqual(@as(usize, 1), first.next_scan_index);

    const second = try bridge.summarizeNextOnlineCpuRouteFromString(
        allocator,
        "0-1,4\n",
        2,
        &.{ 11, 17, 21 },
        2,
    );
    try std.testing.expectEqual(
        online_cpu_routing.OnlineCpuRouteAttemptDisposition.routed_cpu,
        second.disposition,
    );
    try std.testing.expectEqual(@as(?usize, 4), second.cpu_index);
    try std.testing.expectEqual(@as(?i32, 21), second.buffer_fd);
    try std.testing.expectEqual(@as(usize, 1), second.skipped_offline_count);
}

test "phase8 online-cpu routing mask bridge keeps reader-backed next-route summaries aligned" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    var scratch: [2]u8 = undefined;
    var context = ReaderContext{ .input = "1,3-4\n" };
    const reader = bridge.ChunkReader{
        .context = &context,
        .readFn = readCpuMaskChunks,
    };

    const summary = try bridge.summarizeNextOnlineCpuRouteFromReader(
        allocator,
        scratch[0..],
        reader,
        2,
        &.{ 41, 43, 47 },
        1,
    );
    try std.testing.expectEqual(
        online_cpu_routing.OnlineCpuRouteAttemptDisposition.routed_cpu,
        summary.disposition,
    );
    try std.testing.expectEqual(@as(?usize, 3), summary.cpu_index);
    try std.testing.expectEqual(@as(?i32, 43), summary.buffer_fd);
    try std.testing.expectEqual(@as(usize, 4), summary.next_scan_index);
}

test "phase8 online-cpu routing mask bridge keeps typed direct wrappers stable" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    try std.testing.expectEqual(
        @as(usize, 1),
        try bridge.resolveNextOnlineCpuRouteCpuIndexFromString(
            allocator,
            "1-2,5\n",
            0,
            &.{ 31, 37, 41 },
            0,
        ),
    );
    try std.testing.expectEqual(
        @as(i32, 37),
        try bridge.resolveNextOnlineCpuRouteBufferFdFromString(
            allocator,
            "1-2,5\n",
            2,
            &.{ 31, 37, 41 },
            1,
        ),
    );

    var scratch: [2]u8 = undefined;
    var context = ReaderContext{ .input = "1,3-4\n" };
    const reader = bridge.ChunkReader{
        .context = &context,
        .readFn = readCpuMaskChunks,
    };
    try std.testing.expectEqual(
        @as(usize, 3),
        try bridge.resolveNextOnlineCpuRouteCpuIndexFromReader(
            allocator,
            scratch[0..],
            reader,
            2,
            &.{ 41, 43, 47 },
            1,
        ),
    );
}

test "phase8 online-cpu routing mask bridge keeps route failures explicit across mask-backed wrappers" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    try std.testing.expectError(
        error.MissingBufferSlot,
        bridge.resolveNextOnlineCpuRouteCpuIndexFromString(
            allocator,
            "0,2-3\n",
            2,
            &.{11},
            1,
        ),
    );
    try std.testing.expectError(
        error.MissingBufferFd,
        bridge.resolveNextOnlineCpuRouteBufferFdFromString(
            allocator,
            "0,2-3\n",
            2,
            &.{ 11, null, 29 },
            1,
        ),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        bridge.resolveNextOnlineCpuRouteCpuIndexReturnFromString(
            allocator,
            "0,2-3\n",
            2,
            &.{11},
            1,
        ),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
        bridge.resolveNextOnlineCpuRouteBufferFdReturnFromString(
            allocator,
            "0,2-3\n",
            2,
            &.{ 11, null, 29 },
            1,
        ),
    );
}

test "phase8 online-cpu routing mask bridge keeps reader and parse failures fail-closed" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    const empty_reader = bridge.ChunkReader{
        .context = null,
        .readFn = readZeroCpuMaskChunks,
    };
    var scratch: [2]u8 = undefined;
    try std.testing.expectError(
        error.EmptyReadBuffer,
        bridge.summarizeNextOnlineCpuRouteFromReader(
            allocator,
            scratch[0..0],
            empty_reader,
            0,
            &.{11},
            0,
        ),
    );
    try std.testing.expectError(
        error.EmptyReadChunk,
        bridge.resolveNextOnlineCpuRouteCpuIndexFromReader(
            allocator,
            scratch[0..],
            empty_reader,
            0,
            &.{11},
            0,
        ),
    );

    const invalid_count_reader = bridge.ChunkReader{
        .context = null,
        .readFn = readTooManyCpuMaskChunks,
    };
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        bridge.resolveNextOnlineCpuRouteBufferFdReturnFromReader(
            allocator,
            scratch[0..],
            invalid_count_reader,
            0,
            &.{11},
            0,
        ),
    );

    const injected_reader = bridge.ChunkReader{
        .context = null,
        .readFn = readInjectedCpuMaskError,
    };
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.IO)),
        bridge.resolveNextOnlineCpuRouteCpuIndexReturnFromReader(
            allocator,
            scratch[0..],
            injected_reader,
            0,
            &.{11},
            0,
        ),
    );

    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        bridge.resolveNextOnlineCpuRouteCpuIndexReturnFromString(
            allocator,
            "0,+\n",
            0,
            &.{11},
            0,
        ),
    );
}

test "phase8 online-cpu routing mask bridge keeps string-backed route-all summaries stable" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    const summary = try bridge.summarizeOnlineCpuRoutingFromString(
        allocator,
        "0-1,4\n",
        0,
        &.{ 11, 17, 21 },
    );
    try std.testing.expectEqual(@as(usize, 3), summary.online_cpu_count);
    try std.testing.expectEqual(@as(usize, 3), summary.selected_cpu_count);
    try std.testing.expectEqual(@as(usize, 3), summary.routed_cpu_count);
    try std.testing.expectEqual(@as(?usize, 0), summary.first_routed_cpu_index);
    try std.testing.expectEqual(@as(?usize, null), summary.next_online_cpu_index);
    try std.testing.expectEqual(
        online_cpu_routing.OnlineCpuRoutingDisposition.complete,
        summary.disposition,
    );
}

test "phase8 online-cpu routing mask bridge keeps requested subsets explicit from mask text" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    const summary = try bridge.summarizeOnlineCpuRoutingFromString(
        allocator,
        "1-2,5\n",
        2,
        &.{ 31, 37, 41 },
    );
    try std.testing.expectEqual(@as(usize, 3), summary.online_cpu_count);
    try std.testing.expectEqual(@as(usize, 2), summary.selected_cpu_count);
    try std.testing.expectEqual(@as(usize, 2), summary.routed_cpu_count);
    try std.testing.expectEqual(@as(?usize, 1), summary.first_routed_cpu_index);
    try std.testing.expectEqual(@as(?usize, 5), summary.next_online_cpu_index);
    try std.testing.expectEqual(
        online_cpu_routing.OnlineCpuRoutingDisposition.requested_subset,
        summary.disposition,
    );
}

test "phase8 online-cpu routing mask bridge keeps missing buffer-fd summaries explicit" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    const summary = try bridge.summarizeOnlineCpuRoutingFromString(
        allocator,
        "0,2-3\n",
        0,
        &.{ 11, null, 29 },
    );
    try std.testing.expectEqual(@as(usize, 3), summary.online_cpu_count);
    try std.testing.expectEqual(@as(usize, 3), summary.selected_cpu_count);
    try std.testing.expectEqual(@as(usize, 1), summary.routed_cpu_count);
    try std.testing.expectEqual(@as(?usize, 0), summary.first_routed_cpu_index);
    try std.testing.expectEqual(@as(?usize, 2), summary.next_online_cpu_index);
    try std.testing.expectEqual(@as(?usize, 1), summary.missing_buffer_index);
    try std.testing.expectEqual(
        online_cpu_routing.OnlineCpuRoutingDisposition.missing_buffer_fd,
        summary.disposition,
    );
}

test "phase8 online-cpu routing mask bridge keeps reader-backed summaries aligned" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    var scratch: [2]u8 = undefined;
    var context = ReaderContext{ .input = "1,3-4\n" };
    const reader = bridge.ChunkReader{
        .context = &context,
        .readFn = readCpuMaskChunks,
    };

    const summary = try bridge.summarizeOnlineCpuRoutingFromReader(
        allocator,
        scratch[0..],
        reader,
        2,
        &.{ 41, 43, 47 },
    );
    try std.testing.expectEqual(@as(usize, 3), summary.online_cpu_count);
    try std.testing.expectEqual(@as(usize, 2), summary.selected_cpu_count);
    try std.testing.expectEqual(@as(usize, 2), summary.routed_cpu_count);
    try std.testing.expectEqual(@as(?usize, 1), summary.first_routed_cpu_index);
    try std.testing.expectEqual(@as(?usize, 4), summary.next_online_cpu_index);
    try std.testing.expectEqual(
        online_cpu_routing.OnlineCpuRoutingDisposition.requested_subset,
        summary.disposition,
    );
}

test "phase8 online-cpu routing mask bridge keeps malformed mask inputs fail-closed" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    try std.testing.expectError(
        error.InvalidCpuRange,
        bridge.summarizeOnlineCpuRoutingFromString(allocator, "0,+\n", 1, &.{ 11 }),
    );

    var scratch: [2]u8 = undefined;
    var malformed_context = ReaderContext{ .input = "0,+\n" };
    const reader = bridge.ChunkReader{
        .context = &malformed_context,
        .readFn = readCpuMaskChunks,
    };
    try std.testing.expectError(
        error.InvalidCpuRange,
        bridge.summarizeOnlineCpuRoutingFromReader(allocator, scratch[0..], reader, 1, &.{ 11 }),
    );
}
