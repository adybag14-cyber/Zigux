const std = @import("std");
const contract = @import("runtime_loader_contract");

pub const AllocatorHandoff = contract.AllocatorHandoff;
pub const DepmodAliasRecord = contract.DepmodAliasRecord;
pub const HandoffStage = contract.HandoffStage;
pub const InitFlow = contract.InitFlow;
pub const LoadPlan = contract.LoadPlan;
pub const ModuleMetadata = contract.ModuleMetadata;
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
    module_metadata: ModuleMetadata,
    handoff_stage: HandoffStage,
    allocator_handoff: AllocatorHandoff,
};

const approved_pilot_families = [_]ApprovedPilotFamily{
    .{
        .module_name = "runtime_atomic64",
        .anchor = "lib/atomic64_test.c",
        .entry_symbol = "zigux_runtime_atomic64_init",
        .exit_symbol = "zigux_runtime_atomic64_exit",
        .module_metadata = .{
            .license = "GPL",
            .aliases = &.{"zigux:runtime-pilot:runtime_atomic64"},
        },
        .handoff_stage = .selftest_complete,
        .allocator_handoff = .caller_provided,
    },
    .{
        .module_name = "runtime_bitmap",
        .anchor = "lib/test_bitmap.c",
        .entry_symbol = "zigux_runtime_bitmap_init",
        .exit_symbol = "zigux_runtime_bitmap_exit",
        .module_metadata = .{
            .license = "GPL",
            .aliases = &.{"zigux:runtime-pilot:runtime_bitmap"},
        },
        .handoff_stage = .initialized,
        .allocator_handoff = .arena,
    },
    .{
        .module_name = "runtime_trace_events",
        .anchor = "samples/trace_events/trace-events-sample.c",
        .entry_symbol = "zigux_runtime_trace_events_init",
        .exit_symbol = "zigux_runtime_trace_events_exit",
        .module_metadata = .{
            .license = "GPL",
            .aliases = &.{"zigux:runtime-pilot:runtime_trace_events"},
        },
        .handoff_stage = .selftest_complete,
        .allocator_handoff = .caller_provided,
    },
    .{
        .module_name = "runtime_kretprobe",
        .anchor = "samples/kprobes/kretprobe_example.c",
        .entry_symbol = "zigux_runtime_kretprobe_init",
        .exit_symbol = "zigux_runtime_kretprobe_exit",
        .module_metadata = .{
            .license = "GPL",
            .aliases = &.{"zigux:runtime-pilot:runtime_kretprobe"},
        },
        .handoff_stage = .initialized,
        .allocator_handoff = .kernel_heap,
    },
};

fn approvedPilotFamilyFor(plan: LoadPlan) ?ApprovedPilotFamily {
    for (approved_pilot_families) |family| {
        if (std.mem.eql(u8, plan.module_name, family.module_name) and
            std.mem.eql(u8, plan.anchor, family.anchor) and
            std.mem.eql(u8, plan.entry_symbol, family.entry_symbol) and
            std.mem.eql(u8, plan.exit_symbol, family.exit_symbol))
        {
            return family;
        }
    }
    return null;
}

pub fn keepsLoadPlanExplicit(actual: LoadPlan, expected: LoadPlan) bool {
    return contract.keepsLoadPlanExplicit(actual, expected);
}

pub fn keepsApprovedPilotFamilyContract(plan: LoadPlan) bool {
    return approvedPilotFamilyFor(plan) != null;
}

pub fn keepsApprovedPilotFamilyShape(plan: LoadPlan) bool {
    const family = approvedPilotFamilyFor(plan) orelse return false;
    return plan.init_flow.handoff_stage == family.handoff_stage and
        plan.allocator_handoff == family.allocator_handoff;
}

pub fn keepsApprovedPilotModuleMetadata(plan: LoadPlan) bool {
    const family = approvedPilotFamilyFor(plan) orelse return false;
    return contract.keepsModuleMetadataExplicit(plan.module_metadata, family.module_metadata) and
        contract.keepsDepmodAliasReady(plan.module_metadata);
}

