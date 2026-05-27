const std = @import("std");
const runtime_atomic64_sample = @import("runtime_atomic64_sample");
const runtime_bitmap_sample = @import("runtime_bitmap_sample");
const runtime_kretprobe_sample = @import("runtime_kretprobe_sample");

const RuntimeAtomic64Sample = runtime_atomic64_sample.RuntimeAtomic64Sample;
const RuntimeBitmapSample = runtime_bitmap_sample.RuntimeBitmapSample;
const RuntimeKretprobeSample = runtime_kretprobe_sample.RuntimeKretprobeSample;

fn expectLifecycleCounts(
    atomic_module: *const RuntimeAtomic64Sample,
    bitmap_module: *const RuntimeBitmapSample,
    kretprobe_module: *const RuntimeKretprobeSample,
    expected_stage: runtime_atomic64_sample.ModuleStage,
    expected_init_runs: usize,
    expected_selftest_runs: usize,
    expected_exit_runs: usize,
) !void {
    const atomic_snapshot = atomic_module.lifecycleSnapshot();
    const atomic_summary = atomic_module.summary();
    const bitmap_summary = bitmap_module.summary();
    const kretprobe_snapshot = kretprobe_module.lifecycleSnapshot();
    const expected_stage_tag = @intFromEnum(expected_stage);

    try std.testing.expectEqual(expected_stage, atomic_snapshot.stage);
    try std.testing.expectEqual(expected_stage_tag, @intFromEnum(bitmap_module.stage()));
    try std.testing.expectEqual(expected_stage_tag, @intFromEnum(kretprobe_snapshot.stage));

    try std.testing.expectEqual(expected_init_runs, atomic_snapshot.init_runs);
    try std.testing.expectEqual(expected_init_runs, atomic_summary.init_runs);
    try std.testing.expectEqual(expected_init_runs, bitmap_summary.init_runs);
    try std.testing.expectEqual(expected_init_runs, kretprobe_snapshot.init_runs);

    try std.testing.expectEqual(expected_selftest_runs, atomic_snapshot.selftest_runs);
    try std.testing.expectEqual(expected_selftest_runs, atomic_summary.selftest_runs);
    try std.testing.expectEqual(expected_selftest_runs, bitmap_summary.selftest_runs);
    try std.testing.expectEqual(expected_selftest_runs, kretprobe_snapshot.selftest_runs);

    try std.testing.expectEqual(expected_exit_runs, atomic_snapshot.exit_runs);
    try std.testing.expectEqual(expected_exit_runs, atomic_summary.exit_runs);
    try std.testing.expectEqual(expected_exit_runs, bitmap_summary.exit_runs);
    try std.testing.expectEqual(expected_exit_runs, kretprobe_snapshot.exit_runs);
}

test "first-loadable runtime pilot families keep descriptor parity explicit" {
    const atomic_descriptor = RuntimeAtomic64Sample.descriptor();
    const bitmap_descriptor = RuntimeBitmapSample.descriptor();
    const kretprobe_descriptor = RuntimeKretprobeSample.descriptor();

    try std.testing.expectEqualStrings("runtime_atomic64", atomic_descriptor.name);
    try std.testing.expectEqualStrings("runtime_bitmap", bitmap_descriptor.name);
    try std.testing.expectEqualStrings("runtime_kretprobe", kretprobe_descriptor.name);
    try std.testing.expectEqualStrings("lib/atomic64_test.c", atomic_descriptor.anchor);
    try std.testing.expectEqualStrings("lib/test_bitmap.c", bitmap_descriptor.anchor);
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", kretprobe_descriptor.anchor);
    try std.testing.expect(atomic_descriptor.requires_runtime_substrate);
    try std.testing.expect(bitmap_descriptor.requires_runtime_substrate);
    try std.testing.expect(kretprobe_descriptor.requires_runtime_substrate);
    try std.testing.expect(atomic_descriptor.provides_selftest_hook);
    try std.testing.expect(bitmap_descriptor.provides_selftest_hook);
    try std.testing.expect(kretprobe_descriptor.provides_selftest_hook);
}

