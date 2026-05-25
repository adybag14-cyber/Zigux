const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "phase1 bitmap replay keeps cross-word ranges and scans aligned" {
    const nbits = bits_per_long + 13;
    var map = [_]Word{ 0, 0 };

    bitmap.setRange(&map, bits_per_long - 3, 8);
    bitmap.setRange(&map, bits_per_long + 10, 1);

    try std.testing.expectEqual(@as(usize, bits_per_long - 3), find_bit.findFirstBit(&map, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 5), find_bit.findNextBit(&map, nbits, bits_per_long + 5));
    try std.testing.expectEqual(@as(usize, bits_per_long + 10), find_bit.findLastBit(&map, nbits));
    try std.testing.expectEqual(@as(usize, 9), bitmap.weight(&map, nbits));

    var rendered: [64]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&map, nbits, &rendered);

    var expected: [32]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "{d}-{d},{d}",
        .{ bits_per_long - 3, bits_per_long + 4, bits_per_long + 10 },
    );
    try std.testing.expectEqualStrings(expected_text, rendered[0..rendered_len]);
}

test "phase1 bitmap replay keeps copied tails zero-filled for later scans" {
    const count = bits_per_long + 3;
    const size = bits_per_long * 2 + 9;
    var src = [_]Word{ 0, 0 };
    var dst = [_]Word{ ~@as(Word, 0), ~@as(Word, 0), ~@as(Word, 0) };

    bitmap.setRange(&src, 1, 3);
    bitmap.setRange(&src, bits_per_long + 1, 2);
    bitmap.copyAndExtend(&dst, &src, count, size);

    try std.testing.expectEqual(@as(usize, bits_per_long + 2), find_bit.findLastBit(&dst, size));
    try std.testing.expectEqual(@as(usize, bits_per_long + 3), find_bit.findNextZeroBit(&dst, size, bits_per_long + 3));
    try std.testing.expectEqual(@as(Word, 0), dst[2]);
}

test "phase1 bitmap replay keeps andnot weights aligned with scan-visible bits" {
    const nbits = bits_per_long + 6;
    const lhs = [_]Word{
        (@as(Word, 1) << 1) | (@as(Word, 1) << 4),
        (@as(Word, 1) << 2) | (@as(Word, 1) << 5) | (@as(Word, 1) << 10),
    };
    const rhs = [_]Word{
        @as(Word, 1) << 4,
        (@as(Word, 1) << 5) | (@as(Word, 1) << 10),
    };
    var direct = [_]Word{ 0, 0 };
    var alias = [_]Word{ 0, 0 };

    try std.testing.expect(bitmap.andNotBits(&direct, &lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_andnot(&alias, &lhs, &rhs, nbits));
    try std.testing.expectEqualSlices(Word, &direct, &alias);
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&direct, nbits));
    try std.testing.expectEqual(bitmap.weight(&direct, nbits), bitmap.bitmap_weight_andnot(&lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 1), find_bit.findFirstBit(&direct, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 2), find_bit.findNextBit(&direct, nbits, 2));
    try std.testing.expectEqual(@as(usize, bits_per_long + 2), find_bit.findLastBit(&direct, nbits));
}
