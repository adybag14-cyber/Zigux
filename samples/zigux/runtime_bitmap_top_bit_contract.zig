const std = @import("std");
const runtime_bitmap_sample = @import("runtime_bitmap_sample");

test "runtime bitmap top-bit contract keeps the highest valid bit explicit" {
    var module = runtime_bitmap_sample.RuntimeBitmapSample{};
    const top_bit = runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits - 1;

    try module.initWithSetBits(&.{top_bit});

    const summary = module.summary();
    try std.testing.expect(module.isSet(top_bit));
    try std.testing.expect(!module.isSet(top_bit - 1));
    try std.testing.expectEqual(top_bit, summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 1), summary.weight);
    try std.testing.expectEqual(runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits, summary.nbits);
}

test "runtime bitmap top-bit contract keeps boundary mutation and bounds checks reviewable" {
    var module = runtime_bitmap_sample.RuntimeBitmapSample{};
    const top_bit = runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits - 1;

    try module.initWithSetBits(&.{});
    try module.setRange(top_bit, 1);
    try std.testing.expect(module.isSet(top_bit));

    try module.clearRange(top_bit, 1);
    try std.testing.expect(!module.isSet(top_bit));
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.initialized, module.stage());

    try std.testing.expectError(error.BitRangeOutOfBounds, module.setRange(top_bit + 1, 1));
    try std.testing.expectError(error.BitRangeOutOfBounds, module.clearRange(top_bit + 1, 1));
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.initialized, module.stage());
}

test "runtime bitmap top-bit contract keeps selftest and exit summaries stable" {
    var module = runtime_bitmap_sample.RuntimeBitmapSample{};
    const top_bit = runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits - 1;

    try module.initWithSetBits(&.{top_bit});
    const before_selftest = module.summary();

    const selftest = try module.runSelftest();
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqual(@as(usize, 4), selftest.operation_families.len);
    try std.testing.expectEqual(runtime_bitmap_sample.OperationFamily.clear_set, selftest.operation_families[0]);
    try std.testing.expectEqual(runtime_bitmap_sample.OperationFamily.copy, selftest.operation_families[1]);
    try std.testing.expectEqual(runtime_bitmap_sample.OperationFamily.summary, selftest.operation_families[2]);
    try std.testing.expectEqual(runtime_bitmap_sample.OperationFamily.lifecycle, selftest.operation_families[3]);
    try std.testing.expect(selftest.checked_range_mutations);
    try std.testing.expect(selftest.checked_lifecycle_paths);

    const after_selftest = module.summary();
    try std.testing.expect(module.isSet(top_bit));
    try std.testing.expectEqual(before_selftest.first_set, after_selftest.first_set);
    try std.testing.expectEqual(before_selftest.first_zero, after_selftest.first_zero);
    try std.testing.expectEqual(before_selftest.weight, after_selftest.weight);
    try std.testing.expectEqual(before_selftest.nbits, after_selftest.nbits);

    try module.exit();
    const after_exit = module.summary();
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.exited, module.stage());
    try std.testing.expect(module.isSet(top_bit));
    try std.testing.expectEqual(before_selftest.first_set, after_exit.first_set);
    try std.testing.expectEqual(before_selftest.first_zero, after_exit.first_zero);
    try std.testing.expectEqual(before_selftest.weight, after_exit.weight);
    try std.testing.expectEqual(before_selftest.nbits, after_exit.nbits);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.setRange(top_bit, 1));
}
