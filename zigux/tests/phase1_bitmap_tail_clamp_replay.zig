const std = @import("std");
const bitmap = @import("bitmap");

test "phase1 bitmap tail clamp replay keeps equality and logical masks inside the declared window" {
    const exact_nbits = bitmap.bits_per_long;
    const exact_lhs = [_]bitmap.Word{ 0b1011, @as(bitmap.Word, 1) << 7 };
    const exact_rhs = [_]bitmap.Word{ 0b1011, @as(bitmap.Word, 1) << 13 };

    try std.testing.expect(bitmap.equal(&exact_lhs, &exact_rhs, exact_nbits));
    try std.testing.expect(bitmap.bitmap_equal(&exact_lhs, &exact_rhs, exact_nbits));

    const tail_nbits = bitmap.bits_per_long + 5;
    const tail_lhs = [_]bitmap.Word{
        0b1010,
        (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 9),
    };
    const tail_rhs = [_]bitmap.Word{
        0b1010,
        (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 11),
    };
    var and_dst = [_]bitmap.Word{ 0, 0 };
    var andnot_dst = [_]bitmap.Word{ 0, 0 };

    try std.testing.expect(bitmap.equal(&tail_lhs, &tail_rhs, tail_nbits));
    try std.testing.expect(bitmap.intersects(&tail_lhs, &tail_rhs, tail_nbits));
    try std.testing.expect(bitmap.subset(&tail_lhs, &tail_rhs, tail_nbits));

    try std.testing.expect(bitmap.andBits(&and_dst, &tail_lhs, &tail_rhs, tail_nbits));
    try std.testing.expectEqualSlices(bitmap.Word, &[_]bitmap.Word{ 0b1010, @as(bitmap.Word, 1) << 3 }, &and_dst);

    try std.testing.expect(!bitmap.andNotBits(&andnot_dst, &tail_lhs, &tail_rhs, tail_nbits));
    try std.testing.expectEqualSlices(bitmap.Word, &[_]bitmap.Word{ 0, 0 }, &andnot_dst);
}

test "phase1 bitmap tail clamp replay keeps weighted helpers scoped to the caller window" {
    const nbits = bitmap.bits_per_long + 5;
    const or_lhs = [_]bitmap.Word{
        0,
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 8),
    };
    const or_rhs = [_]bitmap.Word{
        0,
        (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 9),
    };
    var or_dst = [_]bitmap.Word{ 0, 0 };

    try std.testing.expectEqual(@as(usize, 2), bitmap.weightedOr(&or_dst, &or_lhs, &or_rhs, nbits));
    try std.testing.expectEqual(@as(usize, 2), bitmap.bitmap_weighted_or(&or_dst, &or_lhs, &or_rhs, nbits));
    try std.testing.expectEqual(@as(bitmap.Word, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 8) | (@as(bitmap.Word, 1) << 9)), or_dst[1]);
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&or_dst, nbits));

    const xor_lhs = [_]bitmap.Word{
        0,
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 8),
    };
    const xor_rhs = [_]bitmap.Word{
        0,
        (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 9),
    };
    var xor_dst = [_]bitmap.Word{ 0, 0 };
    var and_dst = [_]bitmap.Word{ 0, 0 };
    var andnot_dst = [_]bitmap.Word{ 0, 0 };

    try std.testing.expectEqual(@as(usize, 2), bitmap.weightedXor(&xor_dst, &xor_lhs, &xor_rhs, nbits));
    try std.testing.expectEqual(@as(usize, 2), bitmap.bitmap_weighted_xor(&xor_dst, &xor_lhs, &xor_rhs, nbits));
    try std.testing.expect(bitmap.andBits(&and_dst, &xor_lhs, &xor_rhs, nbits));
    try std.testing.expectEqual(@as(usize, 1), bitmap.weight(&and_dst, nbits));
    try std.testing.expect(bitmap.andNotBits(&andnot_dst, &xor_lhs, &xor_rhs, nbits));
    try std.testing.expectEqual(@as(usize, 1), bitmap.weight(&andnot_dst, nbits));
}

test "phase1 bitmap tail clamp replay keeps complement and formatting bounded to in-range bits" {
    const nbits = bitmap.bits_per_long + 8;
    const src = [_]bitmap.Word{
        0b1010,
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 7) | (@as(bitmap.Word, 1) << 10),
    };
    var complemented = [_]bitmap.Word{ 0, 0 };

    bitmap.bitmap_complement(&complemented, &src, nbits);
    try std.testing.expectEqual(~@as(bitmap.Word, 0b1010), complemented[0]);
    try std.testing.expectEqual((~src[1]) & bitmap.lastWordMask(nbits), complemented[1]);

    var map = [_]bitmap.Word{ 0, 0 };
    bitmap.bitmap_set(&map, bitmap.bits_per_long - 2, 5);
    bitmap.bitmap_set(&map, bitmap.bits_per_long + 6, 1);

    var full_buffer: [64]u8 = undefined;
    const full_len = bitmap.bitmap_scnprintf(&map, nbits, &full_buffer);

    var expected: [32]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "{d}-{d},{d}",
        .{ bitmap.bits_per_long - 2, bitmap.bits_per_long + 2, bitmap.bits_per_long + 6 },
    );
    try std.testing.expectEqualStrings(expected_text, full_buffer[0..full_len]);

    var terminator_only = [_]u8{0xaa};
    const tiny_len = bitmap.bitmap_scnprintf(&map, nbits, terminator_only[0..1]);
    try std.testing.expectEqual(@as(usize, 0), tiny_len);
    try std.testing.expectEqual(@as(u8, 0), terminator_only[0]);
}
