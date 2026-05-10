const std = @import("std");

pub const AllocatorHandoff = enum {
    caller_provided,
    arena,
    kernel_heap,
};

pub const HandoffStage = enum(u8) {
    initialized,
    selftest_complete,
};

pub const RequestState = enum(u8) {
    prepared,
    waiting_on_runtime_substrate,
    released_without_substrate,
};

pub const InitFlow = struct {
    handoff_stage: HandoffStage,
    init_runs: usize,
    selftest_runs: usize,
    exit_runs: usize,

    pub fn readyForRuntimeLoad(self: InitFlow) bool {
        if (self.init_runs != 1 or self.exit_runs != 0) return false;

        return switch (self.handoff_stage) {
            .initialized => self.selftest_runs == 0,
            .selftest_complete => self.selftest_runs == 1,
        };
    }
};

pub const LoadPlan = struct {
    module_name: []const u8,
    anchor: []const u8,
    entry_symbol: []const u8,
    exit_symbol: []const u8,
    requires_runtime_substrate: bool,
    provides_selftest_hook: bool,
    allocator_handoff: AllocatorHandoff,
    init_flow: InitFlow,
};

pub fn keepsLoadPlanExplicit(plan: LoadPlan, expected_plan: LoadPlan) bool {
    return std.mem.eql(u8, plan.module_name, expected_plan.module_name) and
        std.mem.eql(u8, plan.anchor, expected_plan.anchor) and
        std.mem.eql(u8, plan.entry_symbol, expected_plan.entry_symbol) and
        std.mem.eql(u8, plan.exit_symbol, expected_plan.exit_symbol) and
        plan.requires_runtime_substrate == expected_plan.requires_runtime_substrate and
        plan.provides_selftest_hook == expected_plan.provides_selftest_hook and
        keepsAllocatorInitFlowConsistent(
            plan,
            expected_plan.allocator_handoff,
            expected_plan.init_flow,
        );
}

fn matchesApprovedPilotFamily(
    plan: LoadPlan,
    module_name: []const u8,
    anchor: []const u8,
    entry_symbol: []const u8,
    exit_symbol: []const u8,
) bool {
    return std.mem.eql(u8, plan.module_name, module_name) and
        std.mem.eql(u8, plan.anchor, anchor) and
        std.mem.eql(u8, plan.entry_symbol, entry_symbol) and
        std.mem.eql(u8, plan.exit_symbol, exit_symbol);
}

pub fn keepsApprovedPilotFamilyContract(plan: LoadPlan) bool {
    return matchesApprovedPilotFamily(
        plan,
        "runtime_atomic64",
        "lib/atomic64_test.c",
        "zigux_runtime_atomic64_init",
        "zigux_runtime_atomic64_exit",
    ) or matchesApprovedPilotFamily(
        plan,
        "runtime_bitmap",
        "lib/test_bitmap.c",
        "zigux_runtime_bitmap_init",
        "zigux_runtime_bitmap_exit",
    ) or matchesApprovedPilotFamily(
        plan,
        "runtime_trace_events",
        "samples/trace_events/trace-events-sample.c",
        "zigux_runtime_trace_events_init",
        "zigux_runtime_trace_events_exit",
    ) or matchesApprovedPilotFamily(
        plan,
        "runtime_kretprobe",
        "samples/kprobes/kretprobe_example.c",
        "zigux_runtime_kretprobe_init",
        "zigux_runtime_kretprobe_exit",
    );
}

fn validatePreparedPlan(plan: LoadPlan) !void {
    if (!plan.requires_runtime_substrate) return error.LoaderNotRequired;
    if (!keepsApprovedPilotFamilyContract(plan)) return error.InvalidPilotFamilyContract;
    if (!keepsSelftestHookEvidenceConsistent(plan)) return error.InvalidSelftestHookEvidence;
    if (!plan.init_flow.readyForRuntimeLoad()) return error.InvalidInitFlow;
}