pub fn depmodAliasRecordCount(plan: LoadPlan) usize {
    return contract.depmodAliasRecordCount(plan);
}

pub fn depmodAliasRecordFor(plan: LoadPlan, alias_index: usize) ?DepmodAliasRecord {
    return contract.depmodAliasRecordFor(plan, alias_index);
}

pub fn keepsDepmodAliasRecordsExplicit(plan: LoadPlan, records: []const DepmodAliasRecord) bool {
    return contract.keepsDepmodAliasRecordsExplicit(plan, records);
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
    if (!keepsApprovedPilotFamilyShape(plan)) return error.InvalidPilotFamilyShape;
    if (!keepsApprovedPilotModuleMetadata(plan)) return error.InvalidPilotModuleMetadata;
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
        .module_metadata = .{
            .license = "GPL",
            .aliases = &.{"zigux:runtime-pilot:runtime_trace_events"},
        },
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

test "keepsApprovedPilotFamilyShape enforces family-specific allocator handoff and handoff stage together" {
    const bitmap_plan = LoadPlan{
        .module_name = "runtime_bitmap",
        .anchor = "lib/test_bitmap.c",
        .entry_symbol = "zigux_runtime_bitmap_init",
        .exit_symbol = "zigux_runtime_bitmap_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .module_metadata = .{
            .license = "GPL",
            .aliases = &.{"zigux:runtime-pilot:runtime_bitmap"},
        },
        .allocator_handoff = .arena,
        .init_flow = .{
            .handoff_stage = .initialized,
            .init_runs = 1,
            .selftest_runs = 0,
            .exit_runs = 0,
        },
    };
    try std.testing.expect(keepsApprovedPilotFamilyContract(bitmap_plan));
    try std.testing.expect(keepsApprovedPilotFamilyShape(bitmap_plan));

    var alternate_bitmap = bitmap_plan;
    alternate_bitmap.allocator_handoff = .caller_provided;
    try std.testing.expect(!keepsApprovedPilotFamilyShape(alternate_bitmap));

    alternate_bitmap = bitmap_plan;
    alternate_bitmap.allocator_handoff = .kernel_heap;
    try std.testing.expect(!keepsApprovedPilotFamilyShape(alternate_bitmap));

    var drifted_bitmap = bitmap_plan;
    drifted_bitmap.init_flow.handoff_stage = .selftest_complete;
    drifted_bitmap.init_flow.selftest_runs = 1;
    try std.testing.expect(!keepsApprovedPilotFamilyShape(drifted_bitmap));

    const trace_events_plan = LoadPlan{
        .module_name = "runtime_trace_events",
        .anchor = "samples/trace_events/trace-events-sample.c",
        .entry_symbol = "zigux_runtime_trace_events_init",
        .exit_symbol = "zigux_runtime_trace_events_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .module_metadata = .{
            .license = "GPL",
            .aliases = &.{"zigux:runtime-pilot:runtime_trace_events"},
        },
        .allocator_handoff = .caller_provided,
        .init_flow = .{
            .handoff_stage = .selftest_complete,
            .init_runs = 1,
            .selftest_runs = 1,
            .exit_runs = 0,
        },
    };
    try std.testing.expect(keepsApprovedPilotFamilyContract(trace_events_plan));
    try std.testing.expect(keepsApprovedPilotFamilyShape(trace_events_plan));

    var alternate_trace_events = trace_events_plan;
    alternate_trace_events.allocator_handoff = .kernel_heap;
    try std.testing.expect(!keepsApprovedPilotFamilyShape(alternate_trace_events));

    var drifted_trace_events = trace_events_plan;
    drifted_trace_events.init_flow.handoff_stage = .initialized;
    drifted_trace_events.init_flow.selftest_runs = 0;
    try std.testing.expect(!keepsApprovedPilotFamilyShape(drifted_trace_events));

    const kretprobe_plan = LoadPlan{
        .module_name = "runtime_kretprobe",
        .anchor = "samples/kprobes/kretprobe_example.c",
        .entry_symbol = "zigux_runtime_kretprobe_init",
        .exit_symbol = "zigux_runtime_kretprobe_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .module_metadata = .{
            .license = "GPL",
            .aliases = &.{"zigux:runtime-pilot:runtime_kretprobe"},
        },
        .allocator_handoff = .kernel_heap,
        .init_flow = .{
            .handoff_stage = .initialized,
            .init_runs = 1,
            .selftest_runs = 0,
            .exit_runs = 0,
        },
    };
    try std.testing.expect(keepsApprovedPilotFamilyContract(kretprobe_plan));
    try std.testing.expect(keepsApprovedPilotFamilyShape(kretprobe_plan));

    var drifted_kretprobe = kretprobe_plan;
    drifted_kretprobe.allocator_handoff = .arena;
    try std.testing.expect(!keepsApprovedPilotFamilyShape(drifted_kretprobe));
}

