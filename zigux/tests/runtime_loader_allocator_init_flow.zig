const std = @import("std");
const runtime_loader = @import("runtime_loader");
const contract = @import("runtime_loader_contract");

const AllocatorHandoff = contract.AllocatorHandoff;
const HandoffStage = contract.HandoffStage;
const LoadPlan = contract.LoadPlan;
const PreparedRequest = runtime_loader.PreparedRequest;
const RequestState = contract.RequestState;

fn makeInitializedPlan(
    module_name: []const u8,
    anchor: []const u8,
    entry_symbol: []const u8,
    exit_symbol: []const u8,
    allocator_handoff: AllocatorHandoff,
) LoadPlan {
    return .{
        .module_name = module_name,
        .anchor = anchor,
        .entry_symbol = entry_symbol,
        .exit_symbol = exit_symbol,
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .allocator_handoff = allocator_handoff,
        .init_flow = .{
            .handoff_stage = .initialized,
            .init_runs = 1,
            .selftest_runs = 0,
            .exit_runs = 0,
        },
    };
}

fn expectInitializedSharedRequestShape(plan: LoadPlan, allocator_handoff: AllocatorHandoff) !void {
    try std.testing.expect(plan.requires_runtime_substrate);
    try std.testing.expect(plan.provides_selftest_hook);
    try std.testing.expectEqual(allocator_handoff, plan.allocator_handoff);
    try std.testing.expectEqual(HandoffStage.initialized, plan.init_flow.handoff_stage);
    try std.testing.expectEqual(@as(usize, 1), plan.init_flow.init_runs);
    try std.testing.expectEqual(@as(usize, 0), plan.init_flow.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), plan.init_flow.exit_runs);
    try std.testing.expect(plan.init_flow.readyForRuntimeLoad());
}

fn expectPreparedRequestStable(request: PreparedRequest, plan: LoadPlan, state: RequestState) !void {
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(request, state, plan));
    try std.testing.expect(
        runtime_loader.keepsAllocatorInitFlowConsistent(
            plan,
            plan.allocator_handoff,
            plan.init_flow,
        ),
    );
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(plan));
}

test "shared runtime loader keeps initialized-stage bitmap and kretprobe request shape aligned" {
    const bitmap_plan = makeInitializedPlan(
        "runtime_bitmap",
        "lib/test_bitmap.c",
        "zigux_runtime_bitmap_init",
        "zigux_runtime_bitmap_exit",
        .arena,
    );
    const kretprobe_plan = makeInitializedPlan(
        "runtime_kretprobe",
        "samples/kprobes/kretprobe_example.c",
        "zigux_runtime_kretprobe_init",
        "zigux_runtime_kretprobe_exit",
        .caller_provided,
    );

    try expectInitializedSharedRequestShape(bitmap_plan, .arena);
    try expectInitializedSharedRequestShape(kretprobe_plan, .caller_provided);
    try std.testing.expect(bitmap_plan.allocator_handoff != kretprobe_plan.allocator_handoff);
    try std.testing.expectEqualStrings("runtime_bitmap", bitmap_plan.module_name);
    try std.testing.expectEqualStrings("runtime_kretprobe", kretprobe_plan.module_name);

    var bitmap_request = try runtime_loader.prepareRequest(bitmap_plan);
    var kretprobe_request = try runtime_loader.prepareRequest(kretprobe_plan);

    try expectPreparedRequestStable(bitmap_request, bitmap_plan, .prepared);
    try expectPreparedRequestStable(kretprobe_request, kretprobe_plan, .prepared);
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(bitmap_request.prepared_plan, bitmap_plan));
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(kretprobe_request.prepared_plan, kretprobe_plan));

    const bitmap_pending = try bitmap_request.requestRuntimeLoad();
    const kretprobe_pending = try kretprobe_request.requestRuntimeLoad();

    try expectPreparedRequestStable(bitmap_request, bitmap_pending, .waiting_on_runtime_substrate);
    try expectPreparedRequestStable(kretprobe_request, kretprobe_pending, .waiting_on_runtime_substrate);
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(bitmap_pending, bitmap_request.prepared_plan));
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(kretprobe_pending, kretprobe_request.prepared_plan));

    try bitmap_request.releaseWithoutSubstrate();
    try kretprobe_request.releaseWithoutSubstrate();

    try expectPreparedRequestStable(bitmap_request, bitmap_pending, .released_without_substrate);
    try expectPreparedRequestStable(kretprobe_request, kretprobe_pending, .released_without_substrate);
}

test "shared runtime loader keeps prepared init-flow counters from drifting before handoff" {
    const kretprobe_plan = makeInitializedPlan(
        "runtime_kretprobe",
        "samples/kprobes/kretprobe_example.c",
        "zigux_runtime_kretprobe_init",
        "zigux_runtime_kretprobe_exit",
        .caller_provided,
    );

    var request = try runtime_loader.prepareRequest(kretprobe_plan);

    request.plan.init_flow.init_runs = 2;
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try expectPreparedRequestStable(request, kretprobe_plan, .prepared);
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(request.prepared_plan, kretprobe_plan));
    try std.testing.expect(!runtime_loader.keepsLoadPlanExplicit(request.plan, kretprobe_plan));

    request.plan = kretprobe_plan;
    request.plan.init_flow.exit_runs = 1;
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try expectPreparedRequestStable(request, kretprobe_plan, .prepared);
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(request.prepared_plan, kretprobe_plan));
    try std.testing.expect(!runtime_loader.keepsLoadPlanExplicit(request.plan, kretprobe_plan));
}
