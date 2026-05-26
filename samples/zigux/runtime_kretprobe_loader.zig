const std = @import("std");
const runtime_kretprobe_sample = @import("runtime_kretprobe_sample");
const runtime_loader = @import("runtime_loader");

pub const LoaderStage = enum(u8) {
    cold,
    prepared,
    waiting_on_runtime_substrate,
    released_without_substrate,
};

pub const RuntimeKretprobeLoader = struct {
    const Self = @This();

    stage_state: LoaderStage = .cold,
    allocator_handoff: runtime_loader.AllocatorHandoff = .kernel_heap,

    pub fn stage(self: *const Self) LoaderStage {
        return self.stage_state;
    }

    pub fn planFor(
        module: *const runtime_kretprobe_sample.RuntimeKretprobeSample,
        allocator_handoff: runtime_loader.AllocatorHandoff,
    ) !runtime_loader.LoadPlan {
        const descriptor = runtime_kretprobe_sample.RuntimeKretprobeSample.descriptor();
        const snapshot = module.lifecycleSnapshot();
        const handoff_stage = switch (snapshot.stage) {
            .initialized => runtime_loader.HandoffStage.initialized,
            .selftest_complete => runtime_loader.HandoffStage.selftest_complete,
            else => return error.InvalidLifecycleTransition,
        };

        return .{
            .module_name = descriptor.name,
            .anchor = descriptor.anchor,
            .entry_symbol = "zigux_runtime_kretprobe_init",
            .exit_symbol = "zigux_runtime_kretprobe_exit",
            .requires_runtime_substrate = descriptor.requires_runtime_substrate,
            .provides_selftest_hook = descriptor.provides_selftest_hook,
            .allocator_handoff = allocator_handoff,
            .init_flow = .{
                .handoff_stage = handoff_stage,
                .init_runs = snapshot.init_runs,
                .selftest_runs = snapshot.selftest_runs,
                .exit_runs = snapshot.exit_runs,
            },
        };
    }

    pub fn prepareSharedRequest(
        self: *Self,
        module: *const runtime_kretprobe_sample.RuntimeKretprobeSample,
    ) !runtime_loader.PreparedRequest {
        if (self.stage_state != .cold) return error.InvalidLoaderState;

        const shared_plan = try planFor(module, self.allocator_handoff);
        const request = try runtime_loader.prepareRequest(shared_plan);
        self.stage_state = .prepared;
        return request;
    }

    pub fn requestSharedRuntimeLoad(
        self: *Self,
        request: *runtime_loader.PreparedRequest,
    ) !runtime_loader.LoadPlan {
        if (self.stage_state != .prepared) return error.InvalidLoaderState;

        const pending_plan = try request.requestRuntimeLoad();
        self.stage_state = .waiting_on_runtime_substrate;
        return pending_plan;
    }

    pub fn releaseSharedWithoutSubstrate(
        self: *Self,
        request: *runtime_loader.PreparedRequest,
    ) !void {
        if (self.stage_state != .waiting_on_runtime_substrate) return error.InvalidLoaderState;

        try request.releaseWithoutSubstrate();
        self.stage_state = .released_without_substrate;
    }
};

test "runtime kretprobe loader keeps initialized-stage shared contract plans explicit" {
    var module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try module.init();

    var loader = RuntimeKretprobeLoader{};
    var shared_request = try loader.prepareSharedRequest(&module);
    const shared_plan = shared_request.plan;

    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);
    try std.testing.expectEqualStrings("runtime_kretprobe", shared_plan.module_name);
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", shared_plan.anchor);
    try std.testing.expectEqualStrings("zigux_runtime_kretprobe_init", shared_plan.entry_symbol);
    try std.testing.expectEqualStrings("zigux_runtime_kretprobe_exit", shared_plan.exit_symbol);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        shared_plan,
    ));
    try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(
        shared_plan,
        .kernel_heap,
        .{
            .handoff_stage = .initialized,
            .init_runs = 1,
            .selftest_runs = 0,
            .exit_runs = 0,
        },
    ));
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(shared_plan));

    const pending_plan = try loader.requestSharedRuntimeLoad(&shared_request);
    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(
        runtime_loader.RequestState.waiting_on_runtime_substrate,
        shared_request.state,
    );
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .waiting_on_runtime_substrate,
        pending_plan,
    ));
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(pending_plan, shared_plan));

    try loader.releaseSharedWithoutSubstrate(&shared_request);
    try std.testing.expectEqual(LoaderStage.released_without_substrate, loader.stage());
    try std.testing.expectEqual(
        runtime_loader.RequestState.released_without_substrate,
        shared_request.state,
    );
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .released_without_substrate,
        pending_plan,
    ));
}

