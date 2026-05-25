const std = @import("std");
const runtime_bitmap_sample = @import("runtime_bitmap_sample");

test "runtime bitmap sample keeps the highest valid bit explicit in the direct sample leg" {
    const top_bit = runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits - 1;

    var direct = runtime_bitmap_sample.RuntimeBitmapSample{};
    try direct.initWithSetBits(&.{top_bit});

    const direct_summary = direct.summary();
    try std.testing.expectEqual(top_bit, direct_summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), direct_summary.first_zero);
    try std.testing.expectEqual(@as(u32, 1), direct_summary.weight);
    try std.testing.expectEqual(runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits, direct_summary.nbits);
    try std.testing.expectEqual(@as(usize, 1), direct_summary.init_runs);
    try std.testing.expect(direct.isSet(top_bit));
    try std.testing.expect(!direct.isSet(top_bit - 1));
    try std.testing.expectEqual(@as(?u32, top_bit), direct.nthSetBit(0));
    try std.testing.expectEqual(@as(?u32, null), direct.nthSetBit(1));
    try std.testing.expectEqual(@as(u32, 1), try direct.countSetBitsInRange(top_bit, 1));

    const direct_formatted = try direct.formatSetBits(std.testing.allocator);
    defer std.testing.allocator.free(direct_formatted);
    try std.testing.expectEqualStrings("127", direct_formatted);
}

test "runtime bitmap sample keeps duplicate boundary init arrays normalized in the top-bit direct sample leg" {
    const top_bit = runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits - 1;

    var direct = runtime_bitmap_sample.RuntimeBitmapSample{};
    try direct.initWithSetBits(&.{ top_bit, 0, top_bit, 0 });

    const direct_summary = direct.summary();
    try std.testing.expectEqual(@as(u32, 0), direct_summary.first_set);
    try std.testing.expectEqual(@as(u32, 1), direct_summary.first_zero);
    try std.testing.expectEqual(@as(u32, 2), direct_summary.weight);
    try std.testing.expectEqual(runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits, direct_summary.nbits);
    try std.testing.expectEqual(@as(usize, 1), direct_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), direct_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), direct_summary.exit_runs);
    try std.testing.expect(direct.isSet(0));
    try std.testing.expect(direct.isSet(top_bit));
    try std.testing.expect(!direct.isSet(1));
    try std.testing.expect(!direct.isSet(top_bit - 1));
    try std.testing.expectEqual(@as(?u32, 0), direct.nthSetBit(0));
    try std.testing.expectEqual(@as(?u32, top_bit), direct.nthSetBit(1));
    try std.testing.expectEqual(@as(?u32, null), direct.nthSetBit(2));
    try std.testing.expectEqual(@as(u32, 1), try direct.countSetBitsInRange(0, 1));
    try std.testing.expectEqual(@as(u32, 1), try direct.countSetBitsInRange(top_bit, 1));

    const direct_formatted = try direct.formatSetBits(std.testing.allocator);
    defer std.testing.allocator.free(direct_formatted);
    try std.testing.expectEqualStrings("0,127", direct_formatted);
}

test "runtime bitmap sample keeps top-bit lifecycle mutation explicit in the direct sample leg" {
    const top_bit = runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits - 1;

    var module = runtime_bitmap_sample.RuntimeBitmapSample{};
    try module.initWithSetBits(&.{top_bit});
    _ = try module.runSelftest();

    try module.clearRange(top_bit, 1);

    const cleared_summary = module.summary();
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqual(runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits, cleared_summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), cleared_summary.first_zero);
    try std.testing.expectEqual(@as(u32, 0), cleared_summary.weight);
    try std.testing.expectEqual(runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits, cleared_summary.nbits);
    try std.testing.expectEqual(@as(usize, 1), cleared_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), cleared_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), cleared_summary.exit_runs);
    try std.testing.expect(!module.isSet(top_bit));
    try std.testing.expectEqual(@as(?u32, null), module.nthSetBit(0));
    try std.testing.expectEqual(@as(u32, 0), try module.countSetBitsInRange(top_bit, 1));

    try module.setRange(top_bit, 1);

    const restored_summary = module.summary();
    try std.testing.expectEqual(@as(u32, top_bit), restored_summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), restored_summary.first_zero);
    try std.testing.expectEqual(@as(u32, 1), restored_summary.weight);
    try std.testing.expectEqual(runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits, restored_summary.nbits);
    try std.testing.expectEqual(@as(usize, 1), restored_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), restored_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), restored_summary.exit_runs);
    try std.testing.expect(module.isSet(top_bit));
    try std.testing.expect(!module.isSet(top_bit - 1));
    try std.testing.expectEqual(@as(?u32, top_bit), module.nthSetBit(0));
    try std.testing.expectEqual(@as(?u32, null), module.nthSetBit(1));
    try std.testing.expectEqual(@as(u32, 1), try module.countSetBitsInRange(top_bit, 1));

    try module.exit();

    const exited_summary = module.summary();
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.exited, module.stage());
    try std.testing.expectEqual(restored_summary.first_set, exited_summary.first_set);
    try std.testing.expectEqual(restored_summary.first_zero, exited_summary.first_zero);
    try std.testing.expectEqual(restored_summary.weight, exited_summary.weight);
    try std.testing.expectEqual(restored_summary.nbits, exited_summary.nbits);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);
    try std.testing.expect(module.isSet(top_bit));
    try std.testing.expect(!module.isSet(top_bit - 1));
    try std.testing.expectEqual(@as(u32, 1), try module.countSetBitsInRange(top_bit, 1));
}

