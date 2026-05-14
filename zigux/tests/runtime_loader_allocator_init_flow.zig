const std = @import("std");
const runtime_loader = @import("runtime_loader");
const runtime_loader_contract = @import("runtime_loader_contract");

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const BaseManifest = struct {
    phase: []const u8,
    anchor: []const u8,
    gaps: []const Gap,
};

const DeliveryEvidence = struct {
    id: []const u8,
    kind: []const u8,
    path: []const u8,
    why_now: []const u8,
};

const OwnershipEntry = struct {
    surface: []const u8,
    role: []const u8,
    owner: []const u8,
    boundary: []const u8,
};

const LifecycleBoundarySummary = struct {
    pre_execution_handoff_only: bool,
    requires_idle_registration_snapshot: bool,
    failed_exit_state_retained_until_drain: bool,
    metadata_only_registration_labels: []const []const u8,
    shared_request_surface: []const u8,
    live_registration_parity: []const u8,
    prepared_snapshot_owned_by_loader_request: bool = false,
};

const KretprobeManifest = struct {
    phase: []const u8,
    anchor: []const u8,
    lifecycle_boundary_summary: LifecycleBoundarySummary,
    gaps: []const Gap,
};

const TraceEventsManifest = struct {
    phase: []const u8,
    anchor: []const u8,
    delivery_evidence_catalog: []const DeliveryEvidence,
    ownership_map: []const OwnershipEntry,
    gaps: []const Gap,
};

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

fn readRepoFileAlloc(allocator: std.mem.Allocator, path: []const u8, max_bytes: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(max_bytes),
    );
}

fn findGap(gaps: []const Gap, id: []const u8) ?Gap {
    for (gaps) |gap| {
        if (std.mem.eql(u8, gap.id, id)) return gap;
    }
    return null;
}

fn findDeliveryEvidence(entries: []const DeliveryEvidence, id: []const u8) ?DeliveryEvidence {
    for (entries) |entry| {
        if (std.mem.eql(u8, entry.id, id)) return entry;
    }
    return null;
}

fn findOwnershipEntry(entries: []const OwnershipEntry, surface: []const u8) ?OwnershipEntry {
    for (entries) |entry| {
        if (std.mem.eql(u8, entry.surface, surface)) return entry;
    }
    return null;
}

fn expectGapStatusAndWhyNow(
    gaps: []const Gap,
    id: []const u8,
    status: []const u8,
    why_now_fragment: []const u8,
) !void {
    const gap = findGap(gaps, id) orelse return error.MissingGap;
    try std.testing.expectEqualStrings(status, gap.status);
    try std.testing.expect(std.mem.indexOf(u8, gap.why_now, why_now_fragment) != null);
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

fn expectInitializedSharedRequestShape(plan: runtime_loader.LoadPlan) !void {
    try std.testing.expect(plan.requires_runtime_substrate);
    try std.testing.expect(plan.provides_selftest_hook);
    try std.testing.expectEqual(runtime_loader.HandoffStage.initialized, plan.init_flow.handoff_stage);
    try std.testing.expectEqual(@as(usize, 1), plan.init_flow.init_runs);
    try std.testing.expectEqual(@as(usize, 0), plan.init_flow.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), plan.init_flow.exit_runs);
}

fn expectCallerProvidedSelftestCompleteSharedRequestShape(plan: runtime_loader.LoadPlan) !void {
    try std.testing.expect(plan.requires_runtime_substrate);
    try std.testing.expect(plan.provides_selftest_hook);
    try std.testing.expectEqual(runtime_loader.AllocatorHandoff.caller_provided, plan.allocator_handoff);
    try std.testing.expectEqual(runtime_loader.HandoffStage.selftest_complete, plan.init_flow.handoff_stage);
    try std.testing.expectEqual(@as(usize, 1), plan.init_flow.init_runs);
    try std.testing.expectEqual(@as(usize, 1), plan.init_flow.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), plan.init_flow.exit_runs);
}

fn expectFileContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectPreparedPlanDriftKeepsPreparedState(
    request: runtime_loader.PreparedRequest,
    stable_plan: runtime_loader.LoadPlan,
) !void {
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, request.state);
    try std.testing.expect(runtime_loader_contract.keepsLoadPlanExplicit(request.prepared_plan, stable_plan));
    try std.testing.expect(!runtime_loader_contract.keepsLoadPlanExplicit(request.plan, stable_plan));
}

test "phase 9 runtime loader allocator/init-flow replay covers all shipped runtime pilot handoffs" {
    const plans = [_]runtime_loader.LoadPlan{
        makePlan("runtime_atomic64", "lib/atomic64_test.c", "zigux_runtime_atomic64_init", "zigux_runtime_atomic64_exit", .caller_provided, .{ .handoff_stage = .selftest_complete, .init_runs = 1, .selftest_runs = 1, .exit_runs = 0 }),
        makePlan("runtime_bitmap", "lib/test_bitmap.c", "zigux_runtime_bitmap_init", "zigux_runtime_bitmap_exit", .arena, .{ .handoff_stage = .initialized, .init_runs = 1, .selftest_runs = 0, .exit_runs = 0 }),
        makePlan("runtime_trace_events", "samples/trace_events/trace-events-sample.c", "zigux_runtime_trace_events_init", "zigux_runtime_trace_events_exit", .caller_provided, .{ .handoff_stage = .selftest_complete, .init_runs = 1, .selftest_runs = 1, .exit_runs = 0 }),
        makePlan("runtime_kretprobe", "samples/kprobes/kretprobe_example.c", "zigux_runtime_kretprobe_init", "zigux_runtime_kretprobe_exit", .kernel_heap, .{ .handoff_stage = .selftest_complete, .init_runs = 1, .selftest_runs = 1, .exit_runs = 0 }),
    };

    for (plans) |plan| {
        var request = try runtime_loader.prepareRequest(plan);
        const pending_plan = try request.requestRuntimeLoad();
        try expectExactLoadPlanParity(plan, pending_plan);
        try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(plan));
        try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(pending_plan, plan.allocator_handoff, plan.init_flow));
        try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(pending_plan));
        try request.releaseWithoutSubstrate();
    }
}

