const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "phase1 bitmap helper smoke keeps tail-clamped copy aliases aligned" {
    const count = bits_per_long + 5;
    const size = bits_per_long * 3;
    const src = [_]Word{ ~@as(Word, 0), ~@as(Word, 0), 0 };

    var direct_tail = [_]Word{ 0, 0, 0 };
    var alias_tail = [_]Word{ 0, 0, 0 };
    bitmap.copyClearTail(&direct_tail, src[0..2], count);
    bitmap.bitmap_copy_clear_tail(&alias_tail, src[0..2], count);
    try std.testing.expectEqualSlices(Word, &direct_tail, &alias_tail);
    try std.testing.expectEqual(bitmap.lastWordMask(count), direct_tail[1]);

    var direct_extend = [_]Word{ 0xaa55, 0xaa55, 0xaa55 };
    var alias_extend = [_]Word{ 0xaa55, 0xaa55, 0xaa55 };
    bitmap.copyAndExtend(&direct_extend, src[0..2], count, size);
    bitmap.bitmap_copy_and_extend(&alias_extend, src[0..2], count, size);
    try std.testing.expectEqualSlices(Word, &direct_extend, &alias_extend);
    try std.testing.expectEqual(@as(Word, 0), direct_extend[2]);

    try std.testing.expectEqual(bitmap.bitsToWords(count) * @sizeOf(Word), bitmap.bitmap_size(count));
}

test "phase1 bitmap helper smoke keeps range and weight aliases aligned across tails" {
    const nbits = bits_per_long + 5;
    const lhs = [_]Word{ 0b1110, (@as(Word, 1) << 2) | (@as(Word, 1) << 9) };
    const rhs = [_]Word{ 0b1010, (@as(Word, 1) << 2) | (@as(Word, 1) << 11) };
    var direct = [_]Word{ 0, 0 };
    var alias = [_]Word{ 0, 0 };

    bitmap.orBits(&direct, &lhs, &rhs, nbits);
    bitmap.bitmap_or(&alias, &lhs, &rhs, nbits);
    try std.testing.expectEqualSlices(Word, &direct, &alias);

    bitmap.xorBits(&direct, &lhs, &rhs, nbits);
    bitmap.bitmap_xor(&alias, &lhs, &rhs, nbits);
    try std.testing.expectEqualSlices(Word, &direct, &alias);

    try std.testing.expectEqual(bitmap.andBits(&direct, &lhs, &rhs, nbits), bitmap.bitmap_and(&alias, &lhs, &rhs, nbits));
    try std.testing.expectEqualSlices(Word, &direct, &alias);

    try std.testing.expectEqual(bitmap.andNotBits(&direct, &lhs, &rhs, nbits), bitmap.bitmap_andnot(&alias, &lhs, &rhs, nbits));
    try std.testing.expectEqualSlices(Word, &direct, &alias);

    try std.testing.expectEqual(bitmap.weightedOr(&direct, &lhs, &rhs, nbits), bitmap.bitmap_weighted_or(&alias, &lhs, &rhs, nbits));
    try std.testing.expectEqual(bitmap.weight(&direct, nbits), bitmap.bitmap_weighted_or(&alias, &lhs, &rhs, nbits));
    try std.testing.expectEqual(bitmap.weightedXor(&direct, &lhs, &rhs, nbits), bitmap.bitmap_weighted_xor(&alias, &lhs, &rhs, nbits));
    try std.testing.expectEqual(bitmap.weight(&direct, nbits), bitmap.bitmap_weighted_xor(&alias, &lhs, &rhs, nbits));

    var direct_range = [_]Word{ 0, 0 };
    var alias_range = [_]Word{ 0, 0 };
    bitmap.setRange(&direct_range, bits_per_long - 1, 3);
    bitmap.bitmap_set(&alias_range, bits_per_long - 1, 3);
    try std.testing.expectEqualSlices(Word, &direct_range, &alias_range);
    try std.testing.expectEqual(@as(usize, bits_per_long - 1), find_bit.findFirstBit(&alias_range, nbits));

    bitmap.clearRange(&direct_range, bits_per_long, 1);
    bitmap.bitmap_clear(&alias_range, bits_per_long, 1);
    try std.testing.expectEqualSlices(Word, &direct_range, &alias_range);
    try std.testing.expectEqual(@as(usize, 2), bitmap.bitmap_weight(&alias_range, nbits));
    try std.testing.expect(!bitmap.bitmap_empty(&alias_range, nbits));
}

test "phase1 bitmap helper smoke keeps formatting and allocation aliases bounded" {
    const allocator = std.testing.allocator;
    const nbits = bits_per_long + 5;

    var range_map = [_]Word{ 0, 0 };
    bitmap.bitmap_set(&range_map, bits_per_long - 2, 5);
    bitmap.bitmap_set(&range_map, bits_per_long + 6, 1);

    var direct_buffer: [64]u8 = undefined;
    var alias_buffer: [64]u8 = undefined;
    const direct_len = bitmap.scnprintf(&range_map, nbits, &direct_buffer);
    const alias_len = bitmap.bitmap_scnprintf(&range_map, nbits, &alias_buffer);
    try std.testing.expectEqual(direct_len, alias_len);
    try std.testing.expectEqualStrings(direct_buffer[0..direct_len], alias_buffer[0..alias_len]);

    var direct_zero = [_]Word{ 0xaa55, 0xaa55 };
    var alias_zero = [_]Word{ 0xaa55, 0xaa55 };
    bitmap.zero(&direct_zero, nbits);
    bitmap.bitmap_zero(&alias_zero, nbits);
    try std.testing.expectEqualSlices(Word, &direct_zero, &alias_zero);
    try std.testing.expect(bitmap.bitmap_empty(&alias_zero, nbits));

    bitmap.fill(&direct_zero, nbits);
    bitmap.bitmap_fill(&alias_zero, nbits);
    try std.testing.expectEqualSlices(Word, &direct_zero, &alias_zero);
    try std.testing.expect(bitmap.bitmap_full(&alias_zero, nbits));

    var plain: ?[]Word = try bitmap.bitmap_alloc(allocator, nbits);
    defer bitmap.bitmap_free(allocator, &plain);
    var zeroed: ?[]Word = try bitmap.bitmap_zalloc(allocator, nbits);
    defer bitmap.bitmap_free(allocator, &zeroed);

    try std.testing.expectEqual(@as(usize, bitmap.bitsToWords(nbits)), plain.?.len);
    try std.testing.expectEqual(plain.?.len, zeroed.?.len);
    for (zeroed.?) |word| {
        try std.testing.expectEqual(@as(Word, 0), word);
    }

    bitmap.bitmap_free(allocator, &plain);
    bitmap.bitmap_free(allocator, &zeroed);
    try std.testing.expect(plain == null);
    try std.testing.expect(zeroed == null);
}
