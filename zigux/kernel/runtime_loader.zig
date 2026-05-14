const std = @import("std");
const contract = @import("runtime_loader_contract.zig");

pub const AllocatorHandoff = contract.AllocatorHandoff;
pub const HandoffStage = contract.HandoffStage;
pub const InitFlow = contract.InitFlow;
pub const LoadPlan = contract.LoadPlan;
pub const RequestState = contract.RequestState;

pub const PreparedRequest = struct {
    plan: LoadPlan,
    prepared_plan: LoadPlan,
    state: RequestState,

    pub fn requestRuntimeLoad(self: *PreparedRequest) !LoadPlan {
        if (self.state != .prepared) return error.InvalidLoaderState;
        if (!keepsLoadPlanExplicit(self.plan, self.prepared_plan)) {
            return error.PreparedPlanDrift;
        }

        _ = try prepareRequest(self.plan);
        self.state = .waiting_on_runtime_substrate;
        return self.plan;
    }

    pub fn releaseWithoutSubstrate(self: *PreparedRequest) !void {
        if (self.state != .waiting_on_runtime_substrate) return error.InvalidLoaderState;
        if (!keepsLoadPlanExplicit(self.plan, self.prepared_plan)) {
            return error.PreparedPlanDrift;
        }
        self.state = .released_without_substrate;
    }
};

const ApprovedPilotFamily = struct {
    module_name: []const u8,
    anchor: []const u8,
    entry_symbol: []const u8,
    exit_symbol: []const u8,
};

const approved_pilot_families = [_]ApprovedPilotFamily{
    .{
        .module_name = "runtime_atomic64",
        .anchor = "lib/atomic64_test.c",
        .entry_symbol = "zigux_runtime_atomic64_init",
        .exit_symbol = "zigux_runtime_atomic64_exit",
    },
    .{
        .module_name = "runtime_bitmap",
        .anchor = "lib/test_bitmap.c",
        .entry_symbol = "zigux_runtime_bitmap_init",
        .exit_symbol = "zigux_runtime_bitmap_exit",
    },
    .{
        .module_name = "runtime_trace_events",
        .anchor = "samples/trace_events/trace-events-sample.c",
        .entry_symbol = "zigux_runtime_trace_events_init",
        .exit_symbol = "zigux_runtime_trace_events_exit",
    },
    .{
        .module_name = "runtime_kretprobe",
        .anchor = "samples/kprobes/kretprobe_example.c",
        .entry_symbol = "zigux_runtime_kretprobe_init",
        .exit_symbol = "zigux_runtime_kretprobe_exit",
    },
};

pub fn keepsLoadPlanExplicit(actual: LoadPlan, expected: LoadPlan) bool {
    return contract.keepsLoadPlanExplicit(actual, expected);
}

pub fn keepsApprovedPilotFamilyContract(plan: LoadPlan) bool {
    for (approved_pilot_families) |family| {
        if (std.mem.eql(u8, plan.module_name, family.module_name) and
            std.mem.eql(u8, plan.anchor, family.anchor) and
            std.mem.eql(u8, plan.entry_symbol, family.entry_symbol) and
            std.mem.eql(u8, plan.exit_symbol, family.exit_symbol))
        {
            return true;
        }
    }
    return false;
}

pub fn keepsSelftestHookEvidenceConsistent(plan: LoadPlan) bool {
    if (!plan.provides_selftest_hook) return false;
    return switch (plan.init_flow.handoff_stage) {
        .initialized => plan.init_flow.selftest_runs == 0,
        .selftest_complete => plan.init_flow.selftest_runs == 1,
    };
}

pub fn keepsAllocatorInitFlowConsistent(
    plan: LoadPlan,
    allocator_handoff: AllocatorHandoff,
    init_flow: InitFlow,
) bool {
    return plan.allocator_handoff == allocator_handoff and
        plan.init_flow.handoff_stage == init_flow.handoff_stage and
        plan.init_flow.init_runs == init_flow.init_runs and
        plan.init_flow.selftest_runs == init_flow.selftest_runs and
        plan.init_flow.exit_runs == init_flow.exit_runs;
}

pub fn keepsRequestStateAndPlanExplicit(
    request: PreparedRequest,
    state: RequestState,
    plan: LoadPlan,
) bool {
    return request.state == state and keepsLoadPlanExplicit(request.plan, plan);
}

