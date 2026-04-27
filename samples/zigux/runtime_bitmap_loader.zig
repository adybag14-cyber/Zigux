const std = @import("std");
const runtime_bitmap_sample = @import("runtime_bitmap_sample");
const runtime_loader = @import("runtime_loader");

pub const LoaderStage = runtime_loader.LoaderStage;

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
    return .{
        .module_name = plan.module_name,
        .anchor = plan.anchor,
        .entry_symbol = plan.entry_symbol,
        .exit_symbol = plan.exit_symbol,
        .requires_runtime_substrate = plan.requires_runtime_substrate,
        .provides_selftest_hook = plan.provides_selftest_hook,
        .handoff_stage = .waiting_on_runtime_substrate,
        .allocator_handoff = runtime_loader.allocatorHandoffFor(.kernel_heap),
        .payload = .{
            .bitmap = .{
                .first_set = plan.summary.first_set,
                .first_zero = plan.summary.first_zero,
                .weight = plan.summary.weight,
                .nbits = plan.summary.nbits,
            },
        },
    };
}

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

test "runtime bitmap loader emits the shared runtime-loader request shape" {
    var module = runtime_bitmap_sample.RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 0, 5, 64, 70 });
    _ = try module.runSelftest();

    var loader = RuntimeBitmapLoader{};
    _ = try loader.prepare(&module);

    const request = try loader.requestSharedRuntimeLoad();
    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.LoaderLane.bitmap, request.lane());
    try std.testing.expect(request.isWaitingOnRuntimeSubstrate());
    try std.testing.expectEqual(@as(u32, 0), request.payload.bitmap.first_set);
    try std.testing.expectEqual(@as(u32, 1), request.payload.bitmap.first_zero);
    try std.testing.expectEqual(@as(u32, 4), request.payload.bitmap.weight);
    try std.testing.expectEqual(runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits, request.payload.bitmap.nbits);
    try std.testing.expectEqual(runtime_loader.LoaderStage.waiting_on_runtime_substrate, request.handoff_stage);
    try std.testing.expectEqual(runtime_loader.LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.LoaderLane.bitmap, std.meta.activeTag(request.payload));
}

test "runtime bitmap loader can release the shared runtime-loader request without substrate" {
    var module = runtime_bitmap_sample.RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 0, 5, 64, 70 });
    _ = try module.runSelftest();

    var loader = RuntimeBitmapLoader{};
    _ = try loader.prepare(&module);

    const released = try loader.releaseSharedRuntimeLoadWithoutSubstrate();
    try std.testing.expectEqual(LoaderStage.released_without_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.LoaderLane.bitmap, released.lane());
    try std.testing.expect(released.isReleasedWithoutSubstrate());
    try std.testing.expect(!released.isWaitingOnRuntimeSubstrate());
    try std.testing.expectEqual(runtime_loader.LoaderStage.released_without_substrate, released.handoff_stage);
    try std.testing.expectEqual(@as(u32, 0), released.payload.bitmap.first_set);
    try std.testing.expectEqual(@as(u32, 1), released.payload.bitmap.first_zero);
    try std.testing.expectEqual(@as(u32, 4), released.payload.bitmap.weight);
    try std.testing.expectEqual(runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits, released.payload.bitmap.nbits);
    try std.testing.expectEqualStrings("zigux_runtime_bitmap_init", released.entry_symbol);
    try std.testing.expectEqualStrings("zigux_runtime_bitmap_exit", released.exit_symbol);
    try std.testing.expectError(error.InvalidLoaderState, loader.requestSharedRuntimeLoad());
}