test "runtime bitmap sample rejects exited top-bit source copies without disturbing the target sample leg" {
    const top_bit = runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits - 1;

    var exited_source = runtime_bitmap_sample.RuntimeBitmapSample{};
    try exited_source.initWithSetBits(&.{top_bit});
    try exited_source.exit();

    const exited_source_summary = exited_source.summary();
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.exited, exited_source.stage());
    try std.testing.expectEqual(@as(u32, top_bit), exited_source_summary.first_set);
    try std.testing.expectEqual(@as(u32, 1), exited_source_summary.weight);

    var target = runtime_bitmap_sample.RuntimeBitmapSample{};
    try target.initWithSetBits(&.{0});

    const target_before = target.summary();
    try std.testing.expectEqual(@as(u32, 0), target_before.first_set);
    try std.testing.expectEqual(@as(u32, 1), target_before.weight);

    try std.testing.expectError(error.InvalidSourceLifecycle, target.copyFrom(&exited_source));

    const target_after = target.summary();
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.initialized, target.stage());
    try std.testing.expectEqual(target_before.first_set, target_after.first_set);
    try std.testing.expectEqual(target_before.first_zero, target_after.first_zero);
    try std.testing.expectEqual(target_before.weight, target_after.weight);
    try std.testing.expectEqual(target_before.nbits, target_after.nbits);
    try std.testing.expectEqual(target_before.init_runs, target_after.init_runs);
    try std.testing.expectEqual(target_before.selftest_runs, target_after.selftest_runs);
    try std.testing.expectEqual(target_before.exit_runs, target_after.exit_runs);
    try std.testing.expect(target.isSet(0));
    try std.testing.expect(!target.isSet(top_bit));
    try std.testing.expectEqual(@as(?u32, 0), target.nthSetBit(0));
    try std.testing.expectEqual(@as(?u32, null), target.nthSetBit(1));
    try std.testing.expectEqual(@as(u32, 1), try target.countSetBitsInRange(0, 1));
}

test "runtime bitmap sample rejects cold top-bit source copies without disturbing the target sample leg" {
    const top_bit = runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits - 1;

    var cold_source = runtime_bitmap_sample.RuntimeBitmapSample{};
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.cold, cold_source.stage());

    var target = runtime_bitmap_sample.RuntimeBitmapSample{};
    try target.initWithSetBits(&.{0});

    const target_before = target.summary();
    try std.testing.expectEqual(@as(u32, 0), target_before.first_set);
    try std.testing.expectEqual(@as(u32, 1), target_before.weight);

    try std.testing.expectError(error.InvalidSourceLifecycle, target.copyFrom(&cold_source));

    const target_after = target.summary();
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.initialized, target.stage());
    try std.testing.expectEqual(target_before.first_set, target_after.first_set);
    try std.testing.expectEqual(target_before.first_zero, target_after.first_zero);
    try std.testing.expectEqual(target_before.weight, target_after.weight);
    try std.testing.expectEqual(target_before.nbits, target_after.nbits);
    try std.testing.expectEqual(target_before.init_runs, target_after.init_runs);
    try std.testing.expectEqual(target_before.selftest_runs, target_after.selftest_runs);
    try std.testing.expectEqual(target_before.exit_runs, target_after.exit_runs);
    try std.testing.expect(target.isSet(0));
    try std.testing.expect(!target.isSet(top_bit));
    try std.testing.expectEqual(@as(?u32, 0), target.nthSetBit(0));
    try std.testing.expectEqual(@as(?u32, null), target.nthSetBit(1));
    try std.testing.expectEqual(@as(u32, 1), try target.countSetBitsInRange(0, 1));
}

