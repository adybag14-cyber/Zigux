const std = @import("std");
const bitmap = @import("bitmap");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "phase1 bitmap transform replay imports the live transform helpers" {
    try std.testing.expect(@hasDecl(bitmap, "bitmap_complement"));
    try std.testing.expect(@hasDecl(bitmap, "bitmap_weighted_xor"));
    try std.testing.expect(@hasDecl(bitmap, "bitmap_copy_and_extend"));
}

test "phase1 bitmap transform replay keeps complement and xor aliases aligned on partial tails" {
    const nbits = bits_per_long + 5;
    const lhs = [_]Word{
        0b10101,
        (@as(Word, 1) << 1) | (@as(Word, 1) << 3) | (@as(Word, 1) << 9),
    };
    const rhs = [_]Word{
        0b00111,
        (@as(Word, 1) << 3) | (@as(Word, 1) << 11),
    };

    var complement_direct = [_]Word{ 0, ~@as(Word, 0) };
    var complement_alias = [_]Word{ 0, ~@as(Word, 0) };
    bitmap.complement(&complement_direct, &lhs, nbits);
    bitmap.bitmap_complement(&complement_alias, &lhs, nbits);

    try std.testing.expectEqualSlices(Word, &complement_direct, &complement_alias);
    try std.testing.expectEqual(~lhs[0], complement_direct[0]);
    try std.testing.expectEqual(bitmap.lastWordMask(nbits) & ~lhs[1], complement_direct[1]);

    var xor_direct = [_]Word{ ~@as(Word, 0), ~@as(Word, 0) };
    var xor_alias = [_]Word{ ~@as(Word, 0), ~@as(Word, 0) };
    const direct_weight = bitmap.weightedXor(&xor_direct, &lhs, &rhs, nbits);
    const alias_weight = bitmap.bitmap_weighted_xor(&xor_alias, &lhs, &rhs, nbits);

    try std.testing.expectEqual(@as(usize, 3), direct_weight);
    try std.testing.expectEqual(direct_weight, alias_weight);
    try std.testing.expectEqual(direct_weight, bitmap.weight(&xor_direct, nbits));
    try std.testing.expectEqualSlices(Word, &xor_direct, &xor_alias);
    try std.testing.expectEqual(@as(Word, 0b10010), xor_direct[0]);
    try std.testing.expectEqual(
        (@as(Word, 1) << 1) | (@as(Word, 1) << 9) | (@as(Word, 1) << 11),
        xor_direct[1],
    );
}

test "phase1 bitmap transform replay keeps copy-and-extend aliases aligned across partial and aligned counts" {
    const partial_count = bits_per_long + 5;
    const size = bits_per_long * 3;
    const partial_src = [_]Word{ ~@as(Word, 0), ~@as(Word, 0), @as(Word, 1) << 7 };

    var partial_direct = [_]Word{ 0xaa55, 0xaa55, 0xaa55 };
    var partial_alias = [_]Word{ 0xaa55, 0xaa55, 0xaa55 };
    bitmap.copyAndExtend(&partial_direct, partial_src[0..2], partial_count, size);
    bitmap.bitmap_copy_and_extend(&partial_alias, partial_src[0..2], partial_count, size);

    try std.testing.expectEqualSlices(Word, &partial_direct, &partial_alias);
    try std.testing.expectEqual(~@as(Word, 0), partial_direct[0]);
    try std.testing.expectEqual(bitmap.lastWordMask(partial_count), partial_direct[1]);
    try std.testing.expectEqual(@as(Word, 0), partial_direct[2]);

    const aligned_count = bits_per_long * 2;
    const aligned_src = [_]Word{ 0x55aa, 0xaa55, ~@as(Word, 0) };

    var aligned_direct = [_]Word{ ~@as(Word, 0), ~@as(Word, 0), ~@as(Word, 0) };
    var aligned_alias = [_]Word{ ~@as(Word, 0), ~@as(Word, 0), ~@as(Word, 0) };
    bitmap.copyAndExtend(&aligned_direct, aligned_src[0..2], aligned_count, size);
    bitmap.bitmap_copy_and_extend(&aligned_alias, aligned_src[0..2], aligned_count, size);

    try std.testing.expectEqualSlices(Word, &aligned_direct, &aligned_alias);
    try std.testing.expectEqual(aligned_src[0], aligned_direct[0]);
    try std.testing.expectEqual(aligned_src[1], aligned_direct[1]);
    try std.testing.expectEqual(@as(Word, 0), aligned_direct[2]);
}