test "runtime kretprobe loader keeps initialized shared-request snapshots stable across later selftest activity" {
    var module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try module.init();

    var loader = RuntimeKretprobeLoader{};
    var shared_request = try loader.prepareSharedRequest(&module);
    const prepared_plan = shared_request.plan;
    const initialized_snapshot = module.lifecycleSnapshot();

    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(
        runtime_loader.RequestState.prepared,
        shared_request.state,
    );
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        prepared_plan,
    ));
    try std.testing.expectEqualStrings("runtime_kretprobe", prepared_plan.module_name);
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", prepared_plan.anchor);
    try std.testing.expectEqualStrings("zigux_runtime_kretprobe_init", prepared_plan.entry_symbol);
    try std.testing.expectEqualStrings("zigux_runtime_kretprobe_exit", prepared_plan.exit_symbol);
    try std.testing.expect(prepared_plan.requires_runtime_substrate);
    try std.testing.expect(prepared_plan.provides_selftest_hook);
    try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(
        prepared_plan,
        .kernel_heap,
        .{
            .handoff_stage = .initialized,
            .init_runs = 1,
            .selftest_runs = 0,
            .exit_runs = 0,
        },
    ));
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(prepared_plan));
    try std.testing.expectEqual(runtime_kretprobe_sample.ModuleStage.initialized, initialized_snapshot.stage);
    try std.testing.expectEqual(@as(usize, 1), initialized_snapshot.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.registration_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.unregistration_runs);
    try std.testing.expect(!initialized_snapshot.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.active_instances);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.completed_instances);
    try std.testing.expectEqual(@as(?i32, null), initialized_snapshot.last_retval);

    _ = try module.runSelftest();
    const live_plan = try RuntimeKretprobeLoader.planFor(&module, .kernel_heap);
    const live_snapshot = module.lifecycleSnapshot();
    const pending_plan = try loader.requestSharedRuntimeLoad(&shared_request);

    try std.testing.expectEqual(
        runtime_kretprobe_sample.ModuleStage.selftest_complete,
        live_snapshot.stage,
    );
    try std.testing.expectEqual(@as(usize, 1), live_snapshot.init_runs);
    try std.testing.expectEqual(@as(usize, 1), live_snapshot.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), live_snapshot.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), live_snapshot.registration_runs);
    try std.testing.expectEqual(@as(usize, 1), live_snapshot.unregistration_runs);
    try std.testing.expect(!live_snapshot.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), live_snapshot.active_instances);
    try std.testing.expectEqual(@as(usize, 1), live_snapshot.completed_instances);
    try std.testing.expectEqual(@as(?i32, 0), live_snapshot.last_retval);
    try std.testing.expectEqual(
        runtime_loader.HandoffStage.selftest_complete,
        live_plan.init_flow.handoff_stage,
    );
    try std.testing.expectEqual(@as(usize, 1), live_plan.init_flow.selftest_runs);
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(live_plan));
    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(
        runtime_loader.RequestState.waiting_on_runtime_substrate,
        shared_request.state,
    );
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .waiting_on_runtime_substrate,
        pending_plan,
    ));
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(pending_plan, prepared_plan));
    try std.testing.expectEqualStrings(prepared_plan.module_name, pending_plan.module_name);
    try std.testing.expectEqualStrings(prepared_plan.anchor, pending_plan.anchor);
    try std.testing.expectEqualStrings(prepared_plan.entry_symbol, pending_plan.entry_symbol);
    try std.testing.expectEqualStrings(prepared_plan.exit_symbol, pending_plan.exit_symbol);
    try std.testing.expect(pending_plan.requires_runtime_substrate);
    try std.testing.expect(pending_plan.provides_selftest_hook);
    try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(
        pending_plan,
        .kernel_heap,
        prepared_plan.init_flow,
    ));
    try std.testing.expectEqual(
        runtime_loader.HandoffStage.initialized,
        pending_plan.init_flow.handoff_stage,
    );
    try std.testing.expectEqual(@as(usize, 0), pending_plan.init_flow.selftest_runs);
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(pending_plan));

    try loader.releaseSharedWithoutSubstrate(&shared_request);
    try std.testing.expectEqual(LoaderStage.released_without_substrate, loader.stage());
    try std.testing.expectEqual(
        runtime_loader.RequestState.released_without_substrate,
        shared_request.state,
    );
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .released_without_substrate,
        pending_plan,
    ));
}

