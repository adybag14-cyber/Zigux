const std = @import("std");
const runtime_atomic64_sample = @import("runtime_atomic64_sample");
const runtime_loader = @import("runtime_loader");

const loaded_operation_families = [_]runtime_atomic64_sample.OperationFamily{
    .arithmetic,
    .bitwise,
    .returning_ops,
    .swap_ops,
    .guard_ops,
};

const empty_operation_families = [_]runtime_atomic64_sample.OperationFamily{};

pub const LoaderStage = enum(u8) {
    idle,
    prepared,
    waiting_on_runtime_substrate,
    released_without_substrate,
};

pub const RuntimeAtomic64LoadSummary = struct {
    anchor: []const u8,
    operation_families: []const runtime_atomic64_sample.OperationFamily,
    checked_returning_paths: bool,
    checked_bitwise_paths: bool,
    checked_guard_paths: bool,
    counter_snapshot: i64,
    selftest_runs: usize,
};

pub const RuntimeAtomic64LoadPlan = struct {
    module_name: []const u8,
    anchor: []const u8,
    entry_symbol: []const u8,
    exit_symbol: []const u8,
    requires_runtime_substrate: bool,
    provides_selftest_hook: bool,
    handoff_stage: runtime_atomic64_sample.ModuleStage,
    summary: RuntimeAtomic64LoadSummary,
};

fn buildSummary(module: *const runtime_atomic64_sample.RuntimeAtomic64Sample) RuntimeAtomic64LoadSummary {
    return .{
        .anchor = runtime_atomic64_sample.RuntimeAtomic64Sample.descriptor().anchor,
        .operation_families = switch (module.stage()) {
            .selftest_complete => loaded_operation_families[0..],
            else => empty_operation_families[0..],
        },
        .checked_returning_paths = module.stage() == .selftest_complete,
        .checked_bitwise_paths = module.stage() == .selftest_complete,
        .checked_guard_paths = module.stage() == .selftest_complete,
        .counter_snapshot = module.snapshotCounter(),
        .selftest_runs = module.selftest_runs,
    };
}

fn sharedHandoffStage(stage: runtime_atomic64_sample.ModuleStage) runtime_loader.HandoffStage {
    return switch (stage) {
        .initialized => .initialized,
        .selftest_complete => .selftest_complete,
        else => unreachable,
    };
}

pub fn toSharedLoadPlan(plan: RuntimeAtomic64LoadPlan) runtime_loader.LoadPlan {
    return .{
        .module_name = plan.module_name,
        .anchor = plan.anchor,
        .entry_symbol = plan.entry_symbol,
        .exit_symbol = plan.exit_symbol,
        .requires_runtime_substrate = plan.requires_runtime_substrate,
        .provides_selftest_hook = plan.provides_selftest_hook,
        .allocator_handoff = .caller_provided,
        .init_flow = .{
            .handoff_stage = sharedHandoffStage(plan.handoff_stage),
            .init_runs = 1,
            .selftest_runs = plan.summary.selftest_runs,
            .exit_runs = 0,
        },
    };
}

pub fn keepsSharedLoadPlanSnapshotExplicit(
    plan: RuntimeAtomic64LoadPlan,
    shared_plan: runtime_loader.LoadPlan,
) bool {
    return std.mem.eql(u8, shared_plan.module_name, plan.module_name) and
        std.mem.eql(u8, shared_plan.anchor, plan.anchor) and
        std.mem.eql(u8, shared_plan.entry_symbol, plan.entry_symbol) and
        std.mem.eql(u8, shared_plan.exit_symbol, plan.exit_symbol) and
        shared_plan.requires_runtime_substrate == plan.requires_runtime_substrate and
        shared_plan.provides_selftest_hook == plan.provides_selftest_hook and
        shared_plan.allocator_handoff == .caller_provided and
        shared_plan.init_flow.handoff_stage == sharedHandoffStage(plan.handoff_stage) and
        shared_plan.init_flow.init_runs == 1 and
        shared_plan.init_flow.selftest_runs == plan.summary.selftest_runs and
        shared_plan.init_flow.exit_runs == 0;
}

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
            .anchor = descriptor.anchor,
            .entry_symbol = "zigux_runtime_atomic64_init",
            .exit_symbol = "zigux_runtime_atomic64_exit",
            .requires_runtime_substrate = descriptor.requires_runtime_substrate,
            .provides_selftest_hook = descriptor.provides_selftest_hook,
            .handoff_stage = module_stage,
            .summary = buildSummary(module),
        };
    }

    pub fn prepare(self: *Self, module: *const runtime_atomic64_sample.RuntimeAtomic64Sample) !RuntimeAtomic64LoadPlan {
        if (self.stage_state != .idle) return error.LoaderAlreadyPrepared;

        const plan = try planFor(module);
        self.cached_plan = plan;
        self.stage_state = .prepared;
        return plan;
    }

    pub fn prepareSharedRequest(self: *Self, module: *const runtime_atomic64_sample.RuntimeAtomic64Sample) !runtime_loader.PreparedRequest {
        const plan = try self.prepare(module);
        return runtime_loader.prepareRequest(toSharedLoadPlan(plan));
    }

    pub fn requestRuntimeLoad(self: *Self) !RuntimeAtomic64LoadPlan {
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

test "runtime atomic64 loader prepares a bounded handoff plan from the sample contract" {
    var module = runtime_atomic64_sample.RuntimeAtomic64Sample{};
    try module.init(0x1111_1111_2222_2222);
    _ = try module.runSelftest();

    var loader = RuntimeAtomic64Loader{};
    const plan = try loader.prepare(&module);

    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqualStrings("runtime_atomic64", plan.module_name);
    try std.testing.expectEqualStrings("lib/atomic64_test.c", plan.anchor);
    try std.testing.expectEqualStrings("zigux_runtime_atomic64_init", plan.entry_symbol);
    try std.testing.expectEqualStrings("zigux_runtime_atomic64_exit", plan.exit_symbol);
    try std.testing.expect(plan.requires_runtime_substrate);
    try std.testing.expect(plan.provides_selftest_hook);
    try std.testing.expectEqual(runtime_atomic64_sample.ModuleStage.selftest_complete, plan.handoff_stage);
    try std.testing.expectEqualStrings("lib/atomic64_test.c", plan.summary.anchor);
    try std.testing.expectEqual(@as(usize, 5), plan.summary.operation_families.len);
    try std.testing.expect(plan.summary.checked_returning_paths);
    try std.testing.expect(plan.summary.checked_bitwise_paths);
    try std.testing.expect(plan.summary.checked_guard_paths);
    try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_2222), plan.summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), plan.summary.selftest_runs);
}