test "prepareRequest keeps bounded module metadata and depmod alias records explicit" {
    const stable = LoadPlan{
        .module_name = "runtime_kretprobe",
        .anchor = "samples/kprobes/kretprobe_example.c",
        .entry_symbol = "zigux_runtime_kretprobe_init",
        .exit_symbol = "zigux_runtime_kretprobe_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .module_metadata = .{
            .license = "GPL",
            .aliases = &.{"zigux:runtime-pilot:runtime_kretprobe"},
        },
        .allocator_handoff = .kernel_heap,
        .init_flow = .{
            .handoff_stage = .initialized,
            .init_runs = 1,
            .selftest_runs = 0,
            .exit_runs = 0,
        },
    };

    try std.testing.expect(keepsApprovedPilotModuleMetadata(stable));
    try std.testing.expectEqual(@as(usize, 1), depmodAliasRecordCount(stable));
    try std.testing.expectEqualStrings(
        "runtime_kretprobe",
        depmodAliasRecordFor(stable, 0).?.module_name,
    );
    try std.testing.expectEqualStrings(
        "zigux:runtime-pilot:runtime_kretprobe",
        depmodAliasRecordFor(stable, 0).?.module_alias,
    );
    const expected_records = [_]DepmodAliasRecord{
        .{
            .module_name = "runtime_kretprobe",
            .module_alias = "zigux:runtime-pilot:runtime_kretprobe",
        },
    };
    try std.testing.expect(keepsDepmodAliasRecordsExplicit(stable, &expected_records));
}

