const std = @import("std");
const runtime_bitmap_sample = @import("runtime_bitmap_sample");
const runtime_loader = @import("runtime_loader");

pub const LoaderStage = runtime_loader.LoaderStage;

pub const RuntimeBitmapLoadPlan = struct {
    module_name: []const u8,
    command_name: ?[]const u8,
    anchor: []const u8,
    entry_symbol: []const u8,
    exit_symbol: []const u8,
    requires_runtime_substrate: bool,
    provides_selftest_hook: bool,
    handoff_stage: runtime_bitmap_sample.ModuleStage,
    summary: runtime_bitmap_sample.RuntimeBitmapSummary,
};

fn optionalStringEql(lhs: ?[]const u8, rhs: ?[]const u8) bool {
    if (lhs) |lhs_value| {
        return if (rhs) |rhs_value| std.mem.eql(u8, lhs_value, rhs_value) else false;
    }
    return rhs == null;
}

pub fn keepsSharedRequestSnapshotExplicit(
    plan: RuntimeBitmapLoadPlan,
    request: runtime_loader.RuntimeLoadRequest,
) bool {
    if (request.lane() != .bitmap) return false;

    return std.mem.eql(u8, request.module_name, plan.module_name) and
        optionalStringEql(plan.command_name, request.command_name) and
        std.mem.eql(u8, request.anchor, plan.anchor) and
        std.mem.eql(u8, request.entry_symbol, plan.entry_symbol) and
        std.mem.eql(u8, request.exit_symbol, plan.exit_symbol) and
        request.requires_runtime_substrate == plan.requires_runtime_substrate and
        request.provides_selftest_hook == plan.provides_selftest_hook and
        request.payload.bitmap.first_set == plan.summary.first_set and
        request.payload.bitmap.first_zero == plan.summary.first_zero and
        request.payload.bitmap.weight == plan.summary.weight and
        request.payload.bitmap.nbits == plan.summary.nbits and
        request.payload.bitmap.init_runs == plan.summary.init_runs and
        request.payload.bitmap.selftest_runs == plan.summary.selftest_runs and
        request.payload.bitmap.exit_runs == plan.summary.exit_runs;
}

pub const RuntimeBitmapLoader = struct {
    const Self = @This();

    stage_state: LoaderStage = .idle,
    cached_plan: ?RuntimeBitmapLoadPlan = null,

    pub fn stage(self: *const Self) LoaderStage {
        return self.stage_state;
    }

    pub fn planFor(module: *const runtime_bitmap_sample.RuntimeBitmapSample) !RuntimeBitmapLoadPlan {
        return planForWithCommandName(module, null);
    }

    pub fn planForWithCommandName(
        module: *const runtime_bitmap_sample.RuntimeBitmapSample,
        command_name: ?[]const u8,
    ) !RuntimeBitmapLoadPlan {
        const descriptor = runtime_bitmap_sample.RuntimeBitmapSample.descriptor();
        const module_stage = module.stage();
        switch (module_stage) {
            .initialized, .selftest_complete => {},
            else => return error.InvalidModuleLifecycleForLoader,
        }

        if (!descriptor.requires_runtime_substrate) return error.LoaderNotRequired;
        if (command_name) |name| {
            if (name.len == 0) return error.EmptyCommandName;
        }

        return .{
            .module_name = descriptor.name,
            .command_name = command_name,
            .anchor = descriptor.anchor,
            .entry_symbol = "zigux_runtime_bitmap_init",
            .exit_symbol = "zigux_runtime_bitmap_exit",
            .requires_runtime_substrate = descriptor.requires_runtime_substrate,
            .provides_selftest_hook = descriptor.provides_selftest_hook,
            .handoff_stage = module_stage,
            .summary = module.summary(),
        };
    }

    pub fn prepare(self: *Self, module: *const runtime_bitmap_sample.RuntimeBitmapSample) !RuntimeBitmapLoadPlan {
        return prepareWithCommandName(self, module, null);
    }

    pub fn prepareWithCommandName(
        self: *Self,
        module: *const runtime_bitmap_sample.RuntimeBitmapSample,
        command_name: ?[]const u8,
    ) !RuntimeBitmapLoadPlan {
        if (self.stage_state != .idle) return error.LoaderAlreadyPrepared;

        const plan = try planForWithCommandName(module, command_name);
        self.cached_plan = plan;
        self.stage_state = .prepared;
        return plan;
    }

    pub fn requestRuntimeLoad(self: *Self) !RuntimeBitmapLoadPlan {
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

pub fn toSharedRequest(plan: RuntimeBitmapLoadPlan) runtime_loader.RuntimeLoadRequest {
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
            .bitmap = .{
                .first_set = plan.summary.first_set,
                .first_zero = plan.summary.first_zero,
                .weight = plan.summary.weight,
                .nbits = plan.summary.nbits,
                .init_runs = plan.summary.init_runs,
                .selftest_runs = plan.summary.selftest_runs,
                .exit_runs = plan.summary.exit_runs,
            },
        },
    }).waitingOnRuntimeSubstrate();
}

