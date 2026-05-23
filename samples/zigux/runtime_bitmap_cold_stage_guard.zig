const std = @import("std");
const runtime_bitmap_sample = @import("runtime_bitmap_sample");

const ModuleStage = runtime_bitmap_sample.ModuleStage;
const RuntimeBitmapSample = runtime_bitmap_sample.RuntimeBitmapSample;
const RuntimeBitmapSummary = runtime_bitmap_sample.RuntimeBitmapSummary;

fn expectSummaryStable(before: RuntimeBitmapSummary, after: RuntimeBitmapSummary) !void {
    try std.testing.expectEqual(before.first_set, after.first_set);
    try std.testing.expectEqual(before.first_zero, after.first_zero);
    try std.testing.expectEqual(before.weight, after.weight);
    try std.testing.expectEqual(before.nbits, after.nbits);
    try std.testing.expectEqual(before.init_runs, after.init_runs);
    try std.testing.expectEqual(before.selftest_runs, after.selftest_runs);
    try std.testing.expectEqual(before.exit_runs, after.exit_runs);
}

test "runtime bitmap sample keeps cold-stage selftest and exit guards explicit" {
    var module = RuntimeBitmapSample{};

    const before = module.summary();
    try std.testing.expectEqual(ModuleStage.cold, module.stage());
    try std.testing.expectEqual(RuntimeBitmapSample.bitmap_nbits, before.first_set);
    try std.testing.expectEqual(@as(u32, 0), before.first_zero);
    try std.testing.expectEqual(@as(u32, 0), before.weight);
    try std.testing.expectEqual(@as(usize, 0), before.init_runs);
    try std.testing.expectEqual(@as(usize, 0), before.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before.exit_runs);

    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());

    const after = module.summary();
    try std.testing.expectEqual(ModuleStage.cold, module.stage());
    try expectSummaryStable(before, after);
}

test "runtime bitmap sample keeps cold-stage mutation guards and source-lifecycle checks explicit" {
    var cold = RuntimeBitmapSample{};

    const before_cold = cold.summary();
    try std.testing.expectError(error.InvalidLifecycleTransition, cold.setRange(0, 1));
    try std.testing.expectError(error.InvalidLifecycleTransition, cold.clearRange(0, 1));
    try std.testing.expectError(error.InvalidLifecycleTransition, cold.copyFrom(&cold));
    const after_cold = cold.summary();
    try std.testing.expectEqual(ModuleStage.cold, cold.stage());
    try expectSummaryStable(before_cold, after_cold);

    var source = RuntimeBitmapSample{};
    var destination = RuntimeBitmapSample{};
    try destination.initWithSetBits(&.{ 1, 65 });

    const before_source = source.summary();
    const before_copy = destination.summary();
    try std.testing.expectEqual(ModuleStage.cold, source.stage());
    try std.testing.expect(destination.isSet(1));
    try std.testing.expect(destination.isSet(65));

    try std.testing.expectError(error.InvalidSourceLifecycle, destination.copyFrom(&source));

    const after_source = source.summary();
    const after_copy = destination.summary();
    try std.testing.expectEqual(ModuleStage.cold, source.stage());
    try expectSummaryStable(before_source, after_source);
    try std.testing.expect(!source.isSet(0));
    try std.testing.expectEqual(@as(?u32, null), source.nthSetBit(0));
    try std.testing.expectEqual(ModuleStage.initialized, destination.stage());
    try expectSummaryStable(before_copy, after_copy);
    try std.testing.expect(destination.isSet(1));
    try std.testing.expect(destination.isSet(65));
    try std.testing.expect(!destination.isSet(0));
    try std.testing.expectEqual(@as(?u32, 1), destination.nthSetBit(0));
    try std.testing.expectEqual(@as(?u32, 65), destination.nthSetBit(1));
    try std.testing.expectEqual(@as(?u32, null), destination.nthSetBit(2));
}

