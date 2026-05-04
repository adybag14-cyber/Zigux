const std = @import("std");
const sample = @import("runtime_bitmap_sample");

test "runtime bitmap sample advertises the bounded pilot-module contract" {
    const descriptor = sample.RuntimeBitmapSample.descriptor();

    try std.testing.expectEqualStrings("runtime_bitmap", descriptor.name);
    try std.testing.expectEqualStrings("lib/test_bitmap.c", descriptor.anchor);
    try std.testing.expect(descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selftest_hook);
}

test "runtime bitmap sample keeps the public review contract explicit at the module boundary" {
    const expected_focus = sample.sample_review_focus;
    const expected_non_goals = sample.sample_review_non_goals;
    const contract = sample.RuntimeBitmapSample.reviewContract();

    try std.testing.expectEqual(@as(usize, expected_focus.len), contract.focus.len);
    for (expected_focus, contract.focus) |expected, actual| {
        try std.testing.expectEqual(expected, actual);
    }

    try std.testing.expectEqual(@as(usize, expected_non_goals.len), contract.non_goals.len);
    for (expected_non_goals, contract.non_goals) |expected, actual| {
        try std.testing.expectEqualStrings(expected, actual);
    }
}

test "runtime bitmap sample enforces lifecycle transitions and bitmap mutations" {
    var module = sample.RuntimeBitmapSample{};
    const second_word_base = sample.RuntimeBitmapSample.bitmap_nbits / 2;

    try std.testing.expectEqual(sample.ModuleStage.cold, module.stage());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());

    try module.initWithSetBits(&.{ 0, 5, second_word_base, second_word_base + 6 });
    try std.testing.expectEqual(sample.ModuleStage.initialized, module.stage());
    var summary = module.summary();
    try std.testing.expectEqual(@as(usize, 1), summary.init_runs);
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

    const summary_before_selftest = module.summary();
    const selftest = try module.runSelftest();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqualStrings("lib/test_bitmap.c", selftest.anchor);
    try std.testing.expectEqual(@as(usize, 4), selftest.operation_families.len);
    try std.testing.expectEqual(sample.OperationFamily.clear_set, selftest.operation_families[0]);
    try std.testing.expectEqual(sample.OperationFamily.copy, selftest.operation_families[1]);
    try std.testing.expectEqual(sample.OperationFamily.parse_and_print, selftest.operation_families[2]);
    try std.testing.expectEqual(sample.OperationFamily.iteration_and_ranges, selftest.operation_families[3]);
    try std.testing.expect(selftest.checked_range_mutations);
    try std.testing.expect(selftest.checked_iteration_paths);
    const summary_after_selftest = module.summary();
    try std.testing.expectEqual(@as(usize, 1), summary_after_selftest.init_runs);
    try std.testing.expectEqual(@as(usize, 1), summary_after_selftest.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), summary_after_selftest.exit_runs);
    try std.testing.expectEqual(summary_before_selftest.first_set, summary_after_selftest.first_set);
    try std.testing.expectEqual(summary_before_selftest.first_zero, summary_after_selftest.first_zero);
    try std.testing.expectEqual(summary_before_selftest.weight, summary_after_selftest.weight);
    try std.testing.expect(module.isSet(second_word_base + 6));
    try std.testing.expect(module.isSet(12));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());

    const summary_before_exit = module.summary();
    try module.exit();
    try std.testing.expectEqual(sample.ModuleStage.exited, module.stage());
    const summary_after_exit = module.summary();
    try std.testing.expectEqual(@as(usize, 1), summary_after_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 1), summary_after_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), summary_after_exit.exit_runs);
    try std.testing.expectEqual(summary_before_exit.first_set, summary_after_exit.first_set);
    try std.testing.expectEqual(summary_before_exit.first_zero, summary_after_exit.first_zero);
    try std.testing.expectEqual(summary_before_exit.weight, summary_after_exit.weight);
    try std.testing.expectEqual(summary_before_exit.nbits, summary_after_exit.nbits);
    try std.testing.expect(module.isSet(second_word_base + 6));
    try std.testing.expect(module.isSet(12));
    try std.testing.expect(!module.isSet(second_word_base));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.setRange(1, 1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.clearRange(1, 1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.initWithSetBits(&.{ 1, 2 }));

    var source = sample.RuntimeBitmapSample{};
    try source.initWithSetBits(&.{ 2, 9 });
    try std.testing.expectError(error.InvalidLifecycleTransition, module.copyFrom(&source));
}

