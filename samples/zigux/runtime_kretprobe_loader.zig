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

fn sharedHandoffStage(stage: runtime_kretprobe_sample.ModuleStage) runtime_loader.HandoffStage {
    return switch (stage) {
        .initialized => .initialized,
        .selftest_complete => .selftest_complete,
        else => unreachable,
    };
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

    pub fn prepareSharedRequest(
        self: *Self,
        module: *const runtime_kretprobe_sample.RuntimeKretprobeSample,
    ) !runtime_loader.PreparedRequest {
        const plan = try self.prepare(module);
        errdefer {
            self.cached_plan = null;
            self.stage_state = .idle;
        }
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
        if (self.stage_state != .prepared) return error.InvalidLoaderState;
        if (shared_request.state != .prepared) return error.InvalidLoaderState;
        if (!runtime_loader.keepsLoadPlanExplicit(shared_request.plan, shared_request.prepared_plan)) {
            return error.PreparedPlanDrift;
        }
        _ = try runtime_loader.prepareRequest(shared_request.plan);

        const plan = self.cached_plan orelse return error.MissingLoadPlan;
        if (!keepsSharedLoadPlanSnapshotExplicit(plan, shared_request.plan)) {
            return error.SharedLoadPlanDrift;
        }

        _ = try self.requestRuntimeLoad();
        return shared_request.requestRuntimeLoad();
    }

    pub fn releaseWithoutSubstrate(self: *Self) !void {
        if (self.stage_state != .waiting_on_runtime_substrate) return error.InvalidLoaderState;
        self.stage_state = .released_without_substrate;
    }

    pub fn releaseSharedWithoutSubstrate(
        self: *Self,
        shared_request: *runtime_loader.PreparedRequest,
    ) !void {
        if (self.stage_state != .waiting_on_runtime_substrate) return error.InvalidLoaderState;
        try shared_request.releaseWithoutSubstrate();
        self.stage_state = .released_without_substrate;
    }
};

test "runtime kretprobe loader prepares a bounded registration handoff plan" {
    var module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try module.retargetSymbol("do_sys_openat2");
    try module.init();
    _ = try module.runSelftest();

    var loader = RuntimeKretprobeLoader{};
    const plan = try loader.prepare(&module);

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

    try std.testing.expect(try module.entryHandler(true, 300));
    const updated = try module.retHandler(12, 380);
    try module.recordMissedInstance();

    const live_summary = module.summary();
    const pending_plan = try loader.requestRuntimeLoad();

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

    _ = prepared;
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
    const initialized_summary = module.summary();
    try std.testing.expect(prepared_plan.provides_selftest_hook);
    try std.testing.expectEqual(runtime_loader.HandoffStage.initialized, prepared_plan.init_flow.handoff_stage);
    try std.testing.expectEqual(@as(usize, 0), prepared_plan.init_flow.selftest_runs);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        prepared_plan,
    ));
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(prepared_plan));
    try std.testing.expectEqualStrings("do_sys_openat2", initialized_summary.symbol_name);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.active_instances);
    try std.testing.expect(!initialized_summary.entry_timestamp_armed);

    _ = try module.runSelftest();
    const live_plan = try RuntimeKretprobeLoader.planFor(&module);
    const pending_plan = try loader.requestSharedRuntimeLoad(&shared_request);

    try std.testing.expectEqual(runtime_kretprobe_sample.ModuleStage.selftest_complete, live_plan.handoff_stage);
    try std.testing.expectEqual(@as(usize, 1), live_plan.summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), live_plan.summary.nmissed);
    try std.testing.expectEqual(@as(usize, 42), live_plan.summary.last_retval);
    try std.testing.expectEqual(@as(i64, 75), live_plan.summary.last_duration_ns);
    try std.testing.expect(!live_plan.summary.entry_timestamp_armed);
    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.waiting_on_runtime_substrate, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .waiting_on_runtime_substrate,
        pending_plan,
    ));
    try std.testing.expectEqualStrings(prepared_plan.module_name, pending_plan.module_name);
    try std.testing.expectEqualStrings(prepared_plan.anchor, pending_plan.anchor);
    try std.testing.expectEqualStrings(prepared_plan.entry_symbol, pending_plan.entry_symbol);
    try std.testing.expectEqualStrings(prepared_plan.exit_symbol, pending_plan.exit_symbol);
    try std.testing.expect(pending_plan.provides_selftest_hook);
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
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .released_without_substrate,
        pending_plan,
    ));
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