test "runtime atomic64 loader keeps unavailable substrate and lifecycle guards explicit" {
    var cold_module = runtime_atomic64_sample.RuntimeAtomic64Sample{};
    try std.testing.expectError(error.InvalidModuleLifecycleForLoader, RuntimeAtomic64Loader.planFor(&cold_module));

    var module = runtime_atomic64_sample.RuntimeAtomic64Sample{};
    try module.init(-9);

    var loader = RuntimeAtomic64Loader{};
    const prepared = try loader.prepare(&module);
    try std.testing.expectEqual(runtime_atomic64_sample.ModuleStage.initialized, prepared.handoff_stage);
    try std.testing.expectEqual(@as(usize, 0), prepared.summary.operation_families.len);
    try std.testing.expect(!prepared.summary.checked_returning_paths);
    try std.testing.expect(!prepared.summary.checked_bitwise_paths);
    try std.testing.expect(!prepared.summary.checked_guard_paths);
    try std.testing.expectEqual(@as(i64, -9), prepared.summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 0), prepared.summary.selftest_runs);

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

test "runtime atomic64 loader keeps the prepared snapshot stable across later counter mutation" {
    var module = runtime_atomic64_sample.RuntimeAtomic64Sample{};
    try module.init(17);
    _ = try module.runSelftest();

    var loader = RuntimeAtomic64Loader{};
    const prepared = try loader.prepare(&module);

    const swapped = try module.swapCounter(-9);
    const compare = try module.compareSwapCounter(-9, 33);
    const add_unless = try module.addUnlessCounter(4, 99);
    const and_previous = try module.andCounter(0b1_1111);
    const xor_previous = try module.xorCounter(0b1010);

    const live_counter = module.snapshotCounter();
    const pending_plan = try loader.requestRuntimeLoad();

    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(@as(i64, 17), swapped);
    try std.testing.expect(compare.stored);
    try std.testing.expectEqual(@as(i64, -9), compare.previous);
    try std.testing.expect(add_unless.changed);
    try std.testing.expectEqual(@as(i64, 33), add_unless.previous);
    try std.testing.expectEqual(@as(i64, 37), and_previous);
    try std.testing.expectEqual(@as(i64, 5), xor_previous);
    try std.testing.expectEqual(@as(i64, 15), live_counter);
    try std.testing.expectEqual(@as(i64, 17), pending_plan.summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 5), pending_plan.summary.operation_families.len);
    try std.testing.expect(pending_plan.summary.checked_returning_paths);
    try std.testing.expect(pending_plan.summary.checked_bitwise_paths);
    try std.testing.expect(pending_plan.summary.checked_guard_paths);
    try std.testing.expectEqual(@as(usize, 1), module.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), pending_plan.summary.selftest_runs);

    _ = prepared;
}

test "runtime atomic64 loader emits the shared runtime-loader contract plan" {
    var module = runtime_atomic64_sample.RuntimeAtomic64Sample{};
    try module.init(0x1111_1111_2222_2222);
    _ = try module.runSelftest();

    var loader = RuntimeAtomic64Loader{};
    const plan = try loader.prepare(&module);
    const shared_plan = toSharedLoadPlan(plan);

    try std.testing.expect(keepsSharedLoadPlanSnapshotExplicit(plan, shared_plan));
    try std.testing.expectEqual(runtime_loader.AllocatorHandoff.caller_provided, shared_plan.allocator_handoff);
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
        .caller_provided,
        shared_plan.init_flow,
    ));

    try shared_request.releaseWithoutSubstrate();
    try std.testing.expectEqual(runtime_loader.RequestState.released_without_substrate, shared_request.state);
}

