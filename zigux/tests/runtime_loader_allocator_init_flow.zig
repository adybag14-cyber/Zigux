const std = @import("std");
const runtime_loader = @import("runtime_loader_contract");

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

const LifecycleBoundarySummary = struct {
    pre_execution_handoff_only: bool,
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

test "phase 9 runtime loader allocator/init-flow replay rejects exited or incomplete handoffs" {
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
    const trace_events = try std.json.parseFromSlice(BaseManifest, std.testing.allocator, trace_events_json, parse_options);
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
        "runtime-trace-events-substrate-handoff",
        "blocked_on_runtime_substrate",
        "tracepoint registration lifecycle",
    );

    try std.testing.expect(kretprobe.value.lifecycle_boundary_summary.pre_execution_handoff_only);
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
}
