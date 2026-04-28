const std = @import("std");
const runtime_atomic64_sample = @import("runtime_atomic64_sample");
const runtime_loader = @import("runtime_loader");

pub const LoaderStage = runtime_loader.LoaderStage;

pub const RuntimeAtomic64LoadPlan = struct {
    module_name: []const u8,
    command_name: ?[]const u8,
    anchor: []const u8,
    entry_symbol: []const u8,
    exit_symbol: []const u8,
    requires_runtime_substrate: bool,
    provides_selftest_hook: bool,
    handoff_stage: runtime_atomic64_sample.ModuleStage,
    summary: runtime_atomic64_sample.RuntimeAtomic64Summary,
};

pub const RuntimeAtomic64Loader = struct {
    const Self = @This();

    stage_state: LoaderStage = .idle,
    cached_plan: ?RuntimeAtomic64LoadPlan = null,

    pub fn stage(self: *const Self) LoaderStage {
        return self.stage_state;
    }

    pub fn planFor(module: *const runtime_atomic64_sample.RuntimeAtomic64Sample) !RuntimeAtomic64LoadPlan {
        const descriptor = runtime_atomic64_sample.RuntimeAtomic64Sample.descriptor();
        const module_stage = module.stage();
        switch (module_stage) {
            .initialized, .selftest_complete => {},
            else => return error.InvalidModuleLifecycleForLoader,
        }

        if (!descriptor.requires_runtime_substrate) return error.LoaderNotRequired;

        return .{
            .module_name = descriptor.name,
            .command_name = null,
            .anchor = descriptor.anchor,
            .entry_symbol = "zigux_runtime_atomic64_init",
            .exit_symbol = "zigux_runtime_atomic64_exit",
            .requires_runtime_substrate = descriptor.requires_runtime_substrate,
            .provides_selftest_hook = descriptor.provides_selftest_hook,
            .handoff_stage = module_stage,
            .summary = module.summary(),
        };
    }

    pub fn prepare(self: *Self, module: *const runtime_atomic64_sample.RuntimeAtomic64Sample) !RuntimeAtomic64LoadPlan {
        if (self.stage_state != .idle) return error.LoaderAlreadyPrepared;

        const plan = try planFor(module);
        self.cached_plan = plan;
        self.stage_state = .prepared;
        return plan;
    }

    pub fn requestRuntimeLoad(self: *Self) !RuntimeAtomic64LoadPlan {
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

pub fn toSharedRequest(plan: RuntimeAtomic64LoadPlan) runtime_loader.RuntimeLoadRequest {
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
            .atomic64 = .{
                .counter_snapshot = plan.summary.counter_snapshot,
                .init_runs = plan.summary.init_runs,
                .selftest_runs = plan.summary.selftest_runs,
                .exit_runs = plan.summary.exit_runs,
            },
        },
    }).waitingOnRuntimeSubstrate();
}

test "runtime atomic64 loader prepares a bounded handoff plan from the sample contract" {
    var module = runtime_atomic64_sample.RuntimeAtomic64Sample{};
    try module.init(0x1111_2222_3333_4444);
    _ = try module.runSelftest();

    var loader = RuntimeAtomic64Loader{};
    const plan = try loader.prepare(&module);

    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqualStrings("runtime_atomic64", plan.module_name);
    try std.testing.expectEqual(@as(?[]const u8, null), plan.command_name);
    try std.testing.expectEqualStrings("lib/atomic64_test.c", plan.anchor);
    try std.testing.expectEqualStrings("zigux_runtime_atomic64_init", plan.entry_symbol);
    try std.testing.expectEqualStrings("zigux_runtime_atomic64_exit", plan.exit_symbol);
    try std.testing.expect(plan.requires_runtime_substrate);
    try std.testing.expect(plan.provides_selftest_hook);
    try std.testing.expectEqual(runtime_atomic64_sample.ModuleStage.selftest_complete, plan.handoff_stage);
    try std.testing.expectEqual(@as(i64, 0x1111_2222_3333_4444), plan.summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), plan.summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), plan.summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), plan.summary.exit_runs);
}

