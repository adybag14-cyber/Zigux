const std = @import("std");
const runtime_atomic64_sample = @import("runtime_atomic64_sample");
const runtime_bitmap_sample = @import("runtime_bitmap_sample");
const runtime_kretprobe_sample = @import("runtime_kretprobe_sample");
const runtime_kretprobe_loader = @import("runtime_kretprobe_loader");
const runtime_loader = @import("runtime_loader");

const RuntimeAtomic64Sample = runtime_atomic64_sample.RuntimeAtomic64Sample;
const RuntimeBitmapSample = runtime_bitmap_sample.RuntimeBitmapSample;
const RuntimeKretprobeSample = runtime_kretprobe_sample.RuntimeKretprobeSample;
const RuntimeKretprobeLoader = runtime_kretprobe_loader.RuntimeKretprobeLoader;

fn atomic64PlanFor(
    module: *const RuntimeAtomic64Sample,
    allocator_handoff: runtime_loader.AllocatorHandoff,
) !runtime_loader.LoadPlan {
    const descriptor = RuntimeAtomic64Sample.descriptor();
    const snapshot = module.lifecycleSnapshot();
    if (snapshot.stage != .selftest_complete) return error.InvalidLifecycleTransition;

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
            .handoff_stage = .selftest_complete,
            .init_runs = snapshot.init_runs,
            .selftest_runs = snapshot.selftest_runs,
            .exit_runs = snapshot.exit_runs,
        },
    };
}

fn bitmapPlanFor(
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

test "first-loadable runtime pilot families keep family-specific shared-loader handoff stages explicit" {
    var atomic_module = RuntimeAtomic64Sample{};
    try atomic_module.init(23);
    _ = try atomic_module.runSelftest();

    const atomic_plan = try atomic64PlanFor(&atomic_module, .caller_provided);
    try std.testing.expect(runtime_loader.keepsApprovedPilotFamilyContract(atomic_plan));
    try std.testing.expect(runtime_loader.keepsApprovedPilotFamilyShape(atomic_plan));
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(atomic_plan));
    try std.testing.expectEqual(runtime_loader.HandoffStage.selftest_complete, atomic_plan.init_flow.handoff_stage);
    try std.testing.expectEqual(@as(usize, 1), atomic_plan.init_flow.selftest_runs);

    var bitmap_module = RuntimeBitmapSample{};
    try bitmap_module.initWithSetBits(&.{ 0, 63, 64, 127 });

    const bitmap_initialized_plan = try bitmapPlanFor(&bitmap_module, .arena);
    try std.testing.expect(runtime_loader.keepsApprovedPilotFamilyContract(bitmap_initialized_plan));
    try std.testing.expect(runtime_loader.keepsApprovedPilotFamilyShape(bitmap_initialized_plan));
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(bitmap_initialized_plan));
    try std.testing.expectEqual(runtime_loader.HandoffStage.initialized, bitmap_initialized_plan.init_flow.handoff_stage);
    try std.testing.expectEqual(@as(usize, 0), bitmap_initialized_plan.init_flow.selftest_runs);

    _ = try bitmap_module.runSelftest();

    const bitmap_selftested_plan = try bitmapPlanFor(&bitmap_module, .arena);
    try std.testing.expect(runtime_loader.keepsApprovedPilotFamilyContract(bitmap_selftested_plan));
    try std.testing.expect(!runtime_loader.keepsApprovedPilotFamilyShape(bitmap_selftested_plan));
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(bitmap_selftested_plan));
    try std.testing.expectEqual(runtime_loader.HandoffStage.selftest_complete, bitmap_selftested_plan.init_flow.handoff_stage);
    try std.testing.expectEqual(@as(usize, 1), bitmap_selftested_plan.init_flow.selftest_runs);

    var kretprobe_module = RuntimeKretprobeSample{};
    try kretprobe_module.init();

    const kretprobe_initialized_plan = try RuntimeKretprobeLoader.planFor(&kretprobe_module, .kernel_heap);
    try std.testing.expect(runtime_loader.keepsApprovedPilotFamilyContract(kretprobe_initialized_plan));
    try std.testing.expect(runtime_loader.keepsApprovedPilotFamilyShape(kretprobe_initialized_plan));
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(kretprobe_initialized_plan));
    try std.testing.expectEqual(
        runtime_loader.HandoffStage.initialized,
        kretprobe_initialized_plan.init_flow.handoff_stage,
    );
    try std.testing.expectEqual(@as(usize, 0), kretprobe_initialized_plan.init_flow.selftest_runs);

    _ = try kretprobe_module.runSelftest();

    const kretprobe_selftested_plan = try RuntimeKretprobeLoader.planFor(&kretprobe_module, .kernel_heap);
    try std.testing.expect(runtime_loader.keepsApprovedPilotFamilyContract(kretprobe_selftested_plan));
    try std.testing.expect(!runtime_loader.keepsApprovedPilotFamilyShape(kretprobe_selftested_plan));
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(kretprobe_selftested_plan));
    try std.testing.expectEqual(
        runtime_loader.HandoffStage.selftest_complete,
        kretprobe_selftested_plan.init_flow.handoff_stage,
    );
    try std.testing.expectEqual(@as(usize, 1), kretprobe_selftested_plan.init_flow.selftest_runs);
}