pub const PreparedRequest = struct {
    state: RequestState = .prepared,
    plan: LoadPlan,
    prepared_plan: LoadPlan,

    pub fn requestRuntimeLoad(self: *PreparedRequest) !LoadPlan {
        if (self.state != .prepared) return error.InvalidLoaderState;
        if (!keepsLoadPlanExplicit(self.plan, self.prepared_plan)) {
            return error.PreparedPlanDrift;
        }
        try validatePreparedPlan(self.plan);

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

pub fn prepareRequest(plan: LoadPlan) !PreparedRequest {
    try validatePreparedPlan(plan);

    return .{ .plan = plan, .prepared_plan = plan };
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
    expected_state: RequestState,
    expected_plan: LoadPlan,
) bool {
    return request.state == expected_state and
        keepsLoadPlanExplicit(request.plan, expected_plan) and
        keepsLoadPlanExplicit(request.prepared_plan, expected_plan);
}

pub fn keepsSelftestHookEvidenceConsistent(plan: LoadPlan) bool {
    if (!plan.provides_selftest_hook) return false;

    return switch (plan.init_flow.handoff_stage) {
        .initialized => true,
        .selftest_complete => plan.init_flow.selftest_runs > 0,
    };
}

test "shared runtime loader contract keeps the shipped init-flow acceptance matrix explicit" {
    try std.testing.expect((InitFlow{
        .handoff_stage = .initialized,
        .init_runs = 1,
        .selftest_runs = 0,
        .exit_runs = 0,
    }).readyForRuntimeLoad());
    try std.testing.expect((InitFlow{
        .handoff_stage = .selftest_complete,
        .init_runs = 1,
        .selftest_runs = 1,
        .exit_runs = 0,
    }).readyForRuntimeLoad());

    try std.testing.expect(!(InitFlow{
        .handoff_stage = .initialized,
        .init_runs = 1,
        .selftest_runs = 1,
        .exit_runs = 0,
    }).readyForRuntimeLoad());
    try std.testing.expect(!(InitFlow{
        .handoff_stage = .selftest_complete,
        .init_runs = 1,
        .selftest_runs = 0,
        .exit_runs = 0,
    }).readyForRuntimeLoad());
    try std.testing.expect(!(InitFlow{
        .handoff_stage = .selftest_complete,
        .init_runs = 1,
        .selftest_runs = 2,
        .exit_runs = 0,
    }).readyForRuntimeLoad());
    try std.testing.expect(!(InitFlow{
        .handoff_stage = .initialized,
        .init_runs = 0,
        .selftest_runs = 0,
        .exit_runs = 0,
    }).readyForRuntimeLoad());
    try std.testing.expect(!(InitFlow{
        .handoff_stage = .selftest_complete,
        .init_runs = 1,
        .selftest_runs = 1,
        .exit_runs = 1,
    }).readyForRuntimeLoad());
}

test "shared runtime loader contract keeps allocator, init flow, approved pilot families, and selftest-hook evidence explicit across handoff variants" {
    const cases = [_]LoadPlan{
        .{
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
        },
        .{
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
        },
        .{
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
        },
        .{
            .module_name = "runtime_kretprobe",
            .anchor = "samples/kprobes/kretprobe_example.c",
            .entry_symbol = "zigux_runtime_kretprobe_init",
            .exit_symbol = "zigux_runtime_kretprobe_exit",
            .requires_runtime_substrate = true,
            .provides_selftest_hook = true,
            .allocator_handoff = .kernel_heap,
            .init_flow = .{
                .handoff_stage = .selftest_complete,
                .init_runs = 1,
                .selftest_runs = 1,
                .exit_runs = 0,
            },
        },
    };

    for (cases) |plan| {
        var request = try prepareRequest(plan);
        try std.testing.expectEqual(RequestState.prepared, request.state);
        try std.testing.expect(keepsApprovedPilotFamilyContract(plan));
        try std.testing.expect(keepsRequestStateAndPlanExplicit(request, .prepared, plan));
        try std.testing.expect(keepsAllocatorInitFlowConsistent(
            plan,
            plan.allocator_handoff,
            plan.init_flow,
        ));
        try std.testing.expect(keepsSelftestHookEvidenceConsistent(plan));

        const pending_plan = try request.requestRuntimeLoad();
        try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, request.state);
        try std.testing.expect(keepsRequestStateAndPlanExplicit(
            request,
            .waiting_on_runtime_substrate,
            plan,
        ));
        try std.testing.expectEqualStrings(plan.module_name, pending_plan.module_name);
        try std.testing.expectEqual(plan.allocator_handoff, pending_plan.allocator_handoff);
        try std.testing.expectEqual(plan.init_flow.handoff_stage, pending_plan.init_flow.handoff_stage);

        try request.releaseWithoutSubstrate();
        try std.testing.expectEqual(RequestState.released_without_substrate, request.state);
        try std.testing.expect(keepsRequestStateAndPlanExplicit(
            request,
            .released_without_substrate,
            plan,
        ));
    }
}

test "shared runtime loader contract rejects impossible, stale, unknown-family, or selftest-hook-inconsistent handoff flows" {
    const missing_init = LoadPlan{
        .module_name = "runtime_atomic64",
        .anchor = "lib/atomic64_test.c",
        .entry_symbol = "zigux_runtime_atomic64_init",
        .exit_symbol = "zigux_runtime_atomic64_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .allocator_handoff = .caller_provided,
        .init_flow = .{
            .handoff_stage = .initialized,
            .init_runs = 0,
            .selftest_runs = 0,
            .exit_runs = 0,
        },
    };
    try std.testing.expectError(error.InvalidInitFlow, prepareRequest(missing_init));

    const duplicate_init = LoadPlan{
        .module_name = "runtime_trace_events",
        .anchor = "samples/trace_events/trace-events-sample.c",
        .entry_symbol = "zigux_runtime_trace_events_init",
        .exit_symbol = "zigux_runtime_trace_events_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .allocator_handoff = .caller_provided,
        .init_flow = .{
            .handoff_stage = .selftest_complete,
            .init_runs = 2,
            .selftest_runs = 1,
            .exit_runs = 0,
        },
    };
    try std.testing.expectError(error.InvalidInitFlow, prepareRequest(duplicate_init));

    const duplicate_selftest = LoadPlan{
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
            .selftest_runs = 2,
            .exit_runs = 0,
        },
    };
    try std.testing.expectError(error.InvalidInitFlow, prepareRequest(duplicate_selftest));

    const initialized_with_premature_selftest = LoadPlan{
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
            .selftest_runs = 1,
            .exit_runs = 0,
        },
    };
    try std.testing.expectError(error.InvalidInitFlow, prepareRequest(initialized_with_premature_selftest));

    const exited_plan = LoadPlan{
        .module_name = "runtime_bitmap",
        .anchor = "lib/test_bitmap.c",
        .entry_symbol = "zigux_runtime_bitmap_init",
        .exit_symbol = "zigux_runtime_bitmap_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .allocator_handoff = .arena,
        .init_flow = .{
            .handoff_stage = .selftest_complete,
            .init_runs = 1,
            .selftest_runs = 1,
            .exit_runs = 1,
        },
    };
    try std.testing.expectError(error.InvalidInitFlow, prepareRequest(exited_plan));

    const mismatched_module_name = LoadPlan{
        .module_name = "runtime_atomic64_drift",
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
    try std.testing.expect(!keepsApprovedPilotFamilyContract(mismatched_module_name));
    try std.testing.expectError(error.InvalidPilotFamilyContract, prepareRequest(mismatched_module_name));

    const mismatched_anchor = LoadPlan{
        .module_name = "runtime_atomic64",
        .anchor = "lib/test_bitmap.c",
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
    try std.testing.expect(!keepsApprovedPilotFamilyContract(mismatched_anchor));
    try std.testing.expectError(error.InvalidPilotFamilyContract, prepareRequest(mismatched_anchor));

    const mismatched_entry_symbol = LoadPlan{
        .module_name = "runtime_trace_events",
        .anchor = "samples/trace_events/trace-events-sample.c",
        .entry_symbol = "zigux_runtime_trace_events_init_drift",
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
    try std.testing.expect(!keepsApprovedPilotFamilyContract(mismatched_entry_symbol));
    try std.testing.expectError(error.InvalidPilotFamilyContract, prepareRequest(mismatched_entry_symbol));

    const mismatched_exit_symbol = LoadPlan{
        .module_name = "runtime_trace_events",
        .anchor = "samples/trace_events/trace-events-sample.c",
        .entry_symbol = "zigux_runtime_trace_events_init",
        .exit_symbol = "zigux_runtime_trace_events_exit_drift",
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
    try std.testing.expect(!keepsApprovedPilotFamilyContract(mismatched_exit_symbol));
    try std.testing.expectError(error.InvalidPilotFamilyContract, prepareRequest(mismatched_exit_symbol));

    const unknown_family = LoadPlan{
        .module_name = "runtime_spinlock",
        .anchor = "kernel/locking/spinlock.c",
        .entry_symbol = "zigux_runtime_spinlock_init",
        .exit_symbol = "zigux_runtime_spinlock_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .allocator_handoff = .kernel_heap,
        .init_flow = .{
            .handoff_stage = .selftest_complete,
            .init_runs = 1,
            .selftest_runs = 1,
            .exit_runs = 0,
        },
    };
    try std.testing.expect(!keepsApprovedPilotFamilyContract(unknown_family));
    try std.testing.expectError(error.InvalidPilotFamilyContract, prepareRequest(unknown_family));

    const mismatched_selftest = LoadPlan{
        .module_name = "runtime_kretprobe",
        .anchor = "samples/kprobes/kretprobe_example.c",
        .entry_symbol = "zigux_runtime_kretprobe_init",
        .exit_symbol = "zigux_runtime_kretprobe_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .allocator_handoff = .kernel_heap,
        .init_flow = .{
            .handoff_stage = .selftest_complete,
            .init_runs = 1,
            .selftest_runs = 0,
            .exit_runs = 0,
        },
    };
    try std.testing.expectError(error.InvalidSelftestHookEvidence, prepareRequest(mismatched_selftest));

    const missing_selftest_hook = LoadPlan{
        .module_name = "runtime_trace_events",
        .anchor = "samples/trace_events/trace-events-sample.c",
        .entry_symbol = "zigux_runtime_trace_events_init",
        .exit_symbol = "zigux_runtime_trace_events_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = false,
        .allocator_handoff = .caller_provided,
        .init_flow = .{
            .handoff_stage = .selftest_complete,
            .init_runs = 1,
            .selftest_runs = 1,
            .exit_runs = 0,
        },
    };
    try std.testing.expect(!keepsSelftestHookEvidenceConsistent(missing_selftest_hook));
    try std.testing.expectError(error.InvalidSelftestHookEvidence, prepareRequest(missing_selftest_hook));

    const initialized_without_selftest_hook = LoadPlan{
        .module_name = "runtime_bitmap",
        .anchor = "lib/test_bitmap.c",
        .entry_symbol = "zigux_runtime_bitmap_init",
        .exit_symbol = "zigux_runtime_bitmap_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = false,
        .allocator_handoff = .arena,
        .init_flow = .{
            .handoff_stage = .initialized,
            .init_runs = 1,
            .selftest_runs = 0,
            .exit_runs = 0,
        },
    };
    try std.testing.expect(!keepsSelftestHookEvidenceConsistent(initialized_without_selftest_hook));
    try std.testing.expectError(error.InvalidSelftestHookEvidence, prepareRequest(initialized_without_selftest_hook));

    const selftest_runs_without_hook = LoadPlan{
        .module_name = "runtime_bitmap",
        .anchor = "lib/test_bitmap.c",
        .entry_symbol = "zigux_runtime_bitmap_init",
        .exit_symbol = "zigux_runtime_bitmap_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = false,
        .allocator_handoff = .arena,
        .init_flow = .{
            .handoff_stage = .initialized,
            .init_runs = 1,
            .selftest_runs = 1,
            .exit_runs = 0,
        },
    };
    try std.testing.expect(!keepsSelftestHookEvidenceConsistent(selftest_runs_without_hook));
    try std.testing.expectError(error.InvalidSelftestHookEvidence, prepareRequest(selftest_runs_without_hook));

    const stable_plan = LoadPlan{
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
    try std.testing.expect(!keepsAllocatorInitFlowConsistent(
        stable_plan,
        .arena,
        stable_plan.init_flow,
    ));
    try std.testing.expect(!keepsAllocatorInitFlowConsistent(
        stable_plan,
        .caller_provided,
        .{
            .handoff_stage = .initialized,
            .init_runs = 1,
            .selftest_runs = 1,
            .exit_runs = 0,
        },
    ));
}

test "shared runtime loader contract rejects request state, approved-family, or plan drift" {
    const stable_plan = LoadPlan{
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

    const request = try prepareRequest(stable_plan);
    try std.testing.expect(keepsApprovedPilotFamilyContract(stable_plan));
    try std.testing.expect(keepsRequestStateAndPlanExplicit(request, .prepared, stable_plan));
    try std.testing.expect(!keepsRequestStateAndPlanExplicit(
        request,
        .waiting_on_runtime_substrate,
        stable_plan,
    ));

    var drifted_module = stable_plan;
    drifted_module.module_name = "runtime_bitmap_drift";
    try std.testing.expect(!keepsApprovedPilotFamilyContract(drifted_module));
    try std.testing.expect(!keepsRequestStateAndPlanExplicit(request, .prepared, drifted_module));

    var drifted_anchor = stable_plan;
    drifted_anchor.anchor = "lib/test_bitmap_drift.c";
    try std.testing.expect(!keepsApprovedPilotFamilyContract(drifted_anchor));
    try std.testing.expect(!keepsRequestStateAndPlanExplicit(request, .prepared, drifted_anchor));

    var drifted_entry_symbol = stable_plan;
    drifted_entry_symbol.entry_symbol = "zigux_runtime_bitmap_init_drift";
    try std.testing.expect(!keepsApprovedPilotFamilyContract(drifted_entry_symbol));
    try std.testing.expect(!keepsRequestStateAndPlanExplicit(request, .prepared, drifted_entry_symbol));

    var drifted_exit_symbol = stable_plan;
    drifted_exit_symbol.exit_symbol = "zigux_runtime_bitmap_exit_drift";
    try std.testing.expect(!keepsApprovedPilotFamilyContract(drifted_exit_symbol));
    try std.testing.expect(!keepsRequestStateAndPlanExplicit(request, .prepared, drifted_exit_symbol));

    var drifted_runtime_requirement = stable_plan;
    drifted_runtime_requirement.requires_runtime_substrate = false;
    try std.testing.expect(!keepsRequestStateAndPlanExplicit(request, .prepared, drifted_runtime_requirement));

    var drifted_selftest_hook = stable_plan;
    drifted_selftest_hook.provides_selftest_hook = false;
    try std.testing.expect(!keepsRequestStateAndPlanExplicit(
        request,
        .prepared,
        drifted_selftest_hook,
    ));

    var drifted_allocator = stable_plan;
    drifted_allocator.allocator_handoff = .caller_provided;
    try std.testing.expect(!keepsRequestStateAndPlanExplicit(request, .prepared, drifted_allocator));

    var drifted_init_flow = stable_plan;
    drifted_init_flow.init_flow.selftest_runs = 1;
    try std.testing.expect(!keepsRequestStateAndPlanExplicit(request, .prepared, drifted_init_flow));
}

test "shared runtime loader contract keeps prepared-request drift from advancing runtime handoff state" {
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

    var request = try prepareRequest(stable_plan);
    try std.testing.expectEqual(RequestState.prepared, request.state);
    try std.testing.expect(keepsRequestStateAndPlanExplicit(request, .prepared, stable_plan));

    request.plan.requires_runtime_substrate = false;
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try std.testing.expectEqual(RequestState.prepared, request.state);
    try std.testing.expect(keepsLoadPlanExplicit(request.prepared_plan, stable_plan));
    try std.testing.expect(!keepsLoadPlanExplicit(request.plan, stable_plan));

    request.plan = stable_plan;
    request.plan.module_name = "runtime_trace_events_drift";
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try std.testing.expectEqual(RequestState.prepared, request.state);
    try std.testing.expect(keepsLoadPlanExplicit(request.prepared_plan, stable_plan));
    try std.testing.expect(!keepsLoadPlanExplicit(request.plan, stable_plan));

    request.plan = stable_plan;
    request.plan.anchor = "samples/trace_events/trace-events-sample-drift.c";
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try std.testing.expectEqual(RequestState.prepared, request.state);
    try std.testing.expect(keepsLoadPlanExplicit(request.prepared_plan, stable_plan));
    try std.testing.expect(!keepsLoadPlanExplicit(request.plan, stable_plan));

    request.plan = stable_plan;
    request.plan.entry_symbol = "zigux_runtime_trace_events_init_drift";
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try std.testing.expectEqual(RequestState.prepared, request.state);
    try std.testing.expect(keepsLoadPlanExplicit(request.prepared_plan, stable_plan));
    try std.testing.expect(!keepsLoadPlanExplicit(request.plan, stable_plan));

    request.plan = stable_plan;
    request.plan.exit_symbol = "zigux_runtime_trace_events_exit_drift";
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try std.testing.expectEqual(RequestState.prepared, request.state);
    try std.testing.expect(keepsLoadPlanExplicit(request.prepared_plan, stable_plan));
    try std.testing.expect(!keepsLoadPlanExplicit(request.plan, stable_plan));

    request.plan = stable_plan;
    request.plan.allocator_handoff = .arena;
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try std.testing.expectEqual(RequestState.prepared, request.state);
    try std.testing.expect(!keepsRequestStateAndPlanExplicit(request, .prepared, stable_plan));

    request.plan = stable_plan;
    request.plan.init_flow = .{
        .handoff_stage = .initialized,
        .init_runs = 1,
        .selftest_runs = 0,
        .exit_runs = 0,
    };
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try std.testing.expectEqual(RequestState.prepared, request.state);
    try std.testing.expect(!keepsRequestStateAndPlanExplicit(request, .prepared, stable_plan));

    request.plan = stable_plan;
    request.plan.provides_selftest_hook = false;
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try std.testing.expectEqual(RequestState.prepared, request.state);
    try std.testing.expect(keepsLoadPlanExplicit(request.prepared_plan, stable_plan));
    try std.testing.expect(!keepsLoadPlanExplicit(request.plan, stable_plan));

    request.plan = stable_plan;
    request.plan.init_flow.selftest_runs = 2;
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try std.testing.expectEqual(RequestState.prepared, request.state);
    try std.testing.expect(keepsLoadPlanExplicit(request.prepared_plan, stable_plan));
    try std.testing.expect(!keepsLoadPlanExplicit(request.plan, stable_plan));
}

test "shared runtime loader contract rejects stale state transitions across initialized and selftest-complete handoffs" {
    const initialized_plan = LoadPlan{
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
    var initialized_request = try prepareRequest(initialized_plan);
    try std.testing.expectEqual(RequestState.prepared, initialized_request.state);
    try std.testing.expectError(error.InvalidLoaderState, initialized_request.releaseWithoutSubstrate());
    const initialized_pending = try initialized_request.requestRuntimeLoad();
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, initialized_request.state);
    try std.testing.expect(keepsRequestStateAndPlanExplicit(
        initialized_request,
        .waiting_on_runtime_substrate,
        initialized_plan,
    ));
    try std.testing.expectEqual(HandoffStage.initialized, initialized_pending.init_flow.handoff_stage);
    try std.testing.expectEqual(@as(usize, 0), initialized_pending.init_flow.selftest_runs);
    try std.testing.expectError(error.InvalidLoaderState, initialized_request.requestRuntimeLoad());
    try initialized_request.releaseWithoutSubstrate();
    try std.testing.expectEqual(RequestState.released_without_substrate, initialized_request.state);
    try std.testing.expect(keepsRequestStateAndPlanExplicit(
        initialized_request,
        .released_without_substrate,
        initialized_plan,
    ));
    try std.testing.expectError(error.InvalidLoaderState, initialized_request.releaseWithoutSubstrate());

    const selftested_plan = LoadPlan{
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
    var selftested_request = try prepareRequest(selftested_plan);
    try std.testing.expectEqual(RequestState.prepared, selftested_request.state);
    try std.testing.expectError(error.InvalidLoaderState, selftested_request.releaseWithoutSubstrate());
    const selftested_pending = try selftested_request.requestRuntimeLoad();
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, selftested_request.state);
    try std.testing.expect(keepsRequestStateAndPlanExplicit(
        selftested_request,
        .waiting_on_runtime_substrate,
        selftested_plan,
    ));
    try std.testing.expectEqual(HandoffStage.selftest_complete, selftested_pending.init_flow.handoff_stage);
    try std.testing.expectEqual(@as(usize, 1), selftested_pending.init_flow.selftest_runs);
    try std.testing.expectError(error.InvalidLoaderState, selftested_request.requestRuntimeLoad());
    try selftested_request.releaseWithoutSubstrate();
    try std.testing.expectEqual(RequestState.released_without_substrate, selftested_request.state);
    try std.testing.expect(keepsRequestStateAndPlanExplicit(
        selftested_request,
        .released_without_substrate,
        selftested_plan,
    ));
    try std.testing.expectError(error.InvalidLoaderState, selftested_request.releaseWithoutSubstrate());
}

test "shared runtime loader contract keeps initialized-stage kretprobe requests stable across later selftest activity" {
    const initialized_plan = LoadPlan{
        .module_name = "runtime_kretprobe",
        .anchor = "samples/kprobes/kretprobe_example.c",
        .entry_symbol = "zigux_runtime_kretprobe_init",
        .exit_symbol = "zigux_runtime_kretprobe_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .allocator_handoff = .kernel_heap,
        .init_flow = .{
            .handoff_stage = .initialized,
            .init_runs = 1,
            .selftest_runs = 0,
            .exit_runs = 0,
        },
    };

    var request = try prepareRequest(initialized_plan);
    try std.testing.expectEqual(RequestState.prepared, request.state);
    try std.testing.expect(keepsApprovedPilotFamilyContract(initialized_plan));
    try std.testing.expect(keepsRequestStateAndPlanExplicit(request, .prepared, initialized_plan));
    try std.testing.expect(keepsSelftestHookEvidenceConsistent(initialized_plan));

    var live_selftested_plan = initialized_plan;
    live_selftested_plan.init_flow.handoff_stage = .selftest_complete;
    live_selftested_plan.init_flow.selftest_runs = 1;
    try std.testing.expect(keepsSelftestHookEvidenceConsistent(live_selftested_plan));
    try std.testing.expect(!keepsRequestStateAndPlanExplicit(
        request,
        .prepared,
        live_selftested_plan,
    ));

    const pending_plan = try request.requestRuntimeLoad();
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, request.state);
    try std.testing.expect(keepsRequestStateAndPlanExplicit(
        request,
        .waiting_on_runtime_substrate,
        initialized_plan,
    ));
    try std.testing.expectEqualStrings(initialized_plan.module_name, pending_plan.module_name);
    try std.testing.expectEqualStrings(initialized_plan.anchor, pending_plan.anchor);
    try std.testing.expectEqualStrings(initialized_plan.entry_symbol, pending_plan.entry_symbol);
    try std.testing.expectEqualStrings(initialized_plan.exit_symbol, pending_plan.exit_symbol);
    try std.testing.expect(pending_plan.provides_selftest_hook);
    try std.testing.expectEqual(HandoffStage.initialized, pending_plan.init_flow.handoff_stage);
    try std.testing.expectEqual(@as(usize, 1), pending_plan.init_flow.init_runs);
    try std.testing.expectEqual(@as(usize, 0), pending_plan.init_flow.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), pending_plan.init_flow.exit_runs);
    try std.testing.expect(keepsAllocatorInitFlowConsistent(
        pending_plan,
        .kernel_heap,
        initialized_plan.init_flow,
    ));
    try std.testing.expect(keepsSelftestHookEvidenceConsistent(pending_plan));
    try request.releaseWithoutSubstrate();
    try std.testing.expectEqual(RequestState.released_without_substrate, request.state);
    try std.testing.expect(keepsRequestStateAndPlanExplicit(request, .released_without_substrate, initialized_plan));
}

test "shared runtime loader contract keeps command, environment, registration-summary, depmod-facing, and study-only core-boundary control surfaces outside the request contract" {
    try std.testing.expect(!@hasField(LoadPlan, "modinfo"));
    try std.testing.expect(!@hasField(LoadPlan, "module_alias"));
    try std.testing.expect(!@hasField(LoadPlan, "module_aliases"));
    try std.testing.expect(!@hasField(LoadPlan, "modules_alias_path"));
    try std.testing.expect(!@hasField(LoadPlan, "depmod_script"));
    try std.testing.expect(!@hasField(LoadPlan, "depmod_manifest"));
    try std.testing.expect(!@hasField(LoadPlan, "depmod_aliases"));
    try std.testing.expect(!@hasField(PreparedRequest, "modinfo"));
    try std.testing.expect(!@hasField(PreparedRequest, "module_alias"));
    try std.testing.expect(!@hasField(PreparedRequest, "module_aliases"));
    try std.testing.expect(!@hasField(PreparedRequest, "modules_alias_path"));
    try std.testing.expect(!@hasField(PreparedRequest, "module_install_root"));
    try std.testing.expect(!@hasField(PreparedRequest, "modules_order_path"));
    try std.testing.expect(!@hasField(PreparedRequest, "modules_builtin_path"));
    try std.testing.expect(!@hasField(PreparedRequest, "depmod_script"));
    try std.testing.expect(!@hasField(PreparedRequest, "depmod_manifest"));
    try std.testing.expect(!@hasField(PreparedRequest, "depmod_aliases"));
}

test "shared runtime loader contract keeps releaseWithoutSubstrate waiting state pinned across broader prepared-plan drift" {
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
    var request = try prepareRequest(stable_plan);
    _ = try request.requestRuntimeLoad();
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, request.state);

    request.plan.requires_runtime_substrate = false;
    try std.testing.expectError(error.PreparedPlanDrift, request.releaseWithoutSubstrate());
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, request.state);
    try std.testing.expect(keepsLoadPlanExplicit(request.prepared_plan, stable_plan));
    try std.testing.expect(!keepsLoadPlanExplicit(request.plan, stable_plan));

    request.plan = stable_plan;
    request.plan.module_name = "runtime_trace_events_drift";
    try std.testing.expectError(error.PreparedPlanDrift, request.releaseWithoutSubstrate());
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, request.state);
    try std.testing.expect(keepsLoadPlanExplicit(request.prepared_plan, stable_plan));
    try std.testing.expect(!keepsLoadPlanExplicit(request.plan, stable_plan));

    request.plan = stable_plan;
    request.plan.anchor = "samples/trace_events/trace-events-sample-drift.c";
    try std.testing.expectError(error.PreparedPlanDrift, request.releaseWithoutSubstrate());
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, request.state);
    try std.testing.expect(keepsLoadPlanExplicit(request.prepared_plan, stable_plan));
    try std.testing.expect(!keepsLoadPlanExplicit(request.plan, stable_plan));

    request.plan = stable_plan;
    request.plan.entry_symbol = "zigux_runtime_trace_events_init_drift";
    try std.testing.expectError(error.PreparedPlanDrift, request.releaseWithoutSubstrate());
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, request.state);
    try std.testing.expect(keepsLoadPlanExplicit(request.prepared_plan, stable_plan));
    try std.testing.expect(!keepsLoadPlanExplicit(request.plan, stable_plan));

    request.plan = stable_plan;
    request.plan.exit_symbol = "zigux_runtime_trace_events_exit_drift";
    try std.testing.expectError(error.PreparedPlanDrift, request.releaseWithoutSubstrate());
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, request.state);
    try std.testing.expect(keepsLoadPlanExplicit(request.prepared_plan, stable_plan));
    try std.testing.expect(!keepsLoadPlanExplicit(request.plan, stable_plan));

    request.plan = stable_plan;
    request.plan.allocator_handoff = .arena;
    try std.testing.expectError(error.PreparedPlanDrift, request.releaseWithoutSubstrate());
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, request.state);
    try std.testing.expect(keepsLoadPlanExplicit(request.prepared_plan, stable_plan));
    try std.testing.expect(!keepsLoadPlanExplicit(request.plan, stable_plan));

    request.plan = stable_plan;
    request.plan.provides_selftest_hook = false;
    try std.testing.expectError(error.PreparedPlanDrift, request.releaseWithoutSubstrate());
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, request.state);
    try std.testing.expect(keepsLoadPlanExplicit(request.prepared_plan, stable_plan));
    try std.testing.expect(!keepsLoadPlanExplicit(request.plan, stable_plan));

    request.plan = stable_plan;
    request.plan.init_flow.selftest_runs = 2;
    try std.testing.expectError(error.PreparedPlanDrift, request.releaseWithoutSubstrate());
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, request.state);
    try std.testing.expect(keepsLoadPlanExplicit(request.prepared_plan, stable_plan));
    try std.testing.expect(!keepsLoadPlanExplicit(request.plan, stable_plan));
}
