const std = @import("std");
const contract = @import("../kernel/runtime_loader_contract.zig");

const LoadPlan = contract.LoadPlan;
const RequestState = contract.RequestState;

test "phase 9 runtime loader release drift keeps waiting shared requests pinned until the prepared snapshot is restored" {
    const stable_plan = LoadPlan{
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

    var request = try contract.prepareRequest(stable_plan);
    const pending_plan = try request.requestRuntimeLoad();
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, request.state);
    try std.testing.expect(contract.keepsRequestStateAndPlanExplicit(
        request,
        .waiting_on_runtime_substrate,
        stable_plan,
    ));

    request.plan.allocator_handoff = .arena;
    try std.testing.expectError(error.PreparedPlanDrift, request.releaseWithoutSubstrate());
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, request.state);
    try std.testing.expect(!contract.keepsRequestStateAndPlanExplicit(
        request,
        .waiting_on_runtime_substrate,
        stable_plan,
    ));

    request.plan = stable_plan;
    request.plan.init_flow = .{
        .handoff_stage = .initialized,
        .init_runs = 1,
        .selftest_runs = 0,
        .exit_runs = 0,
    };
    try std.testing.expectError(error.PreparedPlanDrift, request.releaseWithoutSubstrate());
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, request.state);
    try std.testing.expect(!contract.keepsRequestStateAndPlanExplicit(
        request,
        .waiting_on_runtime_substrate,
        stable_plan,
    ));

    request.plan = stable_plan;
    try request.releaseWithoutSubstrate();
    try std.testing.expectEqual(RequestState.released_without_substrate, request.state);
    try std.testing.expect(contract.keepsRequestStateAndPlanExplicit(
        request,
        .released_without_substrate,
        pending_plan,
    ));
}
