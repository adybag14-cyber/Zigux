const std = @import("std");
const cpu_mask = @import("cpu_mask.zig");
const online_cpu_routing = @import("online_cpu_routing.zig");

pub const ChunkReader = cpu_mask.ChunkReader;
pub const ParseCpuMaskError = cpu_mask.ParseCpuMaskError;
pub const OnlineCpuRoutingSummary = online_cpu_routing.OnlineCpuRoutingSummary;
pub const OnlineCpuRouteCpuIndexError = online_cpu_routing.OnlineCpuRouteCpuIndexError;
pub const OnlineCpuRouteBufferFdError = online_cpu_routing.OnlineCpuRouteBufferFdError;

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
) (ParseCpuMaskError || OnlineCpuRouteCpuIndexError)!usize {
    const parsed = try cpu_mask.parseCpuMaskString(allocator, input);
    defer parsed.deinit(allocator);
    return online_cpu_routing.resolveNextOnlineCpuRouteCpuIndexAtIndex(
        parsed.values,
        start_index,
        buffer_fds,
        routed_cpu_count,
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
    const parsed = try cpu_mask.parseCpuMaskFromReader(allocator, scratch, reader);
    defer parsed.deinit(allocator);
    return online_cpu_routing.resolveNextOnlineCpuRouteCpuIndexAtIndex(
        parsed.values,
        start_index,
        buffer_fds,
        routed_cpu_count,
    );
}

pub fn resolveNextOnlineCpuRouteCpuIndexReturnFromString(
    allocator: std.mem.Allocator,
    input: []const u8,
    start_index: usize,
    buffer_fds: []const ?i32,
    routed_cpu_count: usize,
) ParseCpuMaskError!i32 {
    const parsed = try cpu_mask.parseCpuMaskString(allocator, input);
    defer parsed.deinit(allocator);
    return online_cpu_routing.resolveNextOnlineCpuRouteCpuIndexReturnAtIndex(
        parsed.values,
        start_index,
        buffer_fds,
        routed_cpu_count,
    );
}

pub fn resolveNextOnlineCpuRouteCpuIndexReturnFromReader(
    allocator: std.mem.Allocator,
    scratch: []u8,
    reader: ChunkReader,
    start_index: usize,
    buffer_fds: []const ?i32,
    routed_cpu_count: usize,
) anyerror!i32 {
    const parsed = try cpu_mask.parseCpuMaskFromReader(allocator, scratch, reader);
    defer parsed.deinit(allocator);
    return online_cpu_routing.resolveNextOnlineCpuRouteCpuIndexReturnAtIndex(
        parsed.values,
        start_index,
        buffer_fds,
        routed_cpu_count,
    );
}

pub fn resolveNextOnlineCpuRouteBufferFdFromString(
    allocator: std.mem.Allocator,
    input: []const u8,
    start_index: usize,
    buffer_fds: []const ?i32,
    routed_cpu_count: usize,
) (ParseCpuMaskError || OnlineCpuRouteBufferFdError)!i32 {
    const parsed = try cpu_mask.parseCpuMaskString(allocator, input);
    defer parsed.deinit(allocator);
    return online_cpu_routing.resolveNextOnlineCpuRouteBufferFdAtIndex(
        parsed.values,
        start_index,
        buffer_fds,
        routed_cpu_count,
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
    const parsed = try cpu_mask.parseCpuMaskFromReader(allocator, scratch, reader);
    defer parsed.deinit(allocator);
    return online_cpu_routing.resolveNextOnlineCpuRouteBufferFdAtIndex(
        parsed.values,
        start_index,
        buffer_fds,
        routed_cpu_count,
    );
}

pub fn resolveNextOnlineCpuRouteBufferFdReturnFromString(
    allocator: std.mem.Allocator,
    input: []const u8,
    start_index: usize,
    buffer_fds: []const ?i32,
    routed_cpu_count: usize,
) ParseCpuMaskError!i32 {
    const parsed = try cpu_mask.parseCpuMaskString(allocator, input);
    defer parsed.deinit(allocator);
    return online_cpu_routing.resolveNextOnlineCpuRouteBufferFdReturnAtIndex(
        parsed.values,
        start_index,
        buffer_fds,
        routed_cpu_count,
    );
}

pub fn resolveNextOnlineCpuRouteBufferFdReturnFromReader(
    allocator: std.mem.Allocator,
    scratch: []u8,
    reader: ChunkReader,
    start_index: usize,
    buffer_fds: []const ?i32,
    routed_cpu_count: usize,
) anyerror!i32 {
    const parsed = try cpu_mask.parseCpuMaskFromReader(allocator, scratch, reader);
    defer parsed.deinit(allocator);
    return online_cpu_routing.resolveNextOnlineCpuRouteBufferFdReturnAtIndex(
        parsed.values,
        start_index,
        buffer_fds,
        routed_cpu_count,
    );
}