test "phase 9 runtime loader allocator/init-flow replay keeps the smallest shared bitmap and kretprobe request shape explicit" {
    const expected_bitmap = makePlan("runtime_bitmap", "lib/test_bitmap.c", "zigux_runtime_bitmap_init", "zigux_runtime_bitmap_exit", .arena, .{ .handoff_stage = .initialized, .init_runs = 1, .selftest_runs = 0, .exit_runs = 0 });
    var bitmap_request = try runtime_loader.prepareRequest(expected_bitmap);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(bitmap_request, .prepared, expected_bitmap));
    const bitmap_pending = try bitmap_request.requestRuntimeLoad();
    try expectExactLoadPlanParity(expected_bitmap, bitmap_pending);
    try expectInitializedSharedRequestShape(bitmap_pending);
    try std.testing.expectEqual(runtime_loader.AllocatorHandoff.arena, bitmap_pending.allocator_handoff);
    try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(bitmap_pending, .arena, expected_bitmap.init_flow));
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(bitmap_pending));
    try bitmap_request.releaseWithoutSubstrate();
    try std.testing.expectEqual(runtime_loader.RequestState.released_without_substrate, bitmap_request.state);

    const expected_kretprobe = makePlan("runtime_kretprobe", "samples/kprobes/kretprobe_example.c", "zigux_runtime_kretprobe_init", "zigux_runtime_kretprobe_exit", .kernel_heap, .{ .handoff_stage = .initialized, .init_runs = 1, .selftest_runs = 0, .exit_runs = 0 });
    var kretprobe_request = try runtime_loader.prepareRequest(expected_kretprobe);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(kretprobe_request, .prepared, expected_kretprobe));
    const kretprobe_pending = try kretprobe_request.requestRuntimeLoad();
    try expectExactLoadPlanParity(expected_kretprobe, kretprobe_pending);
    try expectInitializedSharedRequestShape(kretprobe_pending);
    try std.testing.expectEqual(runtime_loader.AllocatorHandoff.kernel_heap, kretprobe_pending.allocator_handoff);
    try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(kretprobe_pending, .kernel_heap, expected_kretprobe.init_flow));
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(kretprobe_pending));
    try kretprobe_request.releaseWithoutSubstrate();
    try std.testing.expectEqual(runtime_loader.RequestState.released_without_substrate, kretprobe_request.state);

    try std.testing.expectEqual(bitmap_pending.init_flow.handoff_stage, kretprobe_pending.init_flow.handoff_stage);
    try std.testing.expectEqual(bitmap_pending.init_flow.init_runs, kretprobe_pending.init_flow.init_runs);
    try std.testing.expectEqual(bitmap_pending.init_flow.selftest_runs, kretprobe_pending.init_flow.selftest_runs);
    try std.testing.expectEqual(bitmap_pending.init_flow.exit_runs, kretprobe_pending.init_flow.exit_runs);
    try std.testing.expectEqual(bitmap_pending.requires_runtime_substrate, kretprobe_pending.requires_runtime_substrate);
    try std.testing.expectEqual(bitmap_pending.provides_selftest_hook, kretprobe_pending.provides_selftest_hook);
}

