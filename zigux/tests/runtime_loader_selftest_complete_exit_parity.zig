const std = @import("std");
const runtime_loader = @import("runtime_loader");

fn makePlan(
    module_name: []const u8,
    anchor: []const u8,
    entry_symbol: []const u8,
    exit_symbol: []const u8,
    allocator_handoff: runtime_loader.AllocatorHandoff,
    init_flow: runtime_loader.InitFlow,
) runtime_loader.LoadPlan {
    return .{
        .module_name = module_name,
        .anchor = anchor,
        .entry_symbol = entry_symbol,
        .exit_symbol = exit_symbol,
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .allocator_handoff = allocator_handoff,
        .init_flow = init_flow,
    };
}

fn expectExactLoadPlanParity(
    expected: runtime_loader.LoadPlan,
    actual: runtime_loader.LoadPlan,
) !void {
    try std.testing.expectEqualStrings(expected.module_name, actual.module_name);
    try std.testing.expectEqualStrings(expected.anchor, actual.anchor);
    try std.testing.expectEqualStrings(expected.entry_symbol, actual.entry_symbol);
    try std.testing.expectEqualStrings(expected.exit_symbol, actual.exit_symbol);
    try std.testing.expectEqual(expected.requires_runtime_substrate, actual.requires_runtime_substrate);
    try std.testing.expectEqual(expected.provides_selftest_hook, actual.provides_selftest_hook);
    try std.testing.expectEqual(expected.allocator_handoff, actual.allocator_handoff);
    try std.testing.expectEqual(expected.init_flow.handoff_stage, actual.init_flow.handoff_stage);
    try std.testing.expectEqual(expected.init_flow.init_runs, actual.init_flow.init_runs);
    try std.testing.expectEqual(expected.init_flow.selftest_runs, actual.init_flow.selftest_runs);
    try std.testing.expectEqual(expected.init_flow.exit_runs, actual.init_flow.exit_runs);
}

fn expectPreparedSnapshotStableAfterLaterLiveExit(
    expected: runtime_loader.LoadPlan,
) !runtime_loader.LoadPlan {
    var request = try runtime_loader.prepareRequest(expected);
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        request,
        .prepared,
        expected,
    ));

    var live_exited = expected;
    live_exited.init_flow.exit_runs = 1;
    try std.testing.expect(!live_exited.init_flow.readyForRuntimeLoad());
    try std.testing.expect(!runtime_loader.keepsRequestStateAndPlanExplicit(
        request,
        .prepared,
        live_exited,
    ));

    const pending = try request.requestRuntimeLoad();
    try std.testing.expectEqual(runtime_loader.RequestState.waiting_on_runtime_substrate, request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        request,
        .waiting_on_runtime_substrate,
        expected,
    ));
    try expectExactLoadPlanParity(expected, pending);
    try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(
        pending,
        expected.allocator_handoff,
        expected.init_flow,
    ));
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(pending));

    try request.releaseWithoutSubstrate();
    try std.testing.expectEqual(runtime_loader.RequestState.released_without_substrate, request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        request,
        .released_without_substrate,
        expected,
    ));

    return pending;
}

test "phase 9 runtime loader keeps selftest-complete prepared snapshots stable even if later live state would look exited across all shipped pilot families" {
    const expected_atomic64 = makePlan(
        "runtime_atomic64",
        "lib/atomic64_test.c",
        "zigux_runtime_atomic64_init",
        "zigux_runtime_atomic64_exit",
        .caller_provided,
        .{ .handoff_stage = .selftest_complete, .init_runs = 1, .selftest_runs = 1, .exit_runs = 0 },
    );
    const atomic64_pending = try expectPreparedSnapshotStableAfterLaterLiveExit(expected_atomic64);

    const expected_bitmap = makePlan(
        "runtime_bitmap",
        "lib/test_bitmap.c",
        "zigux_runtime_bitmap_init",
        "zigux_runtime_bitmap_exit",
        .arena,
        .{ .handoff_stage = .selftest_complete, .init_runs = 1, .selftest_runs = 1, .exit_runs = 0 },
    );
    const bitmap_pending = try expectPreparedSnapshotStableAfterLaterLiveExit(expected_bitmap);

    const expected_trace_events = makePlan(
        "runtime_trace_events",
        "samples/trace_events/trace-events-sample.c",
        "zigux_runtime_trace_events_init",
        "zigux_runtime_trace_events_exit",
        .caller_provided,
        .{ .handoff_stage = .selftest_complete, .init_runs = 1, .selftest_runs = 1, .exit_runs = 0 },
    );
    const trace_events_pending = try expectPreparedSnapshotStableAfterLaterLiveExit(expected_trace_events);

    const expected_kretprobe = makePlan(
        "runtime_kretprobe",
        "samples/kprobes/kretprobe_example.c",
        "zigux_runtime_kretprobe_init",
        "zigux_runtime_kretprobe_exit",
        .kernel_heap,
        .{ .handoff_stage = .selftest_complete, .init_runs = 1, .selftest_runs = 1, .exit_runs = 0 },
    );
    const kretprobe_pending = try expectPreparedSnapshotStableAfterLaterLiveExit(expected_kretprobe);

    const pending_plans = [_]runtime_loader.LoadPlan{
        atomic64_pending,
        bitmap_pending,
        trace_events_pending,
        kretprobe_pending,
    };

    try std.testing.expectEqual(runtime_loader.HandoffStage.selftest_complete, pending_plans[0].init_flow.handoff_stage);
    try std.testing.expectEqual(@as(usize, 1), pending_plans[0].init_flow.init_runs);
    try std.testing.expectEqual(@as(usize, 1), pending_plans[0].init_flow.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), pending_plans[0].init_flow.exit_runs);
    try std.testing.expect(pending_plans[0].requires_runtime_substrate);
    try std.testing.expect(pending_plans[0].provides_selftest_hook);

    for (pending_plans[1..]) |pending| {
        try std.testing.expectEqual(pending_plans[0].init_flow.handoff_stage, pending.init_flow.handoff_stage);
        try std.testing.expectEqual(pending_plans[0].init_flow.init_runs, pending.init_flow.init_runs);
        try std.testing.expectEqual(pending_plans[0].init_flow.selftest_runs, pending.init_flow.selftest_runs);
        try std.testing.expectEqual(pending_plans[0].init_flow.exit_runs, pending.init_flow.exit_runs);
        try std.testing.expectEqual(pending_plans[0].requires_runtime_substrate, pending.requires_runtime_substrate);
        try std.testing.expectEqual(pending_plans[0].provides_selftest_hook, pending.provides_selftest_hook);
    }
}
