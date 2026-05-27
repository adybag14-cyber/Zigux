const std = @import("std");
const runtime_bitmap_sample = @import("runtime_bitmap_sample");

fn expectSummaryStable(
    before: runtime_bitmap_sample.RuntimeBitmapSummary,
    after: runtime_bitmap_sample.RuntimeBitmapSummary,
) !void {
    try std.testing.expectEqual(before.first_set, after.first_set);
    try std.testing.expectEqual(before.first_zero, after.first_zero);
    try std.testing.expectEqual(before.weight, after.weight);
    try std.testing.expectEqual(before.nbits, after.nbits);
    try std.testing.expectEqual(before.init_runs, after.init_runs);
    try std.testing.expectEqual(before.selftest_runs, after.selftest_runs);
    try std.testing.expectEqual(before.exit_runs, after.exit_runs);
}

test "runtime bitmap sample keeps parsed range mutation and formatting replay explicit in the direct sample leg" {
    var module = runtime_bitmap_sample.RuntimeBitmapSample{};
    try module.initFromBitList("0, 5, 64, 70");

    try module.setRange(9, 4);
    try module.clearRange(64, 1);

    const summary = module.summary();
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.initialized, module.stage());
    try std.testing.expectEqual(@as(u32, 0), summary.first_set);
    try std.testing.expectEqual(@as(u32, 1), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 7), summary.weight);
    try std.testing.expectEqual(runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits, summary.nbits);
    try std.testing.expectEqual(@as(usize, 1), summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), summary.exit_runs);
    try std.testing.expect(module.isSet(0));
    try std.testing.expect(module.isSet(5));
    try std.testing.expect(module.isSet(9));
    try std.testing.expect(module.isSet(10));
    try std.testing.expect(module.isSet(11));
    try std.testing.expect(module.isSet(12));
    try std.testing.expect(module.isSet(70));
    try std.testing.expect(!module.isSet(64));
    try std.testing.expectEqual(@as(?u32, 70), module.nthSetBit(6));
    try std.testing.expectEqual(@as(?u32, null), module.nthSetBit(7));
    try std.testing.expectEqual(@as(u32, 4), try module.countSetBitsInRange(9, 4));
    try std.testing.expectEqual(@as(u32, 1), try module.countSetBitsInRange(64, 7));

    const formatted = try module.formatSetBits(std.testing.allocator);
    defer std.testing.allocator.free(formatted);
    try std.testing.expectEqualStrings("0,5,9,10,11,12,70", formatted);
}

test "runtime bitmap sample copies parsed selftested state into an initialized target without disturbing source replay" {
    var source = runtime_bitmap_sample.RuntimeBitmapSample{};
    try source.initFromBitList("1, 64, 65, 90");
    _ = try source.runSelftest();
    try source.clearRange(64, 1);
    try source.setRange(70, 2);

    const source_before = source.summary();
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.selftest_complete, source.stage());
    try std.testing.expectEqual(@as(u32, 1), source_before.first_set);
    try std.testing.expectEqual(@as(u32, 0), source_before.first_zero);
    try std.testing.expectEqual(@as(u32, 5), source_before.weight);
    try std.testing.expectEqual(@as(usize, 1), source_before.init_runs);
    try std.testing.expectEqual(@as(usize, 1), source_before.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), source_before.exit_runs);

    var target = runtime_bitmap_sample.RuntimeBitmapSample{};
    try target.initWithSetBits(&.{ 0, 5, 64, 127 });

    const target_before = target.summary();
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.initialized, target.stage());
    try std.testing.expectEqual(@as(u32, 0), target_before.first_set);
    try std.testing.expectEqual(@as(u32, 4), target_before.weight);
    try std.testing.expectEqual(@as(usize, 1), target_before.init_runs);
    try std.testing.expectEqual(@as(usize, 0), target_before.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), target_before.exit_runs);

    try target.copyFrom(&source);

    const source_after = source.summary();
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.selftest_complete, source.stage());
    try expectSummaryStable(source_before, source_after);
    try std.testing.expect(!source.isSet(0));
    try std.testing.expect(source.isSet(1));
    try std.testing.expect(!source.isSet(64));
    try std.testing.expect(source.isSet(65));
    try std.testing.expect(source.isSet(70));
    try std.testing.expect(source.isSet(71));
    try std.testing.expect(source.isSet(90));
    try std.testing.expectEqual(@as(?u32, 1), source.nthSetBit(0));
    try std.testing.expectEqual(@as(?u32, 90), source.nthSetBit(4));
    try std.testing.expectEqual(@as(?u32, null), source.nthSetBit(5));

    const target_after = target.summary();
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.initialized, target.stage());
    try std.testing.expectEqual(source_before.first_set, target_after.first_set);
    try std.testing.expectEqual(source_before.first_zero, target_after.first_zero);
    try std.testing.expectEqual(source_before.weight, target_after.weight);
    try std.testing.expectEqual(source_before.nbits, target_after.nbits);
    try std.testing.expectEqual(target_before.init_runs, target_after.init_runs);
    try std.testing.expectEqual(target_before.selftest_runs, target_after.selftest_runs);
    try std.testing.expectEqual(target_before.exit_runs, target_after.exit_runs);
    try std.testing.expect(!target.isSet(0));
    try std.testing.expect(target.isSet(1));
    try std.testing.expect(!target.isSet(64));
    try std.testing.expect(target.isSet(65));
    try std.testing.expect(target.isSet(70));
    try std.testing.expect(target.isSet(71));
    try std.testing.expect(target.isSet(90));
    try std.testing.expectEqual(@as(?u32, 1), target.nthSetBit(0));
    try std.testing.expectEqual(@as(?u32, 90), target.nthSetBit(4));
    try std.testing.expectEqual(@as(?u32, null), target.nthSetBit(5));

    const formatted = try target.formatSetBits(std.testing.allocator);
    defer std.testing.allocator.free(formatted);
    try std.testing.expectEqualStrings("1,65,70,71,90", formatted);
}