test "runtime bitmap loader prepares a bounded handoff plan from the sample contract" {
    var module = runtime_bitmap_sample.RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 0, 5, 64, 70 });
    _ = try module.runSelftest();

    var loader = RuntimeBitmapLoader{};
    const plan = try loader.prepare(&module);

    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqualStrings("runtime_bitmap", plan.module_name);
    try std.testing.expectEqual(@as(?[]const u8, null), plan.command_name);
    try std.testing.expectEqualStrings("lib/test_bitmap.c", plan.anchor);
    try std.testing.expectEqualStrings("zigux_runtime_bitmap_init", plan.entry_symbol);
    try std.testing.expectEqualStrings("zigux_runtime_bitmap_exit", plan.exit_symbol);
    try std.testing.expect(plan.requires_runtime_substrate);
    try std.testing.expect(plan.provides_selftest_hook);
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.selftest_complete, plan.handoff_stage);
    try std.testing.expectEqual(@as(u32, 0), plan.summary.first_set);
    try std.testing.expectEqual(@as(u32, 1), plan.summary.first_zero);
    try std.testing.expectEqual(@as(u32, 4), plan.summary.weight);
    try std.testing.expectEqual(@as(usize, 1), plan.summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), plan.summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), plan.summary.exit_runs);
}

test "runtime bitmap loader keeps unavailable substrate and lifecycle guards explicit" {
    var cold_module = runtime_bitmap_sample.RuntimeBitmapSample{};
    try std.testing.expectError(error.InvalidModuleLifecycleForLoader, RuntimeBitmapLoader.planFor(&cold_module));

    var module = runtime_bitmap_sample.RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 2, 7, 9 });

    var loader = RuntimeBitmapLoader{};
    _ = try loader.prepare(&module);
    try std.testing.expectError(error.LoaderAlreadyPrepared, loader.prepare(&module));

    const pending_plan = try loader.requestRuntimeLoad();
    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.initialized, pending_plan.handoff_stage);
    try std.testing.expectEqual(@as(usize, 1), pending_plan.summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), pending_plan.summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), pending_plan.summary.exit_runs);

    try loader.releaseWithoutSubstrate();
    try std.testing.expectEqual(LoaderStage.released_without_substrate, loader.stage());
    try std.testing.expectError(error.InvalidLoaderState, loader.requestRuntimeLoad());

    try module.exit();
    try std.testing.expectError(error.InvalidModuleLifecycleForLoader, RuntimeBitmapLoader.planFor(&module));
}