test "runtime kretprobe loader keeps initialized reusable probe cycles from drifting shared-request plans before selftest" {
    var module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try module.init();
    try module.registerProbe();
    try module.recordEntry();
    try module.recordReturn(19);
    try module.unregisterProbe();

    const initialized_cycle_snapshot = module.lifecycleSnapshot();
    try std.testing.expectEqual(runtime_kretprobe_sample.ModuleStage.initialized, initialized_cycle_snapshot.stage);
    try std.testing.expectEqual(@as(usize, 1), initialized_cycle_snapshot.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_cycle_snapshot.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_cycle_snapshot.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), initialized_cycle_snapshot.registration_runs);
    try std.testing.expectEqual(@as(usize, 1), initialized_cycle_snapshot.unregistration_runs);
    try std.testing.expect(!initialized_cycle_snapshot.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), initialized_cycle_snapshot.active_instances);
    try std.testing.expectEqual(@as(usize, 1), initialized_cycle_snapshot.completed_instances);
    try std.testing.expectEqual(@as(?i32, 19), initialized_cycle_snapshot.last_retval);

    var loader = RuntimeKretprobeLoader{ .allocator_handoff = .arena };
    var shared_request = try loader.prepareSharedRequest(&module);
    const prepared_plan = shared_request.plan;
    const live_plan = try RuntimeKretprobeLoader.planFor(&module, .arena);

    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        prepared_plan,
    ));
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(live_plan, prepared_plan));
    try std.testing.expectEqualStrings("runtime_kretprobe", prepared_plan.module_name);
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", prepared_plan.anchor);
    try std.testing.expectEqualStrings("zigux_runtime_kretprobe_init", prepared_plan.entry_symbol);
    try std.testing.expectEqualStrings("zigux_runtime_kretprobe_exit", prepared_plan.exit_symbol);
    try std.testing.expect(prepared_plan.requires_runtime_substrate);
    try std.testing.expect(prepared_plan.provides_selftest_hook);
    try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(
        prepared_plan,
        .arena,
        .{
            .handoff_stage = .initialized,
            .init_runs = 1,
            .selftest_runs = 0,
            .exit_runs = 0,
        },
    ));
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(prepared_plan));

    const pending_plan = try loader.requestSharedRuntimeLoad(&shared_request);
    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(
        runtime_loader.RequestState.waiting_on_runtime_substrate,
        shared_request.state,
    );
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .waiting_on_runtime_substrate,
        pending_plan,
    ));
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(pending_plan, prepared_plan));
    try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(
        pending_plan,
        .arena,
        prepared_plan.init_flow,
    ));
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(pending_plan));

    try loader.releaseSharedWithoutSubstrate(&shared_request);
    try std.testing.expectEqual(LoaderStage.released_without_substrate, loader.stage());
    try std.testing.expectEqual(
        runtime_loader.RequestState.released_without_substrate,
        shared_request.state,
    );
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .released_without_substrate,
        pending_plan,
    ));
}

