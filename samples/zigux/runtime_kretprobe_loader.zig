const std = @import("std");
const runtime_kretprobe_sample = @import("runtime_kretprobe_sample");
const runtime_loader = @import("runtime_loader");

pub const LoaderStage = runtime_loader.LoaderStage;

pub const RuntimeKretprobeLoadPlan = struct {
    module_name: []const u8,
    command_name: ?[]const u8,
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
            .command_name = null,
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

    pub fn requestRuntimeLoad(self: *Self) !RuntimeKretprobeLoadPlan {
        if (self.stage_state != .prepared) return error.InvalidLoaderState;

        self.stage_state = .waiting_on_runtime_substrate;
        return self.cached_plan orelse error.MissingLoadPlan;
    }

    pub fn requestSharedRuntimeLoad(self: *Self) !runtime_loader.RuntimeLoadRequest {
        const plan = try self.requestRuntimeLoad();
        return toSharedRequest(plan);
    }

    pub fn releaseSharedRuntimeLoadWithoutSubstrate(self: *Self) !runtime_loader.RuntimeLoadRequest {
        const request = try self.requestSharedRuntimeLoad();
        try self.releaseWithoutSubstrate();
        return request.releasedWithoutSubstrate();
    }

    pub fn releaseWithoutSubstrate(self: *Self) !void {
        if (self.stage_state != .waiting_on_runtime_substrate) return error.InvalidLoaderState;
        self.stage_state = .released_without_substrate;
    }
};

pub fn toSharedRequest(plan: RuntimeKretprobeLoadPlan) runtime_loader.RuntimeLoadRequest {
    return .{
        .module_name = plan.module_name,
        .command_name = plan.command_name,
        .anchor = plan.anchor,
        .entry_symbol = plan.entry_symbol,
        .exit_symbol = plan.exit_symbol,
        .requires_runtime_substrate = plan.requires_runtime_substrate,
        .provides_selftest_hook = plan.provides_selftest_hook,
        .handoff_stage = .waiting_on_runtime_substrate,
        .allocator_handoff = runtime_loader.allocatorHandoffFor(.kernel_heap),
        .payload = .{
            .kretprobe = .{
                .register_api = plan.register_api,
                .unregister_api = plan.unregister_api,
                .symbol_name = plan.symbol_name,
                .maxactive = plan.maxactive,
                .private_data_bytes = plan.private_data_bytes,
                .active_instances = plan.summary.active_instances,
                .skipped_kernel_threads = plan.summary.skipped_kernel_threads,
                .nmissed = plan.summary.nmissed,
                .last_retval = plan.summary.last_retval,
                .last_duration_ns = plan.summary.last_duration_ns,
                .selftest_runs = plan.summary.selftest_runs,
                .entry_timestamp_armed = plan.summary.entry_timestamp_armed,
            },
        },
    };
}

test "runtime kretprobe loader prepares a bounded registration handoff plan" {
    var module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try module.retargetSymbol("do_sys_openat2");
    try module.init();
    _ = try module.runSelftest();

    var loader = RuntimeKretprobeLoader{};
    const plan = try loader.prepare(&module);

    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqualStrings("runtime_kretprobe", plan.module_name);
    try std.testing.expectEqual(@as(?[]const u8, null), plan.command_name);
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

test "runtime kretprobe loader emits the shared runtime-loader request shape" {
    var module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try module.retargetSymbol("do_sys_openat2");
    try module.init();
    _ = try module.runSelftest();

    var loader = RuntimeKretprobeLoader{};
    _ = try loader.prepare(&module);

    const request = try loader.requestSharedRuntimeLoad();
    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.LoaderLane.kretprobe, request.lane());
    try std.testing.expectEqual(@as(?[]const u8, null), request.command_name);
    try std.testing.expect(request.keepsCommandNameExplicit());
    try std.testing.expect(request.isWaitingOnRuntimeSubstrate());
    try std.testing.expect(request.keepsInitExitContractExplicit());
    try std.testing.expect(request.keepsStageConsistentWithRuntimeSubstrate());
    try std.testing.expect(request.keepsAllocatorInitFlowConsistent());
    try std.testing.expect(request.keepsSharedHandoffContractExplicit());
    try std.testing.expectEqual(runtime_loader.allocatorHandoffFor(.kernel_heap).init_flow, request.allocator_handoff.init_flow);
    try std.testing.expect(request.allocator_handoff.initializes_owned_state);
    try std.testing.expect(!request.allocator_handoff.requires_reset_on_init);
    try std.testing.expectEqualStrings("register_kretprobe", request.payload.kretprobe.register_api);
    try std.testing.expectEqual(@as(usize, 1), request.payload.kretprobe.selftest_runs);
    try std.testing.expectEqual(runtime_loader.LoaderStage.waiting_on_runtime_substrate, request.handoff_stage);
}

test "runtime kretprobe loader can release the shared runtime-loader request without substrate" {
    var module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try module.retargetSymbol("do_sys_openat2");
    try module.init();
    _ = try module.runSelftest();

    var loader = RuntimeKretprobeLoader{};
    _ = try loader.prepare(&module);

    const released = try loader.releaseSharedRuntimeLoadWithoutSubstrate();
    try std.testing.expectEqual(LoaderStage.released_without_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.LoaderLane.kretprobe, released.lane());
    try std.testing.expectEqual(@as(?[]const u8, null), released.command_name);
    try std.testing.expect(released.keepsCommandNameExplicit());
    try std.testing.expect(released.isReleasedWithoutSubstrate());
    try std.testing.expect(!released.isWaitingOnRuntimeSubstrate());
    try std.testing.expect(released.keepsInitExitContractExplicit());
    try std.testing.expect(released.keepsStageConsistentWithRuntimeSubstrate());
    try std.testing.expect(released.keepsAllocatorInitFlowConsistent());
    try std.testing.expect(released.keepsSharedHandoffContractExplicit());
    try std.testing.expectEqual(runtime_loader.allocatorHandoffFor(.kernel_heap).init_flow, released.allocator_handoff.init_flow);
    try std.testing.expect(released.allocator_handoff.initializes_owned_state);
    try std.testing.expect(!released.allocator_handoff.requires_reset_on_init);
    try std.testing.expectEqual(runtime_loader.LoaderStage.released_without_substrate, released.handoff_stage);
    try std.testing.expectEqualStrings("register_kretprobe", released.payload.kretprobe.register_api);
    try std.testing.expectEqualStrings("unregister_kretprobe", released.payload.kretprobe.unregister_api);
    try std.testing.expectEqualStrings("do_sys_openat2", released.payload.kretprobe.symbol_name);
    try std.testing.expectEqual(@as(usize, 20), released.payload.kretprobe.maxactive);
    try std.testing.expectEqual(@sizeOf(runtime_kretprobe_sample.InstancePrivateData), released.payload.kretprobe.private_data_bytes);
    try std.testing.expectEqual(@as(usize, 1), released.payload.kretprobe.nmissed);
    try std.testing.expectEqual(@as(usize, 1), released.payload.kretprobe.selftest_runs);
    try std.testing.expectEqual(@as(usize, 42), released.payload.kretprobe.last_retval);
    try std.testing.expectEqual(@as(i64, 75), released.payload.kretprobe.last_duration_ns);
    try std.testing.expectEqualStrings("zigux_runtime_kretprobe_init", released.entry_symbol);
    try std.testing.expectEqualStrings("zigux_runtime_kretprobe_exit", released.exit_symbol);
    try std.testing.expectError(error.InvalidLoaderState, loader.requestSharedRuntimeLoad());
}