test "runtime bitmap sample keeps post-selftest mutation replay explicit at the module boundary" {
    var module = sample.RuntimeBitmapSample{};
    const second_word_base = sample.RuntimeBitmapSample.bitmap_nbits / 2;
    try module.initWithSetBits(&.{ 0, 5, second_word_base, second_word_base + 6 });

    const summary_before_selftest = module.summary();
    _ = try module.runSelftest();

    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqual(@as(u32, 4), summary_before_selftest.weight);

    try module.clearRange(second_word_base, 2);
    try module.setRange(9, 4);

    const summary_after_mutation = module.summary();
    try std.testing.expectEqual(@as(u32, 0), summary_after_mutation.first_set);
    try std.testing.expectEqual(@as(u32, 1), summary_after_mutation.first_zero);
    try std.testing.expectEqual(@as(u32, 7), summary_after_mutation.weight);
    try std.testing.expectEqual(sample.RuntimeBitmapSample.bitmap_nbits, summary_after_mutation.nbits);
    try std.testing.expect(module.isSet(12));
    try std.testing.expect(module.isSet(second_word_base + 6));
    try std.testing.expect(!module.isSet(second_word_base));

    var mirror = sample.RuntimeBitmapSample{};
    try mirror.initWithSetBits(&.{});
    try mirror.copyFrom(&module);

    const mirror_summary = mirror.summary();
    try std.testing.expectEqual(summary_after_mutation.first_set, mirror_summary.first_set);
    try std.testing.expectEqual(summary_after_mutation.first_zero, mirror_summary.first_zero);
    try std.testing.expectEqual(summary_after_mutation.weight, mirror_summary.weight);
    try std.testing.expectEqual(summary_after_mutation.nbits, mirror_summary.nbits);
    try std.testing.expect(mirror.isSet(12));
    try std.testing.expect(mirror.isSet(second_word_base + 6));
    try std.testing.expect(!mirror.isSet(second_word_base));
}

test "runtime bitmap sample keeps sparse nth-set-bit replay explicit at the module boundary" {
    var module = sample.RuntimeBitmapSample{};
    const expected = [_]u32{ 10, 20, 30, 40, 50, 60, 80, 123 };
    try module.initWithSetBits(&expected);

    const initialized_summary = module.summary();
    try std.testing.expectEqual(@as(u32, 8), initialized_summary.weight);
    try std.testing.expectEqual(@as(usize, 1), initialized_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.exit_runs);

    for (expected, 0..) |bit, index| {
        try std.testing.expectEqual(bit, module.nthSetBit(@intCast(index)) orelse return error.ExpectedNthSetBit);
    }
    try std.testing.expectEqual(@as(?u32, null), module.nthSetBit(@intCast(expected.len)));

    _ = try module.runSelftest();

    const post_selftest_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqual(@as(u32, 8), post_selftest_summary.weight);
    try std.testing.expectEqual(@as(usize, 1), post_selftest_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), post_selftest_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), post_selftest_summary.exit_runs);

    for (expected, 0..) |bit, index| {
        try std.testing.expectEqual(bit, module.nthSetBit(@intCast(index)) orelse return error.ExpectedNthSetBit);
    }
    try std.testing.expectEqual(@as(?u32, null), module.nthSetBit(@intCast(expected.len)));
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

    var exited_source = sample.RuntimeBitmapSample{};
    try exited_source.initWithSetBits(&.{ 9, 13 });
    try exited_source.exit();
    try std.testing.expectError(error.InvalidSourceLifecycle, module.copyFrom(&exited_source));
}

