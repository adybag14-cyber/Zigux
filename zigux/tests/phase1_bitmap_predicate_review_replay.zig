const std = @import("std");
const bitmap = @import("bitmap");

test "phase 1 bitmap predicate review replay keeps exact-word equality and tail masking aligned" {
    const exact_nbits = bitmap.bits_per_long;
    const exact_lhs = [_]bitmap.Word{ 0b1011, @as(bitmap.Word, 1) << 7 };
    const exact_rhs = [_]bitmap.Word{ 0b1011, @as(bitmap.Word, 1) << 13 };
    const exact_changed = [_]bitmap.Word{ 0b1001, exact_lhs[1] };

    try std.testing.expect(bitmap.equal(&exact_lhs, &exact_rhs, exact_nbits));
    try std.testing.expect(bitmap.bitmap_equal(&exact_lhs, &exact_rhs, exact_nbits));
    try std.testing.expect(!bitmap.equal(&exact_lhs, &exact_changed, exact_nbits));

    const tail_nbits = bitmap.bits_per_long + 5;
    const in_range_tail = @as(bitmap.Word, 1) << 3;
    const out_of_range_lhs = @as(bitmap.Word, 1) << 9;
    const out_of_range_rhs = @as(bitmap.Word, 1) << 11;
    const lhs = [_]bitmap.Word{ 0b1010, in_range_tail | out_of_range_lhs };
    const rhs = [_]bitmap.Word{ 0b1010, in_range_tail | out_of_range_rhs };
    var and_dst = [_]bitmap.Word{ ~@as(bitmap.Word, 0), ~@as(bitmap.Word, 0) };
    var andnot_dst = [_]bitmap.Word{ ~@as(bitmap.Word, 0), ~@as(bitmap.Word, 0) };

    try std.testing.expect(bitmap.equal(&lhs, &rhs, tail_nbits));
    try std.testing.expect(bitmap.bitmap_equal(&lhs, &rhs, tail_nbits));
    try std.testing.expect(bitmap.intersects(&lhs, &rhs, tail_nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&lhs, &rhs, tail_nbits));
    try std.testing.expect(bitmap.subset(&lhs, &rhs, tail_nbits));
    try std.testing.expect(bitmap.bitmap_subset(&lhs, &rhs, tail_nbits));

    try std.testing.expect(bitmap.andBits(&and_dst, &lhs, &rhs, tail_nbits));
    try std.testing.expectEqualSlices(
        bitmap.Word,
        &[_]bitmap.Word{ 0b1010, in_range_tail },
        &and_dst,
    );

    try std.testing.expect(!bitmap.andNotBits(&andnot_dst, &lhs, &rhs, tail_nbits));
    try std.testing.expectEqualSlices(bitmap.Word, &[_]bitmap.Word{ 0, 0 }, &andnot_dst);
}

test "phase 1 bitmap predicate review replay keeps complement tails and zero-bit alias no-ops explicit" {
    const nbits = bitmap.bits_per_long + 5;
    const src = [_]bitmap.Word{
        0b1010,
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 7) | (@as(bitmap.Word, 1) << 10),
    };
    var direct = [_]bitmap.Word{ 0, 0 };
    var alias = [_]bitmap.Word{ 0, 0 };

    bitmap.complement(&direct, &src, nbits);
    bitmap.bitmap_complement(&alias, &src, nbits);
    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);
    try std.testing.expectEqual(~@as(bitmap.Word, 0b1010), direct[0]);
    try std.testing.expectEqual((~src[1]) & bitmap.lastWordMask(nbits), direct[1]);

    const zero_lhs = [_]bitmap.Word{~@as(bitmap.Word, 0)};
    const zero_rhs = [_]bitmap.Word{0x1234};
    var zero_dst = [_]bitmap.Word{0x55aa};
    var buffer = [_]u8{ 0xcc, 0xcc, 0xcc };

    bitmap.bitmap_zero(zero_dst[0..0], 0);
    try std.testing.expectEqual(@as(bitmap.Word, 0x55aa), zero_dst[0]);

    bitmap.bitmap_or(zero_dst[0..0], zero_lhs[0..0], zero_rhs[0..0], 0);
    try std.testing.expectEqual(@as(bitmap.Word, 0x55aa), zero_dst[0]);
    bitmap.bitmap_xor(zero_dst[0..0], zero_lhs[0..0], zero_rhs[0..0], 0);
    try std.testing.expectEqual(@as(bitmap.Word, 0x55aa), zero_dst[0]);
    bitmap.bitmap_copy(zero_dst[0..0], zero_rhs[0..0], 0);
    try std.testing.expectEqual(@as(bitmap.Word, 0x55aa), zero_dst[0]);

    try std.testing.expectEqual(@as(usize, 0), bitmap.bitmap_weighted_or(zero_dst[0..0], zero_lhs[0..0], zero_rhs[0..0], 0));
    try std.testing.expectEqual(@as(usize, 0), bitmap.bitmap_weighted_xor(zero_dst[0..0], zero_lhs[0..0], zero_rhs[0..0], 0));
    try std.testing.expect(bitmap.bitmap_empty(zero_lhs[0..0], 0));
    try std.testing.expect(bitmap.bitmap_full(zero_lhs[0..0], 0));
    try std.testing.expectEqual(@as(usize, 0), bitmap.bitmap_weight(zero_lhs[0..0], 0));
    try std.testing.expect(bitmap.bitmap_equal(zero_lhs[0..0], zero_rhs[0..0], 0));
    try std.testing.expect(!bitmap.bitmap_intersects(zero_lhs[0..0], zero_rhs[0..0], 0));
    try std.testing.expect(bitmap.bitmap_subset(zero_lhs[0..0], zero_rhs[0..0], 0));

    const rendered = bitmap.bitmap_scnprintf(&[_]bitmap.Word{}, 0, &buffer);
    try std.testing.expectEqual(@as(usize, 0), rendered);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xcc, 0xcc, 0xcc }, &buffer);
}
