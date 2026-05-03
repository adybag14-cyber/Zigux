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

    var parsed = runtime_bitmap_sample.RuntimeBitmapSample{};
    try parsed.initFromBitList("127");

    const parsed_summary = parsed.summary();
    try std.testing.expectEqual(direct_summary.first_set, parsed_summary.first_set);
    try std.testing.expectEqual(direct_summary.first_zero, parsed_summary.first_zero);
    try std.testing.expectEqual(direct_summary.weight, parsed_summary.weight);
    try std.testing.expectEqual(direct_summary.nbits, parsed_summary.nbits);
    try std.testing.expectEqual(@as(usize, 1), parsed_summary.init_runs);
    try std.testing.expect(parsed.isSet(top_bit));
    try std.testing.expect(!parsed.isSet(top_bit - 1));
    try std.testing.expectEqual(@as(?u32, top_bit), parsed.nthSetBit(0));
    try std.testing.expectEqual(@as(?u32, null), parsed.nthSetBit(1));
    try std.testing.expectEqual(@as(u32, 1), try parsed.countSetBitsInRange(top_bit, 1));

    const parsed_formatted = try parsed.formatSetBits(std.testing.allocator);
    defer std.testing.allocator.free(parsed_formatted);
    try std.testing.expectEqualStrings("127", parsed_formatted);
}