test "runtime kretprobe loader keeps invalid loader transitions fail-closed without disturbing shared-request snapshots" {
    var module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try module.init();

    var loader = RuntimeKretprobeLoader{};
    var shared_request = try loader.prepareSharedRequest(&module);
    const prepared_plan = shared_request.plan;

    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        prepared_plan,
    ));

    try std.testing.expectError(error.InvalidLoaderState, loader.prepareSharedRequest(&module));
    try std.testing.expectError(
        error.InvalidLoaderState,
        loader.releaseSharedWithoutSubstrate(&shared_request),
    );
    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        prepared_plan,
    ));

    const pending_plan = try loader.requestSharedRuntimeLoad(&shared_request);
    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(
        runtime_loader.RequestState.waiting_on_runtime_substrate,
        shared_request.state,
    );
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .waiting_on_runtime_substrate,
        pending_plan,
    ));
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(pending_plan, prepared_plan));

    try std.testing.expectError(error.InvalidLoaderState, loader.prepareSharedRequest(&module));
    try std.testing.expectError(
        error.InvalidLoaderState,
        loader.requestSharedRuntimeLoad(&shared_request),
    );
    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(
        runtime_loader.RequestState.waiting_on_runtime_substrate,
        shared_request.state,
    );
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .waiting_on_runtime_substrate,
        pending_plan,
    ));

    try loader.releaseSharedWithoutSubstrate(&shared_request);
    try std.testing.expectEqual(LoaderStage.released_without_substrate, loader.stage());
    try std.testing.expectEqual(
        runtime_loader.RequestState.released_without_substrate,
        shared_request.state,
    );
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .released_without_substrate,
        pending_plan,
    ));

    try std.testing.expectError(error.InvalidLoaderState, loader.prepareSharedRequest(&module));
    try std.testing.expectError(
        error.InvalidLoaderState,
        loader.requestSharedRuntimeLoad(&shared_request),
    );
    try std.testing.expectError(
        error.InvalidLoaderState,
        loader.releaseSharedWithoutSubstrate(&shared_request),
    );
    try std.testing.expectEqual(LoaderStage.released_without_substrate, loader.stage());
    try std.testing.expectEqual(
        runtime_loader.RequestState.released_without_substrate,
        shared_request.state,
    );
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .released_without_substrate,
        pending_plan,
    ));
}

test "runtime kretprobe loader keeps selftest-complete shared requests blocked by the current loader family contract" {
    var module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try module.init();
    _ = try module.runSelftest();

    var loader = RuntimeKretprobeLoader{ .allocator_handoff = .caller_provided };
    const selftested_plan = try RuntimeKretprobeLoader.planFor(&module, .caller_provided);

    try std.testing.expectEqual(runtime_loader.HandoffStage.selftest_complete, selftested_plan.init_flow.handoff_stage);
    try std.testing.expectEqual(@as(usize, 1), selftested_plan.init_flow.selftest_runs);
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(selftested_plan));
    try std.testing.expectError(error.InvalidPilotFamilyShape, loader.prepareSharedRequest(&module));
    try std.testing.expectEqual(LoaderStage.cold, loader.stage());
}

test "runtime kretprobe loader rejects cold and exited sample stages before preparing a shared request" {
    var cold_module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try std.testing.expectError(
        error.InvalidLifecycleTransition,
        RuntimeKretprobeLoader.planFor(&cold_module, .kernel_heap),
    );

    var exited_module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try exited_module.init();
    try exited_module.exit();
    try std.testing.expectError(
        error.InvalidLifecycleTransition,
        RuntimeKretprobeLoader.planFor(&exited_module, .kernel_heap),
    );
}