test "runtime atomic64 loader keeps initialized-stage shared contract plans explicit" {
    var module = runtime_atomic64_sample.RuntimeAtomic64Sample{};
    try module.init(9);

    var loader = RuntimeAtomic64Loader{};
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
        .caller_provided,
        shared_plan.init_flow,
    ));
}

test "runtime atomic64 loader keeps initialized shared-request snapshots stable across later selftest activity" {
    var module = runtime_atomic64_sample.RuntimeAtomic64Sample{};
    try module.init(9);

    var loader = RuntimeAtomic64Loader{};
    var shared_request = try loader.prepareSharedRequest(&module);
    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);

    const prepared_plan = shared_request.plan;
    try std.testing.expectEqual(runtime_loader.HandoffStage.initialized, prepared_plan.init_flow.handoff_stage);
    try std.testing.expectEqual(@as(usize, 0), prepared_plan.init_flow.selftest_runs);

    const selftest = try module.runSelftest();
    const live_plan = try RuntimeAtomic64Loader.planFor(&module);
    const pending_plan = try loader.requestSharedRuntimeLoad(&shared_request);

    try std.testing.expectEqual(@as(usize, 5), selftest.operation_families.len);
    try std.testing.expectEqual(runtime_atomic64_sample.ModuleStage.selftest_complete, live_plan.handoff_stage);
    try std.testing.expectEqual(@as(usize, 5), live_plan.summary.operation_families.len);
    try std.testing.expect(live_plan.summary.checked_returning_paths);
    try std.testing.expect(live_plan.summary.checked_bitwise_paths);
    try std.testing.expect(live_plan.summary.checked_guard_paths);
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
        .caller_provided,
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

test "runtime atomic64 loader bridges the shared request lifecycle without widening atomic64 claims" {
    var module = runtime_atomic64_sample.RuntimeAtomic64Sample{};
    try module.init(0x1111_1111_2222_2222);
    _ = try module.runSelftest();

    var loader = RuntimeAtomic64Loader{};
    var shared_request = try loader.prepareSharedRequest(&module);
    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);

    const pending_plan = try loader.requestSharedRuntimeLoad(&shared_request);
    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.waiting_on_runtime_substrate, shared_request.state);
    try std.testing.expectEqualStrings("runtime_atomic64", pending_plan.module_name);
    try std.testing.expectEqualStrings("lib/atomic64_test.c", pending_plan.anchor);
    try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(
        pending_plan,
        .caller_provided,
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

test "runtime atomic64 loader surfaces shared request drift before any live atomic64 claim" {
    var module = runtime_atomic64_sample.RuntimeAtomic64Sample{};
    try module.init(0x1111_1111_2222_2222);
    _ = try module.runSelftest();

    var loader = RuntimeAtomic64Loader{};
    var shared_request = try loader.prepareSharedRequest(&module);
    shared_request.plan.module_name = "runtime_atomic64_drift";

    try std.testing.expectError(error.SharedLoadPlanDrift, loader.requestSharedRuntimeLoad(&shared_request));
    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.waiting_on_runtime_substrate, shared_request.state);

    try loader.releaseSharedWithoutSubstrate(&shared_request);
    try std.testing.expectEqual(LoaderStage.released_without_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.released_without_substrate, shared_request.state);
}

test "runtime atomic64 loader rejects shared-load-plan snapshot drift" {
    var module = runtime_atomic64_sample.RuntimeAtomic64Sample{};
    try module.init(0x1111_1111_2222_2222);
    _ = try module.runSelftest();

    const plan = try RuntimeAtomic64Loader.planFor(&module);
    const shared_plan = toSharedLoadPlan(plan);
    try std.testing.expect(keepsSharedLoadPlanSnapshotExplicit(plan, shared_plan));

    var drifted_module = shared_plan;
    drifted_module.module_name = "runtime_atomic64_drift";
    try std.testing.expect(!keepsSharedLoadPlanSnapshotExplicit(plan, drifted_module));

    var drifted_allocator = shared_plan;
    drifted_allocator.allocator_handoff = .kernel_heap;
    try std.testing.expect(!keepsSharedLoadPlanSnapshotExplicit(plan, drifted_allocator));

    var drifted_stage = shared_plan;
    drifted_stage.init_flow.handoff_stage = .initialized;
    try std.testing.expect(!keepsSharedLoadPlanSnapshotExplicit(plan, drifted_stage));

    var drifted_selftest = shared_plan;
    drifted_selftest.init_flow.selftest_runs += 1;
    try std.testing.expect(!keepsSharedLoadPlanSnapshotExplicit(plan, drifted_selftest));
}