test "prepareRequest rejects loader-not-required, pilot-family drift, pilot-family-shape drift, metadata drift, init-flow drift, and selftest drift" {
    var plan = LoadPlan{
        .module_name = "runtime_bitmap",
        .anchor = "lib/test_bitmap.c",
        .entry_symbol = "zigux_runtime_bitmap_init",
        .exit_symbol = "zigux_runtime_bitmap_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .module_metadata = .{
            .license = "GPL",
            .aliases = &.{"zigux:runtime-pilot:runtime_bitmap"},
        },
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

    plan.anchor = "lib/test_bitmap_drift.c";
    try std.testing.expectError(error.InvalidPilotFamilyContract, prepareRequest(plan));
    plan.anchor = "lib/test_bitmap.c";

    plan.entry_symbol = "zigux_runtime_bitmap_init_drift";
    try std.testing.expectError(error.InvalidPilotFamilyContract, prepareRequest(plan));
    plan.entry_symbol = "zigux_runtime_bitmap_init";

    plan.exit_symbol = "zigux_runtime_bitmap_exit_drift";
    try std.testing.expectError(error.InvalidPilotFamilyContract, prepareRequest(plan));
    plan.exit_symbol = "zigux_runtime_bitmap_exit";

    plan.allocator_handoff = .caller_provided;
    try std.testing.expectError(error.InvalidPilotFamilyShape, prepareRequest(plan));
    plan.allocator_handoff = .arena;

    plan.init_flow.handoff_stage = .selftest_complete;
    plan.init_flow.selftest_runs = 1;
    try std.testing.expectError(error.InvalidPilotFamilyShape, prepareRequest(plan));
    plan.init_flow.handoff_stage = .initialized;
    plan.init_flow.selftest_runs = 0;

    plan.module_metadata.license = "";
    try std.testing.expectError(error.InvalidPilotModuleMetadata, prepareRequest(plan));
    plan.module_metadata.license = "GPL";

    plan.module_metadata.aliases = &.{"runtime_bitmap"};
    try std.testing.expectError(error.InvalidPilotModuleMetadata, prepareRequest(plan));
    plan.module_metadata.aliases = &.{"zigux:runtime-pilot:runtime_bitmap"};

    plan.init_flow.selftest_runs = 1;
    try std.testing.expectError(error.InvalidInitFlow, prepareRequest(plan));
    plan.init_flow.selftest_runs = 0;

    plan.provides_selftest_hook = false;
    try std.testing.expectError(error.InvalidSelftestHookEvidence, prepareRequest(plan));

    var trace_events_plan = LoadPlan{
        .module_name = "runtime_trace_events",
        .anchor = "samples/trace_events/trace-events-sample.c",
        .entry_symbol = "zigux_runtime_trace_events_init",
        .exit_symbol = "zigux_runtime_trace_events_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .module_metadata = .{
            .license = "GPL",
            .aliases = &.{"zigux:runtime-pilot:runtime_trace_events"},
        },
        .allocator_handoff = .caller_provided,
        .init_flow = .{
            .handoff_stage = .selftest_complete,
            .init_runs = 1,
            .selftest_runs = 1,
            .exit_runs = 0,
        },
    };

    trace_events_plan.allocator_handoff = .kernel_heap;
    try std.testing.expectError(error.InvalidPilotFamilyShape, prepareRequest(trace_events_plan));
    trace_events_plan.allocator_handoff = .caller_provided;

    trace_events_plan.init_flow.handoff_stage = .initialized;
    trace_events_plan.init_flow.selftest_runs = 0;
    try std.testing.expectError(error.InvalidPilotFamilyShape, prepareRequest(trace_events_plan));
}

test "PreparedRequest.requestRuntimeLoad preserves the prepared snapshot on drift" {
    const stable = LoadPlan{
        .module_name = "runtime_atomic64",
        .anchor = "lib/atomic64_test.c",
        .entry_symbol = "zigux_runtime_atomic64_init",
        .exit_symbol = "zigux_runtime_atomic64_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .module_metadata = .{
            .license = "GPL",
            .aliases = &.{"zigux:runtime-pilot:runtime_atomic64"},
        },
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

test "releaseWithoutSubstrate preserves the waiting snapshot on drift" {
    const stable = LoadPlan{
        .module_name = "runtime_trace_events",
        .anchor = "samples/trace_events/trace-events-sample.c",
        .entry_symbol = "zigux_runtime_trace_events_init",
        .exit_symbol = "zigux_runtime_trace_events_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .module_metadata = .{
            .license = "GPL",
            .aliases = &.{"zigux:runtime-pilot:runtime_trace_events"},
        },
        .allocator_handoff = .caller_provided,
        .init_flow = .{
            .handoff_stage = .selftest_complete,
            .init_runs = 1,
            .selftest_runs = 1,
            .exit_runs = 0,
        },
    };

    var request = try prepareRequest(stable);
    const pending = try request.requestRuntimeLoad();
    request.plan.requires_runtime_substrate = false;

    try std.testing.expectError(error.PreparedPlanDrift, request.releaseWithoutSubstrate());
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, request.state);
    try std.testing.expect(keepsLoadPlanExplicit(request.prepared_plan, stable));
    try std.testing.expect(keepsLoadPlanExplicit(pending, stable));
    try std.testing.expect(!keepsLoadPlanExplicit(request.plan, stable));

    const initialized = LoadPlan{
        .module_name = "runtime_bitmap",
        .anchor = "lib/test_bitmap.c",
        .entry_symbol = "zigux_runtime_bitmap_init",
        .exit_symbol = "zigux_runtime_bitmap_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .module_metadata = .{
            .license = "GPL",
            .aliases = &.{"zigux:runtime-pilot:runtime_bitmap"},
        },
        .allocator_handoff = .arena,
        .init_flow = .{
            .handoff_stage = .initialized,
            .init_runs = 1,
            .selftest_runs = 0,
            .exit_runs = 0,
        },
    };

    var initialized_request = try prepareRequest(initialized);
    const initialized_pending = try initialized_request.requestRuntimeLoad();
    initialized_request.plan.module_name = "runtime_bitmap_drift";

    try std.testing.expectError(error.PreparedPlanDrift, initialized_request.releaseWithoutSubstrate());
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, initialized_request.state);
    try std.testing.expect(keepsLoadPlanExplicit(initialized_request.prepared_plan, initialized));
    try std.testing.expect(keepsLoadPlanExplicit(initialized_pending, initialized));
    try std.testing.expect(!keepsLoadPlanExplicit(initialized_request.plan, initialized));
}

