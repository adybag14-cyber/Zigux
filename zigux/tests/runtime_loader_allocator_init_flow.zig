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
    metadata_only_registration_labels: []const []const u8,
    shared_request_surface: []const u8,
    live_registration_parity: []const u8,
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

fn expectFileContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 9 runtime loader allocator/init-flow replay covers all shipped runtime pilot handoffs" {
    const plans = [_]runtime_loader.LoadPlan{
        makePlan(
            "runtime_atomic64",
            "lib/atomic64_test.c",
            "zigux_runtime_atomic64_init",
            "zigux_runtime_atomic64_exit",
            .caller_provided,
            .{
                .handoff_stage = .selftest_complete,
                .init_runs = 1,
                .selftest_runs = 1,
                .exit_runs = 0,
            },
        ),
        makePlan(
            "runtime_bitmap",
            "lib/test_bitmap.c",
            "zigux_runtime_bitmap_init",
            "zigux_runtime_bitmap_exit",
            .arena,
            .{
                .handoff_stage = .initialized,
                .init_runs = 1,
                .selftest_runs = 0,
                .exit_runs = 0,
            },
        ),
        makePlan(
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
        ),
        makePlan(
            "runtime_kretprobe",
            "samples/kprobes/kretprobe_example.c",
            "zigux_runtime_kretprobe_init",
            "zigux_runtime_kretprobe_exit",
            .kernel_heap,
            .{
                .handoff_stage = .selftest_complete,
                .init_runs = 1,
                .selftest_runs = 1,
                .exit_runs = 0,
            },
        ),
    };

    for (plans) |plan| {
        var request = try runtime_loader.prepareRequest(plan);
        const pending_plan = try request.requestRuntimeLoad();
        try expectExactLoadPlanParity(plan, pending_plan);
        try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(plan));
        try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(
            pending_plan,
            plan.allocator_handoff,
            plan.init_flow,
        ));
        try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(pending_plan));
        try request.releaseWithoutSubstrate();
    }
}

test "phase 9 runtime loader allocator/init-flow replay keeps the smallest shared bitmap and kretprobe request shape explicit" {
    const expected_bitmap = makePlan(
        "runtime_bitmap",
        "lib/test_bitmap.c",
        "zigux_runtime_bitmap_init",
        "zigux_runtime_bitmap_exit",
        .arena,
        .{
            .handoff_stage = .initialized,
            .init_runs = 1,
            .selftest_runs = 0,
            .exit_runs = 0,
        },
    );

    var bitmap_request = try runtime_loader.prepareRequest(expected_bitmap);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        bitmap_request,
        .prepared,
        expected_bitmap,
    ));
    const bitmap_pending = try bitmap_request.requestRuntimeLoad();
    try expectExactLoadPlanParity(expected_bitmap, bitmap_pending);
    try expectInitializedSharedRequestShape(bitmap_pending);
    try std.testing.expectEqual(runtime_loader.AllocatorHandoff.arena, bitmap_pending.allocator_handoff);
    try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(
        bitmap_pending,
        .arena,
        expected_bitmap.init_flow,
    ));
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(bitmap_pending));
    try bitmap_request.releaseWithoutSubstrate();
    try std.testing.expectEqual(runtime_loader.RequestState.released_without_substrate, bitmap_request.state);

    const expected_kretprobe = makePlan(
        "runtime_kretprobe",
        "samples/kprobes/kretprobe_example.c",
        "zigux_runtime_kretprobe_init",
        "zigux_runtime_kretprobe_exit",
        .kernel_heap,
        .{
            .handoff_stage = .initialized,
            .init_runs = 1,
            .selftest_runs = 0,
            .exit_runs = 0,
        },
    );

    var kretprobe_request = try runtime_loader.prepareRequest(expected_kretprobe);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        kretprobe_request,
        .prepared,
        expected_kretprobe,
    ));
    const kretprobe_pending = try kretprobe_request.requestRuntimeLoad();
    try expectExactLoadPlanParity(expected_kretprobe, kretprobe_pending);
    try expectInitializedSharedRequestShape(kretprobe_pending);
    try std.testing.expectEqual(runtime_loader.AllocatorHandoff.kernel_heap, kretprobe_pending.allocator_handoff);
    try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(
        kretprobe_pending,
        .kernel_heap,
        expected_kretprobe.init_flow,
    ));
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

