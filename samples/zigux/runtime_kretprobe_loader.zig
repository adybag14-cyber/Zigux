const std = @import("std");
const runtime_kretprobe_sample = @import("runtime_kretprobe_sample");

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

    pub fn requestRuntimeLoad(self: *Self) !RuntimeKretprobeLoadPlan {
        if (self.stage_state != .prepared) return error.InvalidLoaderState;

        self.stage_state = .waiting_on_runtime_substrate;
        return self.cached_plan orelse error.MissingLoadPlan;
    }

    pub fn releaseWithoutSubstrate(self: *Self) !void {
        if (self.stage_state != .waiting_on_runtime_substrate) return error.InvalidLoaderState;
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