test "runtime bitmap sample rejects copy reentry after target exit without disturbing either sample leg" {
    const top_bit = runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits - 1;

    var source = runtime_bitmap_sample.RuntimeBitmapSample{};
    try source.initWithSetBits(&.{top_bit});
    const source_before = source.summary();
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.initialized, source.stage());
    try std.testing.expectEqual(@as(u32, top_bit), source_before.first_set);
    try std.testing.expectEqual(@as(u32, 1), source_before.weight);

    var target = runtime_bitmap_sample.RuntimeBitmapSample{};
    try target.initWithSetBits(&.{0});
    try target.exit();

    const target_before = target.summary();
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.exited, target.stage());
    try std.testing.expectEqual(@as(u32, 0), target_before.first_set);
    try std.testing.expectEqual(@as(u32, 1), target_before.weight);
    try std.testing.expectEqual(@as(usize, 1), target_before.exit_runs);

    try std.testing.expectError(error.InvalidLifecycleTransition, target.copyFrom(&source));

    const source_after = source.summary();
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.initialized, source.stage());
    try std.testing.expectEqual(source_before.first_set, source_after.first_set);
    try std.testing.expectEqual(source_before.first_zero, source_after.first_zero);
    try std.testing.expectEqual(source_before.weight, source_after.weight);
    try std.testing.expectEqual(source_before.nbits, source_after.nbits);
    try std.testing.expectEqual(source_before.init_runs, source_after.init_runs);
    try std.testing.expectEqual(source_before.selftest_runs, source_after.selftest_runs);
    try std.testing.expectEqual(source_before.exit_runs, source_after.exit_runs);
    try std.testing.expect(!source.isSet(0));
    try std.testing.expect(source.isSet(top_bit));
    try std.testing.expectEqual(@as(?u32, top_bit), source.nthSetBit(0));
    try std.testing.expectEqual(@as(?u32, null), source.nthSetBit(1));

    const target_after = target.summary();
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.exited, target.stage());
    try std.testing.expectEqual(target_before.first_set, target_after.first_set);
    try std.testing.expectEqual(target_before.first_zero, target_after.first_zero);
    try std.testing.expectEqual(target_before.weight, target_after.weight);
    try std.testing.expectEqual(target_before.nbits, target_after.nbits);
    try std.testing.expectEqual(target_before.init_runs, target_after.init_runs);
    try std.testing.expectEqual(target_before.selftest_runs, target_after.selftest_runs);
    try std.testing.expectEqual(target_before.exit_runs, target_after.exit_runs);
    try std.testing.expect(target.isSet(0));
    try std.testing.expect(!target.isSet(top_bit));
    try std.testing.expectEqual(@as(?u32, 0), target.nthSetBit(0));
    try std.testing.expectEqual(@as(?u32, null), target.nthSetBit(1));
    try std.testing.expectEqual(@as(u32, 1), try target.countSetBitsInRange(0, 1));
}

