const std = @import("std");
const sample = @import("runtime_bitmap_sample");

fn expectSummary(
    summary: sample.RuntimeBitmapSummary,
    first_set: u32,
    first_zero: u32,
    weight: u32,
) !void {
    try std.testing.expectEqual(first_set, summary.first_set);
    try std.testing.expectEqual(first_zero, summary.first_zero);
    try std.testing.expectEqual(weight, summary.weight);
    try std.testing.expectEqual(sample.RuntimeBitmapSample.bitmap_nbits, summary.nbits);
}

test "runtime bitmap diff gate replays bounded lib/test_bitmap.c expectations" {
    var module = sample.RuntimeBitmapSample{};
    const top_bit = sample.RuntimeBitmapSample.bitmap_nbits - 1;

    try module.initWithSetBits(&.{ 0, 5, 64, top_bit });
    try expectSummary(module.summary(), 0, 1, 4);

    try module.clearRange(0, 1);
    try std.testing.expect(!module.isSet(0));
    try expectSummary(module.summary(), 5, 0, 3);

    try module.setRange(1, 4);
    try std.testing.expect(module.isSet(1));
    try std.testing.expect(module.isSet(4));
    try expectSummary(module.summary(), 1, 0, 7);

    try module.clearRange(top_bit, 1);
    try std.testing.expect(!module.isSet(top_bit));
    try expectSummary(module.summary(), 1, 0, 6);

    try std.testing.expectError(error.BitRangeOutOfBounds, module.setRange(top_bit + 1, 1));
    try std.testing.expectError(error.BitRangeOutOfBounds, module.clearRange(top_bit + 1, 1));
}

test "runtime bitmap diff gate keeps copy parity and cleared tail semantics explicit" {
    var source = sample.RuntimeBitmapSample{};
    try source.initWithSetBits(&.{ 0, 5, 64, 70 });

    var target = sample.RuntimeBitmapSample{};
    const top_bit = sample.RuntimeBitmapSample.bitmap_nbits - 1;
    try target.initWithSetBits(&.{ 1, 2, 3, top_bit });
    try std.testing.expect(target.isSet(top_bit));

    try target.copyFrom(&source);
    try expectSummary(target.summary(), 0, 1, 4);
    try std.testing.expect(target.isSet(0));
    try std.testing.expect(target.isSet(70));
    try std.testing.expect(!target.isSet(top_bit));

    try source.setRange(top_bit, 1);
    try std.testing.expect(source.isSet(top_bit));
    try std.testing.expect(!target.isSet(top_bit));
    try expectSummary(source.summary(), 0, 1, 5);
    try expectSummary(target.summary(), 0, 1, 4);
}

test "runtime bitmap diff gate keeps selftest and exit lifecycle guards reviewable" {
    var module = sample.RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 0, 5, 64, 70 });

    const selftest = try module.runSelftest();
    try std.testing.expectEqualStrings("lib/test_bitmap.c", selftest.anchor);
    try std.testing.expectEqual(@as(usize, 4), selftest.operation_families.len);
    try std.testing.expectEqual(sample.OperationFamily.clear_set, selftest.operation_families[0]);
    try std.testing.expectEqual(sample.OperationFamily.copy, selftest.operation_families[1]);
    try std.testing.expectEqual(sample.OperationFamily.summary, selftest.operation_families[2]);
    try std.testing.expectEqual(sample.OperationFamily.lifecycle, selftest.operation_families[3]);
    try std.testing.expect(selftest.checked_range_mutations);
    try std.testing.expect(selftest.checked_lifecycle_paths);

    const selftested = module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, selftested.stage);
    try std.testing.expectEqual(@as(usize, 1), selftested.init_runs);
    try std.testing.expectEqual(@as(usize, 1), selftested.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), selftested.exit_runs);
    try std.testing.expect(selftested.allows_mutation);

    try module.exit();
    const exited = module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.exited, exited.stage);
    try std.testing.expectEqual(@as(usize, 1), exited.init_runs);
    try std.testing.expectEqual(@as(usize, 1), exited.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), exited.exit_runs);
    try std.testing.expect(!exited.allows_mutation);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.setRange(0, 1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.clearRange(0, 1));

    var exited_source = sample.RuntimeBitmapSample{};
    try exited_source.initWithSetBits(&.{1});
    try exited_source.exit();

    var fresh_target = sample.RuntimeBitmapSample{};
    try fresh_target.initWithSetBits(&.{});
    try std.testing.expectError(error.InvalidSourceLifecycle, fresh_target.copyFrom(&exited_source));
}
