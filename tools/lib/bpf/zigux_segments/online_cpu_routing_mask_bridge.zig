const std = @import("std");
const cpu_mask = @import("cpu_mask.zig");
const online_cpu_routing = @import("online_cpu_routing.zig");

pub const ChunkReader = cpu_mask.ChunkReader;
pub const ParseCpuMaskError = cpu_mask.ParseCpuMaskError;
pub const OnlineCpuRouteAttemptSummary = online_cpu_routing.OnlineCpuRouteAttemptSummary;
pub const OnlineCpuRouteBufferFdError = online_cpu_routing.OnlineCpuRouteBufferFdError;
pub const OnlineCpuRouteCpuIndexError = online_cpu_routing.OnlineCpuRouteCpuIndexError;
pub const OnlineCpuRoutingSummary = online_cpu_routing.OnlineCpuRoutingSummary;

fn maskBridgeErrno(err: anyerror) i32 {
    return switch (err) {
        error.EmptyCpuRange,
        error.InvalidCpuRange,
        error.EmptyReadBuffer,
        error.EmptyReadChunk,
        error.InvalidReadCount,
        => -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        error.OutOfMemory => -@as(i32, @intFromEnum(std.os.linux.E.NOMEM)),
        else => -@as(i32, @intFromEnum(std.os.linux.E.IO)),
    };
}

pub fn summarizeNextOnlineCpuRouteFromString(
    allocator: std.mem.Allocator,
    input: []const u8,
    start_index: usize,
    buffer_fds: []const ?i32,
    routed_cpu_count: usize,
) ParseCpuMaskError!OnlineCpuRouteAttemptSummary {
    const parsed = try cpu_mask.parseCpuMaskString(allocator, input);
    defer parsed.deinit(allocator);
    return online_cpu_routing.summarizeNextOnlineCpuRoute(
        parsed.values,
        start_index,
        buffer_fds,
        routed_cpu_count,
    );
}

pub fn summarizeNextOnlineCpuRouteFromReader(
    allocator: std.mem.Allocator,
    scratch: []u8,
    reader: ChunkReader,
    start_index: usize,
    buffer_fds: []const ?i32,
    routed_cpu_count: usize,
) anyerror!OnlineCpuRouteAttemptSummary {
    const parsed = try cpu_mask.parseCpuMaskFromReader(allocator, scratch, reader);
    defer parsed.deinit(allocator);
    return online_cpu_routing.summarizeNextOnlineCpuRoute(
        parsed.values,
        start_index,
        buffer_fds,
        routed_cpu_count,
    );
}

pub fn summarizeOnlineCpuRoutingFromString(
    allocator: std.mem.Allocator,
    input: []const u8,
    requested_cpu_count: usize,
    buffer_fds: []const ?i32,
) ParseCpuMaskError!OnlineCpuRoutingSummary {
    const parsed = try cpu_mask.parseCpuMaskString(allocator, input);
    defer parsed.deinit(allocator);
    return online_cpu_routing.summarizeOnlineCpuRouting(
        parsed.values,
        requested_cpu_count,
        buffer_fds,
    );
}

pub fn summarizeOnlineCpuRoutingFromReader(
    allocator: std.mem.Allocator,
    scratch: []u8,
    reader: ChunkReader,
    requested_cpu_count: usize,
    buffer_fds: []const ?i32,
) anyerror!OnlineCpuRoutingSummary {
    const parsed = try cpu_mask.parseCpuMaskFromReader(allocator, scratch, reader);
    defer parsed.deinit(allocator);
    return online_cpu_routing.summarizeOnlineCpuRouting(
        parsed.values,
        requested_cpu_count,
        buffer_fds,
    );
}

pub fn resolveNextOnlineCpuRouteCpuIndexFromString(
    allocator: std.mem.Allocator,
    input: []const u8,
    start_index: usize,
    buffer_fds: []const ?i32,
    routed_cpu_count: usize,
) anyerror!usize {
    return online_cpu_routing.resolveNextOnlineCpuRouteCpuIndex(
        try summarizeNextOnlineCpuRouteFromString(
            allocator,
            input,
            start_index,
            buffer_fds,
            routed_cpu_count,
        ),
    );
}

