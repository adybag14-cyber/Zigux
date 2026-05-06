const std = @import("std");
const runtime_kretprobe_sample = @import("runtime_kretprobe_sample");
const runtime_loader = @import("runtime_loader");

pub const LoaderStage = enum(u8) {
    idle,
    prepared,
    waiting_on_runtime_substrate,
    released_without_substrate,
};

pub const RuntimeKretprobeLoadPlan = struct {
    module_name: []const u8,
    anchor: []const u8,
    entry_symbol: []const u8,
    exit_symbol: []const u8,
    register_api: []const u8,
    unregister_api: []const u8,
    symbol_name: []const u8,
    maxactive: usize,
    private_data_bytes: usize,
    requires_runtime_substrate: bool,
    provides_selftest_hook: bool,
    handoff_stage: runtime_kretprobe_sample.ModuleStage,
    summary: runtime_kretprobe_sample.RuntimeKretprobeSummary,
};

pub const RuntimeKretprobeRegistrationSnapshot = struct {
    register_api: []const u8,
    unregister_api: []const u8,
    symbol_name: []const u8,
    maxactive: usize,
    private_data_bytes: usize,
    skipped_kernel_threads: usize,
    nmissed: usize,
    last_retval: usize,
    last_duration_ns: i64,
    selftest_runs: usize,
    entry_timestamp_armed: bool,
};

fn sharedHandoffStage(stage: runtime_kretprobe_sample.ModuleStage) runtime_loader.HandoffStage {
    return switch (stage) {
        .initialized => .initialized,
        .selftest_complete => .selftest_complete,
        else => unreachable,
    };
}

fn ensureIdleRegistrationSnapshot(summary: runtime_kretprobe_sample.RuntimeKretprobeSummary) !void {
    if (summary.active_instances != 0 or summary.entry_timestamp_armed) {
        return error.OutstandingProbeStateForLoader;
    }
}

pub fn toSharedLoadPlan(plan: RuntimeKretprobeLoadPlan) runtime_loader.LoadPlan {
    return .{
        .module_name = plan.module_name,
        .anchor = plan.anchor,
        .entry_symbol = plan.entry_symbol,
        .exit_symbol = plan.exit_symbol,
        .requires_runtime_substrate = plan.requires_runtime_substrate,
        .provides_selftest_hook = plan.provides_selftest_hook,
        .allocator_handoff = .kernel_heap,
        .init_flow = .{
            .handoff_stage = sharedHandoffStage(plan.handoff_stage),
            .init_runs = 1,
            .selftest_runs = plan.summary.selftest_runs,
            .exit_runs = 0,
        },
    };
}

pub fn registrationSnapshot(plan: RuntimeKretprobeLoadPlan) RuntimeKretprobeRegistrationSnapshot {
    return .{
        .register_api = plan.register_api,
        .unregister_api = plan.unregister_api,
        .symbol_name = plan.symbol_name,
        .maxactive = plan.maxactive,
        .private_data_bytes = plan.private_data_bytes,
        .skipped_kernel_threads = plan.summary.skipped_kernel_threads,
        .nmissed = plan.summary.nmissed,
        .last_retval = plan.summary.last_retval,
        .last_duration_ns = plan.summary.last_duration_ns,
        .selftest_runs = plan.summary.selftest_runs,
        .entry_timestamp_armed = plan.summary.entry_timestamp_armed,
    };
}

pub fn keepsRegistrationSnapshotExplicit(
    plan: RuntimeKretprobeLoadPlan,
    snapshot: RuntimeKretprobeRegistrationSnapshot,
) bool {
    return std.mem.eql(u8, snapshot.register_api, plan.register_api) and
        std.mem.eql(u8, snapshot.unregister_api, plan.unregister_api) and
        std.mem.eql(u8, snapshot.symbol_name, plan.symbol_name) and
        snapshot.maxactive == plan.maxactive and
        snapshot.private_data_bytes == plan.private_data_bytes and
        snapshot.skipped_kernel_threads == plan.summary.skipped_kernel_threads and
        snapshot.nmissed == plan.summary.nmissed and
        snapshot.last_retval == plan.summary.last_retval and
        snapshot.last_duration_ns == plan.summary.last_duration_ns and
        snapshot.selftest_runs == plan.summary.selftest_runs and
        snapshot.entry_timestamp_armed == plan.summary.entry_timestamp_armed;
}