test "runtime bitmap sample copies selftest-complete top-bit state into an initialized target without disturbing the source sample leg" {
    const top_bit = runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits - 1;

    var source = runtime_bitmap_sample.RuntimeBitmapSample{};
    try source.initWithSetBits(&.{top_bit});
    _ = try source.runSelftest();

    const source_before = source.summary();
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.selftest_complete, source.stage());
    try std.testing.expectEqual(@as(u32, top_bit), source_before.first_set);
    try std.testing.expectEqual(@as(u32, 1), source_before.weight);
    try std.testing.expectEqual(@as(usize, 1), source_before.init_runs);
    try std.testing.expectEqual(@as(usize, 1), source_before.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), source_before.exit_runs);

    var target = runtime_bitmap_sample.RuntimeBitmapSample{};
    try target.initWithSetBits(&.{0});

    const target_before = target.summary();
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.initialized, target.stage());
    try std.testing.expectEqual(@as(u32, 0), target_before.first_set);
    try std.testing.expectEqual(@as(u32, 1), target_before.weight);
    try std.testing.expectEqual(@as(usize, 1), target_before.init_runs);
    try std.testing.expectEqual(@as(usize, 0), target_before.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), target_before.exit_runs);

    try target.copyFrom(&source);

    const source_after = source.summary();
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.selftest_complete, source.stage());
    try std.testing.expectEqual(source_before.first_set, source_after.first_set);
    try std.testing.expectEqual(source_before.first_zero, source_after.first_zero);
    try std.testing.expectEqual(source_before.weight, source_after.weight);
    try std.testing.expectEqual(source_before.nbits, source_after.nbits);
    try std.testing.expectEqual(source_before.init_runs, source_after.init_runs);
    try std.testing.expectEqual(source_before.selftest_runs, source_after.selftest_runs);
    try std.testing.expectEqual(source_before.exit_runs, source_after.exit_runs);
    try std.testing.expect(!source.isSet(0));
    try std.testing.expect(source.isSet(top_bit));

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
    try std.testing.expect(target.isSet(top_bit));
    try std.testing.expectEqual(@as(?u32, top_bit), target.nthSetBit(0));
    try std.testing.expectEqual(@as(?u32, null), target.nthSetBit(1));
    try std.testing.expectEqual(@as(u32, 1), try target.countSetBitsInRange(top_bit, 1));
}

test "runtime bitmap sample copies initialized top-bit state into a selftest-complete target without disturbing either sample leg" {
    const top_bit = runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits - 1;

    var source = runtime_bitmap_sample.RuntimeBitmapSample{};
    try source.initWithSetBits(&.{top_bit});

    const source_before = source.summary();
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.initialized, source.stage());
    try std.testing.expectEqual(@as(u32, top_bit), source_before.first_set);
    try std.testing.expectEqual(@as(u32, 1), source_before.weight);
    try std.testing.expectEqual(@as(usize, 1), source_before.init_runs);
    try std.testing.expectEqual(@as(usize, 0), source_before.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), source_before.exit_runs);

    var target = runtime_bitmap_sample.RuntimeBitmapSample{};
    try target.initWithSetBits(&.{0});
    _ = try target.runSelftest();

    const target_before = target.summary();
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.selftest_complete, target.stage());
    try std.testing.expectEqual(@as(u32, 0), target_before.first_set);
    try std.testing.expectEqual(@as(u32, 1), target_before.weight);
    try std.testing.expectEqual(@as(usize, 1), target_before.init_runs);
    try std.testing.expectEqual(@as(usize, 1), target_before.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), target_before.exit_runs);

    try target.copyFrom(&source);

    const source_after = source.summary();
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.initialized, source.stage());
    try std.testing.expectEqual(source_before.first_set, source_after.first_set);
    try std.testing.expectEqual(source_before.first_zero, source_after.first_zero);
    try std.testing.expectEqual(source_before.weight, source_after.weight);
    try std.testing.expectEqual(source_before.nbits, source_after.nbits);
    try std.testing.expectEqual(source_before.init_runs, source_after.init_runs);
    try std.testing.expectEqual(source_before.selftest_runs, source_after.selftest_runs);
    try std.testing.expectEqual(source_before.exit_runs, source_after.exit_runs);
    try std.testing.expect(!source.isSet(0));
    try std.testing.expect(source.isSet(top_bit));
    try std.testing.expectEqual(@as(?u32, top_bit), source.nthSetBit(0));
    try std.testing.expectEqual(@as(?u32, null), source.nthSetBit(1));

    const target_after = target.summary();
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.selftest_complete, target.stage());
    try std.testing.expectEqual(source_before.first_set, target_after.first_set);
    try std.testing.expectEqual(source_before.first_zero, target_after.first_zero);
    try std.testing.expectEqual(source_before.weight, target_after.weight);
    try std.testing.expectEqual(source_before.nbits, target_after.nbits);
    try std.testing.expectEqual(target_before.init_runs, target_after.init_runs);
    try std.testing.expectEqual(target_before.selftest_runs, target_after.selftest_runs);
    try std.testing.expectEqual(target_before.exit_runs, target_after.exit_runs);
    try std.testing.expect(!target.isSet(0));
    try std.testing.expect(target.isSet(top_bit));
    try std.testing.expectEqual(@as(?u32, top_bit), target.nthSetBit(0));
    try std.testing.expectEqual(@as(?u32, null), target.nthSetBit(1));
    try std.testing.expectEqual(@as(u32, 1), try target.countSetBitsInRange(top_bit, 1));
}