pub fn resolveNextOnlineCpuRouteCpuIndexFromReader(
    allocator: std.mem.Allocator,
    scratch: []u8,
    reader: ChunkReader,
    start_index: usize,
    buffer_fds: []const ?i32,
    routed_cpu_count: usize,
) anyerror!usize {
    return online_cpu_routing.resolveNextOnlineCpuRouteCpuIndex(
        try summarizeNextOnlineCpuRouteFromReader(
            allocator,
            scratch,
            reader,
            start_index,
            buffer_fds,
            routed_cpu_count,
        ),
    );
}

pub fn resolveNextOnlineCpuRouteCpuIndexReturnFromString(
    allocator: std.mem.Allocator,
    input: []const u8,
    start_index: usize,
    buffer_fds: []const ?i32,
    routed_cpu_count: usize,
) i32 {
    const summary = summarizeNextOnlineCpuRouteFromString(
        allocator,
        input,
        start_index,
        buffer_fds,
        routed_cpu_count,
    ) catch |err| return maskBridgeErrno(err);
    return online_cpu_routing.resolveNextOnlineCpuRouteCpuIndexReturn(summary);
}

pub fn resolveNextOnlineCpuRouteCpuIndexReturnFromReader(
    allocator: std.mem.Allocator,
    scratch: []u8,
    reader: ChunkReader,
    start_index: usize,
    buffer_fds: []const ?i32,
    routed_cpu_count: usize,
) i32 {
    const summary = summarizeNextOnlineCpuRouteFromReader(
        allocator,
        scratch,
        reader,
        start_index,
        buffer_fds,
        routed_cpu_count,
    ) catch |err| return maskBridgeErrno(err);
    return online_cpu_routing.resolveNextOnlineCpuRouteCpuIndexReturn(summary);
}

pub fn resolveNextOnlineCpuRouteBufferFdFromString(
    allocator: std.mem.Allocator,
    input: []const u8,
    start_index: usize,
    buffer_fds: []const ?i32,
    routed_cpu_count: usize,
) anyerror!i32 {
    return online_cpu_routing.resolveNextOnlineCpuRouteBufferFd(
        try summarizeNextOnlineCpuRouteFromString(
            allocator,
            input,
            start_index,
            buffer_fds,
            routed_cpu_count,
        ),
    );
}

pub fn resolveNextOnlineCpuRouteBufferFdFromReader(
    allocator: std.mem.Allocator,
    scratch: []u8,
    reader: ChunkReader,
    start_index: usize,
    buffer_fds: []const ?i32,
    routed_cpu_count: usize,
) anyerror!i32 {
    return online_cpu_routing.resolveNextOnlineCpuRouteBufferFd(
        try summarizeNextOnlineCpuRouteFromReader(
            allocator,
            scratch,
            reader,
            start_index,
            buffer_fds,
            routed_cpu_count,
        ),
    );
}

pub fn resolveNextOnlineCpuRouteBufferFdReturnFromString(
    allocator: std.mem.Allocator,
    input: []const u8,
    start_index: usize,
    buffer_fds: []const ?i32,
    routed_cpu_count: usize,
) i32 {
    const summary = summarizeNextOnlineCpuRouteFromString(
        allocator,
        input,
        start_index,
        buffer_fds,
        routed_cpu_count,
    ) catch |err| return maskBridgeErrno(err);
    return online_cpu_routing.resolveNextOnlineCpuRouteBufferFdReturn(summary);
}

pub fn resolveNextOnlineCpuRouteBufferFdReturnFromReader(
    allocator: std.mem.Allocator,
    scratch: []u8,
    reader: ChunkReader,
    start_index: usize,
    buffer_fds: []const ?i32,
    routed_cpu_count: usize,
) i32 {
    const summary = summarizeNextOnlineCpuRouteFromReader(
        allocator,
        scratch,
        reader,
        start_index,
        buffer_fds,
        routed_cpu_count,
    ) catch |err| return maskBridgeErrno(err);
    return online_cpu_routing.resolveNextOnlineCpuRouteBufferFdReturn(summary);
}
