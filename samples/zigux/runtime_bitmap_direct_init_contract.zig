const std = @import("std");
const runtime_bitmap_sample = @import("runtime_bitmap_sample");

const ModuleStage = runtime_bitmap_sample.ModuleStage;
const RuntimeBitmapSample = runtime_bitmap_sample.RuntimeBitmapSample;
const RuntimeBitmapSummary = runtime_bitmap_sample.RuntimeBitmapSummary;

fn expectBitmapShapeStable(before: RuntimeBitmapSummary, after: RuntimeBitmapSummary) !void {
    try std.testing.expectEqual(before.first_set, after.first_set);
    try std.testing.expectEqual(before.first_zero, after.first_zero);
    try std.testing.expectEqual(before.weight, after.weight);
    try std.testing.expectEqual(before.nbits, after.nbits);
}

test "runtime bitmap sample normalizes unsorted duplicate direct init bits without inflating summaries" {
    var module = RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 70, 5, 0, 64, 70, 5 });

    const summary = module.summary();
    try std.testing.expectEqual(ModuleStage.initialized, module.stage());
    try std.testing.expectEqual(@as(u32, 0), summary.first_set);
    try std.testing.expectEqual(@as(u32, 1), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 4), summary.weight);
    try std.testing.expectEqual(RuntimeBitmapSample.bitmap_nbits, summary.nbits);
    try std.testing.expectEqual(@as(usize, 1), summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), summary.exit_runs);
    try std.testing.expect(module.isSet(0));
    try std.testing.expect(module.isSet(5));
    try std.testing.expect(module.isSet(64));
    try std.testing.expect(module.isSet(70));
    try std.testing.expectEqual(@as(?u32, 0), module.nthSetBit(0));
    try std.testing.expectEqual(@as(?u32, 5), module.nthSetBit(1));
    try std.testing.expectEqual(@as(?u32, 64), module.nthSetBit(2));
    try std.testing.expectEqual(@as(?u32, 70), module.nthSetBit(3));
    try std.testing.expectEqual(@as(?u32, null), module.nthSetBit(4));
    try std.testing.expectEqual(@as(u32, 2), try module.countSetBitsInRange(64, 7));

    const formatted = try module.formatSetBits(std.testing.allocator);
    defer std.testing.allocator.free(formatted);
    try std.testing.expectEqualStrings("0,5,64,70", formatted);
}

test "runtime bitmap sample keeps direct-init lifecycle summaries stable through selftest and exit" {
    var module = RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 70, 5, 0, 64, 70, 5 });

    const initialized = module.summary();
    try std.testing.expectEqual(ModuleStage.initialized, module.stage());
    try std.testing.expectEqual(@as(usize, 1), initialized.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized.exit_runs);
    try std.testing.expectEqual(@as(?u32, 70), module.nthSetBit(3));

    const selftest = try module.runSelftest();
    try std.testing.expectEqualStrings("lib/test_bitmap.c", selftest.anchor);
    try std.testing.expectEqual(@as(usize, 4), selftest.operation_families.len);
    try std.testing.expect(selftest.checked_range_mutations);
    try std.testing.expect(selftest.checked_iteration_paths);

    const after_selftest = module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, module.stage());
    try expectBitmapShapeStable(initialized, after_selftest);
    try std.testing.expectEqual(initialized.init_runs, after_selftest.init_runs);
    try std.testing.expectEqual(@as(usize, 1), after_selftest.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), after_selftest.exit_runs);
    try std.testing.expect(module.isSet(0));
    try std.testing.expect(module.isSet(5));
    try std.testing.expect(module.isSet(64));
    try std.testing.expect(module.isSet(70));
    try std.testing.expectEqual(@as(?u32, 70), module.nthSetBit(3));

    try module.exit();

    const after_exit = module.summary();
    try std.testing.expectEqual(ModuleStage.exited, module.stage());
    try expectBitmapShapeStable(initialized, after_exit);
    try std.testing.expectEqual(initialized.init_runs, after_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 1), after_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), after_exit.exit_runs);
    try std.testing.expect(module.isSet(0));
    try std.testing.expect(module.isSet(5));
    try std.testing.expect(module.isSet(64));
    try std.testing.expect(module.isSet(70));
    try std.testing.expectEqual(@as(?u32, 70), module.nthSetBit(3));
    try std.testing.expectEqual(@as(?u32, null), module.nthSetBit(4));
}