test "runtime kretprobe loader keeps shared release failures from desynchronizing loader state" {
    var module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try module.retargetSymbol("do_sys_openat2");
    try module.init();
    _ = try module.runSelftest();

    var loader = RuntimeKretprobeLoader{};
    var shared_request = try loader.prepareSharedRequest(&module);
    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        shared_request.plan,
    ));

    _ = try loader.requestRuntimeLoad();
    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        shared_request.plan,
    ));

    try std.testing.expectError(error.InvalidLoaderState, loader.releaseSharedWithoutSubstrate(&shared_request));
    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        shared_request.plan,
    ));

    const pending_plan = try shared_request.requestRuntimeLoad();
    try loader.releaseSharedWithoutSubstrate(&shared_request);
    try std.testing.expectEqual(LoaderStage.released_without_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.released_without_substrate, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .released_without_substrate,
        pending_plan,
    ));
}

test "runtime kretprobe loader keeps direct shared runtime-load transitions from desynchronizing shared release state" {
    var module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try module.retargetSymbol("do_sys_openat2");
    try module.init();
    _ = try module.runSelftest();

    var loader = RuntimeKretprobeLoader{};
    var shared_request = try loader.prepareSharedRequest(&module);
    const pending_plan = try shared_request.requestRuntimeLoad();

    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.waiting_on_runtime_substrate, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .waiting_on_runtime_substrate,
        pending_plan,
    ));

    try std.testing.expectError(error.InvalidLoaderState, loader.releaseSharedWithoutSubstrate(&shared_request));
    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.waiting_on_runtime_substrate, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .waiting_on_runtime_substrate,
        pending_plan,
    ));
}

test "runtime kretprobe loader surfaces prepared shared selftest-hook drift before any live registration claim" {
    var module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try module.retargetSymbol("do_sys_openat2");
    try module.init();
    _ = try module.runSelftest();

    var loader = RuntimeKretprobeLoader{};
    var shared_request = try loader.prepareSharedRequest(&module);
    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        shared_request.plan,
    ));
    try std.testing.expect(shared_request.plan.provides_selftest_hook);
    shared_request.plan.provides_selftest_hook = false;
    try std.testing.expect(!runtime_loader.keepsSelftestHookEvidenceConsistent(shared_request.plan));

    try std.testing.expectError(error.InvalidSelftestHookEvidence, loader.requestSharedRuntimeLoad(&shared_request));
    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        shared_request.plan,
    ));
}

test "runtime kretprobe loader rejects prepared shared runtime-substrate drift before any live registration claim" {
    var module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try module.retargetSymbol("do_sys_openat2");
    try module.init();
    _ = try module.runSelftest();

    var loader = RuntimeKretprobeLoader{};
    var shared_request = try loader.prepareSharedRequest(&module);
    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        shared_request.plan,
    ));
    shared_request.plan.requires_runtime_substrate = false;

    try std.testing.expectError(error.LoaderNotRequired, loader.requestSharedRuntimeLoad(&shared_request));
    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        shared_request.plan,
    ));
}

test "runtime kretprobe loader rejects prepared shared allocator and init-flow drift before any live registration claim" {
    var module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try module.retargetSymbol("do_sys_openat2");
    try module.init();
    _ = try module.runSelftest();

    var allocator_loader = RuntimeKretprobeLoader{};
    var allocator_request = try allocator_loader.prepareSharedRequest(&module);
    const prepared_allocator_plan = allocator_request.plan;
    try std.testing.expectEqual(LoaderStage.prepared, allocator_loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, allocator_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        allocator_request,
        .prepared,
        allocator_request.plan,
    ));
    allocator_request.plan.allocator_handoff = .caller_provided;

    try std.testing.expectError(error.PreparedPlanDrift, allocator_loader.requestSharedRuntimeLoad(&allocator_request));
    try std.testing.expectEqual(LoaderStage.prepared, allocator_loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, allocator_request.state);
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(
        allocator_request.prepared_plan,
        prepared_allocator_plan,
    ));
    try std.testing.expect(!runtime_loader.keepsLoadPlanExplicit(
        allocator_request.plan,
        prepared_allocator_plan,
    ));

    var init_flow_loader = RuntimeKretprobeLoader{};
    var init_flow_request = try init_flow_loader.prepareSharedRequest(&module);
    const prepared_init_flow_plan = init_flow_request.plan;
    try std.testing.expectEqual(LoaderStage.prepared, init_flow_loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, init_flow_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        init_flow_request,
        .prepared,
        init_flow_request.plan,
    ));
    init_flow_request.plan.init_flow.handoff_stage = .initialized;
    init_flow_request.plan.init_flow.selftest_runs = 0;

    try std.testing.expectError(error.PreparedPlanDrift, init_flow_loader.requestSharedRuntimeLoad(&init_flow_request));
    try std.testing.expectEqual(LoaderStage.prepared, init_flow_loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, init_flow_request.state);
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(
        init_flow_request.prepared_plan,
        prepared_init_flow_plan,
    ));
    try std.testing.expect(!runtime_loader.keepsLoadPlanExplicit(
        init_flow_request.plan,
        prepared_init_flow_plan,
    ));
}