test "phase 9 runtime loader allocator/init-flow replay keeps caller-provided selftest-complete request shape explicit across atomic64 and trace-events" {
    const expected_atomic64 = makePlan("runtime_atomic64", "lib/atomic64_test.c", "zigux_runtime_atomic64_init", "zigux_runtime_atomic64_exit", .caller_provided, .{ .handoff_stage = .selftest_complete, .init_runs = 1, .selftest_runs = 1, .exit_runs = 0 });
    var atomic64_request = try runtime_loader.prepareRequest(expected_atomic64);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(atomic64_request, .prepared, expected_atomic64));
    const atomic64_pending = try atomic64_request.requestRuntimeLoad();
    try expectExactLoadPlanParity(expected_atomic64, atomic64_pending);
    try expectCallerProvidedSelftestCompleteSharedRequestShape(atomic64_pending);
    try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(atomic64_pending, .caller_provided, expected_atomic64.init_flow));
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(atomic64_pending));
    try atomic64_request.releaseWithoutSubstrate();
    try std.testing.expectEqual(runtime_loader.RequestState.released_without_substrate, atomic64_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(atomic64_request, .released_without_substrate, atomic64_pending));

    const expected_trace_events = makePlan("runtime_trace_events", "samples/trace_events/trace-events-sample.c", "zigux_runtime_trace_events_init", "zigux_runtime_trace_events_exit", .caller_provided, .{ .handoff_stage = .selftest_complete, .init_runs = 1, .selftest_runs = 1, .exit_runs = 0 });
    var trace_events_request = try runtime_loader.prepareRequest(expected_trace_events);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(trace_events_request, .prepared, expected_trace_events));
    const trace_events_pending = try trace_events_request.requestRuntimeLoad();
    try expectExactLoadPlanParity(expected_trace_events, trace_events_pending);
    try expectCallerProvidedSelftestCompleteSharedRequestShape(trace_events_pending);
    try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(trace_events_pending, .caller_provided, expected_trace_events.init_flow));
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(trace_events_pending));
    try trace_events_request.releaseWithoutSubstrate();
    try std.testing.expectEqual(runtime_loader.RequestState.released_without_substrate, trace_events_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(trace_events_request, .released_without_substrate, trace_events_pending));

    try std.testing.expectEqual(atomic64_pending.allocator_handoff, trace_events_pending.allocator_handoff);
    try std.testing.expectEqual(atomic64_pending.init_flow.handoff_stage, trace_events_pending.init_flow.handoff_stage);
    try std.testing.expectEqual(atomic64_pending.init_flow.init_runs, trace_events_pending.init_flow.init_runs);
    try std.testing.expectEqual(atomic64_pending.init_flow.selftest_runs, trace_events_pending.init_flow.selftest_runs);
    try std.testing.expectEqual(atomic64_pending.init_flow.exit_runs, trace_events_pending.init_flow.exit_runs);
    try std.testing.expectEqual(atomic64_pending.requires_runtime_substrate, trace_events_pending.requires_runtime_substrate);
    try std.testing.expectEqual(atomic64_pending.provides_selftest_hook, trace_events_pending.provides_selftest_hook);
}

test "phase 9 runtime loader allocator/init-flow replay keeps bitmap and kretprobe selftest-complete request shape parity explicit" {
    const expected_bitmap = makePlan("runtime_bitmap", "lib/test_bitmap.c", "zigux_runtime_bitmap_init", "zigux_runtime_bitmap_exit", .arena, .{ .handoff_stage = .selftest_complete, .init_runs = 1, .selftest_runs = 1, .exit_runs = 0 });
    var bitmap_request = try runtime_loader.prepareRequest(expected_bitmap);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(bitmap_request, .prepared, expected_bitmap));
    const bitmap_pending = try bitmap_request.requestRuntimeLoad();
    try expectExactLoadPlanParity(expected_bitmap, bitmap_pending);
    try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(bitmap_pending, .arena, expected_bitmap.init_flow));
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(bitmap_pending));

    const expected_kretprobe = makePlan("runtime_kretprobe", "samples/kprobes/kretprobe_example.c", "zigux_runtime_kretprobe_init", "zigux_runtime_kretprobe_exit", .kernel_heap, .{ .handoff_stage = .selftest_complete, .init_runs = 1, .selftest_runs = 1, .exit_runs = 0 });
    var kretprobe_request = try runtime_loader.prepareRequest(expected_kretprobe);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(kretprobe_request, .prepared, expected_kretprobe));
    const kretprobe_pending = try kretprobe_request.requestRuntimeLoad();
    try expectExactLoadPlanParity(expected_kretprobe, kretprobe_pending);
    try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(kretprobe_pending, .kernel_heap, expected_kretprobe.init_flow));
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
}

test "phase 9 runtime loader allocator/init-flow replay keeps initialized prepared snapshots stable even if later live state would look exited" {
    const expected_bitmap = makePlan("runtime_bitmap", "lib/test_bitmap.c", "zigux_runtime_bitmap_init", "zigux_runtime_bitmap_exit", .arena, .{ .handoff_stage = .initialized, .init_runs = 1, .selftest_runs = 0, .exit_runs = 0 });
    var bitmap_request = try runtime_loader.prepareRequest(expected_bitmap);
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, bitmap_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(bitmap_request, .prepared, expected_bitmap));

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
    try expectInitializedSharedRequestShape(bitmap_pending);
    try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(
        bitmap_pending,
        .arena,
        expected_bitmap.init_flow,
    ));
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(bitmap_pending));

    const expected_kretprobe = makePlan("runtime_kretprobe", "samples/kprobes/kretprobe_example.c", "zigux_runtime_kretprobe_init", "zigux_runtime_kretprobe_exit", .kernel_heap, .{ .handoff_stage = .initialized, .init_runs = 1, .selftest_runs = 0, .exit_runs = 0 });
    var kretprobe_request = try runtime_loader.prepareRequest(expected_kretprobe);
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, kretprobe_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(kretprobe_request, .prepared, expected_kretprobe));

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
    try expectInitializedSharedRequestShape(kretprobe_pending);
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

