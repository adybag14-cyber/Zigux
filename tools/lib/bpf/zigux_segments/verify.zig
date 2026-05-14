const std = @import("std");
const cpu_mask = @import("cpu_mask.zig");
const logging = @import("logging.zig");
const online_cpu_routing = @import("online_cpu_routing.zig");
const perf_buffer_poll = @import("perf_buffer_poll.zig");
const type_names = @import("type_names.zig");

pub const VerifyShardSummary = struct {
    version: []const u8,
    auto_cpu_count: usize,
    routed_cpu_count: usize,
    first_map_type_name: []const u8,
    debug_logs_visible_at_info_default: bool,
};

pub fn summarizeVerifyShard(
    version_buffer: []u8,
    online_cpu_mask: []const bool,
    requested_cpu_count: usize,
    buffer_fds: []const ?i32,
) !VerifyShardSummary {
    const wait = perf_buffer_poll.classifyObservedWaitResult(1);
    const ready_count = switch (wait) {
        .ready_events => |count| count,
        else => return error.UnexpectedWaitClassification,
    };
    if (ready_count != 1) return error.UnexpectedWaitClassification;

    return .{
        .version = try logging.libbpfVersionString(version_buffer),
        .auto_cpu_count = cpu_mask.derivePerfBufferAutoCpuCount(3, requested_cpu_count),
        .routed_cpu_count = online_cpu_routing
            .summarizeOnlineCpuRouting(online_cpu_mask, requested_cpu_count, buffer_fds).routed_cpu_count,
        .first_map_type_name = type_names.libbpfBpfMapTypeStr(27) orelse return error.MissingMapTypeName,
        .debug_logs_visible_at_info_default = logging.shouldLogWithEnv(.debug, null),
    };
}

test "phase12 libbpf verify shard keeps bounded helper modules reachable" {
    var version_buffer: [16]u8 = undefined;
    const summary = try summarizeVerifyShard(
        version_buffer[0..],
        &.{ true, false, true },
        0,
        &.{ 11, 17 },
    );

    try std.testing.expectEqualStrings("v1.7", summary.version);
    try std.testing.expectEqual(@as(usize, 3), summary.auto_cpu_count);
    try std.testing.expectEqual(@as(usize, 2), summary.routed_cpu_count);
    try std.testing.expectEqualStrings("ringbuf", summary.first_map_type_name);
    try std.testing.expect(!summary.debug_logs_visible_at_info_default);
}
