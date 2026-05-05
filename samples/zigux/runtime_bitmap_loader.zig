const std = @import("std");
const runtime_bitmap_sample = @import("runtime_bitmap_sample");

pub const LoaderStage = enum(u8) {
    idle,
    prepared,
    waiting_on_runtime_substrate,
    released_without_substrate,
};

pub const RuntimeBitmapLoadPlan = struct {
    module_name: []const u8,
    anchor: []const u8,
    entry_symbol: []const u8,
    exit_symbol: []const u8,
    requires_runtime_substrate: bool,
    provides_selftest_hook: bool,
    handoff_stage: runtime_bitmap_sample.ModuleStage,
    summary: runtime_bitmap_sample.RuntimeBitmapSummary,
};

pub const RuntimeBitmapLoader = struct {
    const Self = @This();

    stage_state: LoaderStage = .idle,
    cached_plan: ?RuntimeBitmapLoadPlan = null,

    pub fn stage(self: *const Self) LoaderStage {
        return self.stage_state;
    }

    pub fn planFor(module: *const runtime_bitmap_sample.RuntimeBitmapSample) !RuntimeBitmapLoadPlan {
        const descriptor = runtime_bitmap_sample.RuntimeBitmapSample.descriptor();
        const module_stage = module.stage();
        switch (module_stage) {
            .initialized, .selftest_complete => {},
            else => return error.InvalidModuleLifecycleForLoader,
        }

        if (!descriptor.requires_runtime_substrate) return error.LoaderNotRequired;

        return .{
            .module_name = descriptor.name,
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
        if (self.stage_state != .idle) return error.LoaderAlreadyPrepared;

        const plan = try planFor(module);
        self.cached_plan = plan;
        self.stage_state = .prepared;
        return plan;
    }

    pub fn requestRuntimeLoad(self: *Self) !RuntimeBitmapLoadPlan {
        if (self.stage_state != .prepared) return error.InvalidLoaderState;

        self.stage_state = .waiting_on_runtime_substrate;
        return self.cached_plan orelse error.MissingLoadPlan;
    }

    pub fn releaseWithoutSubstrate(self: *Self) !void {
        if (self.stage_state != .waiting_on_runtime_substrate) return error.InvalidLoaderState;
        self.stage_state = .released_without_substrate;
    }
};

test "runtime bitmap loader prepares a bounded handoff plan from the sample contract" {
    var module = runtime_bitmap_sample.RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 0, 5, 64, 70 });
    _ = try module.runSelftest();

    var loader = RuntimeBitmapLoader{};
    const plan = try loader.prepare(&module);

    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqualStrings("runtime_bitmap", plan.module_name);
    try std.testing.expectEqualStrings("lib/test_bitmap.c", plan.anchor);
    try std.testing.expectEqualStrings("zigux_runtime_bitmap_init", plan.entry_symbol);
    try std.testing.expectEqualStrings("zigux_runtime_bitmap_exit", plan.exit_symbol);
    try std.testing.expect(plan.requires_runtime_substrate);
    try std.testing.expect(plan.provides_selftest_hook);
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.selftest_complete, plan.handoff_stage);
    try std.testing.expectEqual(@as(u32, 0), plan.summary.first_set);
    try std.testing.expectEqual(@as(u32, 1), plan.summary.first_zero);
    try std.testing.expectEqual(@as(u32, 4), plan.summary.weight);
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

    try loader.releaseWithoutSubstrate();
    try std.testing.expectEqual(LoaderStage.released_without_substrate, loader.stage());
    try std.testing.expectError(error.InvalidLoaderState, loader.requestRuntimeLoad());

    try module.exit();
    try std.testing.expectError(error.InvalidModuleLifecycleForLoader, RuntimeBitmapLoader.planFor(&module));
}

test "runtime bitmap loader keeps the prepared snapshot stable across later bitmap mutation" {
    var module = runtime_bitmap_sample.RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 0, 5, 64, 70 });
    _ = try module.runSelftest();

    var loader = RuntimeBitmapLoader{};
    const prepared = try loader.prepare(&module);

    try module.clearRange(0, 1);
    try module.setRange(9, 4);

    const live_summary = module.summary();
    const pending_plan = try loader.requestRuntimeLoad();

    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(@as(u32, 5), live_summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), live_summary.first_zero);
    try std.testing.expectEqual(@as(u32, 7), live_summary.weight);
    try std.testing.expectEqual(@as(u32, 0), pending_plan.summary.first_set);
    try std.testing.expectEqual(@as(u32, 1), pending_plan.summary.first_zero);
    try std.testing.expectEqual(@as(u32, 4), pending_plan.summary.weight);
    try std.testing.expectEqual(runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits, live_summary.nbits);
    try std.testing.expectEqual(runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits, pending_plan.summary.nbits);

    _ = prepared;
}
