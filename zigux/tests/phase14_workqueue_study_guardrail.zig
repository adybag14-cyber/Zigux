const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectLacks(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn readWorkqueueBridgeSource() ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "kernel/workqueue_bridge.zig",
        std.testing.allocator,
        .limited(64 * 1024),
    );
}

test "phase14 workqueue bridge keeps the study-only descriptor explicit" {
    const workqueue_bridge_source = try readWorkqueueBridgeSource();
    defer std.testing.allocator.free(workqueue_bridge_source);

    try expectContains(workqueue_bridge_source, ".touches_live_worker_pools = false");
    try expectContains(workqueue_bridge_source, ".touches_live_work_execution = false");
    try expectContains(workqueue_bridge_source, ".touches_scheduler_hooks = false");
    try expectContains(workqueue_bridge_source, ".posture = \"boundary_map_only\"");
    try expectContains(workqueue_bridge_source, ".provides_stay_in_c_decisions = true");
    try expectContains(workqueue_bridge_source, "pub const Ownership = enum");
    try expectContains(workqueue_bridge_source, "boundary_map_only");
    try expectContains(workqueue_bridge_source, "stay_in_c");
}

test "phase14 workqueue bridge keeps blocked live ownership explicit" {
    const workqueue_bridge_source = try readWorkqueueBridgeSource();
    defer std.testing.allocator.free(workqueue_bridge_source);

    try expectContains(workqueue_bridge_source, "const blocked_live_behaviors = [_][]const u8{");
    try expectContains(workqueue_bridge_source, "\"live worker_pool execution\"");
    try expectContains(workqueue_bridge_source, "\"flush, drain, and cancellation completion ownership\"");
    try expectContains(workqueue_bridge_source, "\"delayed-work requeue control\"");
    try expectContains(workqueue_bridge_source, "\"runtime max_active retuning ownership\"");
    try expectContains(workqueue_bridge_source, "\"scheduler callback parity\"");
    try expectContains(workqueue_bridge_source, "\"rescuer execution ownership\"");
    try expectContains(workqueue_bridge_source, "\"hotplug-driven worker migration and topology rebinding\"");
    try expectContains(workqueue_bridge_source, "Keep the packet in blocked maintenance");
    try expectContains(workqueue_bridge_source, "without implying live execution ownership");
}

test "phase14 workqueue bridge does not drift into live-owner booleans" {
    const workqueue_bridge_source = try readWorkqueueBridgeSource();
    defer std.testing.allocator.free(workqueue_bridge_source);

    try expectLacks(workqueue_bridge_source, ".touches_live_worker_pools = true");
    try expectLacks(workqueue_bridge_source, ".touches_live_work_execution = true");
    try expectLacks(workqueue_bridge_source, ".touches_scheduler_hooks = true");
}
