const std = @import("std");
const runtime_atomic64_sample = @import("runtime_atomic64_sample");
const runtime_bitmap_sample = @import("runtime_bitmap_sample");
const runtime_loader = @import("runtime_loader");

const RuntimeAtomic64Sample = runtime_atomic64_sample.RuntimeAtomic64Sample;
const RuntimeBitmapSample = runtime_bitmap_sample.RuntimeBitmapSample;

const Atomic64SharedLoader = struct {
    pub fn planFor(
        module: *const RuntimeAtomic64Sample,
        allocator_handoff: runtime_loader.AllocatorHandoff,
    ) !runtime_loader.LoadPlan {
        const descriptor = RuntimeAtomic64Sample.descriptor();
        const snapshot = module.lifecycleSnapshot();
        const handoff_stage = switch (snapshot.stage) {
            .initialized => runtime_loader.HandoffStage.initialized,
            .selftest_complete => runtime_loader.HandoffStage.selftest_complete,
            else => return error.InvalidLifecycleTransition,
        };

        return .{
            .module_name = descriptor.name,
            .anchor = descriptor.anchor,
            .entry_symbol = "zigux_runtime_atomic64_init",
            .exit_symbol = "zigux_runtime_atomic64_exit",
            .requires_runtime_substrate = descriptor.requires_runtime_substrate,
            .provides_selftest_hook = descriptor.provides_selftest_hook,
            .module_metadata = .{
                .license = "GPL",
                .aliases = &.{"zigux:runtime-pilot:runtime_atomic64"},
            },
            .allocator_handoff = allocator_handoff,
            .init_flow = .{
                .handoff_stage = handoff_stage,
                .init_runs = snapshot.init_runs,
                .selftest_runs = snapshot.selftest_runs,
                .exit_runs = snapshot.exit_runs,
            },
        };
    }
};

const BitmapSharedLoader = struct {
    pub fn planFor(
        module: *const RuntimeBitmapSample,
        allocator_handoff: runtime_loader.AllocatorHandoff,
    ) !runtime_loader.LoadPlan {
        const descriptor = RuntimeBitmapSample.descriptor();
        const summary = module.summary();
        const handoff_stage = switch (module.stage()) {
            .initialized => runtime_loader.HandoffStage.initialized,
            .selftest_complete => runtime_loader.HandoffStage.selftest_complete,
            else => return error.InvalidLifecycleTransition,
        };

        return .{
            .module_name = descriptor.name,
            .anchor = descriptor.anchor,
            .entry_symbol = "zigux_runtime_bitmap_init",
            .exit_symbol = "zigux_runtime_bitmap_exit",
            .requires_runtime_substrate = descriptor.requires_runtime_substrate,
            .provides_selftest_hook = descriptor.provides_selftest_hook,
            .module_metadata = .{
                .license = "GPL",
                .aliases = &.{"zigux:runtime-pilot:runtime_bitmap"},
            },
            .allocator_handoff = allocator_handoff,
            .init_flow = .{
                .handoff_stage = handoff_stage,
                .init_runs = summary.init_runs,
                .selftest_runs = summary.selftest_runs,
                .exit_runs = summary.exit_runs,
            },
        };
    }
};

test "first-loadable loader parity keeps atomic64 selftest-complete handoff explicit" {
    var module = RuntimeAtomic64Sample{};
    try module.init(0x2aaa_3137_4001_500d);
    _ = try module.runSelftest();

    const plan = try Atomic64SharedLoader.planFor(&module, .caller_provided);
    try std.testing.expectEqualStrings("runtime_atomic64", plan.module_name);
    try std.testing.expectEqualStrings("lib/atomic64_test.c", plan.anchor);
    try std.testing.expectEqualStrings("zigux_runtime_atomic64_init", plan.entry_symbol);
    try std.testing.expectEqualStrings("zigux_runtime_atomic64_exit", plan.exit_symbol);
    try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(
        plan,
        .caller_provided,
        .{
            .handoff_stage = .selftest_complete,
            .init_runs = 1,
            .selftest_runs = 1,
            .exit_runs = 0,
        },
    ));
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(plan));

    var request = try runtime_loader.prepareRequest(plan);
    const pending_plan = try request.requestRuntimeLoad();
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(pending_plan, plan));
    try request.releaseWithoutSubstrate();
    try std.testing.expectEqual(
        runtime_loader.RequestState.released_without_substrate,
        request.state,
    );
}

