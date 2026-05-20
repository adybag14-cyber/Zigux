const std = @import("std");
const bitmap = @import("bitmap");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "phase1 bitmap tail-state replay keeps logical aliases aligned on partial tails" {
    const nbits = bits_per_long + 5;
    const in_range_tail = @as(Word, 1) << 3;
    const out_of_range_lhs = @as(Word, 1) << 9;
    const out_of_range_rhs = @as(Word, 1) << 11;

    const lhs = [_]Word{ 0b1010, in_range_tail | out_of_range_lhs };
    const rhs = [_]Word{ 0b1010, in_range_tail | out_of_range_rhs };
    const outside_only = [_]Word{ 0, out_of_range_lhs };
    const zero_tail = [_]Word{ 0, 0 };

    try std.testing.expect(bitmap.equal(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_equal(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.intersects(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.subset(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&lhs, &rhs, nbits));

    try std.testing.expect(bitmap.equal(&outside_only, &zero_tail, nbits));
    try std.testing.expect(bitmap.bitmap_equal(&outside_only, &zero_tail, nbits));
    try std.testing.expect(!bitmap.intersects(&outside_only, &outside_only, nbits));
    try std.testing.expect(!bitmap.bitmap_intersects(&outside_only, &outside_only, nbits));
    try std.testing.expect(bitmap.subset(&outside_only, &zero_tail, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&outside_only, &zero_tail, nbits));
}

test "phase1 bitmap tail-state replay keeps and/andnot aliases masked to the declared window" {
    const nbits = bits_per_long + 5;
    const lhs = [_]Word{ 0b1010, (@as(Word, 1) << 3) | (@as(Word, 1) << 9) };
    const rhs = [_]Word{ 0b1010, (@as(Word, 1) << 11) };

    var direct_and = [_]Word{ ~@as(Word, 0), ~@as(Word, 0) };
    var alias_and = [_]Word{ ~@as(Word, 0), ~@as(Word, 0) };
    try std.testing.expect(bitmap.andBits(&direct_and, &lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_and(&alias_and, &lhs, &rhs, nbits));
    try std.testing.expectEqualSlices(Word, &direct_and, &alias_and);
    try std.testing.expectEqualSlices(Word, &[_]Word{ 0b1010, 0 }, &direct_and);

    var direct_andnot = [_]Word{ ~@as(Word, 0), ~@as(Word, 0) };
    var alias_andnot = [_]Word{ ~@as(Word, 0), ~@as(Word, 0) };
    try std.testing.expect(bitmap.andNotBits(&direct_andnot, &lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_andnot(&alias_andnot, &lhs, &rhs, nbits));
    try std.testing.expectEqualSlices(Word, &direct_andnot, &alias_andnot);
    try std.testing.expectEqualSlices(Word, &[_]Word{ 0, @as(Word, 1) << 3 }, &direct_andnot);

    const outside_only = [_]Word{ 0, (@as(Word, 1) << 9) | (@as(Word, 1) << 11) };
    try std.testing.expect(!bitmap.andBits(&direct_and, &outside_only, &outside_only, nbits));
    try std.testing.expect(!bitmap.bitmap_and(&alias_and, &outside_only, &outside_only, nbits));
    try std.testing.expectEqualSlices(Word, &[_]Word{ 0, 0 }, &direct_and);
    try std.testing.expectEqualSlices(Word, &direct_and, &alias_and);
}

test "phase1 bitmap tail-state replay keeps zero-width aliases explicit" {
    const lhs = [_]Word{~@as(Word, 0)};
    const rhs = [_]Word{0x1234};

    var and_dst = [_]Word{0x55aa};
    var and_alias = [_]Word{0x55aa};
    var andnot_dst = [_]Word{0xaa55};
    var andnot_alias = [_]Word{0xaa55};

    try std.testing.expect(!bitmap.andBits(and_dst[0..0], lhs[0..0], rhs[0..0], 0));
    try std.testing.expect(!bitmap.bitmap_and(and_alias[0..0], lhs[0..0], rhs[0..0], 0));
    try std.testing.expectEqualSlices(Word, &and_dst, &and_alias);

    try std.testing.expect(!bitmap.andNotBits(andnot_dst[0..0], lhs[0..0], rhs[0..0], 0));
    try std.testing.expect(!bitmap.bitmap_andnot(andnot_alias[0..0], lhs[0..0], rhs[0..0], 0));
    try std.testing.expectEqualSlices(Word, &andnot_dst, &andnot_alias);

    try std.testing.expect(bitmap.empty(lhs[0..0], 0));
    try std.testing.expect(bitmap.bitmap_empty(lhs[0..0], 0));
    try std.testing.expect(bitmap.full(lhs[0..0], 0));
    try std.testing.expect(bitmap.bitmap_full(lhs[0..0], 0));
    try std.testing.expectEqual(@as(usize, 0), bitmap.weight(lhs[0..0], 0));
    try std.testing.expectEqual(@as(usize, 0), bitmap.bitmap_weight(lhs[0..0], 0));
    try std.testing.expect(bitmap.equal(lhs[0..0], rhs[0..0], 0));
    try std.testing.expect(bitmap.bitmap_equal(lhs[0..0], rhs[0..0], 0));
    try std.testing.expect(!bitmap.intersects(lhs[0..0], rhs[0..0], 0));
    try std.testing.expect(!bitmap.bitmap_intersects(lhs[0..0], rhs[0..0], 0));
    try std.testing.expect(bitmap.subset(lhs[0..0], rhs[0..0], 0));
    try std.testing.expect(bitmap.bitmap_subset(lhs[0..0], rhs[0..0], 0));
}