test "phase 9 runtime loader allocator/init-flow replay keeps bitmap and kretprobe selftest-complete request shape parity explicit" {
    const expected_bitmap = makePlan(
        "runtime_bitmap",
        "lib/test_bitmap.c",
        "zigux_runtime_bitmap_init",
        "zigux_runtime_bitmap_exit",
        .arena,
        .{
            .handoff_stage = .selftest_complete,
            .init_runs = 1,
            .selftest_runs = 1,
            .exit_runs = 0,
        },
    );

    var bitmap_request = try runtime_loader.prepareRequest(expected_bitmap);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        bitmap_request,
        .prepared,
        expected_bitmap,
    ));
    const bitmap_pending = try bitmap_request.requestRuntimeLoad();
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
        .{
            .handoff_stage = .selftest_complete,
            .init_runs = 1,
            .selftest_runs = 1,
            .exit_runs = 0,
        },
    );

    var kretprobe_request = try runtime_loader.prepareRequest(expected_kretprobe);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        kretprobe_request,
        .prepared,
        expected_kretprobe,
    ));
    const kretprobe_pending = try kretprobe_request.requestRuntimeLoad();
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
}

test "phase 9 runtime loader allocator/init-flow replay rejects exited, duplicate-init, or incomplete handoffs" {
    const exited_plan = makePlan(
        "runtime_bitmap",
        "lib/test_bitmap.c",
        "zigux_runtime_bitmap_init",
        "zigux_runtime_bitmap_exit",
        .arena,
        .{
            .handoff_stage = .selftest_complete,
            .init_runs = 1,
            .selftest_runs = 1,
            .exit_runs = 1,
        },
    );
    try std.testing.expectError(error.InvalidInitFlow, runtime_loader.prepareRequest(exited_plan));

    const duplicate_init_plan = makePlan(
        "runtime_trace_events",
        "samples/trace_events/trace-events-sample.c",
        "zigux_runtime_trace_events_init",
        "zigux_runtime_trace_events_exit",
        .caller_provided,
        .{
            .handoff_stage = .selftest_complete,
            .init_runs = 2,
            .selftest_runs = 1,
            .exit_runs = 0,
        },
    );
    try std.testing.expectError(error.InvalidInitFlow, runtime_loader.prepareRequest(duplicate_init_plan));

    const incomplete_plan = makePlan(
        "runtime_kretprobe",
        "samples/kprobes/kretprobe_example.c",
        "zigux_runtime_kretprobe_init",
        "zigux_runtime_kretprobe_exit",
        .kernel_heap,
        .{
            .handoff_stage = .selftest_complete,
            .init_runs = 1,
            .selftest_runs = 0,
            .exit_runs = 0,
        },
    );
    try std.testing.expectError(error.InvalidSelftestHookEvidence, runtime_loader.prepareRequest(incomplete_plan));
}