test "runtime bitmap sample copies parsed initialized state into a selftested target without disturbing target lifecycle replay" {
    var source = runtime_bitmap_sample.RuntimeBitmapSample{};
    try source.initFromBitList("9, 10, 11, 12, 70");

    const source_before = source.summary();
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.initialized, source.stage());
    try std.testing.expectEqual(@as(u32, 9), source_before.first_set);
    try std.testing.expectEqual(@as(u32, 0), source_before.first_zero);
    try std.testing.expectEqual(@as(u32, 5), source_before.weight);
    try std.testing.expectEqual(@as(usize, 1), source_before.init_runs);
    try std.testing.expectEqual(@as(usize, 0), source_before.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), source_before.exit_runs);

    var target = runtime_bitmap_sample.RuntimeBitmapSample{};
    try target.initFromBitList("0, 5, 64, 127");
    _ = try target.runSelftest();

    const target_before = target.summary();
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.selftest_complete, target.stage());
    try std.testing.expectEqual(@as(u32, 0), target_before.first_set);
    try std.testing.expectEqual(@as(u32, 4), target_before.weight);
    try std.testing.expectEqual(@as(usize, 1), target_before.init_runs);
    try std.testing.expectEqual(@as(usize, 1), target_before.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), target_before.exit_runs);

    try target.copyFrom(&source);

    const source_after = source.summary();
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.initialized, source.stage());
    try expectSummaryStable(source_before, source_after);

    const target_after = target.summary();
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.selftest_complete, target.stage());
    try std.testing.expectEqual(source_before.first_set, target_after.first_set);
    try std.testing.expectEqual(source_before.first_zero, target_after.first_zero);
    try std.testing.expectEqual(source_before.weight, target_after.weight);
    try std.testing.expectEqual(source_before.nbits, target_after.nbits);
    try std.testing.expectEqual(target_before.init_runs, target_after.init_runs);
    try std.testing.expectEqual(target_before.selftest_runs, target_after.selftest_runs);
    try std.testing.expectEqual(target_before.exit_runs, target_after.exit_runs);
    try std.testing.expect(target.isSet(9));
    try std.testing.expect(target.isSet(10));
    try std.testing.expect(target.isSet(11));
    try std.testing.expect(target.isSet(12));
    try std.testing.expect(target.isSet(70));
    try std.testing.expect(!target.isSet(0));
    try std.testing.expectEqual(@as(?u32, 9), target.nthSetBit(0));
    try std.testing.expectEqual(@as(?u32, 70), target.nthSetBit(4));
    try std.testing.expectEqual(@as(?u32, null), target.nthSetBit(5));

    const formatted = try target.formatSetBits(std.testing.allocator);
    defer std.testing.allocator.free(formatted);
    try std.testing.expectEqualStrings("9,10,11,12,70", formatted);
}