test "runtime bitmap sample keeps exited-stage mutation and second-exit guards explicit" {
    var initialized_module = RuntimeBitmapSample{};
    try initialized_module.initFromBitList("0, 63, 64, 127");
    try initialized_module.exit();

    const before_initialized_reexit = initialized_module.summary();
    try std.testing.expectEqual(ModuleStage.exited, initialized_module.stage());
    try std.testing.expectEqual(@as(u32, 0), before_initialized_reexit.first_set);
    try std.testing.expectEqual(@as(u32, 1), before_initialized_reexit.first_zero);
    try std.testing.expectEqual(@as(u32, 4), before_initialized_reexit.weight);
    try std.testing.expectEqual(RuntimeBitmapSample.bitmap_nbits, before_initialized_reexit.nbits);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_reexit.init_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_reexit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_reexit.exit_runs);
    try std.testing.expect(initialized_module.isSet(0));
    try std.testing.expect(initialized_module.isSet(63));
    try std.testing.expect(initialized_module.isSet(64));
    try std.testing.expect(initialized_module.isSet(127));
    try std.testing.expectEqual(@as(?u32, 127), initialized_module.nthSetBit(3));
    try std.testing.expectEqual(@as(u32, 4), try initialized_module.countSetBitsInRange(0, RuntimeBitmapSample.bitmap_nbits));

    try std.testing.expectError(error.InvalidLifecycleTransition, initialized_module.setRange(5, 1));
    try std.testing.expectError(error.InvalidLifecycleTransition, initialized_module.clearRange(63, 1));
    try std.testing.expectError(error.InvalidLifecycleTransition, initialized_module.exit());

    const after_initialized_reexit = initialized_module.summary();
    try std.testing.expectEqual(ModuleStage.exited, initialized_module.stage());
    try expectSummaryStable(before_initialized_reexit, after_initialized_reexit);
    try std.testing.expect(initialized_module.isSet(0));
    try std.testing.expect(initialized_module.isSet(63));
    try std.testing.expect(initialized_module.isSet(64));
    try std.testing.expect(initialized_module.isSet(127));
    try std.testing.expectEqual(@as(?u32, 127), initialized_module.nthSetBit(3));
    try std.testing.expectEqual(@as(u32, 4), try initialized_module.countSetBitsInRange(0, RuntimeBitmapSample.bitmap_nbits));

    var selftested_module = RuntimeBitmapSample{};
    try selftested_module.initFromBitList("0, 63, 64, 127");
    _ = try selftested_module.runSelftest();
    try selftested_module.exit();

    const before_selftested_reexit = selftested_module.summary();
    try std.testing.expectEqual(ModuleStage.exited, selftested_module.stage());
    try std.testing.expectEqual(@as(u32, 0), before_selftested_reexit.first_set);
    try std.testing.expectEqual(@as(u32, 1), before_selftested_reexit.first_zero);
    try std.testing.expectEqual(@as(u32, 4), before_selftested_reexit.weight);
    try std.testing.expectEqual(RuntimeBitmapSample.bitmap_nbits, before_selftested_reexit.nbits);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_reexit.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_reexit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_reexit.exit_runs);
    try std.testing.expect(selftested_module.isSet(0));
    try std.testing.expect(selftested_module.isSet(63));
    try std.testing.expect(selftested_module.isSet(64));
    try std.testing.expect(selftested_module.isSet(127));
    try std.testing.expectEqual(@as(?u32, 127), selftested_module.nthSetBit(3));
    try std.testing.expectEqual(@as(u32, 4), try selftested_module.countSetBitsInRange(0, RuntimeBitmapSample.bitmap_nbits));

    try std.testing.expectError(error.InvalidLifecycleTransition, selftested_module.setRange(5, 1));
    try std.testing.expectError(error.InvalidLifecycleTransition, selftested_module.clearRange(63, 1));
    try std.testing.expectError(error.InvalidLifecycleTransition, selftested_module.exit());

    const after_selftested_reexit = selftested_module.summary();
    try std.testing.expectEqual(ModuleStage.exited, selftested_module.stage());
    try expectSummaryStable(before_selftested_reexit, after_selftested_reexit);
    try std.testing.expect(selftested_module.isSet(0));
    try std.testing.expect(selftested_module.isSet(63));
    try std.testing.expect(selftested_module.isSet(64));
    try std.testing.expect(selftested_module.isSet(127));
    try std.testing.expectEqual(@as(?u32, 127), selftested_module.nthSetBit(3));
    try std.testing.expectEqual(@as(u32, 4), try selftested_module.countSetBitsInRange(0, RuntimeBitmapSample.bitmap_nbits));
}