test "first-loadable runtime pilot families keep cold-state selftest and exit rejection aligned" {
    var atomic_module = RuntimeAtomic64Sample{};
    var bitmap_module = RuntimeBitmapSample{};
    var kretprobe_module = RuntimeKretprobeSample{};

    const cold_atomic_snapshot = atomic_module.lifecycleSnapshot();
    const cold_atomic_summary = atomic_module.summary();
    const cold_bitmap_summary = bitmap_module.summary();
    const cold_kretprobe_snapshot = kretprobe_module.lifecycleSnapshot();
    try expectLifecycleCounts(&atomic_module, &bitmap_module, &kretprobe_module, .cold, 0, 0, 0);

    try std.testing.expectError(error.InvalidLifecycleTransition, atomic_module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, bitmap_module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, kretprobe_module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, atomic_module.exit());
    try std.testing.expectError(error.InvalidLifecycleTransition, bitmap_module.exit());
    try std.testing.expectError(error.InvalidLifecycleTransition, kretprobe_module.exit());

    try expectLifecycleCounts(&atomic_module, &bitmap_module, &kretprobe_module, .cold, 0, 0, 0);
    try std.testing.expectEqual(cold_atomic_snapshot.allows_counter_ops, atomic_module.lifecycleSnapshot().allows_counter_ops);
    try std.testing.expectEqual(cold_atomic_summary.counter_snapshot, atomic_module.summary().counter_snapshot);
    try std.testing.expectEqual(cold_bitmap_summary.first_set, bitmap_module.summary().first_set);
    try std.testing.expectEqual(cold_bitmap_summary.first_zero, bitmap_module.summary().first_zero);
    try std.testing.expectEqual(cold_bitmap_summary.weight, bitmap_module.summary().weight);
    try std.testing.expectEqual(cold_bitmap_summary.nbits, bitmap_module.summary().nbits);
    try std.testing.expectEqual(cold_kretprobe_snapshot.registration_runs, kretprobe_module.lifecycleSnapshot().registration_runs);
    try std.testing.expectEqual(cold_kretprobe_snapshot.unregistration_runs, kretprobe_module.lifecycleSnapshot().unregistration_runs);
    try std.testing.expectEqual(cold_kretprobe_snapshot.completed_instances, kretprobe_module.lifecycleSnapshot().completed_instances);
    try std.testing.expectEqual(cold_kretprobe_snapshot.last_retval, kretprobe_module.lifecycleSnapshot().last_retval);
}

test "first-loadable runtime pilot families keep init selftest and exit counts aligned" {
    var atomic_module = RuntimeAtomic64Sample{};
    var bitmap_module = RuntimeBitmapSample{};
    var kretprobe_module = RuntimeKretprobeSample{};

    try expectLifecycleCounts(&atomic_module, &bitmap_module, &kretprobe_module, .cold, 0, 0, 0);

    try atomic_module.init(11);
    try bitmap_module.initWithSetBits(&.{ 0, 63, 64, 127 });
    try kretprobe_module.init();
    try expectLifecycleCounts(&atomic_module, &bitmap_module, &kretprobe_module, .initialized, 1, 0, 0);

    _ = try atomic_module.runSelftest();
    _ = try bitmap_module.runSelftest();
    _ = try kretprobe_module.runSelftest();
    try expectLifecycleCounts(&atomic_module, &bitmap_module, &kretprobe_module, .selftest_complete, 1, 1, 0);

    try atomic_module.exit();
    try bitmap_module.exit();
    try kretprobe_module.exit();
    try expectLifecycleCounts(&atomic_module, &bitmap_module, &kretprobe_module, .exited, 1, 1, 1);
}

test "first-loadable runtime pilot families keep direct exit parity explicit before selftest" {
    var atomic_module = RuntimeAtomic64Sample{};
    var bitmap_module = RuntimeBitmapSample{};
    var kretprobe_module = RuntimeKretprobeSample{};

    try atomic_module.init(-9);
    try bitmap_module.initFromBitList("0, 5, 64, 70");
    try kretprobe_module.init();
    try expectLifecycleCounts(&atomic_module, &bitmap_module, &kretprobe_module, .initialized, 1, 0, 0);

    try atomic_module.exit();
    try bitmap_module.exit();
    try kretprobe_module.exit();
    try expectLifecycleCounts(&atomic_module, &bitmap_module, &kretprobe_module, .exited, 1, 0, 1);
}