pub fn prepareRequest(plan: LoadPlan) !PreparedRequest {
    if (!plan.requires_runtime_substrate) return error.LoaderNotRequired;
    if (!keepsApprovedPilotFamilyContract(plan)) return error.InvalidPilotFamilyContract;
    if (!plan.init_flow.readyForRuntimeLoad()) return error.InvalidInitFlow;
    if (!keepsSelftestHookEvidenceConsistent(plan)) return error.InvalidSelftestHookEvidence;

    return .{
        .plan = plan,
        .prepared_plan = plan,
        .state = .prepared,
    };
}

test "prepareRequest enforces the bounded runtime loader contract" {
    const stable = LoadPlan{
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

    var request = try prepareRequest(stable);
    try std.testing.expectEqual(RequestState.prepared, request.state);
    try std.testing.expect(keepsRequestStateAndPlanExplicit(request, .prepared, stable));
    const pending = try request.requestRuntimeLoad();
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, request.state);
    try std.testing.expect(keepsRequestStateAndPlanExplicit(request, .waiting_on_runtime_substrate, pending));
    try request.releaseWithoutSubstrate();
    try std.testing.expectEqual(RequestState.released_without_substrate, request.state);
    try std.testing.expect(keepsRequestStateAndPlanExplicit(request, .released_without_substrate, pending));
}

test "prepareRequest rejects loader-not-required, pilot-family drift, init-flow drift, duplicate-selftest drift, and selftest drift" {
    var plan = LoadPlan{
        .module_name = "runtime_bitmap",
        .anchor = "lib/test_bitmap.c",
        .entry_symbol = "zigux_runtime_bitmap_init",
        .exit_symbol = "zigux_runtime_bitmap_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .allocator_handoff = .arena,
        .init_flow = .{
            .handoff_stage = .initialized,
            .init_runs = 1,
            .selftest_runs = 0,
            .exit_runs = 0,
        },
    };

    plan.requires_runtime_substrate = false;
    try std.testing.expectError(error.LoaderNotRequired, prepareRequest(plan));
    plan.requires_runtime_substrate = true;

    plan.module_name = "runtime_bitmap_drift";
    try std.testing.expectError(error.InvalidPilotFamilyContract, prepareRequest(plan));
    plan.module_name = "runtime_bitmap";

    plan.init_flow.selftest_runs = 1;
    try std.testing.expectError(error.InvalidInitFlow, prepareRequest(plan));
    plan.init_flow.selftest_runs = 0;

    plan.init_flow.handoff_stage = .selftest_complete;
    plan.init_flow.selftest_runs = 2;
    try std.testing.expectError(error.InvalidInitFlow, prepareRequest(plan));
    plan.init_flow.handoff_stage = .initialized;
    plan.init_flow.selftest_runs = 0;

    plan.provides_selftest_hook = false;
    try std.testing.expectError(error.InvalidSelftestHookEvidence, prepareRequest(plan));
}

test "PreparedRequest.requestRuntimeLoad preserves the prepared snapshot on drift" {
    const stable = LoadPlan{
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

    var request = try prepareRequest(stable);
    request.plan.module_name = "runtime_atomic64_drift";
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try std.testing.expectEqual(RequestState.prepared, request.state);
    try std.testing.expect(keepsLoadPlanExplicit(request.prepared_plan, stable));
    try std.testing.expect(!keepsLoadPlanExplicit(request.plan, stable));
}

test "PreparedRequest.releaseWithoutSubstrate preserves the pending snapshot on drift" {
    const stable = LoadPlan{
        .module_name = "runtime_bitmap",
        .anchor = "lib/test_bitmap.c",
        .entry_symbol = "zigux_runtime_bitmap_init",
        .exit_symbol = "zigux_runtime_bitmap_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .allocator_handoff = .arena,
        .init_flow = .{
            .handoff_stage = .initialized,
            .init_runs = 1,
            .selftest_runs = 0,
            .exit_runs = 0,
        },
    };

    var request = try prepareRequest(stable);
    const pending = try request.requestRuntimeLoad();
    request.plan.exit_symbol = "zigux_runtime_bitmap_exit_drift";
    try std.testing.expectError(error.PreparedPlanDrift, request.releaseWithoutSubstrate());
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, request.state);
    try std.testing.expect(keepsLoadPlanExplicit(request.prepared_plan, stable));
    try std.testing.expect(keepsLoadPlanExplicit(pending, stable));
    try std.testing.expect(!keepsLoadPlanExplicit(request.plan, stable));

    request.plan = stable;
    try request.releaseWithoutSubstrate();
    try std.testing.expectEqual(RequestState.released_without_substrate, request.state);
    try std.testing.expect(keepsRequestStateAndPlanExplicit(request, .released_without_substrate, stable));
}