test "runtime bitmap loader snapshots the prepared bitmap summary before later sample mutation" {
    var module = runtime_bitmap_sample.RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 0, 5, 64, 70 });

    var loader = RuntimeBitmapLoader{};
    const prepared = try loader.prepare(&module);

    try module.clearRange(0, 1);
    try module.setRange(9, 4);

    const mutated_summary = module.summary();
    try std.testing.expectEqual(@as(u32, 5), mutated_summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), mutated_summary.first_zero);
    try std.testing.expectEqual(@as(u32, 7), mutated_summary.weight);

    const pending_plan = try loader.requestRuntimeLoad();
    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.initialized, prepared.handoff_stage);
    try std.testing.expectEqual(prepared.handoff_stage, pending_plan.handoff_stage);
    try std.testing.expectEqual(prepared.summary.first_set, pending_plan.summary.first_set);
    try std.testing.expectEqual(prepared.summary.first_zero, pending_plan.summary.first_zero);
    try std.testing.expectEqual(prepared.summary.weight, pending_plan.summary.weight);
    try std.testing.expectEqual(prepared.summary.nbits, pending_plan.summary.nbits);
    try std.testing.expectEqual(prepared.summary.init_runs, pending_plan.summary.init_runs);
    try std.testing.expectEqual(prepared.summary.selftest_runs, pending_plan.summary.selftest_runs);
    try std.testing.expectEqual(prepared.summary.exit_runs, pending_plan.summary.exit_runs);
    try std.testing.expectEqual(@as(u32, 0), pending_plan.summary.first_set);
    try std.testing.expectEqual(@as(u32, 1), pending_plan.summary.first_zero);
    try std.testing.expectEqual(@as(u32, 4), pending_plan.summary.weight);
    try std.testing.expectEqual(@as(usize, 1), pending_plan.summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), pending_plan.summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), pending_plan.summary.exit_runs);
}

test "runtime bitmap loader emits the shared runtime-loader request shape" {
    var module = runtime_bitmap_sample.RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 0, 5, 64, 70 });
    _ = try module.runSelftest();

    var loader = RuntimeBitmapLoader{};
    const plan = try loader.prepare(&module);

    const request = try loader.requestSharedRuntimeLoad();
    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.LoaderLane.bitmap, request.lane());
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
    try std.testing.expectEqual(@as(u32, 0), request.payload.bitmap.first_set);
    try std.testing.expectEqual(@as(u32, 1), request.payload.bitmap.first_zero);
    try std.testing.expectEqual(@as(u32, 4), request.payload.bitmap.weight);
    try std.testing.expectEqual(runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits, request.payload.bitmap.nbits);
    try std.testing.expectEqual(@as(usize, 1), request.payload.bitmap.init_runs);
    try std.testing.expectEqual(@as(usize, 1), request.payload.bitmap.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), request.payload.bitmap.exit_runs);
    try std.testing.expectEqual(runtime_loader.LoaderStage.waiting_on_runtime_substrate, request.handoff_stage);
    try std.testing.expectEqual(runtime_loader.LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.LoaderLane.bitmap, std.meta.activeTag(request.payload));
}

test "runtime bitmap loader can release the shared runtime-loader request without substrate" {
    var module = runtime_bitmap_sample.RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 0, 5, 64, 70 });
    _ = try module.runSelftest();

    var loader = RuntimeBitmapLoader{};
    const plan = try loader.prepare(&module);

    const released = try loader.releaseSharedRuntimeLoadWithoutSubstrate();
    try std.testing.expectEqual(LoaderStage.released_without_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.LoaderLane.bitmap, released.lane());
    try std.testing.expectEqual(@as(?[]const u8, null), released.command_name);
    try std.testing.expect(released.keepsCommandNameExplicit());
    try std.testing.expect(released.isReleasedWithoutSubstrate());
    try std.testing.expect(!released.isWaitingOnRuntimeSubstrate());
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
    try std.testing.expectEqual(@as(u32, 0), released.payload.bitmap.first_set);
    try std.testing.expectEqual(@as(u32, 1), released.payload.bitmap.first_zero);
    try std.testing.expectEqual(@as(u32, 4), released.payload.bitmap.weight);
    try std.testing.expectEqual(runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits, released.payload.bitmap.nbits);
    try std.testing.expectEqual(@as(usize, 1), released.payload.bitmap.init_runs);
    try std.testing.expectEqual(@as(usize, 1), released.payload.bitmap.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), released.payload.bitmap.exit_runs);
    try std.testing.expectEqualStrings("zigux_runtime_bitmap_init", released.entry_symbol);
    try std.testing.expectEqualStrings("zigux_runtime_bitmap_exit", released.exit_symbol);
    try std.testing.expectError(error.InvalidLoaderState, loader.requestSharedRuntimeLoad());
}