test "first-loadable runtime pilot families keep captured initialized direct-activity parity explicit across later selftest and exit" {
    var atomic_module = RuntimeAtomic64Sample{};
    var bitmap_module = RuntimeBitmapSample{};
    var kretprobe_module = RuntimeKretprobeSample{};

    try atomic_module.init(21);
    try bitmap_module.initWithSetBits(&.{ 0, 64, 70 });
    try kretprobe_module.init();

    const atomic_update = try atomic_module.addCounter(6);
    try std.testing.expectEqual(@as(i64, 21), atomic_update.previous);
    try std.testing.expectEqual(@as(i64, 27), atomic_update.final);

    try bitmap_module.setRange(9, 3);
    try std.testing.expectEqual(@as(u32, 3), try bitmap_module.countSetBitsInRange(9, 3));

    try kretprobe_module.registerProbe();
    try kretprobe_module.recordEntry();
    try kretprobe_module.recordReturn(13);
    try kretprobe_module.unregisterProbe();

    const initialized_atomic_summary = atomic_module.summary();
    const initialized_bitmap_summary = bitmap_module.summary();
    const initialized_kretprobe_snapshot = kretprobe_module.lifecycleSnapshot();
    try expectLifecycleCounts(
        &atomic_module,
        &bitmap_module,
        &kretprobe_module,
        .initialized,
        1,
        0,
        0,
    );
    try std.testing.expectEqual(@as(i64, 27), initialized_atomic_summary.counter_snapshot);
    try std.testing.expectEqual(@as(u32, 0), initialized_bitmap_summary.first_set);
    try std.testing.expectEqual(@as(u32, 6), initialized_bitmap_summary.weight);
    try std.testing.expectEqual(@as(usize, 1), initialized_kretprobe_snapshot.registration_runs);
    try std.testing.expectEqual(@as(usize, 1), initialized_kretprobe_snapshot.unregistration_runs);
    try std.testing.expectEqual(@as(usize, 1), initialized_kretprobe_snapshot.completed_instances);
    try std.testing.expectEqual(@as(?i32, 13), initialized_kretprobe_snapshot.last_retval);

    _ = try atomic_module.runSelftest();
    _ = try bitmap_module.runSelftest();
    _ = try kretprobe_module.runSelftest();
    try atomic_module.exit();
    try bitmap_module.exit();
    try kretprobe_module.exit();

    const exited_atomic_summary = atomic_module.summary();
    const exited_bitmap_summary = bitmap_module.summary();
    const exited_kretprobe_snapshot = kretprobe_module.lifecycleSnapshot();
    try expectLifecycleCounts(
        &atomic_module,
        &bitmap_module,
        &kretprobe_module,
        .exited,
        1,
        1,
        1,
    );

    try std.testing.expectEqual(@as(i64, 27), initialized_atomic_summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 0), initialized_atomic_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_atomic_summary.exit_runs);
    try std.testing.expectEqual(@as(u32, 6), initialized_bitmap_summary.weight);
    try std.testing.expectEqual(@as(usize, 0), initialized_bitmap_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_bitmap_summary.exit_runs);
    try std.testing.expectEqual(runtime_kretprobe_sample.ModuleStage.initialized, initialized_kretprobe_snapshot.stage);
    try std.testing.expectEqual(@as(usize, 0), initialized_kretprobe_snapshot.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_kretprobe_snapshot.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), initialized_kretprobe_snapshot.registration_runs);
    try std.testing.expectEqual(@as(usize, 1), initialized_kretprobe_snapshot.unregistration_runs);
    try std.testing.expectEqual(@as(usize, 1), initialized_kretprobe_snapshot.completed_instances);
    try std.testing.expectEqual(@as(?i32, 13), initialized_kretprobe_snapshot.last_retval);

    try std.testing.expectEqual(@as(i64, 27), exited_atomic_summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), exited_atomic_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_atomic_summary.exit_runs);
    try std.testing.expectEqual(@as(u32, 6), exited_bitmap_summary.weight);
    try std.testing.expectEqual(@as(usize, 1), exited_bitmap_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_bitmap_summary.exit_runs);
    try std.testing.expectEqual(@as(usize, 2), exited_kretprobe_snapshot.registration_runs);
    try std.testing.expectEqual(@as(usize, 2), exited_kretprobe_snapshot.unregistration_runs);
    try std.testing.expectEqual(@as(usize, 2), exited_kretprobe_snapshot.completed_instances);
    try std.testing.expectEqual(@as(?i32, 0), exited_kretprobe_snapshot.last_retval);
}

