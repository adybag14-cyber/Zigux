const std = @import("std");

fn readRepoFileAlloc(allocator: std.mem.Allocator, path: []const u8, max_bytes: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, allocator, .limited(max_bytes));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 9 runtime loader caller-provided selftest-complete survey keeps atomic64 and trace-events parity explicit" {
    const allocator = std.testing.allocator;
    const replay = try readRepoFileAlloc(
        allocator,
        "zigux/tests/runtime_loader_allocator_init_flow.zig",
        128 * 1024,
    );
    defer allocator.free(replay);

    try expectContains(
        replay,
        "test \"phase 9 runtime loader allocator/init-flow replay keeps caller-provided selftest-complete request shape explicit across atomic64 and trace-events\" {",
    );
    try expectContains(
        replay,
        "const expected_atomic64 = makePlan(\"runtime_atomic64\", \"lib/atomic64_test.c\", \"zigux_runtime_atomic64_init\", \"zigux_runtime_atomic64_exit\", .caller_provided, .{ .handoff_stage = .selftest_complete, .init_runs = 1, .selftest_runs = 1, .exit_runs = 0 });",
    );
    try expectContains(
        replay,
        "const expected_trace_events = makePlan(\"runtime_trace_events\", \"samples/trace_events/trace-events-sample.c\", \"zigux_runtime_trace_events_init\", \"zigux_runtime_trace_events_exit\", .caller_provided, .{ .handoff_stage = .selftest_complete, .init_runs = 1, .selftest_runs = 1, .exit_runs = 0 });",
    );
    try expectContains(
        replay,
        "try expectCallerProvidedSelftestCompleteSharedRequestShape(atomic64_pending);",
    );
    try expectContains(
        replay,
        "try expectCallerProvidedSelftestCompleteSharedRequestShape(trace_events_pending);",
    );
    try expectContains(
        replay,
        "try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(atomic64_pending, .caller_provided, expected_atomic64.init_flow));",
    );
    try expectContains(
        replay,
        "try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(trace_events_pending, .caller_provided, expected_trace_events.init_flow));",
    );
    try expectContains(
        replay,
        "try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(atomic64_request, .released_without_substrate, atomic64_pending));",
    );
    try expectContains(
        replay,
        "try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(trace_events_request, .released_without_substrate, trace_events_pending));",
    );
    try expectContains(
        replay,
        "try std.testing.expectEqual(atomic64_pending.init_flow.handoff_stage, trace_events_pending.init_flow.handoff_stage);",
    );
    try expectContains(
        replay,
        "try std.testing.expectEqual(atomic64_pending.init_flow.selftest_runs, trace_events_pending.init_flow.selftest_runs);",
    );
    try expectContains(
        replay,
        "try std.testing.expectEqual(atomic64_pending.provides_selftest_hook, trace_events_pending.provides_selftest_hook);",
    );
}