test "phase 9 runtime loader allocator/init-flow replay keeps selftest-complete prepared snapshots stable even if later live state would look exited" {
    const expected_atomic64 = makePlan("runtime_atomic64", "lib/atomic64_test.c", "zigux_runtime_atomic64_init", "zigux_runtime_atomic64_exit", .caller_provided, .{ .handoff_stage = .selftest_complete, .init_runs = 1, .selftest_runs = 1, .exit_runs = 0 });
    var atomic64_request = try runtime_loader.prepareRequest(expected_atomic64);
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, atomic64_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(atomic64_request, .prepared, expected_atomic64));

    var atomic64_live_exited = expected_atomic64;
    atomic64_live_exited.init_flow.exit_runs = 1;
    try std.testing.expect(!atomic64_live_exited.init_flow.readyForRuntimeLoad());
    try std.testing.expect(!runtime_loader.keepsRequestStateAndPlanExplicit(
        atomic64_request,
        .prepared,
        atomic64_live_exited,
    ));

    const atomic64_pending = try atomic64_request.requestRuntimeLoad();
    try std.testing.expectEqual(runtime_loader.RequestState.waiting_on_runtime_substrate, atomic64_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        atomic64_request,
        .waiting_on_runtime_substrate,
        expected_atomic64,
    ));
    try expectExactLoadPlanParity(expected_atomic64, atomic64_pending);
    try expectCallerProvidedSelftestCompleteSharedRequestShape(atomic64_pending);
    try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(
        atomic64_pending,
        .caller_provided,
        expected_atomic64.init_flow,
    ));
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(atomic64_pending));

    const expected_trace_events = makePlan("runtime_trace_events", "samples/trace_events/trace-events-sample.c", "zigux_runtime_trace_events_init", "zigux_runtime_trace_events_exit", .caller_provided, .{ .handoff_stage = .selftest_complete, .init_runs = 1, .selftest_runs = 1, .exit_runs = 0 });
    var trace_events_request = try runtime_loader.prepareRequest(expected_trace_events);
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, trace_events_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        trace_events_request,
        .prepared,
        expected_trace_events,
    ));

    var trace_events_live_exited = expected_trace_events;
    trace_events_live_exited.init_flow.exit_runs = 1;
    try std.testing.expect(!trace_events_live_exited.init_flow.readyForRuntimeLoad());
    try std.testing.expect(!runtime_loader.keepsRequestStateAndPlanExplicit(
        trace_events_request,
        .prepared,
        trace_events_live_exited,
    ));

    const trace_events_pending = try trace_events_request.requestRuntimeLoad();
    try std.testing.expectEqual(runtime_loader.RequestState.waiting_on_runtime_substrate, trace_events_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        trace_events_request,
        .waiting_on_runtime_substrate,
        expected_trace_events,
    ));
    try expectExactLoadPlanParity(expected_trace_events, trace_events_pending);
    try expectCallerProvidedSelftestCompleteSharedRequestShape(trace_events_pending);
    try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(
        trace_events_pending,
        .caller_provided,
        expected_trace_events.init_flow,
    ));
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(trace_events_pending));

    try std.testing.expectEqual(atomic64_pending.allocator_handoff, trace_events_pending.allocator_handoff);
    try std.testing.expectEqual(atomic64_pending.init_flow.handoff_stage, trace_events_pending.init_flow.handoff_stage);
    try std.testing.expectEqual(atomic64_pending.init_flow.init_runs, trace_events_pending.init_flow.init_runs);
    try std.testing.expectEqual(atomic64_pending.init_flow.selftest_runs, trace_events_pending.init_flow.selftest_runs);
    try std.testing.expectEqual(atomic64_pending.init_flow.exit_runs, trace_events_pending.init_flow.exit_runs);
    try std.testing.expectEqual(atomic64_pending.requires_runtime_substrate, trace_events_pending.requires_runtime_substrate);
    try std.testing.expectEqual(atomic64_pending.provides_selftest_hook, trace_events_pending.provides_selftest_hook);
    try atomic64_request.releaseWithoutSubstrate();
    try trace_events_request.releaseWithoutSubstrate();
    try std.testing.expectEqual(runtime_loader.RequestState.released_without_substrate, atomic64_request.state);
    try std.testing.expectEqual(runtime_loader.RequestState.released_without_substrate, trace_events_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        atomic64_request,
        .released_without_substrate,
        expected_atomic64,
    ));
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        trace_events_request,
        .released_without_substrate,
        expected_trace_events,
    ));
}