test "first-loadable runtime pilot families keep rejected repeat selftest and exit stable" {
    var atomic_module = RuntimeAtomic64Sample{};
    var bitmap_module = RuntimeBitmapSample{};
    var kretprobe_module = RuntimeKretprobeSample{};

    try atomic_module.init(23);
    try bitmap_module.initWithSetBits(&.{ 1, 64, 65, 90 });
    try kretprobe_module.init();
    _ = try atomic_module.runSelftest();
    _ = try bitmap_module.runSelftest();
    _ = try kretprobe_module.runSelftest();
    try expectLifecycleCounts(&atomic_module, &bitmap_module, &kretprobe_module, .selftest_complete, 1, 1, 0);

    try std.testing.expectError(error.InvalidLifecycleTransition, atomic_module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, bitmap_module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, kretprobe_module.runSelftest());
    try expectLifecycleCounts(&atomic_module, &bitmap_module, &kretprobe_module, .selftest_complete, 1, 1, 0);

    try atomic_module.exit();
    try bitmap_module.exit();
    try kretprobe_module.exit();
    try expectLifecycleCounts(&atomic_module, &bitmap_module, &kretprobe_module, .exited, 1, 1, 1);

    try std.testing.expectError(error.InvalidLifecycleTransition, atomic_module.exit());
    try std.testing.expectError(error.InvalidLifecycleTransition, bitmap_module.exit());
    try std.testing.expectError(error.InvalidLifecycleTransition, kretprobe_module.exit());
    try expectLifecycleCounts(&atomic_module, &bitmap_module, &kretprobe_module, .exited, 1, 1, 1);
}

