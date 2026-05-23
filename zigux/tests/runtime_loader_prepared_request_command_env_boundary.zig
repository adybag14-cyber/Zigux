const std = @import("std");
const runtime_loader = @import("runtime_loader");

fn makeTraceEventsPlan() runtime_loader.LoadPlan {
    return .{
        .module_name = "runtime_trace_events",
        .anchor = "samples/trace_events/trace-events-sample.c",
        .entry_symbol = "zigux_runtime_trace_events_init",
        .exit_symbol = "zigux_runtime_trace_events_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .allocator_handoff = .caller_provided,
        .init_flow = .{
            .handoff_stage = .selftest_complete,
            .init_runs = 1,
            .selftest_runs = 1,
            .exit_runs = 0,
        },
    };
}

test "PreparedRequest keeps Phase 8 command and environment control fields out of the shared request boundary" {
    const blocked_control_fields = [_][]const u8{
        "activation_env",
        "argv_policy",
        "command_env",
        "command_name",
        "exec_name",
        "exec_path",
        "exec_path_env",
    };

    inline for (blocked_control_fields) |field| {
        try std.testing.expect(!@hasField(runtime_loader.PreparedRequest, field));
    }
}

test "PreparedRequest preserves the bounded shared request surface across the staged handoff" {
    const stable = makeTraceEventsPlan();
    var request = try runtime_loader.prepareRequest(stable);

    try std.testing.expect(
        runtime_loader.keepsRequestStateAndPlanExplicit(request, .prepared, stable),
    );

    const pending = try request.requestRuntimeLoad();
    try std.testing.expect(
        runtime_loader.keepsRequestStateAndPlanExplicit(
            request,
            .waiting_on_runtime_substrate,
            pending,
        ),
    );

    try request.releaseWithoutSubstrate();
    try std.testing.expect(
        runtime_loader.keepsRequestStateAndPlanExplicit(
            request,
            .released_without_substrate,
            pending,
        ),
    );
}
