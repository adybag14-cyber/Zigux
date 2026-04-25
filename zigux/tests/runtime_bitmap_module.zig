const std = @import("std");
const sample = @import("runtime_bitmap_sample");

test "runtime bitmap sample advertises the bounded pilot-module contract" {
    const descriptor = sample.RuntimeBitmapSample.descriptor();

    try std.testing.expectEqualStrings("runtime_bitmap", descriptor.name);
    try std.testing.expectEqualStrings("lib/test_bitmap.c", descriptor.anchor);
    try std.testing.expect(descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selftest_hook);
}

test "runtime bitmap sample enforces lifecycle transitions and bitmap mutations" {
    var module = sample.RuntimeBitmapSample{};
    const second_word_base = sample.RuntimeBitmapSample.bitmap_nbits / 2;

    try std.testing.expectEqual(sample.ModuleStage.cold, module.stage());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());

    try module.initWithSetBits(&.{ 0, 5, second_word_base, second_word_base + 6 });
    try std.testing.expectEqual(sample.ModuleStage.initialized, module.stage());
    try std.testing.expectEqual(@as(usize, 1), module.init_runs);

    var summary = module.summary();
    try std.testing.expectEqual(@as(u32, 0), summary.first_set);
    try std.testing.expectEqual(@as(u32, 1), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 4), summary.weight);
    try std.testing.expect(module.isSet(second_word_base));
    try std.testing.expect(!module.isSet(1));

    try module.clearRange(second_word_base, 2);
    try std.testing.expect(!module.isSet(second_word_base));
    try std.testing.expect(module.isSet(second_word_base + 6));

    try module.setRange(9, 4);
    summary = module.summary();
    try std.testing.expectEqual(@as(u32, 7), summary.weight);

    var mirror = sample.RuntimeBitmapSample{};
    try mirror.initWithSetBits(&.{});
    try mirror.copyFrom(&module);

    const mirror_summary = mirror.summary();
    try std.testing.expectEqual(summary.weight, mirror_summary.weight);
    try std.testing.expect(mirror.isSet(second_word_base + 6));
    try std.testing.expect(mirror.isSet(12));

    const selftest = try module.runSelftest();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqualStrings("lib/test_bitmap.c", selftest.anchor);
    try std.testing.expectEqual(@as(usize, 4), selftest.operation_families.len);
    try std.testing.expect(selftest.checked_range_mutations);
    try std.testing.expect(selftest.checked_iteration_paths);
    try std.testing.expectEqual(@as(usize, 1), module.selftest_runs);

    try module.exit();
    try std.testing.expectEqual(sample.ModuleStage.exited, module.stage());
    try std.testing.expectEqual(@as(usize, 1), module.exit_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.setRange(1, 1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());
}

test "runtime bitmap sample keeps bounded errors explicit" {
    var module = sample.RuntimeBitmapSample{};

    try std.testing.expectError(error.BitRangeOutOfBounds, module.initWithSetBits(&.{sample.RuntimeBitmapSample.bitmap_nbits}));
    try module.initWithSetBits(&.{ 1, 3 });
    try std.testing.expectError(error.BitRangeOutOfBounds, module.setRange(sample.RuntimeBitmapSample.bitmap_nbits - 1, 2));
    try std.testing.expectError(error.BitRangeOutOfBounds, module.clearRange(sample.RuntimeBitmapSample.bitmap_nbits, 1));
}

test "runtime bitmap sample keeps zero-length mutations and invalid copy sources explicit" {
    var module = sample.RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 2, 7 });

    const before = module.summary();
    try module.setRange(5, 0);
    try module.clearRange(sample.RuntimeBitmapSample.bitmap_nbits, 0);

    const after = module.summary();
    try std.testing.expectEqual(before.first_set, after.first_set);
    try std.testing.expectEqual(before.first_zero, after.first_zero);
    try std.testing.expectEqual(before.weight, after.weight);

    var cold_source = sample.RuntimeBitmapSample{};
    try std.testing.expectError(error.InvalidSourceLifecycle, module.copyFrom(&cold_source));
}