test "runtime bitmap sample accepts selftest-complete copy sources at the module boundary" {
    const second_word_base = sample.RuntimeBitmapSample.bitmap_nbits / 2;

    var source = sample.RuntimeBitmapSample{};
    try source.initWithSetBits(&.{ 4, 7, second_word_base + 1, second_word_base + 9 });
    const source_summary_before_selftest = source.summary();
    _ = try source.runSelftest();

    var mirror = sample.RuntimeBitmapSample{};
    try mirror.initWithSetBits(&.{});
    try mirror.copyFrom(&source);

    const mirror_summary = mirror.summary();
    try std.testing.expectEqual(sample.ModuleStage.initialized, mirror.stage());
    try std.testing.expectEqual(source_summary_before_selftest.first_set, mirror_summary.first_set);
    try std.testing.expectEqual(source_summary_before_selftest.first_zero, mirror_summary.first_zero);
    try std.testing.expectEqual(source_summary_before_selftest.weight, mirror_summary.weight);
    try std.testing.expectEqual(source_summary_before_selftest.nbits, mirror_summary.nbits);
    try std.testing.expectEqual(@as(usize, 1), mirror_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), mirror_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), mirror_summary.exit_runs);
    try std.testing.expect(mirror.isSet(4));
    try std.testing.expect(mirror.isSet(7));
    try std.testing.expect(mirror.isSet(second_word_base + 1));
    try std.testing.expect(mirror.isSet(second_word_base + 9));

    const formatted = try mirror.formatSetBits(std.testing.allocator);
    defer std.testing.allocator.free(formatted);
    try std.testing.expectEqualStrings("4,7,65,73", formatted);

    const selftest = try mirror.runSelftest();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, mirror.stage());
    try std.testing.expectEqual(@as(usize, 4), selftest.operation_families.len);
    try std.testing.expectEqual(sample.OperationFamily.copy, selftest.operation_families[1]);
}

test "runtime bitmap sample keeps parse-and-print and bit-list guards explicit at the module boundary" {
    var module = sample.RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 0, 5, 64, 70 });

    const formatted = try module.formatSetBits(std.testing.allocator);
    defer std.testing.allocator.free(formatted);
    try std.testing.expectEqualStrings("0,5,64,70", formatted);

    var parsed = sample.RuntimeBitmapSample{};
    try parsed.initFromBitList("0, 5, 64, 70");

    const parsed_summary = parsed.summary();
    const module_summary = module.summary();
    try std.testing.expectEqual(module_summary.first_set, parsed_summary.first_set);
    try std.testing.expectEqual(module_summary.first_zero, parsed_summary.first_zero);
    try std.testing.expectEqual(module_summary.weight, parsed_summary.weight);
    try std.testing.expectEqual(module_summary.nbits, parsed_summary.nbits);
    try std.testing.expect(parsed.isSet(0));
    try std.testing.expect(parsed.isSet(5));
    try std.testing.expect(parsed.isSet(64));
    try std.testing.expect(parsed.isSet(70));
    try std.testing.expectEqual(@as(usize, 1), parsed_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), parsed_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), parsed_summary.exit_runs);
    try std.testing.expectEqual(sample.ModuleStage.initialized, parsed.stage());

    var empty = sample.RuntimeBitmapSample{};
    try empty.initFromBitList("  ");
    const empty_summary = empty.summary();
    try std.testing.expectEqual(sample.RuntimeBitmapSample.bitmap_nbits, empty_summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), empty_summary.first_zero);
    try std.testing.expectEqual(@as(u32, 0), empty_summary.weight);
    try std.testing.expectEqual(sample.RuntimeBitmapSample.bitmap_nbits, empty_summary.nbits);
    try std.testing.expectEqual(@as(?u32, null), empty.nthSetBit(0));

    const empty_formatted = try empty.formatSetBits(std.testing.allocator);
    defer std.testing.allocator.free(empty_formatted);
    try std.testing.expectEqualStrings("", empty_formatted);

    var invalid = sample.RuntimeBitmapSample{};
    try std.testing.expectError(error.InvalidBitList, invalid.initFromBitList("0, nope"));

    var trailing_comma = sample.RuntimeBitmapSample{};
    try std.testing.expectError(error.InvalidBitList, trailing_comma.initFromBitList("0,"));

    var doubled_separator = sample.RuntimeBitmapSample{};
    try std.testing.expectError(error.InvalidBitList, doubled_separator.initFromBitList("0,,5"));

    var out_of_bounds = sample.RuntimeBitmapSample{};
    try std.testing.expectError(
        error.BitRangeOutOfBounds,
        out_of_bounds.initFromBitList("0, 5, 64, 128"),
    );

    try std.testing.expectError(error.InvalidLifecycleTransition, parsed.initFromBitList("1"));
}