test "PreparedRequest.requestRuntimeLoad rejects invalid lifecycle states without disturbing snapshots" {
    const stable = LoadPlan{
        .module_name = "runtime_trace_events",
        .anchor = "samples/trace_events/trace-events-sample.c",
        .entry_symbol = "zigux_runtime_trace_events_init",
        .exit_symbol = "zigux_runtime_trace_events_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .module_metadata = .{
            .license = "GPL",
            .aliases = &.{"zigux:runtime-pilot:runtime_trace_events"},
        },
        .allocator_handoff = .caller_provided,
        .init_flow = .{
            .handoff_stage = .selftest_complete,
            .init_runs = 1,
            .selftest_runs = 1,
            .exit_runs = 0,
        },
    };

    var waiting_request = try prepareRequest(stable);
    const waiting_pending = try waiting_request.requestRuntimeLoad();
    try std.testing.expectError(error.InvalidLoaderState, waiting_request.requestRuntimeLoad());
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, waiting_request.state);
    try std.testing.expect(keepsLoadPlanExplicit(waiting_request.prepared_plan, stable));
    try std.testing.expect(keepsLoadPlanExplicit(waiting_request.plan, waiting_pending));
    try std.testing.expect(keepsLoadPlanExplicit(waiting_pending, stable));

    var released_request = try prepareRequest(stable);
    const released_pending = try released_request.requestRuntimeLoad();
    try released_request.releaseWithoutSubstrate();
    try std.testing.expectError(error.InvalidLoaderState, released_request.requestRuntimeLoad());
    try std.testing.expectEqual(RequestState.released_without_substrate, released_request.state);
    try std.testing.expect(keepsLoadPlanExplicit(released_request.prepared_plan, stable));
    try std.testing.expect(keepsLoadPlanExplicit(released_request.plan, released_pending));
    try std.testing.expect(keepsLoadPlanExplicit(released_pending, stable));
}