test "runtime kretprobe loader surfaces shared request drift before any live registration claim" {
    var module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try module.retargetSymbol("do_sys_openat2");
    try module.init();
    _ = try module.runSelftest();

    var loader = RuntimeKretprobeLoader{};
    var shared_request = try loader.prepareSharedRequest(&module);
    const prepared_plan = loader.cached_plan orelse unreachable;
    const prepared_shared_plan = shared_request.prepared_plan;
    const prepared_request_plan = shared_request.plan;
    shared_request.plan.module_name = "runtime_kretprobe_drift";

    try std.testing.expectError(error.SharedLoadPlanDrift, loader.requestSharedRuntimeLoad(&shared_request));
    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);
    try std.testing.expectEqualStrings(prepared_plan.module_name, (loader.cached_plan orelse unreachable).module_name);
    try std.testing.expectEqualStrings(prepared_plan.anchor, (loader.cached_plan orelse unreachable).anchor);
    try std.testing.expectEqualStrings(prepared_shared_plan.module_name, shared_request.prepared_plan.module_name);
    try std.testing.expectEqualStrings(prepared_request_plan.anchor, shared_request.plan.anchor);
    try std.testing.expectEqualStrings("runtime_kretprobe_drift", shared_request.plan.module_name);
}

test "runtime kretprobe loader rejects non-prepared shared requests before any live registration claim" {
    var module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try module.retargetSymbol("do_sys_openat2");
    try module.init();
    _ = try module.runSelftest();

    var loader = RuntimeKretprobeLoader{};
    var shared_request = try loader.prepareSharedRequest(&module);
    _ = try shared_request.requestRuntimeLoad();

    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.waiting_on_runtime_substrate, shared_request.state);
    try std.testing.expectError(error.InvalidLoaderState, loader.requestSharedRuntimeLoad(&shared_request));
    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.waiting_on_runtime_substrate, shared_request.state);
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

test "runtime kretprobe loader keeps selftest-complete shared-request snapshots stable across later exit activity" {
    var module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try module.retargetSymbol("do_sys_openat2");
    try module.init();
    _ = try module.runSelftest();

    var loader = RuntimeKretprobeLoader{};
    var shared_request = try loader.prepareSharedRequest(&module);
    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);

    const prepared_plan = shared_request.plan;
    const selftested_summary = module.summary();
    try std.testing.expect(prepared_plan.provides_selftest_hook);
    try std.testing.expectEqual(runtime_loader.HandoffStage.selftest_complete, prepared_plan.init_flow.handoff_stage);
    try std.testing.expectEqual(@as(usize, 1), prepared_plan.init_flow.selftest_runs);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        prepared_plan,
    ));
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(prepared_plan));
    try std.testing.expectEqualStrings("do_sys_openat2", selftested_summary.symbol_name);
    try std.testing.expectEqual(@as(usize, 1), selftested_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), selftested_summary.active_instances);
    try std.testing.expectEqual(@as(usize, 42), selftested_summary.last_retval);
    try std.testing.expectEqual(@as(i64, 75), selftested_summary.last_duration_ns);
    try std.testing.expect(!selftested_summary.entry_timestamp_armed);

    const exit_report = try module.exit();
    try std.testing.expectEqualStrings("do_sys_openat2", exit_report.symbol_name);
    try std.testing.expectEqual(@as(usize, 1), exit_report.selftest_runs);
    try std.testing.expectEqual(runtime_kretprobe_sample.ModuleStage.exited, module.stage());
    try std.testing.expectError(error.InvalidModuleLifecycleForLoader, RuntimeKretprobeLoader.planFor(&module));

    const pending_plan = try loader.requestSharedRuntimeLoad(&shared_request);

    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.waiting_on_runtime_substrate, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .waiting_on_runtime_substrate,
        pending_plan,
    ));
    try std.testing.expectEqualStrings(prepared_plan.module_name, pending_plan.module_name);
    try std.testing.expectEqualStrings(prepared_plan.anchor, pending_plan.anchor);
    try std.testing.expectEqualStrings(prepared_plan.entry_symbol, pending_plan.entry_symbol);
    try std.testing.expectEqualStrings(prepared_plan.exit_symbol, pending_plan.exit_symbol);
    try std.testing.expect(pending_plan.provides_selftest_hook);
    try std.testing.expectEqual(runtime_loader.HandoffStage.selftest_complete, pending_plan.init_flow.handoff_stage);
    try std.testing.expectEqual(@as(usize, 1), pending_plan.init_flow.selftest_runs);
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
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(pending_plan));

    try loader.releaseSharedWithoutSubstrate(&shared_request);
    try std.testing.expectEqual(LoaderStage.released_without_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.released_without_substrate, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .released_without_substrate,
        pending_plan,
    ));
}