test "runtime bitmap sample keeps transactional init failures explicit at the module boundary" {
    var parsed = sample.RuntimeBitmapSample{};
    try std.testing.expectError(
        error.BitRangeOutOfBounds,
        parsed.initFromBitList("0, 5, 64, 128"),
    );
    try std.testing.expectEqual(sample.ModuleStage.cold, parsed.stage());

    const parsed_summary = parsed.summary();
    try std.testing.expectEqual(sample.RuntimeBitmapSample.bitmap_nbits, parsed_summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), parsed_summary.first_zero);
    try std.testing.expectEqual(@as(u32, 0), parsed_summary.weight);
    try std.testing.expectEqual(@as(usize, 0), parsed_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), parsed_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), parsed_summary.exit_runs);
    try std.testing.expectEqual(@as(?u32, null), parsed.nthSetBit(0));
    try std.testing.expect(!parsed.isSet(0));
    try std.testing.expect(!parsed.isSet(5));
    try std.testing.expect(!parsed.isSet(64));

    const parsed_formatted = try parsed.formatSetBits(std.testing.allocator);
    defer std.testing.allocator.free(parsed_formatted);
    try std.testing.expectEqualStrings("", parsed_formatted);

    try parsed.initFromBitList("0, 5, 64, 70");
    try std.testing.expectEqual(sample.ModuleStage.initialized, parsed.stage());
    try std.testing.expect(parsed.isSet(0));
    try std.testing.expect(parsed.isSet(5));
    try std.testing.expect(parsed.isSet(64));
    try std.testing.expect(parsed.isSet(70));

    var direct = sample.RuntimeBitmapSample{};
    try std.testing.expectError(
        error.BitRangeOutOfBounds,
        direct.initWithSetBits(&.{ 1, sample.RuntimeBitmapSample.bitmap_nbits }),
    );
    try std.testing.expectEqual(sample.ModuleStage.cold, direct.stage());

    const direct_summary = direct.summary();
    try std.testing.expectEqual(sample.RuntimeBitmapSample.bitmap_nbits, direct_summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), direct_summary.first_zero);
    try std.testing.expectEqual(@as(u32, 0), direct_summary.weight);
    try std.testing.expectEqual(@as(usize, 0), direct_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), direct_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), direct_summary.exit_runs);
    try std.testing.expect(!direct.isSet(1));
    try std.testing.expectEqual(@as(?u32, null), direct.nthSetBit(0));

    try direct.initWithSetBits(&.{ 1, 3 });
    try std.testing.expectEqual(sample.ModuleStage.initialized, direct.stage());
    try std.testing.expect(direct.isSet(1));
    try std.testing.expect(direct.isSet(3));
}
