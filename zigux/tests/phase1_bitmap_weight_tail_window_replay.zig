const std = @import("std");
const bitmap = @import("bitmap");

const Word = bitmap.Word;

test "phase1 bitmap weighted or and xor clamp counts to the declared tail window" {
    const nbits = bitmap.bits_per_long + 5;
    const or_lhs = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 8) };
    const or_rhs = [_]Word{ 0, (@as(Word, 1) << 3) | (@as(Word, 1) << 9) };
    var direct_or = [_]Word{ 0, 0 };
    var alias_or = [_]Word{ 0, 0 };

    const direct_or_weight = bitmap.weightedOr(&direct_or, &or_lhs, &or_rhs, nbits);
    const alias_or_weight = bitmap.bitmap_weighted_or(&alias_or, &or_lhs, &or_rhs, nbits);
    try std.testing.expectEqual(@as(usize, 2), direct_or_weight);
    try std.testing.expectEqual(direct_or_weight, alias_or_weight);
    try std.testing.expectEqualSlices(Word, &direct_or, &alias_or);
    try std.testing.expectEqual(
        @as(Word, (@as(Word, 1) << 1) | (@as(Word, 1) << 3) | (@as(Word, 1) << 8) | (@as(Word, 1) << 9)),
        direct_or[1],
    );
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&direct_or, nbits));

    const xor_lhs = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 3) | (@as(Word, 1) << 8) };
    const xor_rhs = [_]Word{ 0, (@as(Word, 1) << 3) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9) };
    var direct_xor = [_]Word{ 0, 0 };
    var alias_xor = [_]Word{ 0, 0 };

    const direct_xor_weight = bitmap.weightedXor(&direct_xor, &xor_lhs, &xor_rhs, nbits);
    const alias_xor_weight = bitmap.bitmap_weighted_xor(&alias_xor, &xor_lhs, &xor_rhs, nbits);
    try std.testing.expectEqual(@as(usize, 2), direct_xor_weight);
    try std.testing.expectEqual(direct_xor_weight, alias_xor_weight);
    try std.testing.expectEqualSlices(Word, &direct_xor, &alias_xor);
    try std.testing.expectEqual(
        @as(Word, (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 8) | (@as(Word, 1) << 9)),
        direct_xor[1],
    );
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&direct_xor, nbits));
}

test "phase1 bitmap logical and andnot keep exact-word and tail windows aligned" {
    const exact_nbits = bitmap.bits_per_long;
    const exact_lhs = [_]Word{ 0b1011, (@as(Word, 1) << 3) | (@as(Word, 1) << 9) };
    const exact_rhs = [_]Word{ 0b0011, (@as(Word, 1) << 4) | (@as(Word, 1) << 9) };
    var direct_and = [_]Word{ 0, 0 };
    var alias_and = [_]Word{ 0, 0 };
    var direct_andnot = [_]Word{ 0, 0 };
    var alias_andnot = [_]Word{ 0, 0 };

    try std.testing.expect(bitmap.andBits(&direct_and, &exact_lhs, &exact_rhs, exact_nbits));
    try std.testing.expectEqual(
        bitmap.andBits(&direct_and, &exact_lhs, &exact_rhs, exact_nbits),
        bitmap.bitmap_and(&alias_and, &exact_lhs, &exact_rhs, exact_nbits),
    );
    try std.testing.expectEqualSlices(Word, &direct_and, &alias_and);
    try std.testing.expectEqual(@as(Word, 0b0011), direct_and[0]);
    try std.testing.expectEqual(@as(Word, 0), direct_and[1]);
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&direct_and, exact_nbits));

    try std.testing.expect(bitmap.andNotBits(&direct_andnot, &exact_lhs, &exact_rhs, exact_nbits));
    try std.testing.expectEqual(
        bitmap.andNotBits(&direct_andnot, &exact_lhs, &exact_rhs, exact_nbits),
        bitmap.bitmap_andnot(&alias_andnot, &exact_lhs, &exact_rhs, exact_nbits),
    );
    try std.testing.expectEqualSlices(Word, &direct_andnot, &alias_andnot);
    try std.testing.expectEqual(@as(Word, 0b1000), direct_andnot[0]);
    try std.testing.expectEqual(@as(Word, 0), direct_andnot[1]);
    try std.testing.expectEqual(@as(usize, 1), bitmap.weight(&direct_andnot, exact_nbits));

    const tail_nbits = bitmap.bits_per_long + 5;
    const tail_lhs = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 3) | (@as(Word, 1) << 8) };
    const tail_rhs = [_]Word{ 0, (@as(Word, 1) << 3) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9) };
    try std.testing.expect(bitmap.andBits(&direct_and, &tail_lhs, &tail_rhs, tail_nbits));
    try std.testing.expectEqual(@as(usize, 1), bitmap.weight(&direct_and, tail_nbits));
    try std.testing.expect(bitmap.andNotBits(&direct_andnot, &tail_lhs, &tail_rhs, tail_nbits));
    try std.testing.expectEqual(@as(usize, 1), bitmap.weight(&direct_andnot, tail_nbits));
}

test "phase1 bitmap weighted helpers leave zero-sized caller views untouched" {
    const populated = [_]Word{~@as(Word, 0)};
    var direct_or = [_]Word{0x55aa};
    var alias_or = [_]Word{0x55aa};
    var direct_xor = [_]Word{0xaa55};
    var alias_xor = [_]Word{0xaa55};

    try std.testing.expectEqual(
        @as(usize, 0),
        bitmap.weightedOr(direct_or[0..0], populated[0..0], populated[0..0], 0),
    );
    try std.testing.expectEqual(
        @as(usize, 0),
        bitmap.bitmap_weighted_or(alias_or[0..0], populated[0..0], populated[0..0], 0),
    );
    try std.testing.expectEqualSlices(Word, &direct_or, &alias_or);

    try std.testing.expectEqual(
        @as(usize, 0),
        bitmap.weightedXor(direct_xor[0..0], populated[0..0], populated[0..0], 0),
    );
    try std.testing.expectEqual(
        @as(usize, 0),
        bitmap.bitmap_weighted_xor(alias_xor[0..0], populated[0..0], populated[0..0], 0),
    );
    try std.testing.expectEqualSlices(Word, &direct_xor, &alias_xor);

    var direct_and = [_]Word{0x1234};
    var alias_and = [_]Word{0x1234};
    var direct_andnot = [_]Word{0x5678};
    var alias_andnot = [_]Word{0x5678};

    try std.testing.expectEqual(
        @as(bool, false),
        bitmap.andBits(direct_and[0..0], populated[0..0], populated[0..0], 0),
    );
    try std.testing.expectEqual(
        @as(bool, false),
        bitmap.bitmap_and(alias_and[0..0], populated[0..0], populated[0..0], 0),
    );
    try std.testing.expectEqualSlices(Word, &direct_and, &alias_and);

    try std.testing.expectEqual(
        @as(bool, false),
        bitmap.andNotBits(direct_andnot[0..0], populated[0..0], populated[0..0], 0),
    );
    try std.testing.expectEqual(
        @as(bool, false),
        bitmap.bitmap_andnot(alias_andnot[0..0], populated[0..0], populated[0..0], 0),
    );
    try std.testing.expectEqualSlices(Word, &direct_andnot, &alias_andnot);
}