test "first-loadable runtime pilot families keep rejected repeat selftest stable after initialized direct activity" {
    var atomic_module = RuntimeAtomic64Sample{};
    var bitmap_module = RuntimeBitmapSample{};
    var kretprobe_module = RuntimeKretprobeSample{};

    try atomic_module.init(21);
    try bitmap_module.initWithSetBits(&.{ 0, 64, 70 });
    try kretprobe_module.init();

    const atomic_update = try atomic_module.addCounter(6);
    try std.testing.expectEqual(@as(i64, 21), atomic_update.previous);
    try std.testing.expectEqual(@as(i64, 27), atomic_update.final);

    try bitmap_module.setRange(9, 3);
    try std.testing.expectEqual(@as(u32, 3), try bitmap_module.countSetBitsInRange(9, 3));

    try kretprobe_module.registerProbe();
    try kretprobe_module.recordEntry();
    try kretprobe_module.recordReturn(13);
    try kretprobe_module.unregisterProbe();
    try expectLifecycleCounts(&atomic_module, &bitmap_module, &kretprobe_module, .initialized, 1, 0, 0);

    _ = try atomic_module.runSelftest();
    _ = try bitmap_module.runSelftest();
    _ = try kretprobe_module.runSelftest();

    const before_rejected_selftest_atomic_summary = atomic_module.summary();
    const before_rejected_selftest_bitmap_summary = bitmap_module.summary();
    const before_rejected_selftest_kretprobe_snapshot = kretprobe_module.lifecycleSnapshot();
    try expectLifecycleCounts(&atomic_module, &bitmap_module, &kretprobe_module, .selftest_complete, 1, 1, 0);
    try std.testing.expectEqual(@as(i64, 27), before_rejected_selftest_atomic_summary.counter_snapshot);
    try std.testing.expectEqual(@as(u32, 6), before_rejected_selftest_bitmap_summary.weight);
    try std.testing.expectEqual(@as(usize, 2), before_rejected_selftest_kretprobe_snapshot.registration_runs);
    try std.testing.expectEqual(@as(usize, 2), before_rejected_selftest_kretprobe_snapshot.unregistration_runs);
    try std.testing.expectEqual(@as(usize, 2), before_rejected_selftest_kretprobe_snapshot.completed_instances);
    try std.testing.expectEqual(@as(?i32, 0), before_rejected_selftest_kretprobe_snapshot.last_retval);

    try std.testing.expectError(error.InvalidLifecycleTransition, atomic_module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, bitmap_module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, kretprobe_module.runSelftest());
    try expectLifecycleCounts(&atomic_module, &bitmap_module, &kretprobe_module, .selftest_complete, 1, 1, 0);
    try std.testing.expectEqual(
        before_rejected_selftest_atomic_summary.counter_snapshot,
        atomic_module.summary().counter_snapshot,
    );
    try std.testing.expectEqual(
        before_rejected_selftest_bitmap_summary.first_set,
        bitmap_module.summary().first_set,
    );
    try std.testing.expectEqual(
        before_rejected_selftest_bitmap_summary.weight,
        bitmap_module.summary().weight,
    );
    try std.testing.expectEqual(
        before_rejected_selftest_kretprobe_snapshot.completed_instances,
        kretprobe_module.lifecycleSnapshot().completed_instances,
    );
    try std.testing.expectEqual(
        before_rejected_selftest_kretprobe_snapshot.last_retval,
        kretprobe_module.lifecycleSnapshot().last_retval,
    );

    try atomic_module.exit();
    try bitmap_module.exit();
    try kretprobe_module.exit();

    const before_rejected_exit_selftest_atomic_summary = atomic_module.summary();
    const before_rejected_exit_selftest_bitmap_summary = bitmap_module.summary();
    const before_rejected_exit_selftest_kretprobe_snapshot = kretprobe_module.lifecycleSnapshot();
    try expectLifecycleCounts(&atomic_module, &bitmap_module, &kretprobe_module, .exited, 1, 1, 1);
    try std.testing.expectEqual(@as(i64, 27), before_rejected_exit_selftest_atomic_summary.counter_snapshot);
    try std.testing.expectEqual(@as(u32, 6), before_rejected_exit_selftest_bitmap_summary.weight);
    try std.testing.expectEqual(@as(usize, 2), before_rejected_exit_selftest_kretprobe_snapshot.registration_runs);
    try std.testing.expectEqual(@as(usize, 2), before_rejected_exit_selftest_kretprobe_snapshot.unregistration_runs);
    try std.testing.expectEqual(@as(usize, 2), before_rejected_exit_selftest_kretprobe_snapshot.completed_instances);
    try std.testing.expectEqual(@as(?i32, 0), before_rejected_exit_selftest_kretprobe_snapshot.last_retval);

    try std.testing.expectError(error.InvalidLifecycleTransition, atomic_module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, bitmap_module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, kretprobe_module.runSelftest());
    try expectLifecycleCounts(&atomic_module, &bitmap_module, &kretprobe_module, .exited, 1, 1, 1);
    try std.testing.expectEqual(
        before_rejected_exit_selftest_atomic_summary.counter_snapshot,
        atomic_module.summary().counter_snapshot,
    );
    try std.testing.expectEqual(
        before_rejected_exit_selftest_bitmap_summary.first_set,
        bitmap_module.summary().first_set,
    );
    try std.testing.expectEqual(
        before_rejected_exit_selftest_bitmap_summary.weight,
        bitmap_module.summary().weight,
    );
    try std.testing.expectEqual(
        before_rejected_exit_selftest_kretprobe_snapshot.completed_instances,
        kretprobe_module.lifecycleSnapshot().completed_instances,
    );
    try std.testing.expectEqual(
        before_rejected_exit_selftest_kretprobe_snapshot.last_retval,
        kretprobe_module.lifecycleSnapshot().last_retval,
    );
}

