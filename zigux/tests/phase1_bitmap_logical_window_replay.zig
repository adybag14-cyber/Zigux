const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");

fn maskedWord(value: bitmap.Word, nbits: usize) bitmap.Word {
    return value & bitmap.lastWordMask(nbits);
}

test "phase1 bitmap logical window replay keeps partial-tail set algebra aligned" {
    const nbits = bitmap.bits_per_long + 5;
    const lhs = [_]bitmap.Word{
        0b101101,
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 9),
    };
    const rhs = [_]bitmap.Word{
        0b011011,
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 11),
    };

    var union_bits = [_]bitmap.Word{ 0, 0 };
    bitmap.bitmap_or(&union_bits, &lhs, &rhs, nbits);
    try std.testing.expectEqualSlices(
        bitmap.Word,
        &[_]bitmap.Word{ 0b11_1111, 0b1_1010 },
        &[_]bitmap.Word{ union_bits[0], maskedWord(union_bits[1], nbits) },
    );
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstBit(&union_bits, nbits));
    try std.testing.expectEqual(@as(usize, 6), find_bit.findFirstZeroBit(&union_bits, nbits));
    try std.testing.expectEqual(@as(usize, 9), bitmap.bitmap_weight(&union_bits, nbits));

    var intersection = [_]bitmap.Word{ 0, 0 };
    try std.testing.expect(bitmap.bitmap_and(&intersection, &lhs, &rhs, nbits));
    try std.testing.expectEqualSlices(
        bitmap.Word,
        &[_]bitmap.Word{ 0b00_1001, 0b0_0010 },
        &[_]bitmap.Word{ intersection[0], maskedWord(intersection[1], nbits) },
    );
    try std.testing.expect(bitmap.bitmap_intersects(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&intersection, &union_bits, nbits));
    try std.testing.expect(!bitmap.bitmap_equal(&lhs, &rhs, nbits));

    var lhs_only = [_]bitmap.Word{ 0, 0 };
    try std.testing.expect(bitmap.bitmap_andnot(&lhs_only, &lhs, &rhs, nbits));
    try std.testing.expectEqualSlices(
        bitmap.Word,
        &[_]bitmap.Word{ 0b10_0100, 0b1_0000 },
        &[_]bitmap.Word{ lhs_only[0], maskedWord(lhs_only[1], nbits) },
    );
    try std.testing.expectEqual(@as(usize, 2), find_bit.findFirstBit(&lhs_only, nbits));
    try std.testing.expectEqual(@as(usize, 3), bitmap.bitmap_weight(&lhs_only, nbits));
}

test "phase1 bitmap logical window replay keeps cross-word edits and formatting explicit" {
    const nbits = bitmap.bits_per_long * 2 + 10;
    const first_range_start = bitmap.bits_per_long - 2;
    const second_range_start = bitmap.bits_per_long + 6;

    var direct = [_]bitmap.Word{ 0, 0, 0 };
    var alias = [_]bitmap.Word{ 0, 0, 0 };

    bitmap.setRange(&direct, first_range_start, 5);
    bitmap.bitmap_set(&alias, first_range_start, 5);
    bitmap.setRange(&direct, second_range_start, 4);
    bitmap.bitmap_set(&alias, second_range_start, 4);
    bitmap.clearRange(&direct, second_range_start + 1, 1);
    bitmap.bitmap_clear(&alias, second_range_start + 1, 1);
    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);

    try std.testing.expectEqual(@as(usize, first_range_start), find_bit.findFirstBit(&alias, nbits));
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstZeroBit(&alias, nbits));
    try std.testing.expectEqual(@as(usize, 8), bitmap.bitmap_weight(&alias, nbits));

    var rendered: [64]u8 = undefined;
    const rendered_len = bitmap.bitmap_scnprintf(&alias, nbits, &rendered);

    var expected: [48]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "{d}-{d},{d},{d}-{d}",
        .{
            first_range_start,
            first_range_start + 4,
            second_range_start,
            second_range_start + 2,
            second_range_start + 3,
        },
    );
    try std.testing.expectEqualStrings(expected_text, rendered[0..rendered_len]);

    bitmap.bitmap_zero(&alias, nbits);
    try std.testing.expect(bitmap.bitmap_empty(&alias, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findFirstBit(&alias, nbits));
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstZeroBit(&alias, nbits));

    bitmap.bitmap_fill(&alias, nbits);
    try std.testing.expect(bitmap.bitmap_full(&alias, nbits));
    try std.testing.expectEqual(@as(usize, nbits), bitmap.bitmap_weight(&alias, nbits));
    try std.testing.expectEqual(maskedWord(alias[2], nbits), bitmap.lastWordMask(nbits));
}
