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

fn optionalStringEql(lhs: ?[]const u8, rhs: ?[]const u8) bool {
    if (lhs) |lhs_value| {
        return if (rhs) |rhs_value| std.mem.eql(u8, lhs_value, rhs_value) else false;
    }
    return rhs == null;
}

pub fn keepsSharedRequestSnapshotExplicit(
    plan: RuntimeKretprobeLoadPlan,
    request: runtime_loader.RuntimeLoadRequest,
) bool {
    if (request.lane() != .kretprobe) return false;

    return std.mem.eql(u8, request.module_name, plan.module_name) and
        optionalStringEql(plan.command_name, request.command_name) and
        std.mem.eql(u8, request.anchor, plan.anchor) and
        std.mem.eql(u8, request.entry_symbol, plan.entry_symbol) and
        std.mem.eql(u8, request.exit_symbol, plan.exit_symbol) and
        request.requires_runtime_substrate == plan.requires_runtime_substrate and
        request.provides_selftest_hook == plan.provides_selftest_hook and
        std.mem.eql(u8, request.payload.kretprobe.register_api, plan.register_api) and
        std.mem.eql(u8, request.payload.kretprobe.unregister_api, plan.unregister_api) and
        std.mem.eql(u8, request.payload.kretprobe.symbol_name, plan.symbol_name) and
        request.payload.kretprobe.maxactive == plan.maxactive and
        request.payload.kretprobe.private_data_bytes == plan.private_data_bytes and
        request.payload.kretprobe.active_instances == plan.summary.active_instances and
        request.payload.kretprobe.skipped_kernel_threads == plan.summary.skipped_kernel_threads and
        request.payload.kretprobe.nmissed == plan.summary.nmissed and
        request.payload.kretprobe.last_retval == plan.summary.last_retval and
        request.payload.kretprobe.last_duration_ns == plan.summary.last_duration_ns and
        request.payload.kretprobe.init_runs == plan.summary.init_runs and
        request.payload.kretprobe.selftest_runs == plan.summary.selftest_runs and
        request.payload.kretprobe.exit_runs == plan.summary.exit_runs and
        request.payload.kretprobe.entry_timestamp_armed == plan.summary.entry_timestamp_armed;
}

pub const RuntimeKretprobeLoader = struct {
    const Self = @This();

    stage_state: LoaderStage = .idle,
    cached_plan: ?RuntimeKretprobeLoadPlan = null,

    pub fn stage(self: *const Self) LoaderStage {
        return self.stage_state;
    }

    pub fn planFor(module: *const runtime_kretprobe_sample.RuntimeKretprobeSample) !RuntimeKretprobeLoadPlan {
        return planForWithCommandName(module, null);
    }

    pub fn planForWithCommandName(
        module: *const runtime_kretprobe_sample.RuntimeKretprobeSample,
        command_name: ?[]const u8,
    ) !RuntimeKretprobeLoadPlan {
        const descriptor = runtime_kretprobe_sample.RuntimeKretprobeSample.descriptor();
        const module_stage = module.stage();
        switch (module_stage) {
            .initialized, .selftest_complete => {},
            else => return error.InvalidModuleLifecycleForLoader,
        }

        if (!descriptor.requires_runtime_substrate) return error.LoaderNotRequired;
        if (command_name) |name| {
            if (name.len == 0) return error.EmptyCommandName;
        }

        const summary = module.summary();
        return .{
            .module_name = descriptor.name,
            .command_name = command_name,
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
        return prepareWithCommandName(self, module, null);
    }

    pub fn prepareWithCommandName(
        self: *Self,
        module: *const runtime_kretprobe_sample.RuntimeKretprobeSample,
        command_name: ?[]const u8,
    ) !RuntimeKretprobeLoadPlan {
        if (self.stage_state != .idle) return error.LoaderAlreadyPrepared;

        const plan = try planForWithCommandName(module, command_name);
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
    return (runtime_loader.RuntimeLoadRequest{
        .module_name = plan.module_name,
        .command_name = plan.command_name,
        .anchor = plan.anchor,
        .entry_symbol = plan.entry_symbol,
        .exit_symbol = plan.exit_symbol,
        .requires_runtime_substrate = plan.requires_runtime_substrate,
        .provides_selftest_hook = plan.provides_selftest_hook,
        .handoff_stage = .prepared,
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
                .init_runs = plan.summary.init_runs,
                .selftest_runs = plan.summary.selftest_runs,
                .exit_runs = plan.summary.exit_runs,
                .entry_timestamp_armed = plan.summary.entry_timestamp_armed,
            },
        },
    }).waitingOnRuntimeSubstrate();
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
    try std.testing.expectEqual(runtime_kretprobe_sample.ModuleStage.selftest_complete, plan.summary.stage);
    try std.testing.expectEqual(@as(usize, 1), plan.summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), plan.summary.skipped_kernel_threads);
    try std.testing.expectEqual(@as(usize, 1), plan.summary.nmissed);
    try std.testing.expectEqual(@as(usize, 42), plan.summary.last_retval);
    try std.testing.expectEqual(@as(i64, 75), plan.summary.last_duration_ns);
    try std.testing.expectEqual(@as(usize, 1), plan.summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), plan.summary.exit_runs);
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
    try std.testing.expectEqual(runtime_kretprobe_sample.ModuleStage.initialized, prepared.summary.stage);
    try std.testing.expectEqual(@as(usize, 1), prepared.summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), prepared.summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), prepared.summary.exit_runs);

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