test "runtime atomic64 loader keeps unavailable substrate and lifecycle guards explicit" {
    var cold_module = runtime_atomic64_sample.RuntimeAtomic64Sample{};
    try std.testing.expectError(error.InvalidModuleLifecycleForLoader, RuntimeAtomic64Loader.planFor(&cold_module));

    var module = runtime_atomic64_sample.RuntimeAtomic64Sample{};
    try module.init(9);

    var loader = RuntimeAtomic64Loader{};
    _ = try loader.prepare(&module);
    try std.testing.expectError(error.LoaderAlreadyPrepared, loader.prepare(&module));

    const pending_plan = try loader.requestRuntimeLoad();
    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(runtime_atomic64_sample.ModuleStage.initialized, pending_plan.handoff_stage);

    try loader.releaseWithoutSubstrate();
    try std.testing.expectEqual(LoaderStage.released_without_substrate, loader.stage());
    try std.testing.expectError(error.InvalidLoaderState, loader.requestRuntimeLoad());

    try module.exit();
    try std.testing.expectError(error.InvalidModuleLifecycleForLoader, RuntimeAtomic64Loader.planFor(&module));
}

test "runtime atomic64 loader snapshots the prepared counter summary before later sample mutation" {
    var module = runtime_atomic64_sample.RuntimeAtomic64Sample{};
    try module.init(7);

    var loader = RuntimeAtomic64Loader{};
    const prepared = try loader.prepare(&module);

    _ = try module.addCounter(5);
    const compare = try module.compareSwapCounter(12, 17);
    try std.testing.expect(compare.stored);
    try std.testing.expectEqual(@as(i64, 17), module.snapshotCounter());

    const pending_plan = try loader.requestRuntimeLoad();
    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(runtime_atomic64_sample.ModuleStage.initialized, prepared.handoff_stage);
    try std.testing.expectEqual(prepared.handoff_stage, pending_plan.handoff_stage);
    try std.testing.expectEqual(prepared.summary.counter_snapshot, pending_plan.summary.counter_snapshot);
    try std.testing.expectEqual(prepared.summary.init_runs, pending_plan.summary.init_runs);
    try std.testing.expectEqual(prepared.summary.selftest_runs, pending_plan.summary.selftest_runs);
    try std.testing.expectEqual(prepared.summary.exit_runs, pending_plan.summary.exit_runs);
    try std.testing.expectEqual(@as(i64, 7), pending_plan.summary.counter_snapshot);
}

test "runtime atomic64 loader emits the shared runtime-loader request shape" {
    var module = runtime_atomic64_sample.RuntimeAtomic64Sample{};
    try module.init(0x1111_2222_3333_4444);
    _ = try module.runSelftest();

    var loader = RuntimeAtomic64Loader{};
    _ = try loader.prepare(&module);

    const request = try loader.requestSharedRuntimeLoad();
    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.LoaderLane.atomic64, request.lane());
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
    try std.testing.expectEqual(@as(i64, 0x1111_2222_3333_4444), request.payload.atomic64.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), request.payload.atomic64.init_runs);
    try std.testing.expectEqual(@as(usize, 1), request.payload.atomic64.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), request.payload.atomic64.exit_runs);
    try std.testing.expectEqual(runtime_loader.LoaderStage.waiting_on_runtime_substrate, request.handoff_stage);
    try std.testing.expectEqual(runtime_loader.LoaderLane.atomic64, std.meta.activeTag(request.payload));
}

test "runtime atomic64 loader can release the shared runtime-loader request without substrate" {
    var module = runtime_atomic64_sample.RuntimeAtomic64Sample{};
    try module.init(0x1111_2222_3333_4444);
    _ = try module.runSelftest();

    var loader = RuntimeAtomic64Loader{};
    _ = try loader.prepare(&module);

    const released = try loader.releaseSharedRuntimeLoadWithoutSubstrate();
    try std.testing.expectEqual(LoaderStage.released_without_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.LoaderLane.atomic64, released.lane());
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
    try std.testing.expectEqual(@as(i64, 0x1111_2222_3333_4444), released.payload.atomic64.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), released.payload.atomic64.init_runs);
    try std.testing.expectEqual(@as(usize, 1), released.payload.atomic64.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), released.payload.atomic64.exit_runs);
    try std.testing.expectEqualStrings("zigux_runtime_atomic64_init", released.entry_symbol);
    try std.testing.expectEqualStrings("zigux_runtime_atomic64_exit", released.exit_symbol);
    try std.testing.expectError(error.InvalidLoaderState, loader.requestSharedRuntimeLoad());
}
