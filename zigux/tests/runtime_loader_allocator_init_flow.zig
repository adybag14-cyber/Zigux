const std = @import("std");
const runtime_loader = @import("runtime_loader_contract");

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
        try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(
            pending_plan,
            plan.allocator_handoff,
            plan.init_flow,
        ));
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
    try std.testing.expectError(error.InvalidInitFlow, runtime_loader.prepareRequest(incomplete_plan));
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
