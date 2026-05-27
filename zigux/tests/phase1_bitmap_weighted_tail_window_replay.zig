const std = @import("std");
const bitmap = @import("bitmap");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "phase1 bitmap weighted helpers clamp counts to the declared tail window" {
    const nbits = bits_per_long + 5;

    const or_lhs = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 8) };
    const or_rhs = [_]Word{ 0, (@as(Word, 1) << 3) | (@as(Word, 1) << 9) };
    var weighted_or_direct = [_]Word{ 0, 0 };
    var weighted_or_alias = [_]Word{ 0, 0 };

    try std.testing.expectEqual(
        @as(usize, 2),
        bitmap.weightedOr(&weighted_or_direct, &or_lhs, &or_rhs, nbits),
    );
    try std.testing.expectEqual(
        @as(usize, 2),
        bitmap.bitmap_weighted_or(&weighted_or_alias, &or_lhs, &or_rhs, nbits),
    );
    try std.testing.expectEqualSlices(Word, &weighted_or_direct, &weighted_or_alias);
    try std.testing.expectEqual(
        (@as(Word, 1) << 1) | (@as(Word, 1) << 3),
        weighted_or_direct[1] & bitmap.lastWordMask(nbits),
    );
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&weighted_or_direct, nbits));

    const xor_lhs = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 3) | (@as(Word, 1) << 8) };
    const xor_rhs = [_]Word{ 0, (@as(Word, 1) << 3) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9) };
    var weighted_xor_direct = [_]Word{ 0, 0 };
    var weighted_xor_alias = [_]Word{ 0, 0 };

    try std.testing.expectEqual(
        @as(usize, 2),
        bitmap.weightedXor(&weighted_xor_direct, &xor_lhs, &xor_rhs, nbits),
    );
    try std.testing.expectEqual(
        @as(usize, 2),
        bitmap.bitmap_weighted_xor(&weighted_xor_alias, &xor_lhs, &xor_rhs, nbits),
    );
    try std.testing.expectEqualSlices(Word, &weighted_xor_direct, &weighted_xor_alias);
    try std.testing.expectEqual(
        (@as(Word, 1) << 1) | (@as(Word, 1) << 4),
        weighted_xor_direct[1] & bitmap.lastWordMask(nbits),
    );
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&weighted_xor_direct, nbits));

    const and_lhs = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 3) | (@as(Word, 1) << 8) };
    const and_rhs = [_]Word{ 0, (@as(Word, 1) << 3) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9) };
    var and_direct = [_]Word{ 0, 0 };
    var and_alias = [_]Word{ 0, 0 };
    try std.testing.expect(bitmap.andBits(&and_direct, &and_lhs, &and_rhs, nbits));
    try std.testing.expect(bitmap.bitmap_and(&and_alias, &and_lhs, &and_rhs, nbits));
    try std.testing.expectEqualSlices(Word, &and_direct, &and_alias);
    try std.testing.expectEqual((@as(Word, 1) << 3), and_direct[1] & bitmap.lastWordMask(nbits));

    const andnot_lhs = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 3) | (@as(Word, 1) << 8) };
    const andnot_rhs = [_]Word{ 0, (@as(Word, 1) << 3) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9) };
    var andnot_direct = [_]Word{ 0, 0 };
    var andnot_alias = [_]Word{ 0, 0 };
    try std.testing.expect(bitmap.andNotBits(&andnot_direct, &andnot_lhs, &andnot_rhs, nbits));
    try std.testing.expect(bitmap.bitmap_andnot(&andnot_alias, &andnot_lhs, &andnot_rhs, nbits));
    try std.testing.expectEqualSlices(Word, &andnot_direct, &andnot_alias);
    try std.testing.expectEqual((@as(Word, 1) << 1), andnot_direct[1] & bitmap.lastWordMask(nbits));
}

test "phase1 bitmap tail-window replay keeps complement and copy extension reviewable" {
    const count = bits_per_long + 5;
    const size = bits_per_long * 3;
    const src = [_]Word{ ~@as(Word, 0), ~@as(Word, 0), 0 };

    var copy_clear_tail = [_]Word{ 0, 0 };
    bitmap.copyClearTail(&copy_clear_tail, src[0..2], count);
    try std.testing.expectEqual(~@as(Word, 0), copy_clear_tail[0]);
    try std.testing.expectEqual(bitmap.lastWordMask(count), copy_clear_tail[1]);

    var copy_and_extend = [_]Word{ ~@as(Word, 0), ~@as(Word, 0), ~@as(Word, 0) };
    bitmap.copyAndExtend(&copy_and_extend, src[0..2], count, size);
    try std.testing.expectEqual(~@as(Word, 0), copy_and_extend[0]);
    try std.testing.expectEqual(bitmap.lastWordMask(count), copy_and_extend[1]);
    try std.testing.expectEqual(@as(Word, 0), copy_and_extend[2]);

    const complement_src = [_]Word{
        0b1010,
        (@as(Word, 1) << 1) | (@as(Word, 1) << 7) | (@as(Word, 1) << 10),
    };
    var direct = [_]Word{ 0, 0 };
    var alias = [_]Word{ 0, 0 };
    bitmap.complement(&direct, &complement_src, count);
    bitmap.bitmap_complement(&alias, &complement_src, count);

    try std.testing.expectEqualSlices(Word, &direct, &alias);
    try std.testing.expectEqual(~@as(Word, 0b1010), direct[0]);
    try std.testing.expectEqual((~complement_src[1]) & bitmap.lastWordMask(count), direct[1]);
}