pub fn keepsSharedLoadPlanSnapshotExplicit(
    plan: RuntimeKretprobeLoadPlan,
    shared_plan: runtime_loader.LoadPlan,
) bool {
    return std.mem.eql(u8, shared_plan.module_name, plan.module_name) and
        std.mem.eql(u8, shared_plan.anchor, plan.anchor) and
        std.mem.eql(u8, shared_plan.entry_symbol, plan.entry_symbol) and
        std.mem.eql(u8, shared_plan.exit_symbol, plan.exit_symbol) and
        shared_plan.requires_runtime_substrate == plan.requires_runtime_substrate and
        shared_plan.provides_selftest_hook == plan.provides_selftest_hook and
        shared_plan.allocator_handoff == .kernel_heap and
        shared_plan.init_flow.handoff_stage == sharedHandoffStage(plan.handoff_stage) and
        shared_plan.init_flow.init_runs == 1 and
        shared_plan.init_flow.selftest_runs == plan.summary.selftest_runs and
        shared_plan.init_flow.exit_runs == 0;
}

pub const RuntimeKretprobeLoader = struct {
    const Self = @This();

    stage_state: LoaderStage = .idle,
    cached_plan: ?RuntimeKretprobeLoadPlan = null,

    pub fn stage(self: *const Self) LoaderStage {
        return self.stage_state;
    }

    pub fn planFor(module: *const runtime_kretprobe_sample.RuntimeKretprobeSample) !RuntimeKretprobeLoadPlan {
        const descriptor = runtime_kretprobe_sample.RuntimeKretprobeSample.descriptor();
        const module_stage = module.stage();
        switch (module_stage) {
            .initialized, .selftest_complete => {},
            else => return error.InvalidModuleLifecycleForLoader,
        }

        if (!descriptor.requires_runtime_substrate) return error.LoaderNotRequired;

        const summary = module.summary();
        try ensureIdleRegistrationSnapshot(summary);
        return .{
            .module_name = descriptor.name,
            .anchor = descriptor.anchor,
            .entry_symbol = "zigux_runtime_kretprobe_init",
            .exit_symbol = "zigux_runtime_kretprobe_exit",
            .register_api = "register_kretprobe",
            .unregister_api = "unregister_kretprobe",
            .symbol_name = summary.symbol_name,
            .maxactive = summary.maxactive,
            .private_data_bytes = @sizeOf(runtime_kretprobe_sample.InstancePrivateData),
            .requires_runtime_substrate = descriptor.requires_runtime_substrate,
            .provides_selftest_hook = descriptor.provides_selftest_hook,
            .handoff_stage = module_stage,
            .summary = summary,
        };
    }

    pub fn prepare(self: *Self, module: *const runtime_kretprobe_sample.RuntimeKretprobeSample) !RuntimeKretprobeLoadPlan {
        if (self.stage_state != .idle) return error.LoaderAlreadyPrepared;

        const plan = try planFor(module);
        self.cached_plan = plan;
        self.stage_state = .prepared;
        return plan;
    }

    pub fn prepareSharedRequest(self: *Self, module: *const runtime_kretprobe_sample.RuntimeKretprobeSample) !runtime_loader.PreparedRequest {
        const plan = try self.prepare(module);
        return runtime_loader.prepareRequest(toSharedLoadPlan(plan));
    }

    pub fn requestRuntimeLoad(self: *Self) !RuntimeKretprobeLoadPlan {
        if (self.stage_state != .prepared) return error.InvalidLoaderState;

        self.stage_state = .waiting_on_runtime_substrate;
        return self.cached_plan orelse error.MissingLoadPlan;
    }

    pub fn requestSharedRuntimeLoad(
        self: *Self,
        shared_request: *runtime_loader.PreparedRequest,
    ) !runtime_loader.LoadPlan {
        const plan = try self.requestRuntimeLoad();
        const shared_plan = try shared_request.requestRuntimeLoad();
        if (!keepsSharedLoadPlanSnapshotExplicit(plan, shared_plan)) {
            return error.SharedLoadPlanDrift;
        }
        return shared_plan;
    }

    pub fn releaseWithoutSubstrate(self: *Self) !void {
        if (self.stage_state != .waiting_on_runtime_substrate) return error.InvalidLoaderState;
        self.stage_state = .released_without_substrate;
    }

    pub fn releaseSharedWithoutSubstrate(
        self: *Self,
        shared_request: *runtime_loader.PreparedRequest,
    ) !void {
        try self.releaseWithoutSubstrate();
        try shared_request.releaseWithoutSubstrate();
    }
};