test "runtime kretprobe loader snapshots the prepared probe summary before later sample mutation" {
    var module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try module.retargetSymbol("do_sys_openat2");
    try module.init();

    var loader = RuntimeKretprobeLoader{};
    const prepared = try loader.prepare(&module);

    const selftest = try module.runSelftest();
    const mutated_summary = module.summary();
    try std.testing.expectEqual(runtime_kretprobe_sample.ModuleStage.selftest_complete, mutated_summary.stage);
    try std.testing.expectEqualStrings("do_sys_openat2", selftest.symbol_name);
    try std.testing.expectEqualStrings("do_sys_openat2", mutated_summary.symbol_name);
    try std.testing.expectEqual(@as(usize, 0), prepared.summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), prepared.summary.skipped_kernel_threads);
    try std.testing.expectEqual(@as(usize, 0), prepared.summary.nmissed);
    try std.testing.expectEqual(@as(usize, 0), prepared.summary.last_retval);
    try std.testing.expectEqual(@as(i64, 0), prepared.summary.last_duration_ns);
    try std.testing.expect(!prepared.summary.entry_timestamp_armed);
    try std.testing.expectEqual(@as(usize, 1), mutated_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), mutated_summary.skipped_kernel_threads);
    try std.testing.expectEqual(@as(usize, 1), mutated_summary.nmissed);
    try std.testing.expectEqual(@as(usize, 42), mutated_summary.last_retval);
    try std.testing.expectEqual(@as(i64, 75), mutated_summary.last_duration_ns);
    try std.testing.expect(!mutated_summary.entry_timestamp_armed);

    const pending_plan = try loader.requestRuntimeLoad();
    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(runtime_kretprobe_sample.ModuleStage.initialized, prepared.handoff_stage);
    try std.testing.expectEqual(prepared.handoff_stage, pending_plan.handoff_stage);
    try std.testing.expectEqual(prepared.summary.stage, pending_plan.summary.stage);
    try std.testing.expectEqualStrings(prepared.summary.symbol_name, pending_plan.summary.symbol_name);
    try std.testing.expectEqual(prepared.summary.maxactive, pending_plan.summary.maxactive);
    try std.testing.expectEqual(prepared.summary.active_instances, pending_plan.summary.active_instances);
    try std.testing.expectEqual(prepared.summary.skipped_kernel_threads, pending_plan.summary.skipped_kernel_threads);
    try std.testing.expectEqual(prepared.summary.nmissed, pending_plan.summary.nmissed);
    try std.testing.expectEqual(prepared.summary.last_retval, pending_plan.summary.last_retval);
    try std.testing.expectEqual(prepared.summary.last_duration_ns, pending_plan.summary.last_duration_ns);
    try std.testing.expectEqual(prepared.summary.init_runs, pending_plan.summary.init_runs);
    try std.testing.expectEqual(prepared.summary.selftest_runs, pending_plan.summary.selftest_runs);
    try std.testing.expectEqual(prepared.summary.exit_runs, pending_plan.summary.exit_runs);
    try std.testing.expectEqual(prepared.summary.entry_timestamp_armed, pending_plan.summary.entry_timestamp_armed);
    try std.testing.expectEqual(runtime_kretprobe_sample.ModuleStage.initialized, pending_plan.summary.stage);
    try std.testing.expectEqual(@as(usize, 0), pending_plan.summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), pending_plan.summary.skipped_kernel_threads);
    try std.testing.expectEqual(@as(usize, 0), pending_plan.summary.nmissed);
    try std.testing.expectEqual(@as(usize, 0), pending_plan.summary.last_retval);
    try std.testing.expectEqual(@as(i64, 0), pending_plan.summary.last_duration_ns);
    try std.testing.expect(!pending_plan.summary.entry_timestamp_armed);
}

