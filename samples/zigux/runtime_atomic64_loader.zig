const std = @import("std");
const runtime_atomic64_sample = @import("runtime_atomic64_sample");

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

pub const RuntimeAtomic64Loader = struct {
    const Self = @This();

    stage_state: LoaderStage = .idle,
    cached_plan: ?RuntimeAtomic64LoadPlan = null,

    pub fn stage(self: *const Self) LoaderStage {
        return self.stage_state;
    }

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

    pub fn requestRuntimeLoad(self: *Self) !RuntimeAtomic64LoadPlan {
        if (self.stage_state != .prepared) return error.InvalidLoaderState;

        self.stage_state = .waiting_on_runtime_substrate;
        return self.cached_plan orelse error.MissingLoadPlan;
    }

    pub fn releaseWithoutSubstrate(self: *Self) !void {
        if (self.stage_state != .waiting_on_runtime_substrate) return error.InvalidLoaderState;
        self.stage_state = .released_without_substrate;
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