test "runtime kretprobe loader prepares a bounded registration handoff plan" {
    var module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try module.retargetSymbol("do_sys_openat2");
    try module.init();
    _ = try module.runSelftest();

    var loader = RuntimeKretprobeLoader{};
    const plan = try loader.prepare(&module);
    const snapshot = registrationSnapshot(plan);

    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqualStrings("runtime_kretprobe", plan.module_name);
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", plan.anchor);
    try std.testing.expectEqualStrings("zigux_runtime_kretprobe_init", plan.entry_symbol);
    try std.testing.expectEqualStrings("zigux_runtime_kretprobe_exit", plan.exit_symbol);
    try std.testing.expectEqualStrings("register_kretprobe", plan.register_api);
    try std.testing.expectEqualStrings("unregister_kretprobe", plan.unregister_api);
    try std.testing.expectEqualStrings("do_sys_openat2", plan.symbol_name);
    try std.testing.expectEqual(@as(usize, 20), plan.maxactive);
    try std.testing.expectEqual(@sizeOf(runtime_kretprobe_sample.InstancePrivateData), plan.private_data_bytes);
    try std.testing.expect(plan.requires_runtime_substrate);
    try std.testing.expect(plan.provides_selftest_hook);
    try std.testing.expectEqual(runtime_kretprobe_sample.ModuleStage.selftest_complete, plan.handoff_stage);
    try std.testing.expectEqual(@as(usize, 1), plan.summary.skipped_kernel_threads);
    try std.testing.expectEqual(@as(usize, 1), plan.summary.nmissed);
    try std.testing.expectEqual(@as(usize, 42), plan.summary.last_retval);
    try std.testing.expectEqual(@as(i64, 75), plan.summary.last_duration_ns);
    try std.testing.expectEqual(@as(usize, 1), plan.summary.selftest_runs);
    try std.testing.expect(!plan.summary.entry_timestamp_armed);
    try std.testing.expect(keepsRegistrationSnapshotExplicit(plan, snapshot));
    try std.testing.expectEqualStrings("register_kretprobe", snapshot.register_api);
    try std.testing.expectEqualStrings("unregister_kretprobe", snapshot.unregister_api);
    try std.testing.expectEqualStrings("do_sys_openat2", snapshot.symbol_name);
    try std.testing.expectEqual(@as(usize, 20), snapshot.maxactive);
    try std.testing.expectEqual(@sizeOf(runtime_kretprobe_sample.InstancePrivateData), snapshot.private_data_bytes);
    try std.testing.expectEqual(@as(usize, 1), snapshot.skipped_kernel_threads);
    try std.testing.expectEqual(@as(usize, 1), snapshot.nmissed);
    try std.testing.expectEqual(@as(usize, 42), snapshot.last_retval);
    try std.testing.expectEqual(@as(i64, 75), snapshot.last_duration_ns);
    try std.testing.expectEqual(@as(usize, 1), snapshot.selftest_runs);
    try std.testing.expect(!snapshot.entry_timestamp_armed);
}

test "runtime kretprobe loader keeps unavailable substrate and lifecycle guards explicit" {
    var cold_module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try std.testing.expectError(error.InvalidModuleLifecycleForLoader, RuntimeKretprobeLoader.planFor(&cold_module));

    var module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try module.init();

    var loader = RuntimeKretprobeLoader{};
    const prepared = try loader.prepare(&module);
    try std.testing.expectEqual(runtime_kretprobe_sample.ModuleStage.initialized, prepared.handoff_stage);
    try std.testing.expectEqual(@as(usize, 0), prepared.summary.selftest_runs);

    try std.testing.expectError(error.LoaderAlreadyPrepared, loader.prepare(&module));

    const pending_plan = try loader.requestRuntimeLoad();
    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(runtime_kretprobe_sample.ModuleStage.initialized, pending_plan.handoff_stage);

    try loader.releaseWithoutSubstrate();
    try std.testing.expectEqual(LoaderStage.released_without_substrate, loader.stage());
    try std.testing.expectError(error.InvalidLoaderState, loader.requestRuntimeLoad());

    try module.exit();
    try std.testing.expectError(error.InvalidModuleLifecycleForLoader, RuntimeKretprobeLoader.planFor(&module));
}

