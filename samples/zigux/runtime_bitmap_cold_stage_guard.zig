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

    const before_copy = destination.summary();
    try std.testing.expect(destination.isSet(1));
    try std.testing.expect(destination.isSet(65));

    try std.testing.expectError(error.InvalidSourceLifecycle, destination.copyFrom(&source));

    const after_copy = destination.summary();
    try std.testing.expectEqual(ModuleStage.initialized, destination.stage());
    try expectSummaryStable(before_copy, after_copy);
    try std.testing.expect(destination.isSet(1));
    try std.testing.expect(destination.isSet(65));
    try std.testing.expect(!destination.isSet(0));
    try std.testing.expectEqual(@as(?u32, 1), destination.nthSetBit(0));
    try std.testing.expectEqual(@as(?u32, 65), destination.nthSetBit(1));
    try std.testing.expectEqual(@as(?u32, null), destination.nthSetBit(2));
}
