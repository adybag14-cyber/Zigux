const std = @import("std");
const cpu_mask = @import("cpu_mask.zig");
const online_cpu_routing = @import("online_cpu_routing.zig");

pub const ChunkReader = cpu_mask.ChunkReader;
pub const ParseCpuMaskError = cpu_mask.ParseCpuMaskError;
pub const OnlineCpuRoutingSummary = online_cpu_routing.OnlineCpuRoutingSummary;

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