test "first-loadable initialized-stage shared requests stay frozen across later selftest activity" {
    var bitmap_module = RuntimeBitmapSample{};
    try bitmap_module.initWithSetBits(&.{ 0, 63, 64, 127 });

    const bitmap_prepared_plan = try bitmapPlanFor(&bitmap_module, .arena);
    var bitmap_request = try runtime_loader.prepareRequest(bitmap_prepared_plan);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        bitmap_request,
        .prepared,
        bitmap_prepared_plan,
    ));

    _ = try bitmap_module.runSelftest();

    const bitmap_live_plan = try bitmapPlanFor(&bitmap_module, .arena);
    try std.testing.expect(!runtime_loader.keepsApprovedPilotFamilyShape(bitmap_live_plan));
    try std.testing.expectEqual(
        runtime_loader.HandoffStage.selftest_complete,
        bitmap_live_plan.init_flow.handoff_stage,
    );

    const bitmap_pending_plan = try bitmap_request.requestRuntimeLoad();
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(bitmap_pending_plan, bitmap_prepared_plan));
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        bitmap_request,
        .waiting_on_runtime_substrate,
        bitmap_pending_plan,
    ));
    try std.testing.expectEqual(
        runtime_loader.HandoffStage.initialized,
        bitmap_pending_plan.init_flow.handoff_stage,
    );
    try std.testing.expectEqual(@as(usize, 0), bitmap_pending_plan.init_flow.selftest_runs);

    try bitmap_request.releaseWithoutSubstrate();
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        bitmap_request,
        .released_without_substrate,
        bitmap_pending_plan,
    ));

    var kretprobe_module = RuntimeKretprobeSample{};
    try kretprobe_module.init();

    var kretprobe_loader = RuntimeKretprobeLoader{ .allocator_handoff = .kernel_heap };
    var kretprobe_request = try kretprobe_loader.prepareSharedRequest(&kretprobe_module);
    const kretprobe_prepared_plan = kretprobe_request.plan;
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        kretprobe_request,
        .prepared,
        kretprobe_prepared_plan,
    ));
    try std.testing.expectEqual(runtime_kretprobe_loader.LoaderStage.prepared, kretprobe_loader.stage());

    _ = try kretprobe_module.runSelftest();

    const kretprobe_live_plan = try RuntimeKretprobeLoader.planFor(&kretprobe_module, .kernel_heap);
    try std.testing.expect(!runtime_loader.keepsApprovedPilotFamilyShape(kretprobe_live_plan));
    try std.testing.expectEqual(
        runtime_loader.HandoffStage.selftest_complete,
        kretprobe_live_plan.init_flow.handoff_stage,
    );

    const kretprobe_pending_plan = try kretprobe_loader.requestSharedRuntimeLoad(&kretprobe_request);
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(kretprobe_pending_plan, kretprobe_prepared_plan));
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        kretprobe_request,
        .waiting_on_runtime_substrate,
        kretprobe_pending_plan,
    ));
    try std.testing.expectEqual(
        runtime_loader.HandoffStage.initialized,
        kretprobe_pending_plan.init_flow.handoff_stage,
    );
    try std.testing.expectEqual(@as(usize, 0), kretprobe_pending_plan.init_flow.selftest_runs);

    try kretprobe_loader.releaseSharedWithoutSubstrate(&kretprobe_request);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        kretprobe_request,
        .released_without_substrate,
        kretprobe_pending_plan,
    ));
    try std.testing.expectEqual(
        runtime_kretprobe_loader.LoaderStage.released_without_substrate,
        kretprobe_loader.stage(),
    );
}

test "first-loadable selftest-complete readiness stays split between atomic64 and the initialized-stage families" {
    var atomic_module = RuntimeAtomic64Sample{};
    try atomic_module.init(41);
    _ = try atomic_module.runSelftest();

    const atomic_plan = try atomic64PlanFor(&atomic_module, .caller_provided);
    var atomic_request = try runtime_loader.prepareRequest(atomic_plan);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        atomic_request,
        .prepared,
        atomic_plan,
    ));

    const atomic_pending_plan = try atomic_request.requestRuntimeLoad();
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(atomic_pending_plan, atomic_plan));
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        atomic_request,
        .waiting_on_runtime_substrate,
        atomic_pending_plan,
    ));
    try atomic_request.releaseWithoutSubstrate();
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        atomic_request,
        .released_without_substrate,
        atomic_pending_plan,
    ));

    var bitmap_module = RuntimeBitmapSample{};
    try bitmap_module.initWithSetBits(&.{ 0, 63, 64, 127 });
    _ = try bitmap_module.runSelftest();

    const bitmap_selftested_plan = try bitmapPlanFor(&bitmap_module, .caller_provided);
    try std.testing.expect(!runtime_loader.keepsApprovedPilotFamilyShape(bitmap_selftested_plan));
    try std.testing.expectError(
        error.InvalidPilotFamilyShape,
        runtime_loader.prepareRequest(bitmap_selftested_plan),
    );

    var kretprobe_module = RuntimeKretprobeSample{};
    try kretprobe_module.init();
    _ = try kretprobe_module.runSelftest();

    const kretprobe_selftested_plan = try RuntimeKretprobeLoader.planFor(&kretprobe_module, .caller_provided);
    try std.testing.expect(!runtime_loader.keepsApprovedPilotFamilyShape(kretprobe_selftested_plan));

    var kretprobe_loader = RuntimeKretprobeLoader{ .allocator_handoff = .caller_provided };
    try std.testing.expectError(
        error.InvalidPilotFamilyShape,
        kretprobe_loader.prepareSharedRequest(&kretprobe_module),
    );
    try std.testing.expectEqual(runtime_kretprobe_loader.LoaderStage.cold, kretprobe_loader.stage());
}
