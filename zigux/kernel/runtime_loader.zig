const std = @import("std");
const contract = @import("runtime_loader_contract.zig");

pub const AllocatorHandoff = contract.AllocatorHandoff;
pub const HandoffStage = contract.HandoffStage;
pub const RequestState = contract.RequestState;
pub const InitFlow = contract.InitFlow;
pub const LoadPlan = contract.LoadPlan;
pub const PreparedRequest = contract.PreparedRequest;

pub fn prepareRequest(plan: LoadPlan) !PreparedRequest {
    return contract.prepareRequest(plan);
}

pub fn keepsAllocatorInitFlowConsistent(
    plan: LoadPlan,
    allocator_handoff: AllocatorHandoff,
    init_flow: InitFlow,
) bool {
    return contract.keepsAllocatorInitFlowConsistent(plan, allocator_handoff, init_flow);
}

test "runtime loader facade keeps the shared loader contract reachable from the Phase 9 kernel surface" {
    const plan = LoadPlan{
        .module_name = "runtime_atomic64",
        .anchor = "lib/atomic64_test.c",
        .entry_symbol = "zigux_runtime_atomic64_init",
        .exit_symbol = "zigux_runtime_atomic64_exit",
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

    var request = try prepareRequest(plan);
    try std.testing.expectEqual(RequestState.prepared, request.state);

    const pending_plan = try request.requestRuntimeLoad();
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, request.state);
    try std.testing.expectEqualStrings("runtime_atomic64", pending_plan.module_name);
    try std.testing.expect(keepsAllocatorInitFlowConsistent(
        pending_plan,
        .caller_provided,
        .{
            .handoff_stage = .selftest_complete,
            .init_runs = 1,
            .selftest_runs = 1,
            .exit_runs = 0,
        },
    ));

    try request.releaseWithoutSubstrate();
    try std.testing.expectEqual(RequestState.released_without_substrate, request.state);
}