test "runtime kretprobe loader keeps the prepared snapshot stable across later sample mutation" {
    var module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try module.retargetSymbol("do_sys_openat2");
    try module.init();
    _ = try module.runSelftest();

    var loader = RuntimeKretprobeLoader{};
    const prepared = try loader.prepare(&module);
    const prepared_snapshot = registrationSnapshot(prepared);

    try std.testing.expect(try module.entryHandler(true, 300));
    const updated = try module.retHandler(12, 380);
    try module.recordMissedInstance();

    const live_summary = module.summary();
    const pending_plan = try loader.requestRuntimeLoad();
    const pending_snapshot = registrationSnapshot(pending_plan);

    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(@as(usize, 12), updated.retval);
    try std.testing.expectEqual(@as(i64, 80), updated.duration_ns);
    try std.testing.expectEqual(@as(usize, 2), live_summary.nmissed);
    try std.testing.expectEqual(@as(usize, 1), pending_plan.summary.nmissed);
    try std.testing.expectEqual(@as(usize, 12), live_summary.last_retval);
    try std.testing.expectEqual(@as(usize, 42), pending_plan.summary.last_retval);
    try std.testing.expectEqual(@as(i64, 80), live_summary.last_duration_ns);
    try std.testing.expectEqual(@as(i64, 75), pending_plan.summary.last_duration_ns);
    try std.testing.expectEqual(@as(usize, 1), live_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), pending_plan.summary.selftest_runs);
    try std.testing.expect(!live_summary.entry_timestamp_armed);
    try std.testing.expect(!pending_plan.summary.entry_timestamp_armed);
    try std.testing.expect(keepsRegistrationSnapshotExplicit(pending_plan, prepared_snapshot));
    try std.testing.expect(keepsRegistrationSnapshotExplicit(pending_plan, pending_snapshot));
    try std.testing.expectEqual(@as(usize, 1), prepared_snapshot.nmissed);
    try std.testing.expectEqual(@as(usize, 1), pending_snapshot.nmissed);
    try std.testing.expectEqual(@as(usize, 42), prepared_snapshot.last_retval);
    try std.testing.expectEqual(@as(usize, 42), pending_snapshot.last_retval);
    try std.testing.expectEqual(@as(i64, 75), prepared_snapshot.last_duration_ns);
    try std.testing.expectEqual(@as(i64, 75), pending_snapshot.last_duration_ns);
}

test "runtime kretprobe loader emits the shared runtime-loader contract plan" {
    var module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try module.retargetSymbol("do_sys_openat2");
    try module.init();
    _ = try module.runSelftest();

    var loader = RuntimeKretprobeLoader{};
    const plan = try loader.prepare(&module);
    const shared_plan = toSharedLoadPlan(plan);

    try std.testing.expect(keepsSharedLoadPlanSnapshotExplicit(plan, shared_plan));
    try std.testing.expectEqual(runtime_loader.AllocatorHandoff.kernel_heap, shared_plan.allocator_handoff);
    try std.testing.expectEqual(runtime_loader.HandoffStage.selftest_complete, shared_plan.init_flow.handoff_stage);
    try std.testing.expectEqual(@as(usize, 1), shared_plan.init_flow.init_runs);
    try std.testing.expectEqual(@as(usize, 1), shared_plan.init_flow.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), shared_plan.init_flow.exit_runs);

    var shared_request = try runtime_loader.prepareRequest(shared_plan);
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);

    const pending_plan = try shared_request.requestRuntimeLoad();
    try std.testing.expectEqual(runtime_loader.RequestState.waiting_on_runtime_substrate, shared_request.state);
    try std.testing.expect(keepsSharedLoadPlanSnapshotExplicit(plan, pending_plan));
    try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(
        pending_plan,
        .kernel_heap,
        shared_plan.init_flow,
    ));

    try shared_request.releaseWithoutSubstrate();
    try std.testing.expectEqual(runtime_loader.RequestState.released_without_substrate, shared_request.state);
}

