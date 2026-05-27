const std = @import("std");
const runtime_bitmap_sample = @import("runtime_bitmap_sample");

fn secondWordStart() u32 {
    return runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits / 2;
}

fn secondWordTailBit() u32 {
    return secondWordStart() - 1;
}

fn secondWordPreviewBit() u32 {
    return secondWordStart() + 6;
}

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
    const expected = try std.fmt.allocPrint(std.testing.allocator, "{}", .{top_bit});
    defer std.testing.allocator.free(expected);
    try std.testing.expectEqualStrings(expected, direct_formatted);
}

test "runtime bitmap sample keeps active word-width boundary bits explicit in the direct sample leg" {
    const second_word_start = secondWordStart();
    const second_word_tail = secondWordTailBit();
    const second_word_preview = secondWordPreviewBit();
    const top_bit = runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits - 1;

    var direct = runtime_bitmap_sample.RuntimeBitmapSample{};
    try direct.initWithSetBits(&.{ second_word_tail, second_word_start, second_word_preview, top_bit });

    const direct_summary = direct.summary();
    try std.testing.expectEqual(second_word_tail, direct_summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), direct_summary.first_zero);
    try std.testing.expectEqual(@as(u32, 4), direct_summary.weight);
    try std.testing.expectEqual(runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits, direct_summary.nbits);
    try std.testing.expectEqual(@as(usize, 1), direct_summary.init_runs);
    try std.testing.expect(direct.isSet(second_word_tail));
    try std.testing.expect(direct.isSet(second_word_start));
    try std.testing.expect(direct.isSet(second_word_preview));
    try std.testing.expect(direct.isSet(top_bit));
    try std.testing.expect(!direct.isSet(second_word_tail - 1));
    try std.testing.expect(!direct.isSet(second_word_start + 1));
    try std.testing.expectEqual(@as(?u32, second_word_tail), direct.nthSetBit(0));
    try std.testing.expectEqual(@as(?u32, second_word_start), direct.nthSetBit(1));
    try std.testing.expectEqual(@as(?u32, second_word_preview), direct.nthSetBit(2));
    try std.testing.expectEqual(@as(?u32, top_bit), direct.nthSetBit(3));
    try std.testing.expectEqual(@as(?u32, null), direct.nthSetBit(4));
    try std.testing.expectEqual(@as(u32, 2), try direct.countSetBitsInRange(second_word_tail, 2));
    try std.testing.expectEqual(@as(u32, 2), try direct.countSetBitsInRange(second_word_start, 7));

    const direct_formatted = try direct.formatSetBits(std.testing.allocator);
    defer std.testing.allocator.free(direct_formatted);
    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "{},{},{},{}",
        .{ second_word_tail, second_word_start, second_word_preview, top_bit },
    );
    defer std.testing.allocator.free(expected);
    try std.testing.expectEqualStrings(expected, direct_formatted);
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
    const expected = try std.fmt.allocPrint(std.testing.allocator, "0,{}", .{top_bit});
    defer std.testing.allocator.free(expected);
    try std.testing.expectEqualStrings(expected, direct_formatted);
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