test "runtime kretprobe loader emits the shared runtime-loader request shape" {
    var module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try module.retargetSymbol("do_sys_openat2");
    try module.init();
    _ = try module.runSelftest();

    var loader = RuntimeKretprobeLoader{};
    const plan = try loader.prepare(&module);

    const request = try loader.requestSharedRuntimeLoad();
    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.LoaderLane.kretprobe, request.lane());
    try std.testing.expectEqual(@as(?[]const u8, null), request.command_name);
    try std.testing.expect(request.keepsCommandNameExplicit());
    try std.testing.expect(request.isWaitingOnRuntimeSubstrate());
    try std.testing.expect(request.keepsInitExitContractExplicit());
    try std.testing.expect(request.keepsStageConsistentWithRuntimeSubstrate());
    try std.testing.expect(request.keepsAllocatorInitFlowConsistent());
    try std.testing.expect(request.keepsLifecyclePayloadConsistent());
    try std.testing.expect(request.keepsSharedHandoffContractExplicit());
    try std.testing.expect(keepsSharedRequestSnapshotExplicit(plan, request));
    try std.testing.expectEqual(runtime_loader.allocatorHandoffFor(.kernel_heap).init_flow, request.allocator_handoff.init_flow);
    try std.testing.expect(request.allocator_handoff.initializes_owned_state);
    try std.testing.expect(!request.allocator_handoff.requires_reset_on_init);
    try std.testing.expectEqualStrings("register_kretprobe", request.payload.kretprobe.register_api);
    try std.testing.expectEqual(@as(usize, 1), request.payload.kretprobe.init_runs);
    try std.testing.expectEqual(@as(usize, 1), request.payload.kretprobe.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), request.payload.kretprobe.exit_runs);
    try std.testing.expectEqual(runtime_loader.LoaderStage.waiting_on_runtime_substrate, request.handoff_stage);
}

test "runtime kretprobe loader can release the shared runtime-loader request without substrate" {
    var module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try module.retargetSymbol("do_sys_openat2");
    try module.init();
    _ = try module.runSelftest();

    var loader = RuntimeKretprobeLoader{};
    const plan = try loader.prepare(&module);

    const released = try loader.releaseSharedRuntimeLoadWithoutSubstrate();
    try std.testing.expectEqual(LoaderStage.released_without_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.LoaderLane.kretprobe, released.lane());
    try std.testing.expect(released.keepsCommandNameExplicit());
    try std.testing.expect(released.isReleasedWithoutSubstrate());
    try std.testing.expect(released.keepsInitExitContractExplicit());
    try std.testing.expect(released.keepsStageConsistentWithRuntimeSubstrate());
    try std.testing.expect(released.keepsAllocatorInitFlowConsistent());
    try std.testing.expect(released.keepsLifecyclePayloadConsistent());
    try std.testing.expect(released.keepsSharedHandoffContractExplicit());
    try std.testing.expect(keepsSharedRequestSnapshotExplicit(plan, released));
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
    try std.testing.expectEqual(@as(usize, 1), released.payload.kretprobe.init_runs);
    try std.testing.expectEqual(@as(usize, 1), released.payload.kretprobe.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), released.payload.kretprobe.exit_runs);
    try std.testing.expectEqual(@as(usize, 42), released.payload.kretprobe.last_retval);
    try std.testing.expectEqual(@as(i64, 75), released.payload.kretprobe.last_duration_ns);
    try std.testing.expectEqualStrings("zigux_runtime_kretprobe_init", released.entry_symbol);
    try std.testing.expectEqualStrings("zigux_runtime_kretprobe_exit", released.exit_symbol);
}

