const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");

const Word = find_bit.Word;
const bits_per_long = find_bit.bits_per_long;

test "phase1 bitmap logic window masks partial tails across primary and Linux-style helpers" {
    const nbits = bits_per_long + 5;
    const lhs = [_]Word{ 0b101100, (@as(Word, 1) << 0) | (@as(Word, 1) << 2) | (@as(Word, 1) << 9) };
    const rhs = [_]Word{ 0b001111, (@as(Word, 1) << 1) | (@as(Word, 1) << 9) };

    var primary_or = [_]Word{ 0, 0 };
    var alias_or = [_]Word{ 0, 0 };
    bitmap.orBits(&primary_or, &lhs, &rhs, nbits);
    bitmap.bitmap_or(&alias_or, &lhs, &rhs, nbits);

    try std.testing.expectEqualSlices(Word, &primary_or, &alias_or);
    try std.testing.expectEqual(@as(Word, 0b101111), primary_or[0]);
    try std.testing.expectEqual(@as(Word, 0b111), primary_or[1] & bitmap.lastWordMask(nbits));

    const primary_or_weight = bitmap.weight(&primary_or, nbits);
    const alias_or_weight = bitmap.bitmap_weighted_or(&alias_or, &lhs, &rhs, nbits);
    try std.testing.expectEqual(primary_or_weight, alias_or_weight);
    try std.testing.expectEqual(@as(usize, 8), primary_or_weight);
}

test "phase1 bitmap and andnot aliases clamp partial tails without leaking caller garbage" {
    const nbits = bits_per_long + 5;
    const lhs = [_]Word{ 0b101100, (@as(Word, 1) << 0) | (@as(Word, 1) << 2) | (@as(Word, 1) << 9) };
    const rhs = [_]Word{ 0b001111, (@as(Word, 1) << 1) | (@as(Word, 1) << 9) };

    var primary_and = [_]Word{ ~@as(Word, 0), ~@as(Word, 0) };
    var alias_and = [_]Word{ 0, 0 };
    try std.testing.expectEqual(bitmap.andBits(&primary_and, &lhs, &rhs, nbits), bitmap.bitmap_and(&alias_and, &lhs, &rhs, nbits));
    try std.testing.expectEqualSlices(Word, &primary_and, &alias_and);
    try std.testing.expectEqual(@as(Word, 0b001100), primary_and[0]);
    try std.testing.expectEqual(@as(Word, 0), primary_and[1]);
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&primary_and, nbits));

    var primary_andnot = [_]Word{ ~@as(Word, 0), ~@as(Word, 0) };
    var alias_andnot = [_]Word{ 0, 0 };
    try std.testing.expectEqual(bitmap.andNotBits(&primary_andnot, &lhs, &rhs, nbits), bitmap.bitmap_andnot(&alias_andnot, &lhs, &rhs, nbits));
    try std.testing.expectEqualSlices(Word, &primary_andnot, &alias_andnot);
    try std.testing.expectEqual(@as(Word, 0b100000), primary_andnot[0]);
    try std.testing.expectEqual(@as(Word, 0b101), primary_andnot[1]);
    try std.testing.expectEqual(@as(usize, 3), bitmap.weight(&primary_andnot, nbits));
}