test "runtime kretprobe loader keeps initialized-stage shared contract plans explicit" {
    var module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try module.init();

    var loader = RuntimeKretprobeLoader{};
    const plan = try loader.prepare(&module);
    const shared_plan = toSharedLoadPlan(plan);

    try std.testing.expect(keepsSharedLoadPlanSnapshotExplicit(plan, shared_plan));
    try std.testing.expectEqual(runtime_loader.HandoffStage.initialized, shared_plan.init_flow.handoff_stage);
    try std.testing.expectEqual(@as(usize, 0), shared_plan.init_flow.selftest_runs);

    var shared_request = try runtime_loader.prepareRequest(shared_plan);
    const pending_plan = try shared_request.requestRuntimeLoad();
    try std.testing.expect(keepsSharedLoadPlanSnapshotExplicit(plan, pending_plan));
    try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(
        pending_plan,
        .kernel_heap,
        shared_plan.init_flow,
    ));
}

test "runtime kretprobe loader keeps initialized shared-request snapshots stable across later selftest activity" {
    var module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try module.retargetSymbol("do_sys_openat2");
    try module.init();

    var loader = RuntimeKretprobeLoader{};
    var shared_request = try loader.prepareSharedRequest(&module);
    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);

    const prepared_plan = shared_request.plan;
    try std.testing.expectEqual(runtime_loader.HandoffStage.initialized, prepared_plan.init_flow.handoff_stage);
    try std.testing.expectEqual(@as(usize, 0), prepared_plan.init_flow.selftest_runs);

    const selftest = try module.runSelftest();
    const live_plan = try RuntimeKretprobeLoader.planFor(&module);
    const pending_plan = try loader.requestSharedRuntimeLoad(&shared_request);

    try std.testing.expectEqual(@as(usize, 4), selftest.probe_focus.len);
    try std.testing.expectEqual(runtime_kretprobe_sample.ModuleStage.selftest_complete, live_plan.handoff_stage);
    try std.testing.expectEqualStrings("do_sys_openat2", live_plan.symbol_name);
    try std.testing.expectEqual(@as(usize, 1), live_plan.summary.nmissed);
    try std.testing.expectEqual(@as(usize, 42), live_plan.summary.last_retval);
    try std.testing.expectEqual(@as(i64, 75), live_plan.summary.last_duration_ns);
    try std.testing.expectEqual(@as(usize, 1), live_plan.summary.selftest_runs);
    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.waiting_on_runtime_substrate, shared_request.state);
    try std.testing.expectEqualStrings(prepared_plan.module_name, pending_plan.module_name);
    try std.testing.expectEqualStrings(prepared_plan.anchor, pending_plan.anchor);
    try std.testing.expectEqualStrings(prepared_plan.entry_symbol, pending_plan.entry_symbol);
    try std.testing.expectEqualStrings(prepared_plan.exit_symbol, pending_plan.exit_symbol);
    try std.testing.expectEqual(runtime_loader.HandoffStage.initialized, pending_plan.init_flow.handoff_stage);
    try std.testing.expectEqual(@as(usize, 0), pending_plan.init_flow.selftest_runs);
    try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(
        pending_plan,
        .kernel_heap,
        .{
            .handoff_stage = .initialized,
            .init_runs = 1,
            .selftest_runs = 0,
            .exit_runs = 0,
        },
    ));
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(pending_plan));

    try loader.releaseSharedWithoutSubstrate(&shared_request);
    try std.testing.expectEqual(LoaderStage.released_without_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.released_without_substrate, shared_request.state);
}

test "runtime kretprobe loader bridges the shared request lifecycle without widening registration claims" {
    var module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try module.retargetSymbol("do_sys_openat2");
    try module.init();
    _ = try module.runSelftest();

    var loader = RuntimeKretprobeLoader{};
    var shared_request = try loader.prepareSharedRequest(&module);
    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);

    const pending_plan = try loader.requestSharedRuntimeLoad(&shared_request);
    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.waiting_on_runtime_substrate, shared_request.state);
    try std.testing.expectEqualStrings("runtime_kretprobe", pending_plan.module_name);
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", pending_plan.anchor);
    try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(
        pending_plan,
        .kernel_heap,
        .{
            .handoff_stage = .selftest_complete,
            .init_runs = 1,
            .selftest_runs = 1,
            .exit_runs = 0,
        },
    ));

    try loader.releaseSharedWithoutSubstrate(&shared_request);
    try std.testing.expectEqual(LoaderStage.released_without_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.released_without_substrate, shared_request.state);
}

