const std = @import("std");
const bitmap = @import("bitmap");

const Word = bitmap.Word;

test "phase1 bitmap relation helpers clamp shared and lhs-only tail weights" {
    const nbits = bitmap.bits_per_long + 5;
    const lhs = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 3) | (@as(Word, 1) << 8) };
    const rhs = [_]Word{ 0, (@as(Word, 1) << 3) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9) };

    try std.testing.expectEqual(@as(usize, 1), bitmap.weightAnd(&lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 1), bitmap.bitmap_weight_and(&lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 1), bitmap.weightAndNot(&lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 1), bitmap.bitmap_weight_andnot(&lhs, &rhs, nbits));

    var direct_and = [_]Word{ ~@as(Word, 0), ~@as(Word, 0) };
    var alias_and = [_]Word{ 0, 0 };
    try std.testing.expect(bitmap.andBits(&direct_and, &lhs, &rhs, nbits));
    try std.testing.expectEqual(bitmap.andBits(&direct_and, &lhs, &rhs, nbits), bitmap.bitmap_and(&alias_and, &lhs, &rhs, nbits));
    try std.testing.expectEqualSlices(Word, &direct_and, &alias_and);
    try std.testing.expectEqualSlices(Word, &[_]Word{ 0, @as(Word, 1) << 3 }, &direct_and);

    var direct_andnot = [_]Word{ ~@as(Word, 0), ~@as(Word, 0) };
    var alias_andnot = [_]Word{ 0, 0 };
    try std.testing.expect(bitmap.andNotBits(&direct_andnot, &lhs, &rhs, nbits));
    try std.testing.expectEqual(
        bitmap.andNotBits(&direct_andnot, &lhs, &rhs, nbits),
        bitmap.bitmap_andnot(&alias_andnot, &lhs, &rhs, nbits),
    );
    try std.testing.expectEqualSlices(Word, &direct_andnot, &alias_andnot);
    try std.testing.expectEqualSlices(Word, &[_]Word{ 0, @as(Word, 1) << 1 }, &direct_andnot);
}

test "phase1 bitmap relation aliases ignore storage beyond an exact word boundary" {
    const nbits = bitmap.bits_per_long;
    const lhs = [_]Word{ 0b1011, @as(Word, 1) << 7 };
    const rhs = [_]Word{ 0b1011, @as(Word, 1) << 13 };
    const superset = [_]Word{ 0b1111, 0 };
    const changed = [_]Word{ 0b1001, rhs[1] };

    try std.testing.expect(bitmap.equal(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_equal(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.intersects(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.subset(&lhs, &superset, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&lhs, &superset, nbits));

    try std.testing.expect(!bitmap.equal(&lhs, &changed, nbits));
    try std.testing.expect(!bitmap.bitmap_equal(&lhs, &changed, nbits));
    try std.testing.expect(!bitmap.subset(&superset, &lhs, nbits));
    try std.testing.expect(!bitmap.bitmap_subset(&superset, &lhs, nbits));
}

test "phase1 bitmap relation helpers keep zero-sized caller views neutral" {
    const populated = [_]Word{~@as(Word, 0)};

    try std.testing.expectEqual(@as(usize, 0), bitmap.weightAnd(populated[0..0], populated[0..0], 0));
    try std.testing.expectEqual(@as(usize, 0), bitmap.bitmap_weight_and(populated[0..0], populated[0..0], 0));
    try std.testing.expectEqual(@as(usize, 0), bitmap.weightAndNot(populated[0..0], populated[0..0], 0));
    try std.testing.expectEqual(@as(usize, 0), bitmap.bitmap_weight_andnot(populated[0..0], populated[0..0], 0));

    try std.testing.expect(bitmap.equal(populated[0..0], populated[0..0], 0));
    try std.testing.expect(bitmap.bitmap_equal(populated[0..0], populated[0..0], 0));
    try std.testing.expect(!bitmap.intersects(populated[0..0], populated[0..0], 0));
    try std.testing.expect(!bitmap.bitmap_intersects(populated[0..0], populated[0..0], 0));
    try std.testing.expect(bitmap.subset(populated[0..0], populated[0..0], 0));
    try std.testing.expect(bitmap.bitmap_subset(populated[0..0], populated[0..0], 0));
}