test "PreparedRequest.releaseWithoutSubstrate rejects invalid lifecycle states without disturbing snapshots" {
    const stable = LoadPlan{
        .module_name = "runtime_bitmap",
        .anchor = "lib/test_bitmap.c",
        .entry_symbol = "zigux_runtime_bitmap_init",
        .exit_symbol = "zigux_runtime_bitmap_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .module_metadata = .{
            .license = "GPL",
            .aliases = &.{"zigux:runtime-pilot:runtime_bitmap"},
        },
        .allocator_handoff = .arena,
        .init_flow = .{
            .handoff_stage = .initialized,
            .init_runs = 1,
            .selftest_runs = 0,
            .exit_runs = 0,
        },
    };

    var prepared_request = try prepareRequest(stable);
    try std.testing.expectError(error.InvalidLoaderState, prepared_request.releaseWithoutSubstrate());
    try std.testing.expectEqual(RequestState.prepared, prepared_request.state);
    try std.testing.expect(keepsLoadPlanExplicit(prepared_request.prepared_plan, stable));
    try std.testing.expect(keepsLoadPlanExplicit(prepared_request.plan, stable));

    var released_request = try prepareRequest(stable);
    const released_pending = try released_request.requestRuntimeLoad();
    try released_request.releaseWithoutSubstrate();
    try std.testing.expectError(error.InvalidLoaderState, released_request.releaseWithoutSubstrate());
    try std.testing.expectEqual(RequestState.released_without_substrate, released_request.state);
    try std.testing.expect(keepsLoadPlanExplicit(released_request.prepared_plan, stable));
    try std.testing.expect(keepsLoadPlanExplicit(released_request.plan, released_pending));
    try std.testing.expect(keepsLoadPlanExplicit(released_pending, stable));
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
        try std.testing.expect(!@hasField(PreparedRequest, field));
    }
}

test "PreparedRequest keeps blocked publication outputs and install-root surfaces out of the shared request boundary" {
    const blocked_publication_fields = [_][]const u8{
        "modinfo",
        "module_alias",
        "modules_alias_path",
        "module_install_root",
        "modules_order_path",
        "modules_builtin_path",
        "module_symvers_path",
        "depmod_script",
        "depmod_manifest",
    };

    inline for (blocked_publication_fields) |field| {
        try std.testing.expect(!@hasField(PreparedRequest, field));
    }
}

test "PreparedRequest keeps blocked registration-summary surfaces out of the shared request boundary" {
    const blocked_registration_summary_fields = [_][]const u8{
        "register_api",
        "unregister_api",
        "summary",
        "registration_snapshot",
    };

    inline for (blocked_registration_summary_fields) |field| {
        try std.testing.expect(!@hasField(PreparedRequest, field));
    }
}

test "PreparedRequest keeps blocked initcall metadata surfaces out of the shared request boundary" {
    const blocked_initcall_fields = [_][]const u8{
        "module_init",
        "module_exit",
        "initcall",
        "exitcall",
    };

    inline for (blocked_initcall_fields) |field| {
        try std.testing.expect(!@hasField(PreparedRequest, field));
    }
}

test "ApprovedPilotFamily keeps Phase 8 command and environment control fields out of the shared family contract" {
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
        try std.testing.expect(!@hasField(ApprovedPilotFamily, field));
    }
}

test "ApprovedPilotFamily keeps blocked publication outputs and install-root surfaces out of the shared family contract" {
    const blocked_publication_fields = [_][]const u8{
        "modinfo",
        "module_alias",
        "modules_alias_path",
        "module_install_root",
        "modules_order_path",
        "modules_builtin_path",
        "module_symvers_path",
        "depmod_script",
        "depmod_manifest",
    };

    inline for (blocked_publication_fields) |field| {
        try std.testing.expect(!@hasField(ApprovedPilotFamily, field));
    }
}

test "ApprovedPilotFamily keeps blocked registration-summary surfaces out of the shared family contract" {
    const blocked_registration_summary_fields = [_][]const u8{
        "register_api",
        "unregister_api",
        "summary",
        "registration_snapshot",
    };

    inline for (blocked_registration_summary_fields) |field| {
        try std.testing.expect(!@hasField(ApprovedPilotFamily, field));
    }
}

test "ApprovedPilotFamily keeps blocked initcall metadata surfaces out of the shared family contract" {
    const blocked_initcall_fields = [_][]const u8{
        "module_init",
        "module_exit",
        "initcall",
        "exitcall",
    };

    inline for (blocked_initcall_fields) |field| {
        try std.testing.expect(!@hasField(ApprovedPilotFamily, field));
    }
}
