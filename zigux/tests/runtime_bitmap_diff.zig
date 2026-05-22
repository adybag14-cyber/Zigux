const std = @import("std");
const sample = @import("runtime_bitmap_sample");

const DiffCase = struct {
    name: []const u8,
    init_bits: []const u32,
    expected_first_set: u32,
    expected_first_zero: u32,
    expected_weight: u32,
    expected_last_nth: ?u32,
    range_start: u32,
    range_len: u32,
    expected_range_weight: u32,
};

fn expectSummary(
    summary: sample.RuntimeBitmapSummary,
    expected_first_set: u32,
    expected_first_zero: u32,
    expected_weight: u32,
) !void {
    try std.testing.expectEqual(expected_first_set, summary.first_set);
    try std.testing.expectEqual(expected_first_zero, summary.first_zero);
    try std.testing.expectEqual(expected_weight, summary.weight);
    try std.testing.expectEqual(sample.RuntimeBitmapSample.bitmap_nbits, summary.nbits);
}

fn expectSummaryStable(
    before: sample.RuntimeBitmapSummary,
    after: sample.RuntimeBitmapSummary,
) !void {
    try std.testing.expectEqual(before.first_set, after.first_set);
    try std.testing.expectEqual(before.first_zero, after.first_zero);
    try std.testing.expectEqual(before.weight, after.weight);
    try std.testing.expectEqual(before.nbits, after.nbits);
    try std.testing.expectEqual(before.init_runs, after.init_runs);
    try std.testing.expectEqual(before.selftest_runs, after.selftest_runs);
    try std.testing.expectEqual(before.exit_runs, after.exit_runs);
}

test "runtime bitmap diff gate replays bounded summary and sparse nth-set expectations" {
    const cases = [_]DiffCase{
        .{
            .name = "sparse cross-word starter keeps early and late bits reviewable",
            .init_bits = &.{ 10, 20, 30, 40, 50, 60, 80, 123 },
            .expected_first_set = 10,
            .expected_first_zero = 0,
            .expected_weight = 8,
            .expected_last_nth = 123,
            .range_start = 0,
            .range_len = 81,
            .expected_range_weight = 7,
        },
        .{
            .name = "edge bits across both words keep the tail visible",
            .init_bits = &.{ 0, 63, 64, 127 },
            .expected_first_set = 0,
            .expected_first_zero = 1,
            .expected_weight = 4,
            .expected_last_nth = 127,
            .range_start = 63,
            .range_len = 2,
            .expected_range_weight = 2,
        },
    };

    for (cases) |case| {
        _ = case.name;

        var bitmap = sample.RuntimeBitmapSample{};
        try bitmap.initWithSetBits(case.init_bits);

        const summary = bitmap.summary();
        try expectSummary(
            summary,
            case.expected_first_set,
            case.expected_first_zero,
            case.expected_weight,
        );
        try std.testing.expectEqual(@as(?u32, case.expected_first_set), bitmap.nthSetBit(0));
        try std.testing.expectEqual(case.expected_last_nth, bitmap.nthSetBit(summary.weight - 1));
        try std.testing.expectEqual(@as(?u32, null), bitmap.nthSetBit(summary.weight));
        try std.testing.expectEqual(
            case.expected_range_weight,
            try bitmap.countSetBitsInRange(case.range_start, case.range_len),
        );
    }
}

test "runtime bitmap diff gate keeps copy parity explicit after a cleared tail mutation" {
    var source = sample.RuntimeBitmapSample{};
    try source.initWithSetBits(&.{ 0, 5, 64, 70, 127 });
    _ = try source.runSelftest();

    try source.clearRange(64, 1);
    try source.clearRange(127, 1);
    try source.setRange(9, 4);

    const source_summary = source.summary();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, source.stage());
    try expectSummary(source_summary, 0, 1, 7);
    try std.testing.expect(source.isSet(0));
    try std.testing.expect(source.isSet(5));
    try std.testing.expect(source.isSet(9));
    try std.testing.expect(source.isSet(10));
    try std.testing.expect(source.isSet(11));
    try std.testing.expect(source.isSet(12));
    try std.testing.expect(source.isSet(70));
    try std.testing.expect(!source.isSet(64));
    try std.testing.expect(!source.isSet(127));
    try std.testing.expectEqual(@as(?u32, 70), source.nthSetBit(6));
    try std.testing.expectEqual(@as(u32, 4), try source.countSetBitsInRange(9, 4));

    var target = sample.RuntimeBitmapSample{};
    try target.initWithSetBits(&.{ 1, 2, 3 });
    try target.copyFrom(&source);

    const target_summary = target.summary();
    try std.testing.expectEqual(sample.ModuleStage.initialized, target.stage());
    try std.testing.expectEqual(source_summary.first_set, target_summary.first_set);
    try std.testing.expectEqual(source_summary.first_zero, target_summary.first_zero);
    try std.testing.expectEqual(source_summary.weight, target_summary.weight);
    try std.testing.expectEqual(source_summary.nbits, target_summary.nbits);
    try std.testing.expectEqual(@as(usize, 1), target_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), target_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), target_summary.exit_runs);
    try std.testing.expect(target.isSet(0));
    try std.testing.expect(target.isSet(5));
    try std.testing.expect(target.isSet(9));
    try std.testing.expect(target.isSet(10));
    try std.testing.expect(target.isSet(11));
    try std.testing.expect(target.isSet(12));
    try std.testing.expect(target.isSet(70));
    try std.testing.expect(!target.isSet(64));
    try std.testing.expect(!target.isSet(127));
    try std.testing.expectEqual(@as(?u32, 70), target.nthSetBit(6));
    try std.testing.expectEqual(@as(?u32, null), target.nthSetBit(7));
}

test "runtime bitmap diff gate keeps selftest and exit lifecycle guards explicit" {
    var bitmap = sample.RuntimeBitmapSample{};
    try bitmap.initFromBitList("0, 63, 64, 127");

    const initialized = bitmap.summary();
    try expectSummary(initialized, 0, 1, 4);

    const selftest = try bitmap.runSelftest();
    try std.testing.expectEqualStrings("lib/test_bitmap.c", selftest.anchor);
    try std.testing.expectEqual(@as(usize, 4), selftest.operation_families.len);
    try std.testing.expect(selftest.checked_range_mutations);
    try std.testing.expect(selftest.checked_iteration_paths);

    const after_selftest = bitmap.summary();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, bitmap.stage());
    try std.testing.expectEqual(initialized.first_set, after_selftest.first_set);
    try std.testing.expectEqual(initialized.first_zero, after_selftest.first_zero);
    try std.testing.expectEqual(initialized.weight, after_selftest.weight);
    try std.testing.expectEqual(@as(usize, 1), after_selftest.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), after_selftest.exit_runs);

    try bitmap.exit();

    const before_rejected_ops = bitmap.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, bitmap.stage());
    try std.testing.expectEqual(@as(usize, 1), before_rejected_ops.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), before_rejected_ops.exit_runs);

    var fresh_source = sample.RuntimeBitmapSample{};
    try fresh_source.initWithSetBits(&.{10});

    try std.testing.expectError(error.InvalidLifecycleTransition, bitmap.setRange(5, 1));
    try std.testing.expectError(error.InvalidLifecycleTransition, bitmap.clearRange(63, 1));
    try std.testing.expectError(error.InvalidLifecycleTransition, bitmap.copyFrom(&fresh_source));
    try std.testing.expectError(error.InvalidLifecycleTransition, bitmap.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, bitmap.exit());

    const after_rejected_ops = bitmap.summary();
    try expectSummaryStable(before_rejected_ops, after_rejected_ops);
}