test "phase 9 runtime loader allocator/init-flow replay rejects missing-init, premature-selftest, exited, duplicate-init, duplicate-selftest, or incomplete handoffs" {
    const missing_init_plan = makePlan("runtime_atomic64", "lib/atomic64_test.c", "zigux_runtime_atomic64_init", "zigux_runtime_atomic64_exit", .caller_provided, .{ .handoff_stage = .initialized, .init_runs = 0, .selftest_runs = 0, .exit_runs = 0 });
    try std.testing.expectError(error.InvalidInitFlow, runtime_loader.prepareRequest(missing_init_plan));
    const premature_selftest_plan = makePlan("runtime_bitmap", "lib/test_bitmap.c", "zigux_runtime_bitmap_init", "zigux_runtime_bitmap_exit", .arena, .{ .handoff_stage = .initialized, .init_runs = 1, .selftest_runs = 1, .exit_runs = 0 });
    try std.testing.expectError(error.InvalidInitFlow, runtime_loader.prepareRequest(premature_selftest_plan));
    const exited_plan = makePlan("runtime_bitmap", "lib/test_bitmap.c", "zigux_runtime_bitmap_init", "zigux_runtime_bitmap_exit", .arena, .{ .handoff_stage = .selftest_complete, .init_runs = 1, .selftest_runs = 1, .exit_runs = 1 });
    try std.testing.expectError(error.InvalidInitFlow, runtime_loader.prepareRequest(exited_plan));
    const duplicate_init_plan = makePlan("runtime_trace_events", "samples/trace_events/trace-events-sample.c", "zigux_runtime_trace_events_init", "zigux_runtime_trace_events_exit", .caller_provided, .{ .handoff_stage = .selftest_complete, .init_runs = 2, .selftest_runs = 1, .exit_runs = 0 });
    try std.testing.expectError(error.InvalidInitFlow, runtime_loader.prepareRequest(duplicate_init_plan));
    const duplicate_selftest_plan = makePlan("runtime_trace_events", "samples/trace_events/trace-events-sample.c", "zigux_runtime_trace_events_init", "zigux_runtime_trace_events_exit", .caller_provided, .{ .handoff_stage = .selftest_complete, .init_runs = 1, .selftest_runs = 2, .exit_runs = 0 });
    try std.testing.expectError(error.InvalidInitFlow, runtime_loader.prepareRequest(duplicate_selftest_plan));
    const incomplete_plan = makePlan("runtime_kretprobe", "samples/kprobes/kretprobe_example.c", "zigux_runtime_kretprobe_init", "zigux_runtime_kretprobe_exit", .kernel_heap, .{ .handoff_stage = .selftest_complete, .init_runs = 1, .selftest_runs = 0, .exit_runs = 0 });
    try std.testing.expectError(error.InvalidSelftestHookEvidence, runtime_loader.prepareRequest(incomplete_plan));
}

test "phase 9 runtime loader allocator/init-flow replay rejects direct approved-pilot-family drift" {
    const stable_bitmap = makePlan("runtime_bitmap", "lib/test_bitmap.c", "zigux_runtime_bitmap_init", "zigux_runtime_bitmap_exit", .arena, .{ .handoff_stage = .initialized, .init_runs = 1, .selftest_runs = 0, .exit_runs = 0 });

    var drifted_module = stable_bitmap;
    drifted_module.module_name = "runtime_bitmap_drift";
    try std.testing.expect(!runtime_loader.keepsApprovedPilotFamilyContract(drifted_module));
    try std.testing.expectError(error.InvalidPilotFamilyContract, runtime_loader.prepareRequest(drifted_module));

    var drifted_anchor = stable_bitmap;
    drifted_anchor.anchor = "lib/test_bitmap_drift.c";
    try std.testing.expect(!runtime_loader.keepsApprovedPilotFamilyContract(drifted_anchor));
    try std.testing.expectError(error.InvalidPilotFamilyContract, runtime_loader.prepareRequest(drifted_anchor));

    const stable_trace_events = makePlan("runtime_trace_events", "samples/trace_events/trace-events-sample.c", "zigux_runtime_trace_events_init", "zigux_runtime_trace_events_exit", .caller_provided, .{ .handoff_stage = .selftest_complete, .init_runs = 1, .selftest_runs = 1, .exit_runs = 0 });

    var drifted_entry_symbol = stable_trace_events;
    drifted_entry_symbol.entry_symbol = "zigux_runtime_trace_events_init_drift";
    try std.testing.expect(!runtime_loader.keepsApprovedPilotFamilyContract(drifted_entry_symbol));
    try std.testing.expectError(error.InvalidPilotFamilyContract, runtime_loader.prepareRequest(drifted_entry_symbol));

    var drifted_exit_symbol = stable_trace_events;
    drifted_exit_symbol.exit_symbol = "zigux_runtime_trace_events_exit_drift";
    try std.testing.expect(!runtime_loader.keepsApprovedPilotFamilyContract(drifted_exit_symbol));
    try std.testing.expectError(error.InvalidPilotFamilyContract, runtime_loader.prepareRequest(drifted_exit_symbol));

    const unknown_family = makePlan(
        "runtime_spinlock",
        "kernel/locking/spinlock.c",
        "zigux_runtime_spinlock_init",
        "zigux_runtime_spinlock_exit",
        .kernel_heap,
        .{
            .handoff_stage = .selftest_complete,
            .init_runs = 1,
            .selftest_runs = 1,
            .exit_runs = 0,
        },
    );
    try std.testing.expect(!runtime_loader.keepsApprovedPilotFamilyContract(unknown_family));
    try std.testing.expectError(error.InvalidPilotFamilyContract, runtime_loader.prepareRequest(unknown_family));
}

test "phase 9 runtime loader allocator/init-flow replay rejects loader-not-required handoffs directly" {
    var no_loader_needed_plan = makePlan(
        "runtime_trace_events",
        "samples/trace_events/trace-events-sample.c",
        "zigux_runtime_trace_events_init",
        "zigux_runtime_trace_events_exit",
        .caller_provided,
        .{
            .handoff_stage = .selftest_complete,
            .init_runs = 1,
            .selftest_runs = 1,
            .exit_runs = 0,
        },
    );
    no_loader_needed_plan.requires_runtime_substrate = false;
    try std.testing.expectError(error.LoaderNotRequired, runtime_loader.prepareRequest(no_loader_needed_plan));
}

