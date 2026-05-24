const std = @import("std");
const runtime_atomic64_sample = @import("runtime_atomic64_sample");
const runtime_bitmap_sample = @import("runtime_bitmap_sample");

const RuntimeAtomic64Sample = runtime_atomic64_sample.RuntimeAtomic64Sample;
const RuntimeBitmapSample = runtime_bitmap_sample.RuntimeBitmapSample;

fn expectLifecycleCounts(
    atomic_module: *const RuntimeAtomic64Sample,
    bitmap_module: *const RuntimeBitmapSample,
    expected_stage: runtime_atomic64_sample.ModuleStage,
    expected_init_runs: usize,
    expected_selftest_runs: usize,
    expected_exit_runs: usize,
) !void {
    const atomic_snapshot = atomic_module.lifecycleSnapshot();
    const atomic_summary = atomic_module.summary();
    const bitmap_summary = bitmap_module.summary();
    const expected_stage_tag = @intFromEnum(expected_stage);

    try std.testing.expectEqual(expected_stage, atomic_snapshot.stage);
    try std.testing.expectEqual(expected_stage_tag, @intFromEnum(bitmap_module.stage()));

    try std.testing.expectEqual(expected_init_runs, atomic_snapshot.init_runs);
    try std.testing.expectEqual(expected_init_runs, atomic_summary.init_runs);
    try std.testing.expectEqual(expected_init_runs, bitmap_summary.init_runs);

    try std.testing.expectEqual(expected_selftest_runs, atomic_snapshot.selftest_runs);
    try std.testing.expectEqual(expected_selftest_runs, atomic_summary.selftest_runs);
    try std.testing.expectEqual(expected_selftest_runs, bitmap_summary.selftest_runs);

    try std.testing.expectEqual(expected_exit_runs, atomic_snapshot.exit_runs);
    try std.testing.expectEqual(expected_exit_runs, atomic_summary.exit_runs);
    try std.testing.expectEqual(expected_exit_runs, bitmap_summary.exit_runs);
}

test "first-loadable runtime pilot families keep descriptor parity explicit" {
    const atomic_descriptor = RuntimeAtomic64Sample.descriptor();
    const bitmap_descriptor = RuntimeBitmapSample.descriptor();

    try std.testing.expectEqualStrings("runtime_atomic64", atomic_descriptor.name);
    try std.testing.expectEqualStrings("runtime_bitmap", bitmap_descriptor.name);
    try std.testing.expectEqualStrings("lib/atomic64_test.c", atomic_descriptor.anchor);
    try std.testing.expectEqualStrings("lib/test_bitmap.c", bitmap_descriptor.anchor);
    try std.testing.expect(atomic_descriptor.requires_runtime_substrate);
    try std.testing.expect(bitmap_descriptor.requires_runtime_substrate);
    try std.testing.expect(atomic_descriptor.provides_selftest_hook);
    try std.testing.expect(bitmap_descriptor.provides_selftest_hook);
}

test "first-loadable runtime pilot families keep init selftest and exit counts aligned" {
    var atomic_module = RuntimeAtomic64Sample{};
    var bitmap_module = RuntimeBitmapSample{};

    try expectLifecycleCounts(&atomic_module, &bitmap_module, .cold, 0, 0, 0);

    try atomic_module.init(11);
    try bitmap_module.initWithSetBits(&.{ 0, 63, 64, 127 });
    try expectLifecycleCounts(&atomic_module, &bitmap_module, .initialized, 1, 0, 0);

    _ = try atomic_module.runSelftest();
    _ = try bitmap_module.runSelftest();
    try expectLifecycleCounts(&atomic_module, &bitmap_module, .selftest_complete, 1, 1, 0);

    try atomic_module.exit();
    try bitmap_module.exit();
    try expectLifecycleCounts(&atomic_module, &bitmap_module, .exited, 1, 1, 1);
}

test "first-loadable runtime pilot families keep direct exit parity explicit before selftest" {
    var atomic_module = RuntimeAtomic64Sample{};
    var bitmap_module = RuntimeBitmapSample{};

    try atomic_module.init(-9);
    try bitmap_module.initFromBitList("0, 5, 64, 70");
    try expectLifecycleCounts(&atomic_module, &bitmap_module, .initialized, 1, 0, 0);

    try atomic_module.exit();
    try bitmap_module.exit();
    try expectLifecycleCounts(&atomic_module, &bitmap_module, .exited, 1, 0, 1);
}

test "first-loadable runtime pilot families keep rejected repeat selftest and exit stable" {
    var atomic_module = RuntimeAtomic64Sample{};
    var bitmap_module = RuntimeBitmapSample{};

    try atomic_module.init(23);
    try bitmap_module.initWithSetBits(&.{ 1, 64, 65, 90 });
    _ = try atomic_module.runSelftest();
    _ = try bitmap_module.runSelftest();
    try expectLifecycleCounts(&atomic_module, &bitmap_module, .selftest_complete, 1, 1, 0);

    try std.testing.expectError(error.InvalidLifecycleTransition, atomic_module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, bitmap_module.runSelftest());
    try expectLifecycleCounts(&atomic_module, &bitmap_module, .selftest_complete, 1, 1, 0);

    try atomic_module.exit();
    try bitmap_module.exit();
    try expectLifecycleCounts(&atomic_module, &bitmap_module, .exited, 1, 1, 1);

    try std.testing.expectError(error.InvalidLifecycleTransition, atomic_module.exit());
    try std.testing.expectError(error.InvalidLifecycleTransition, bitmap_module.exit());
    try expectLifecycleCounts(&atomic_module, &bitmap_module, .exited, 1, 1, 1);
}
