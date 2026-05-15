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

test "phase 9 runtime loader keeps bitmap and kretprobe selftest-complete prepared snapshots stable even if later live state would look exited" {
    const expected_bitmap = makePlan(
        "runtime_bitmap",
        "lib/test_bitmap.c",
        "zigux_runtime_bitmap_init",
        "zigux_runtime_bitmap_exit",
        .arena,
        .{ .handoff_stage = .selftest_complete, .init_runs = 1, .selftest_runs = 1, .exit_runs = 0 },
    );
    var bitmap_request = try runtime_loader.prepareRequest(expected_bitmap);
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, bitmap_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        bitmap_request,
        .prepared,
        expected_bitmap,
    ));

    var bitmap_live_exited = expected_bitmap;
    bitmap_live_exited.init_flow.exit_runs = 1;
    try std.testing.expect(!bitmap_live_exited.init_flow.readyForRuntimeLoad());
    try std.testing.expect(!runtime_loader.keepsRequestStateAndPlanExplicit(
        bitmap_request,
        .prepared,
        bitmap_live_exited,
    ));

    const bitmap_pending = try bitmap_request.requestRuntimeLoad();
    try std.testing.expectEqual(runtime_loader.RequestState.waiting_on_runtime_substrate, bitmap_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        bitmap_request,
        .waiting_on_runtime_substrate,
        expected_bitmap,
    ));
    try expectExactLoadPlanParity(expected_bitmap, bitmap_pending);
    try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(
        bitmap_pending,
        .arena,
        expected_bitmap.init_flow,
    ));
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(bitmap_pending));

    const expected_kretprobe = makePlan(
        "runtime_kretprobe",
        "samples/kprobes/kretprobe_example.c",
        "zigux_runtime_kretprobe_init",
        "zigux_runtime_kretprobe_exit",
        .kernel_heap,
        .{ .handoff_stage = .selftest_complete, .init_runs = 1, .selftest_runs = 1, .exit_runs = 0 },
    );
    var kretprobe_request = try runtime_loader.prepareRequest(expected_kretprobe);
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, kretprobe_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        kretprobe_request,
        .prepared,
        expected_kretprobe,
    ));

    var kretprobe_live_exited = expected_kretprobe;
    kretprobe_live_exited.init_flow.exit_runs = 1;
    try std.testing.expect(!kretprobe_live_exited.init_flow.readyForRuntimeLoad());
    try std.testing.expect(!runtime_loader.keepsRequestStateAndPlanExplicit(
        kretprobe_request,
        .prepared,
        kretprobe_live_exited,
    ));

    const kretprobe_pending = try kretprobe_request.requestRuntimeLoad();
    try std.testing.expectEqual(runtime_loader.RequestState.waiting_on_runtime_substrate, kretprobe_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        kretprobe_request,
        .waiting_on_runtime_substrate,
        expected_kretprobe,
    ));
    try expectExactLoadPlanParity(expected_kretprobe, kretprobe_pending);
    try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(
        kretprobe_pending,
        .kernel_heap,
        expected_kretprobe.init_flow,
    ));
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(kretprobe_pending));

    try std.testing.expectEqual(bitmap_pending.init_flow.handoff_stage, kretprobe_pending.init_flow.handoff_stage);
    try std.testing.expectEqual(bitmap_pending.init_flow.init_runs, kretprobe_pending.init_flow.init_runs);
    try std.testing.expectEqual(bitmap_pending.init_flow.selftest_runs, kretprobe_pending.init_flow.selftest_runs);
    try std.testing.expectEqual(bitmap_pending.init_flow.exit_runs, kretprobe_pending.init_flow.exit_runs);
    try std.testing.expectEqual(bitmap_pending.requires_runtime_substrate, kretprobe_pending.requires_runtime_substrate);
    try std.testing.expectEqual(bitmap_pending.provides_selftest_hook, kretprobe_pending.provides_selftest_hook);

    try bitmap_request.releaseWithoutSubstrate();
    try kretprobe_request.releaseWithoutSubstrate();
    try std.testing.expectEqual(runtime_loader.RequestState.released_without_substrate, bitmap_request.state);
    try std.testing.expectEqual(runtime_loader.RequestState.released_without_substrate, kretprobe_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        bitmap_request,
        .released_without_substrate,
        expected_bitmap,
    ));
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        kretprobe_request,
        .released_without_substrate,
        expected_kretprobe,
    ));
}