test "phase 9 runtime loader allocator/init-flow replay rejects selftest-hook evidence drift" {
    var missing_hook_after_selftest = makePlan("runtime_trace_events", "samples/trace_events/trace-events-sample.c", "zigux_runtime_trace_events_init", "zigux_runtime_trace_events_exit", .caller_provided, .{ .handoff_stage = .selftest_complete, .init_runs = 1, .selftest_runs = 1, .exit_runs = 0 });
    missing_hook_after_selftest.provides_selftest_hook = false;
    try std.testing.expect(!runtime_loader.keepsSelftestHookEvidenceConsistent(missing_hook_after_selftest));
    try std.testing.expectError(error.InvalidSelftestHookEvidence, runtime_loader.prepareRequest(missing_hook_after_selftest));

    var initialized_without_hook = makePlan("runtime_bitmap", "lib/test_bitmap.c", "zigux_runtime_bitmap_init", "zigux_runtime_bitmap_exit", .arena, .{ .handoff_stage = .initialized, .init_runs = 1, .selftest_runs = 0, .exit_runs = 0 });
    initialized_without_hook.provides_selftest_hook = false;
    try std.testing.expect(!runtime_loader.keepsSelftestHookEvidenceConsistent(initialized_without_hook));
    try std.testing.expectError(error.InvalidSelftestHookEvidence, runtime_loader.prepareRequest(initialized_without_hook));

    var selftest_runs_without_hook = makePlan("runtime_bitmap", "lib/test_bitmap.c", "zigux_runtime_bitmap_init", "zigux_runtime_bitmap_exit", .arena, .{ .handoff_stage = .initialized, .init_runs = 1, .selftest_runs = 1, .exit_runs = 0 });
    selftest_runs_without_hook.provides_selftest_hook = false;
    try std.testing.expect(!runtime_loader.keepsSelftestHookEvidenceConsistent(selftest_runs_without_hook));
    try std.testing.expectError(error.InvalidSelftestHookEvidence, runtime_loader.prepareRequest(selftest_runs_without_hook));
}

test "phase 9 runtime loader allocator/init-flow replay keeps prepared snapshots pinned when requestRuntimeLoad sees prepared-plan drift" {
    const stable_plan = makePlan(
        "runtime_trace_events",
        "samples/trace_events/trace-events-sample.c",
        "zigux_runtime_trace_events_init",
        "zigux_runtime_trace_events_exit",
        .caller_provided,
        .{
            .handoff_stage = .selftest_complete,
            .init_runs = 1,
            .selftest_runs = 1,
            .exit_runs = 0,
        },
    );

    var request = try runtime_loader.prepareRequest(stable_plan);
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(request, .prepared, stable_plan));

    request.plan.requires_runtime_substrate = false;
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try expectPreparedPlanDriftKeepsPreparedState(request, stable_plan);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(request, .prepared, request.plan));

    request.plan = stable_plan;
    request.plan.module_name = "runtime_trace_events_drift";
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try expectPreparedPlanDriftKeepsPreparedState(request, stable_plan);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(request, .prepared, request.plan));
    try std.testing.expectEqualStrings(stable_plan.module_name, request.prepared_plan.module_name);
    try std.testing.expectEqualStrings("runtime_trace_events_drift", request.plan.module_name);

    request.plan = stable_plan;
    request.plan.anchor = "samples/trace_events/trace-events-sample-drift.c";
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try expectPreparedPlanDriftKeepsPreparedState(request, stable_plan);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(request, .prepared, request.plan));

    request.plan = stable_plan;
    request.plan.entry_symbol = "zigux_runtime_trace_events_init_drift";
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try expectPreparedPlanDriftKeepsPreparedState(request, stable_plan);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(request, .prepared, request.plan));

    request.plan = stable_plan;
    request.plan.exit_symbol = "zigux_runtime_trace_events_exit_drift";
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try expectPreparedPlanDriftKeepsPreparedState(request, stable_plan);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(request, .prepared, request.plan));
    request.plan = stable_plan;

    request.plan.allocator_handoff = .arena;
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try expectPreparedPlanDriftKeepsPreparedState(request, stable_plan);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(request, .prepared, request.plan));
    try std.testing.expectEqual(runtime_loader.AllocatorHandoff.caller_provided, request.prepared_plan.allocator_handoff);
    try std.testing.expectEqual(runtime_loader.AllocatorHandoff.arena, request.plan.allocator_handoff);

    request.plan = stable_plan;
    request.plan.provides_selftest_hook = false;
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try expectPreparedPlanDriftKeepsPreparedState(request, stable_plan);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(request, .prepared, request.plan));

    request.plan = stable_plan;
    request.plan.init_flow.selftest_runs = 2;
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try expectPreparedPlanDriftKeepsPreparedState(request, stable_plan);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(request, .prepared, request.plan));
}