test "runtime bitmap loader preserves an explicit shared command name" {
    var module = runtime_bitmap_sample.RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 0, 5, 64, 70 });
    _ = try module.runSelftest();

    var loader = RuntimeBitmapLoader{};
    const plan = try loader.prepareWithCommandName(&module, "perf-runtime-bitmap");
    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqualStrings("perf-runtime-bitmap", plan.command_name.?);

    const request = try loader.requestSharedRuntimeLoad();
    try std.testing.expectEqualStrings("perf-runtime-bitmap", request.command_name.?);
    try std.testing.expect(request.keepsCommandNameExplicit());
    try std.testing.expect(keepsSharedRequestSnapshotExplicit(plan, request));
    try std.testing.expectEqual(runtime_loader.LoaderStage.waiting_on_runtime_substrate, request.handoff_stage);

    var fallback_loader = RuntimeBitmapLoader{};
    const fallback_plan = try fallback_loader.prepareWithCommandName(&module, "perf-runtime-bitmap");
    const released = try fallback_loader.releaseSharedRuntimeLoadWithoutSubstrate();
    try std.testing.expectEqualStrings("perf-runtime-bitmap", released.command_name.?);
    try std.testing.expect(released.keepsCommandNameExplicit());
    try std.testing.expect(keepsSharedRequestSnapshotExplicit(fallback_plan, released));
    try std.testing.expectEqual(runtime_loader.LoaderStage.released_without_substrate, released.handoff_stage);
}

test "runtime bitmap loader rejects shared-request snapshot drift" {
    var module = runtime_bitmap_sample.RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 0, 5, 64, 70 });
    _ = try module.runSelftest();

    var loader = RuntimeBitmapLoader{};
    const plan = try loader.prepareWithCommandName(&module, "perf-runtime-bitmap");
    const request = try loader.requestSharedRuntimeLoad();
    try std.testing.expect(keepsSharedRequestSnapshotExplicit(plan, request));

    var drifted_command = request;
    drifted_command.command_name = "perf-runtime-bitmap-drift";
    try std.testing.expect(!keepsSharedRequestSnapshotExplicit(plan, drifted_command));

    var drifted_weight = request;
    drifted_weight.payload.bitmap.weight += 1;
    try std.testing.expect(!keepsSharedRequestSnapshotExplicit(plan, drifted_weight));

    var drifted_lane = request;
    drifted_lane.payload = .{
        .atomic64 = .{
            .counter_snapshot = 4,
            .init_runs = plan.summary.init_runs,
            .selftest_runs = plan.summary.selftest_runs,
            .exit_runs = plan.summary.exit_runs,
        },
    };
    try std.testing.expect(!keepsSharedRequestSnapshotExplicit(plan, drifted_lane));

    const released = request.releasedWithoutSubstrate();
    try std.testing.expect(keepsSharedRequestSnapshotExplicit(plan, released));
}

test "runtime bitmap loader rejects an empty explicit shared command name" {
    var module = runtime_bitmap_sample.RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 2, 7, 9 });

    try std.testing.expectError(
        error.EmptyCommandName,
        RuntimeBitmapLoader.planForWithCommandName(&module, ""),
    );

    var loader = RuntimeBitmapLoader{};
    try std.testing.expectError(
        error.EmptyCommandName,
        loader.prepareWithCommandName(&module, ""),
    );
    try std.testing.expectEqual(LoaderStage.idle, loader.stage());
}