test "runtime kretprobe loader preserves an explicit shared command name" {
    var module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try module.retargetSymbol("do_sys_openat2");
    try module.init();
    _ = try module.runSelftest();

    var loader = RuntimeKretprobeLoader{};
    const plan = try loader.prepareWithCommandName(&module, "perf-runtime-kretprobe");
    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqualStrings("perf-runtime-kretprobe", plan.command_name.?);

    const request = try loader.requestSharedRuntimeLoad();
    try std.testing.expectEqualStrings("perf-runtime-kretprobe", request.command_name.?);
    try std.testing.expect(request.keepsCommandNameExplicit());
    try std.testing.expect(keepsSharedRequestSnapshotExplicit(plan, request));
    try std.testing.expectEqual(runtime_loader.LoaderStage.waiting_on_runtime_substrate, request.handoff_stage);

    var fallback_loader = RuntimeKretprobeLoader{};
    const fallback_plan = try fallback_loader.prepareWithCommandName(&module, "perf-runtime-kretprobe");
    const released = try fallback_loader.releaseSharedRuntimeLoadWithoutSubstrate();
    try std.testing.expectEqualStrings("perf-runtime-kretprobe", released.command_name.?);
    try std.testing.expect(released.keepsCommandNameExplicit());
    try std.testing.expect(keepsSharedRequestSnapshotExplicit(fallback_plan, released));
    try std.testing.expectEqual(runtime_loader.LoaderStage.released_without_substrate, released.handoff_stage);
}

test "runtime kretprobe loader rejects shared-request snapshot drift" {
    var module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try module.retargetSymbol("do_sys_openat2");
    try module.init();
    _ = try module.runSelftest();

    var loader = RuntimeKretprobeLoader{};
    const plan = try loader.prepareWithCommandName(&module, "perf-runtime-kretprobe");
    const request = try loader.requestSharedRuntimeLoad();
    try std.testing.expect(keepsSharedRequestSnapshotExplicit(plan, request));

    var drifted_command = request;
    drifted_command.command_name = "perf-runtime-kretprobe-drift";
    try std.testing.expect(!keepsSharedRequestSnapshotExplicit(plan, drifted_command));

    var drifted_symbol = request;
    drifted_symbol.payload.kretprobe.symbol_name = "vfs_read";
    try std.testing.expect(!keepsSharedRequestSnapshotExplicit(plan, drifted_symbol));

    var drifted_nmissed = request;
    drifted_nmissed.payload.kretprobe.nmissed += 1;
    try std.testing.expect(!keepsSharedRequestSnapshotExplicit(plan, drifted_nmissed));

    var drifted_lane = request;
    drifted_lane.payload = .{
        .bitmap = .{
            .first_set = 0,
            .first_zero = 1,
            .weight = 4,
            .nbits = 128,
            .init_runs = plan.summary.init_runs,
            .selftest_runs = plan.summary.selftest_runs,
            .exit_runs = plan.summary.exit_runs,
        },
    };
    try std.testing.expect(!keepsSharedRequestSnapshotExplicit(plan, drifted_lane));

    const released = request.releasedWithoutSubstrate();
    try std.testing.expect(keepsSharedRequestSnapshotExplicit(plan, released));
}

test "runtime kretprobe loader rejects an empty explicit shared command name" {
    var module = runtime_kretprobe_sample.RuntimeKretprobeSample{};
    try module.init();

    try std.testing.expectError(
        error.EmptyCommandName,
        RuntimeKretprobeLoader.planForWithCommandName(&module, ""),
    );

    var loader = RuntimeKretprobeLoader{};
    try std.testing.expectError(
        error.EmptyCommandName,
        loader.prepareWithCommandName(&module, ""),
    );
    try std.testing.expectEqual(LoaderStage.idle, loader.stage());
}