test "phase 9 runtime loader allocator/init-flow replay rejects stale loader state transitions" {
    const stable_plan = makePlan("runtime_atomic64", "lib/atomic64_test.c", "zigux_runtime_atomic64_init", "zigux_runtime_atomic64_exit", .caller_provided, .{ .handoff_stage = .selftest_complete, .init_runs = 1, .selftest_runs = 1, .exit_runs = 0 });
    var request = try runtime_loader.prepareRequest(stable_plan);
    try std.testing.expectError(error.InvalidLoaderState, request.releaseWithoutSubstrate());
    _ = try request.requestRuntimeLoad();
    try std.testing.expectError(error.InvalidLoaderState, request.requestRuntimeLoad());
    try request.releaseWithoutSubstrate();
    try std.testing.expectError(error.InvalidLoaderState, request.releaseWithoutSubstrate());
    const no_loader_needed = runtime_loader.LoadPlan{ .module_name = "runtime_trace_events", .anchor = "samples/trace_events/trace-events-sample.c", .entry_symbol = "zigux_runtime_trace_events_init", .exit_symbol = "zigux_runtime_trace_events_exit", .requires_runtime_substrate = false, .provides_selftest_hook = true, .allocator_handoff = .caller_provided, .init_flow = .{ .handoff_stage = .selftest_complete, .init_runs = 1, .selftest_runs = 1, .exit_runs = 0 } };
    try std.testing.expectError(error.LoaderNotRequired, runtime_loader.prepareRequest(no_loader_needed));
}

test "phase 9 runtime loader allocator/init-flow replay keeps the shared build route explicit" {
    const phase9_build = try readRepoFileAlloc(std.testing.allocator, "zigux/tests/phase9_build.zig", 96 * 1024);
    defer std.testing.allocator.free(phase9_build);
    try expectFileContains(phase9_build, ".root_source_file = b.path(\"runtime_loader_allocator_init_flow.zig\")");
    try expectFileContains(phase9_build, "runtime_loader_allocator_init_flow_module.addImport(\"runtime_loader\", runtime_loader_facade_module);");
    try expectFileContains(phase9_build, "runtime_loader_allocator_init_flow_module.addImport(\"runtime_loader_contract\", runtime_loader_contract_module);");
    try expectFileContains(phase9_build, ".name = \"phase9-runtime-loader-allocator-init-flow-tests\"");
    try expectFileContains(phase9_build, "const runtime_loader_shared_tests_step = b.step(");
    try expectFileContains(phase9_build, "\"phase9-runtime-loader-shared-tests\"");
    try expectFileContains(phase9_build, "runtime_loader_shared_tests_step.dependOn(&run_runtime_loader_contract_tests.step);");
    try expectFileContains(phase9_build, "runtime_loader_shared_tests_step.dependOn(&run_runtime_loader_facade_tests.step);");
    try expectFileContains(phase9_build, "runtime_loader_shared_tests_step.dependOn(&run_runtime_loader_allocator_init_flow_tests.step);");
    try expectFileContains(phase9_build, "test_step.dependOn(&run_runtime_loader_allocator_init_flow_tests.step);");
}