test "runtime bitmap loader keeps initialized-stage shared requests and fallback counters explicit" {
    var module = runtime_bitmap_sample.RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 2, 7, 9 });

    var loader = RuntimeBitmapLoader{};
    const plan = try loader.prepare(&module);

    const request = try loader.requestSharedRuntimeLoad();
    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.LoaderLane.bitmap, request.lane());
    try std.testing.expectEqual(@as(?[]const u8, null), request.command_name);
    try std.testing.expect(request.keepsCommandNameExplicit());
    try std.testing.expect(request.isWaitingOnRuntimeSubstrate());
    try std.testing.expect(request.keepsInitExitContractExplicit());
    try std.testing.expect(request.keepsStageConsistentWithRuntimeSubstrate());
    try std.testing.expect(request.keepsAllocatorInitFlowConsistent());
    try std.testing.expect(request.keepsLifecyclePayloadConsistent());
    try std.testing.expect(request.keepsSharedHandoffContractExplicit());
    try std.testing.expect(keepsSharedRequestSnapshotExplicit(plan, request));
    try std.testing.expectEqual(runtime_loader.LoaderStage.waiting_on_runtime_substrate, request.handoff_stage);
    try std.testing.expectEqual(@as(u32, 2), request.payload.bitmap.first_set);
    try std.testing.expectEqual(@as(u32, 0), request.payload.bitmap.first_zero);
    try std.testing.expectEqual(@as(u32, 3), request.payload.bitmap.weight);
    try std.testing.expectEqual(runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits, request.payload.bitmap.nbits);
    try std.testing.expectEqual(@as(usize, 1), request.payload.bitmap.init_runs);
    try std.testing.expectEqual(@as(usize, 0), request.payload.bitmap.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), request.payload.bitmap.exit_runs);

    var fallback_loader = RuntimeBitmapLoader{};
    const fallback_plan = try fallback_loader.prepare(&module);

    const released = try fallback_loader.releaseSharedRuntimeLoadWithoutSubstrate();
    try std.testing.expectEqual(LoaderStage.released_without_substrate, fallback_loader.stage());
    try std.testing.expectEqual(runtime_loader.LoaderLane.bitmap, released.lane());
    try std.testing.expectEqual(@as(?[]const u8, null), released.command_name);
    try std.testing.expect(released.keepsCommandNameExplicit());
    try std.testing.expect(released.isReleasedWithoutSubstrate());
    try std.testing.expect(!released.isWaitingOnRuntimeSubstrate());
    try std.testing.expect(released.keepsInitExitContractExplicit());
    try std.testing.expect(released.keepsStageConsistentWithRuntimeSubstrate());
    try std.testing.expect(released.keepsAllocatorInitFlowConsistent());
    try std.testing.expect(released.keepsLifecyclePayloadConsistent());
    try std.testing.expect(released.keepsSharedHandoffContractExplicit());
    try std.testing.expect(keepsSharedRequestSnapshotExplicit(fallback_plan, released));
    try std.testing.expectEqual(runtime_loader.LoaderStage.released_without_substrate, released.handoff_stage);
    try std.testing.expectEqual(@as(u32, 2), released.payload.bitmap.first_set);
    try std.testing.expectEqual(@as(u32, 0), released.payload.bitmap.first_zero);
    try std.testing.expectEqual(@as(u32, 3), released.payload.bitmap.weight);
    try std.testing.expectEqual(runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits, released.payload.bitmap.nbits);
    try std.testing.expectEqual(@as(usize, 1), released.payload.bitmap.init_runs);
    try std.testing.expectEqual(@as(usize, 0), released.payload.bitmap.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), released.payload.bitmap.exit_runs);
}