test "first-loadable runtime pilot families keep rejected repeat init stable" {
    var atomic_module = RuntimeAtomic64Sample{};
    var bitmap_module = RuntimeBitmapSample{};
    var kretprobe_module = RuntimeKretprobeSample{};

    try atomic_module.init(-41);
    try bitmap_module.initWithSetBits(&.{ 0, 5, 64, 70 });
    try kretprobe_module.init();

    const initialized_atomic_summary = atomic_module.summary();
    const initialized_bitmap_summary = bitmap_module.summary();
    const initialized_kretprobe_snapshot = kretprobe_module.lifecycleSnapshot();
    try expectLifecycleCounts(&atomic_module, &bitmap_module, &kretprobe_module, .initialized, 1, 0, 0);

    try std.testing.expectError(error.InvalidLifecycleTransition, atomic_module.init(9));
    try std.testing.expectError(error.InvalidLifecycleTransition, bitmap_module.initWithSetBits(&.{ 1, 2 }));
    try std.testing.expectError(error.InvalidLifecycleTransition, kretprobe_module.init());
    try expectLifecycleCounts(&atomic_module, &bitmap_module, &kretprobe_module, .initialized, 1, 0, 0);
    try std.testing.expectEqual(initialized_atomic_summary.counter_snapshot, atomic_module.summary().counter_snapshot);
    try std.testing.expectEqual(initialized_bitmap_summary.first_set, bitmap_module.summary().first_set);
    try std.testing.expectEqual(initialized_bitmap_summary.weight, bitmap_module.summary().weight);
    try std.testing.expectEqual(initialized_kretprobe_snapshot.completed_instances, kretprobe_module.lifecycleSnapshot().completed_instances);
    try std.testing.expectEqual(initialized_kretprobe_snapshot.last_retval, kretprobe_module.lifecycleSnapshot().last_retval);

    _ = try atomic_module.runSelftest();
    _ = try bitmap_module.runSelftest();
    _ = try kretprobe_module.runSelftest();

    const selftested_atomic_summary = atomic_module.summary();
    const selftested_bitmap_summary = bitmap_module.summary();
    const selftested_kretprobe_snapshot = kretprobe_module.lifecycleSnapshot();
    try expectLifecycleCounts(&atomic_module, &bitmap_module, &kretprobe_module, .selftest_complete, 1, 1, 0);

    try std.testing.expectError(error.InvalidLifecycleTransition, atomic_module.init(11));
    try std.testing.expectError(error.InvalidLifecycleTransition, bitmap_module.initWithSetBits(&.{ 3, 4 }));
    try std.testing.expectError(error.InvalidLifecycleTransition, kretprobe_module.init());
    try expectLifecycleCounts(&atomic_module, &bitmap_module, &kretprobe_module, .selftest_complete, 1, 1, 0);
    try std.testing.expectEqual(selftested_atomic_summary.counter_snapshot, atomic_module.summary().counter_snapshot);
    try std.testing.expectEqual(selftested_bitmap_summary.first_set, bitmap_module.summary().first_set);
    try std.testing.expectEqual(selftested_bitmap_summary.weight, bitmap_module.summary().weight);
    try std.testing.expectEqual(selftested_kretprobe_snapshot.completed_instances, kretprobe_module.lifecycleSnapshot().completed_instances);
    try std.testing.expectEqual(selftested_kretprobe_snapshot.last_retval, kretprobe_module.lifecycleSnapshot().last_retval);

    try atomic_module.exit();
    try bitmap_module.exit();
    try kretprobe_module.exit();

    const exited_atomic_summary = atomic_module.summary();
    const exited_bitmap_summary = bitmap_module.summary();
    const exited_kretprobe_snapshot = kretprobe_module.lifecycleSnapshot();
    try expectLifecycleCounts(&atomic_module, &bitmap_module, &kretprobe_module, .exited, 1, 1, 1);

    try std.testing.expectError(error.InvalidLifecycleTransition, atomic_module.init(13));
    try std.testing.expectError(error.InvalidLifecycleTransition, bitmap_module.initWithSetBits(&.{ 7, 8 }));
    try std.testing.expectError(error.InvalidLifecycleTransition, kretprobe_module.init());
    try expectLifecycleCounts(&atomic_module, &bitmap_module, &kretprobe_module, .exited, 1, 1, 1);
    try std.testing.expectEqual(exited_atomic_summary.counter_snapshot, atomic_module.summary().counter_snapshot);
    try std.testing.expectEqual(exited_bitmap_summary.first_set, bitmap_module.summary().first_set);
    try std.testing.expectEqual(exited_bitmap_summary.weight, bitmap_module.summary().weight);
    try std.testing.expectEqual(exited_kretprobe_snapshot.completed_instances, kretprobe_module.lifecycleSnapshot().completed_instances);
    try std.testing.expectEqual(exited_kretprobe_snapshot.last_retval, kretprobe_module.lifecycleSnapshot().last_retval);
}