test "runtime kretprobe loader surfaces shared request drift before any live registration claim" {
    var module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try module.retargetSymbol("do_sys_openat2");
    try module.init();
    _ = try module.runSelftest();

    var loader = RuntimeKretprobeLoader{};
    var shared_request = try loader.prepareSharedRequest(&module);
    shared_request.plan.module_name = "runtime_kretprobe_drift";

    try std.testing.expectError(error.SharedLoadPlanDrift, loader.requestSharedRuntimeLoad(&shared_request));
    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.waiting_on_runtime_substrate, shared_request.state);

    try loader.releaseSharedWithoutSubstrate(&shared_request);
    try std.testing.expectEqual(LoaderStage.released_without_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.released_without_substrate, shared_request.state);
}

test "runtime kretprobe loader rejects shared-load-plan snapshot drift" {
    var module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try module.retargetSymbol("do_sys_openat2");
    try module.init();
    _ = try module.runSelftest();

    const plan = try RuntimeKretprobeLoader.planFor(&module);
    const shared_plan = toSharedLoadPlan(plan);
    try std.testing.expect(keepsSharedLoadPlanSnapshotExplicit(plan, shared_plan));

    var drifted_module = shared_plan;
    drifted_module.module_name = "runtime_kretprobe_drift";
    try std.testing.expect(!keepsSharedLoadPlanSnapshotExplicit(plan, drifted_module));

    var drifted_allocator = shared_plan;
    drifted_allocator.allocator_handoff = .caller_provided;
    try std.testing.expect(!keepsSharedLoadPlanSnapshotExplicit(plan, drifted_allocator));

    var drifted_stage = shared_plan;
    drifted_stage.init_flow.handoff_stage = .initialized;
    try std.testing.expect(!keepsSharedLoadPlanSnapshotExplicit(plan, drifted_stage));

    var drifted_selftest = shared_plan;
    drifted_selftest.init_flow.selftest_runs += 1;
    try std.testing.expect(!keepsSharedLoadPlanSnapshotExplicit(plan, drifted_selftest));
}

test "runtime kretprobe loader rejects registration snapshot drift" {
    var module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try module.retargetSymbol("do_sys_openat2");
    try module.init();
    _ = try module.runSelftest();

    const plan = try RuntimeKretprobeLoader.planFor(&module);
    const snapshot = registrationSnapshot(plan);
    try std.testing.expect(keepsRegistrationSnapshotExplicit(plan, snapshot));

    var drifted_symbol = snapshot;
    drifted_symbol.symbol_name = "do_exit";
    try std.testing.expect(!keepsRegistrationSnapshotExplicit(plan, drifted_symbol));

    var drifted_maxactive = snapshot;
    drifted_maxactive.maxactive += 1;
    try std.testing.expect(!keepsRegistrationSnapshotExplicit(plan, drifted_maxactive));

    var drifted_private_data = snapshot;
    drifted_private_data.private_data_bytes += 8;
    try std.testing.expect(!keepsRegistrationSnapshotExplicit(plan, drifted_private_data));

    var drifted_summary = snapshot;
    drifted_summary.nmissed += 1;
    try std.testing.expect(!keepsRegistrationSnapshotExplicit(plan, drifted_summary));
}

test "runtime kretprobe loader rejects non-idle probe state at the metadata-only handoff boundary" {
    var module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try module.init();
    try std.testing.expect(try module.entryHandler(true, 500));

    try std.testing.expectError(error.OutstandingProbeStateForLoader, RuntimeKretprobeLoader.planFor(&module));

    const drained = try module.retHandler(17, 560);
    try std.testing.expectEqual(@as(usize, 17), drained.retval);
    try std.testing.expectEqual(@as(i64, 60), drained.duration_ns);

    const recovered_plan = try RuntimeKretprobeLoader.planFor(&module);
    try std.testing.expectEqual(@as(usize, 0), recovered_plan.summary.active_instances);
    try std.testing.expect(!recovered_plan.summary.entry_timestamp_armed);
}