test "phase 9 runtime loader allocator/init-flow replay keeps exact current init and registration evidence explicit" {
    const atomic64_json = try readRepoFileAlloc(std.testing.allocator, "zigux/tests/runtime_atomic64_manifest.json", 32 * 1024);
    defer std.testing.allocator.free(atomic64_json);
    const bitmap_json = try readRepoFileAlloc(std.testing.allocator, "zigux/tests/runtime_bitmap_manifest.json", 32 * 1024);
    defer std.testing.allocator.free(bitmap_json);
    const trace_events_json = try readRepoFileAlloc(std.testing.allocator, "zigux/tests/runtime_trace_events_manifest.json", 32 * 1024);
    defer std.testing.allocator.free(trace_events_json);
    const kretprobe_json = try readRepoFileAlloc(std.testing.allocator, "zigux/tests/runtime_kretprobe_manifest.json", 32 * 1024);
    defer std.testing.allocator.free(kretprobe_json);

    const parse_options: std.json.ParseOptions = .{ .ignore_unknown_fields = true };
    const atomic64 = try std.json.parseFromSlice(BaseManifest, std.testing.allocator, atomic64_json, parse_options);
    defer atomic64.deinit();
    const bitmap = try std.json.parseFromSlice(BaseManifest, std.testing.allocator, bitmap_json, parse_options);
    defer bitmap.deinit();
    const trace_events = try std.json.parseFromSlice(TraceEventsManifest, std.testing.allocator, trace_events_json, parse_options);
    defer trace_events.deinit();
    const kretprobe = try std.json.parseFromSlice(KretprobeManifest, std.testing.allocator, kretprobe_json, parse_options);
    defer kretprobe.deinit();

    try std.testing.expectEqualStrings("Phase 9", atomic64.value.phase);
    try std.testing.expectEqualStrings("lib/atomic64_test.c", atomic64.value.anchor);
    try std.testing.expectEqualStrings("Phase 9", bitmap.value.phase);
    try std.testing.expectEqualStrings("lib/test_bitmap.c", bitmap.value.anchor);
    try std.testing.expectEqualStrings("Phase 9", trace_events.value.phase);
    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", trace_events.value.anchor);
    try std.testing.expectEqualStrings("Phase 9", kretprobe.value.phase);
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", kretprobe.value.anchor);
    try std.testing.expectEqual(@as(usize, 4), trace_events.value.delivery_evidence_catalog.len);
    try std.testing.expectEqual(@as(usize, 6), trace_events.value.ownership_map.len);

    const trace_events_survey_note = findDeliveryEvidence(trace_events.value.delivery_evidence_catalog, "trace-events-survey-note") orelse return error.MissingTraceEventsSurveyNote;
    try std.testing.expectEqualStrings("Documentation/zigux/phase9-runtime-trace-events-survey.md", trace_events_survey_note.path);
    const trace_events_module_slice = findDeliveryEvidence(trace_events.value.delivery_evidence_catalog, "trace-events-module-slice-note") orelse return error.MissingTraceEventsModuleSlice;
    try std.testing.expectEqualStrings("Documentation/zigux/phase9-runtime-trace-events-module-slice.md", trace_events_module_slice.path);
    const trace_events_survey_gate = findDeliveryEvidence(trace_events.value.delivery_evidence_catalog, "trace-events-survey-gate") orelse return error.MissingTraceEventsSurveyGate;
    try std.testing.expectEqualStrings("zigux/tests/runtime_trace_events_survey.zig", trace_events_survey_gate.path);
    const trace_events_build_gate = findDeliveryEvidence(trace_events.value.delivery_evidence_catalog, "trace-events-shared-build-gate") orelse return error.MissingTraceEventsBuildGate;
    try std.testing.expectEqualStrings("zigux/tests/phase9_build.zig", trace_events_build_gate.path);

    const trace_events_loader_owner = findOwnershipEntry(trace_events.value.ownership_map, "samples/zigux/runtime_trace_events_loader.zig") orelse return error.MissingTraceEventsLoaderOwnership;
    try std.testing.expectEqualStrings("loader_scaffold", trace_events_loader_owner.role);
    try std.testing.expectEqualStrings("P9-L10", trace_events_loader_owner.owner);
    try std.testing.expect(std.mem.indexOf(u8, trace_events_loader_owner.boundary, "release-without-substrate behavior") != null);
    const trace_events_build_owner = findOwnershipEntry(trace_events.value.ownership_map, "zigux/tests/phase9_build.zig") orelse return error.MissingTraceEventsBuildOwnership;
    try std.testing.expectEqualStrings("shared_build_bundle", trace_events_build_owner.role);
    try std.testing.expectEqualStrings("P9-L10", trace_events_build_owner.owner);
    try std.testing.expect(std.mem.indexOf(u8, trace_events_build_owner.boundary, "shared Phase 9 replay bundle only") != null);

    try expectGapStatusAndWhyNow(atomic64.value.gaps, "runtime-atomic64-loader-scaffold", "starter_landed", "entry and exit symbol names");
    try expectGapStatusAndWhyNow(atomic64.value.gaps, "runtime-atomic64-live-loader-binding", "blocked_on_runtime_substrate", "full runtime module lifecycle parity");
    try expectGapStatusAndWhyNow(bitmap.value.gaps, "runtime-bitmap-loader-scaffold", "starter_landed", "entry and exit symbol names");
    try expectGapStatusAndWhyNow(bitmap.value.gaps, "runtime-bitmap-live-loader-binding", "blocked_on_runtime_substrate", "lifecycle parity still depend on shared runtime substrate pieces");
    try expectGapStatusAndWhyNow(trace_events.value.gaps, "runtime-trace-events-loader-scaffold", "starter_landed", "tracepoint register and unregister APIs");
    try expectGapStatusAndWhyNow(trace_events.value.gaps, "runtime-trace-events-loader-scaffold", "starter_landed", "prepared and initialized-stage handoff snapshots");
    try expectGapStatusAndWhyNow(trace_events.value.gaps, "runtime-trace-events-substrate-handoff", "blocked_on_runtime_substrate", "tracepoint registration lifecycle");

    try std.testing.expect(kretprobe.value.lifecycle_boundary_summary.pre_execution_handoff_only);
    try std.testing.expect(kretprobe.value.lifecycle_boundary_summary.requires_idle_registration_snapshot);
    try std.testing.expect(kretprobe.value.lifecycle_boundary_summary.failed_exit_state_retained_until_drain);
    try std.testing.expect(kretprobe.value.lifecycle_boundary_summary.prepared_snapshot_owned_by_loader_request);
    try std.testing.expectEqual(@as(usize, 2), kretprobe.value.lifecycle_boundary_summary.metadata_only_registration_labels.len);
    try std.testing.expectEqualStrings("register_kretprobe", kretprobe.value.lifecycle_boundary_summary.metadata_only_registration_labels[0]);
    try std.testing.expectEqualStrings("unregister_kretprobe", kretprobe.value.lifecycle_boundary_summary.metadata_only_registration_labels[1]);
    try std.testing.expectEqualStrings("zigux/kernel/runtime_loader.zig", kretprobe.value.lifecycle_boundary_summary.shared_request_surface);
    try std.testing.expectEqualStrings("blocked_on_runtime_substrate", kretprobe.value.lifecycle_boundary_summary.live_registration_parity);
    try expectGapStatusAndWhyNow(kretprobe.value.gaps, "runtime-kretprobe-loader-plan", "starter_landed", "register_kretprobe and unregister_kretprobe lifecycle");
    try expectGapStatusAndWhyNow(kretprobe.value.gaps, "runtime-kretprobe-substrate-handoff", "blocked_on_runtime_substrate", "real register_kretprobe parity");

    try std.testing.expectEqual(@as(usize, 3), @typeInfo(runtime_loader.AllocatorHandoff).@"enum".fields.len);
    try std.testing.expectEqual(@as(usize, 2), @typeInfo(runtime_loader.HandoffStage).@"enum".fields.len);
    try std.testing.expectEqual(@as(usize, 3), @typeInfo(runtime_loader_contract.RequestState).@"enum".fields.len);
}