test "first-loadable runtime pilot families keep post-selftest mutation parity explicit" {
    var atomic_module = RuntimeAtomic64Sample{};
    var bitmap_module = RuntimeBitmapSample{};
    var kretprobe_module = RuntimeKretprobeSample{};

    try atomic_module.init(9);
    try bitmap_module.initWithSetBits(&.{ 0, 5, 64, 70 });
    try kretprobe_module.init();

    _ = try atomic_module.runSelftest();
    _ = try bitmap_module.runSelftest();
    _ = try kretprobe_module.runSelftest();
    try expectLifecycleCounts(&atomic_module, &bitmap_module, &kretprobe_module, .selftest_complete, 1, 1, 0);

    const atomic_add = try atomic_module.addCounter(4);
    try std.testing.expectEqual(@as(i64, 9), atomic_add.previous);
    try std.testing.expectEqual(@as(i64, 13), atomic_add.final);

    try bitmap_module.setRange(9, 4);
    const bitmap_before_exit = bitmap_module.summary();
    try std.testing.expectEqual(@as(u32, 8), bitmap_before_exit.weight);
    try std.testing.expectEqual(@as(u32, 4), try bitmap_module.countSetBitsInRange(9, 4));

    try kretprobe_module.registerProbe();
    try kretprobe_module.recordEntry();
    try kretprobe_module.recordReturn(42);
    try kretprobe_module.unregisterProbe();
    const kretprobe_before_exit = kretprobe_module.lifecycleSnapshot();
    try std.testing.expectEqual(@as(usize, 2), kretprobe_before_exit.registration_runs);
    try std.testing.expectEqual(@as(usize, 2), kretprobe_before_exit.unregistration_runs);
    try std.testing.expectEqual(@as(usize, 2), kretprobe_before_exit.completed_instances);
    try std.testing.expectEqual(@as(?i32, 42), kretprobe_before_exit.last_retval);

    try expectLifecycleCounts(&atomic_module, &bitmap_module, &kretprobe_module, .selftest_complete, 1, 1, 0);

    try atomic_module.exit();
    try bitmap_module.exit();
    try kretprobe_module.exit();
    try expectLifecycleCounts(&atomic_module, &bitmap_module, &kretprobe_module, .exited, 1, 1, 1);
    try std.testing.expectEqual(@as(i64, 13), atomic_module.summary().counter_snapshot);
    try std.testing.expectEqual(bitmap_before_exit.weight, bitmap_module.summary().weight);
    try std.testing.expectEqual(kretprobe_before_exit.completed_instances, kretprobe_module.lifecycleSnapshot().completed_instances);
    try std.testing.expectEqual(kretprobe_before_exit.last_retval, kretprobe_module.lifecycleSnapshot().last_retval);
}

test "first-loadable runtime pilot families keep post-exit mutation guards aligned" {
    var atomic_module = RuntimeAtomic64Sample{};
    var bitmap_module = RuntimeBitmapSample{};
    var kretprobe_module = RuntimeKretprobeSample{};

    try atomic_module.init(17);
    try bitmap_module.initWithSetBits(&.{ 0, 5, 64, 70 });
    try kretprobe_module.init();

    _ = try atomic_module.runSelftest();
    _ = try bitmap_module.runSelftest();
    _ = try kretprobe_module.runSelftest();

    try atomic_module.exit();
    try bitmap_module.exit();
    try kretprobe_module.exit();
    try expectLifecycleCounts(&atomic_module, &bitmap_module, &kretprobe_module, .exited, 1, 1, 1);

    const exited_atomic_summary = atomic_module.summary();
    const exited_bitmap_summary = bitmap_module.summary();
    const exited_kretprobe_snapshot = kretprobe_module.lifecycleSnapshot();

    try std.testing.expectError(error.InvalidLifecycleTransition, atomic_module.addCounter(1));
    try std.testing.expectError(error.InvalidLifecycleTransition, bitmap_module.setRange(9, 4));
    try std.testing.expectError(error.InvalidLifecycleTransition, kretprobe_module.registerProbe());

    try expectLifecycleCounts(&atomic_module, &bitmap_module, &kretprobe_module, .exited, 1, 1, 1);
    try std.testing.expectEqual(exited_atomic_summary.counter_snapshot, atomic_module.summary().counter_snapshot);
    try std.testing.expectEqual(exited_bitmap_summary.first_set, bitmap_module.summary().first_set);
    try std.testing.expectEqual(exited_bitmap_summary.weight, bitmap_module.summary().weight);
    try std.testing.expectEqual(exited_kretprobe_snapshot.completed_instances, kretprobe_module.lifecycleSnapshot().completed_instances);
    try std.testing.expectEqual(exited_kretprobe_snapshot.last_retval, kretprobe_module.lifecycleSnapshot().last_retval);
}