test "phase 9 runtime loader allocator/init-flow replay rejects selftest-hook evidence drift" {
    var missing_hook_after_selftest = makePlan(
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
    missing_hook_after_selftest.provides_selftest_hook = false;
    try std.testing.expect(!runtime_loader.keepsSelftestHookEvidenceConsistent(missing_hook_after_selftest));
    try std.testing.expectError(
        error.InvalidSelftestHookEvidence,
        runtime_loader.prepareRequest(missing_hook_after_selftest),
    );

    var selftest_runs_without_hook = makePlan(
        "runtime_bitmap",
        "lib/test_bitmap.c",
        "zigux_runtime_bitmap_init",
        "zigux_runtime_bitmap_exit",
        .arena,
        .{
            .handoff_stage = .initialized,
            .init_runs = 1,
            .selftest_runs = 1,
            .exit_runs = 0,
        },
    );
    selftest_runs_without_hook.provides_selftest_hook = false;
    try std.testing.expect(!runtime_loader.keepsSelftestHookEvidenceConsistent(selftest_runs_without_hook));
    try std.testing.expectError(
        error.InvalidSelftestHookEvidence,
        runtime_loader.prepareRequest(selftest_runs_without_hook),
    );
}

test "phase 9 runtime loader allocator/init-flow replay rejects stale loader state transitions" {
    const stable_plan = makePlan(
        "runtime_atomic64",
        "lib/atomic64_test.c",
        "zigux_runtime_atomic64_init",
        "zigux_runtime_atomic64_exit",
        .caller_provided,
        .{
            .handoff_stage = .selftest_complete,
            .init_runs = 1,
            .selftest_runs = 1,
            .exit_runs = 0,
        },
    );

    var request = try runtime_loader.prepareRequest(stable_plan);
    try std.testing.expectError(error.InvalidLoaderState, request.releaseWithoutSubstrate());

    _ = try request.requestRuntimeLoad();
    try std.testing.expectError(error.InvalidLoaderState, request.requestRuntimeLoad());

    try request.releaseWithoutSubstrate();
    try std.testing.expectError(error.InvalidLoaderState, request.releaseWithoutSubstrate());

    const no_loader_needed = runtime_loader.LoadPlan{
        .module_name = "runtime_trace_events",
        .anchor = "samples/trace_events/trace-events-sample.c",
        .entry_symbol = "zigux_runtime_trace_events_init",
        .exit_symbol = "zigux_runtime_trace_events_exit",
        .requires_runtime_substrate = false,
        .provides_selftest_hook = true,
        .allocator_handoff = .caller_provided,
        .init_flow = .{
            .handoff_stage = .selftest_complete,
            .init_runs = 1,
            .selftest_runs = 1,
            .exit_runs = 0,
        },
    };
    try std.testing.expectError(error.LoaderNotRequired, runtime_loader.prepareRequest(no_loader_needed));
}

test "phase 9 runtime loader allocator/init-flow replay keeps the shared build route explicit" {
    const phase9_build = try readRepoFileAlloc(std.testing.allocator, "zigux/tests/phase9_build.zig", 96 * 1024);
    defer std.testing.allocator.free(phase9_build);

    try expectFileContains(
        phase9_build,
        ".root_source_file = b.path(\"runtime_loader_allocator_init_flow.zig\")",
    );
    try expectFileContains(
        phase9_build,
        "runtime_loader_allocator_init_flow_module.addImport(\"runtime_loader\", runtime_loader_facade_module);",
    );
    try expectFileContains(
        phase9_build,
        "runtime_loader_allocator_init_flow_module.addImport(\"runtime_loader_contract\", runtime_loader_contract_module);",
    );
    try expectFileContains(
        phase9_build,
        ".name = \"phase9-runtime-loader-allocator-init-flow-tests\"",
    );
    try expectFileContains(
        phase9_build,
        "const runtime_loader_shared_tests_step = b.step(",
    );
    try expectFileContains(
        phase9_build,
        "\"phase9-runtime-loader-shared-tests\"",
    );
    try expectFileContains(
        phase9_build,
        "runtime_loader_shared_tests_step.dependOn(&run_runtime_loader_contract_tests.step);",
    );
    try expectFileContains(
        phase9_build,
        "runtime_loader_shared_tests_step.dependOn(&run_runtime_loader_facade_tests.step);",
    );
    try expectFileContains(
        phase9_build,
        "runtime_loader_shared_tests_step.dependOn(&run_runtime_loader_allocator_init_flow_tests.step);",
    );
    try expectFileContains(
        phase9_build,
        "test_step.dependOn(&run_runtime_loader_allocator_init_flow_tests.step);",
    );
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

    const trace_events_survey_note = findDeliveryEvidence(
        trace_events.value.delivery_evidence_catalog,
        "trace-events-survey-note",
    ) orelse return error.MissingTraceEventsSurveyNote;
    try std.testing.expectEqualStrings(
        "Documentation/zigux/phase9-runtime-trace-events-survey.md",
        trace_events_survey_note.path,
    );
    const trace_events_module_slice = findDeliveryEvidence(
        trace_events.value.delivery_evidence_catalog,
        "trace-events-module-slice-note",
    ) orelse return error.MissingTraceEventsModuleSlice;
    try std.testing.expectEqualStrings(
        "Documentation/zigux/phase9-runtime-trace-events-module-slice.md",
        trace_events_module_slice.path,
    );
    const trace_events_survey_gate = findDeliveryEvidence(
        trace_events.value.delivery_evidence_catalog,
        "trace-events-survey-gate",
    ) orelse return error.MissingTraceEventsSurveyGate;
    try std.testing.expectEqualStrings(
        "zigux/tests/runtime_trace_events_survey.zig",
        trace_events_survey_gate.path,
    );
    const trace_events_build_gate = findDeliveryEvidence(
        trace_events.value.delivery_evidence_catalog,
        "trace-events-shared-build-gate",
    ) orelse return error.MissingTraceEventsBuildGate;
    try std.testing.expectEqualStrings(
        "zigux/tests/phase9_build.zig",
        trace_events_build_gate.path,
    );

    const trace_events_loader_owner = findOwnershipEntry(
        trace_events.value.ownership_map,
        "samples/zigux/runtime_trace_events_loader.zig",
    ) orelse return error.MissingTraceEventsLoaderOwnership;
    try std.testing.expectEqualStrings("loader_scaffold", trace_events_loader_owner.role);
    try std.testing.expectEqualStrings("P9-L12", trace_events_loader_owner.owner);
    try std.testing.expect(std.mem.indexOf(
        u8,
        trace_events_loader_owner.boundary,
        "release-without-substrate behavior",
    ) != null);
    const trace_events_build_owner = findOwnershipEntry(
        trace_events.value.ownership_map,
        "zigux/tests/phase9_build.zig",
    ) orelse return error.MissingTraceEventsBuildOwnership;
    try std.testing.expectEqualStrings("shared_build_bundle", trace_events_build_owner.role);
    try std.testing.expectEqualStrings("P9-L12", trace_events_build_owner.owner);
    try std.testing.expect(std.mem.indexOf(
        u8,
        trace_events_build_owner.boundary,
        "shared Phase 9 replay bundle only",
    ) != null);

    try expectGapStatusAndWhyNow(
        atomic64.value.gaps,
        "runtime-atomic64-loader-scaffold",
        "starter_landed",
        "entry and exit symbol names",
    );
    try expectGapStatusAndWhyNow(
        atomic64.value.gaps,
        "runtime-atomic64-live-loader-binding",
        "blocked_on_runtime_substrate",
        "full runtime module lifecycle parity",
    );

    try expectGapStatusAndWhyNow(
        bitmap.value.gaps,
        "runtime-bitmap-loader-scaffold",
        "starter_landed",
        "entry and exit symbol names",
    );
    try expectGapStatusAndWhyNow(
        bitmap.value.gaps,
        "runtime-bitmap-live-loader-binding",
        "blocked_on_runtime_substrate",
        "lifecycle parity still depend on shared runtime substrate pieces",
    );

    try expectGapStatusAndWhyNow(
        trace_events.value.gaps,
        "runtime-trace-events-loader-scaffold",
        "starter_landed",
        "tracepoint register and unregister APIs",
    );
    try expectGapStatusAndWhyNow(
        trace_events.value.gaps,
        "runtime-trace-events-loader-scaffold",
        "starter_landed",
        "prepared and initialized-stage handoff snapshots",
    );
    try expectGapStatusAndWhyNow(
        trace_events.value.gaps,
        "runtime-trace-events-substrate-handoff",
        "blocked_on_runtime_substrate",
        "tracepoint registration lifecycle",
    );

    try std.testing.expect(kretprobe.value.lifecycle_boundary_summary.pre_execution_handoff_only);
    try std.testing.expect(kretprobe.value.lifecycle_boundary_summary.requires_idle_registration_snapshot);
    try std.testing.expectEqual(@as(usize, 2), kretprobe.value.lifecycle_boundary_summary.metadata_only_registration_labels.len);
    try std.testing.expectEqualStrings(
        "register_kretprobe",
        kretprobe.value.lifecycle_boundary_summary.metadata_only_registration_labels[0],
    );
    try std.testing.expectEqualStrings(
        "unregister_kretprobe",
        kretprobe.value.lifecycle_boundary_summary.metadata_only_registration_labels[1],
    );
    try std.testing.expectEqualStrings(
        "zigux/kernel/runtime_loader.zig",
        kretprobe.value.lifecycle_boundary_summary.shared_request_surface,
    );
    try std.testing.expectEqualStrings(
        "blocked_on_runtime_substrate",
        kretprobe.value.lifecycle_boundary_summary.live_registration_parity,
    );
    try expectGapStatusAndWhyNow(
        kretprobe.value.gaps,
        "runtime-kretprobe-loader-plan",
        "starter_landed",
        "register_kretprobe and unregister_kretprobe lifecycle",
    );
    try expectGapStatusAndWhyNow(
        kretprobe.value.gaps,
        "runtime-kretprobe-substrate-handoff",
        "blocked_on_runtime_substrate",
        "real register_kretprobe parity",
    );

    try std.testing.expectEqual(@as(usize, 3), @typeInfo(runtime_loader_contract.RequestState).@"enum".fields.len);
}