test "first-loadable loader parity keeps atomic64 initialized handoff blocked by the current family contract" {
    var module = RuntimeAtomic64Sample{};
    try module.init(17);

    const plan = try Atomic64SharedLoader.planFor(&module, .caller_provided);
    try std.testing.expectEqual(
        runtime_loader.HandoffStage.initialized,
        plan.init_flow.handoff_stage,
    );
    try std.testing.expectError(error.InvalidPilotFamilyShape, runtime_loader.prepareRequest(plan));
}

test "first-loadable loader parity keeps bitmap initialized handoff explicit" {
    var module = RuntimeBitmapSample{};
    try module.initFromBitList("0, 63, 64, 127");

    const plan = try BitmapSharedLoader.planFor(&module, .arena);
    try std.testing.expectEqualStrings("runtime_bitmap", plan.module_name);
    try std.testing.expectEqualStrings("lib/test_bitmap.c", plan.anchor);
    try std.testing.expectEqualStrings("zigux_runtime_bitmap_init", plan.entry_symbol);
    try std.testing.expectEqualStrings("zigux_runtime_bitmap_exit", plan.exit_symbol);
    try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(
        plan,
        .arena,
        .{
            .handoff_stage = .initialized,
            .init_runs = 1,
            .selftest_runs = 0,
            .exit_runs = 0,
        },
    ));
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(plan));

    var request = try runtime_loader.prepareRequest(plan);
    const pending_plan = try request.requestRuntimeLoad();
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(pending_plan, plan));
    try request.releaseWithoutSubstrate();
    try std.testing.expectEqual(
        runtime_loader.RequestState.released_without_substrate,
        request.state,
    );
}

test "first-loadable loader parity keeps bitmap prepared requests stable across later selftest activity" {
    var module = RuntimeBitmapSample{};
    try module.initFromBitList("0, 63, 64, 127");

    const initialized_plan = try BitmapSharedLoader.planFor(&module, .kernel_heap);
    var request = try runtime_loader.prepareRequest(initialized_plan);

    _ = try module.runSelftest();
    const selftested_plan = try BitmapSharedLoader.planFor(&module, .kernel_heap);
    try std.testing.expectEqual(
        runtime_loader.HandoffStage.selftest_complete,
        selftested_plan.init_flow.handoff_stage,
    );
    try std.testing.expectEqual(@as(usize, 1), selftested_plan.init_flow.selftest_runs);
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(selftested_plan));

    const pending_plan = try request.requestRuntimeLoad();
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(pending_plan, initialized_plan));
    try std.testing.expectEqual(
        runtime_loader.HandoffStage.initialized,
        pending_plan.init_flow.handoff_stage,
    );
    try std.testing.expectEqual(@as(usize, 0), pending_plan.init_flow.selftest_runs);
}

test "first-loadable loader parity keeps bitmap selftest-complete handoff blocked by the current family contract" {
    var module = RuntimeBitmapSample{};
    try module.initFromBitList("0, 63, 64, 127");
    _ = try module.runSelftest();

    const plan = try BitmapSharedLoader.planFor(&module, .arena);
    try std.testing.expectEqual(
        runtime_loader.HandoffStage.selftest_complete,
        plan.init_flow.handoff_stage,
    );
    try std.testing.expectError(error.InvalidPilotFamilyShape, runtime_loader.prepareRequest(plan));
}
