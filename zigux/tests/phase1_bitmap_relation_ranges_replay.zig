const std = @import("std");
const bitmap = @import("bitmap");

test "phase1 bitmap exact-word relation helpers ignore trailing storage" {
    const nbits = bitmap.bits_per_long;
    const lhs = [_]bitmap.Word{ 0b10101, @as(bitmap.Word, 1) << 5 };
    const rhs = [_]bitmap.Word{ 0b10101, @as(bitmap.Word, 1) << 17 };
    const superset = [_]bitmap.Word{ 0b11101, @as(bitmap.Word, 1) << 29 };
    const disjoint = [_]bitmap.Word{ (@as(bitmap.Word, 1) << 9) | (@as(bitmap.Word, 1) << 11), ~@as(bitmap.Word, 0) };

    try std.testing.expect(bitmap.bitmap_equal(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&lhs, &superset, nbits));
    try std.testing.expect(!bitmap.bitmap_subset(&superset, &lhs, nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&lhs, &superset, nbits));
    try std.testing.expect(!bitmap.bitmap_intersects(&lhs, &disjoint, nbits));
}

test "phase1 bitmap range updates preserve subset and intersection transitions across a word boundary" {
    const nbits = bitmap.bits_per_long * 2 + 8;
    const start = bitmap.bits_per_long - 1;
    var witness = [_]bitmap.Word{ 0, 0, 0 };
    var superset = [_]bitmap.Word{ 0, 0, 0 };

    bitmap.bitmap_set(&witness, start, 4);
    bitmap.bitmap_set(&superset, start, 4);
    bitmap.bitmap_set(&superset, bitmap.bits_per_long + 4, 2);

    try std.testing.expect(bitmap.bitmap_subset(&witness, &superset, nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&witness, &superset, nbits));

    bitmap.bitmap_clear(&superset, bitmap.bits_per_long, 2);
    try std.testing.expect(!bitmap.bitmap_subset(&witness, &superset, nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&witness, &superset, nbits));

    bitmap.bitmap_clear(&superset, start, 1);
    bitmap.bitmap_clear(&superset, bitmap.bits_per_long + 2, 1);
    try std.testing.expect(!bitmap.bitmap_intersects(&witness, &superset, nbits));
}

test "phase1 bitmap tail-masked relation helpers ignore out-of-range tail bits" {
    const nbits = bitmap.bits_per_long + 5;
    const in_range_tail_bit = @as(bitmap.Word, 1) << 3;
    const out_of_range_tail_bit = @as(bitmap.Word, 1) << 11;

    const lhs = [_]bitmap.Word{ @as(bitmap.Word, 1) << 2, in_range_tail_bit | out_of_range_tail_bit };
    const rhs = [_]bitmap.Word{ @as(bitmap.Word, 1) << 2, in_range_tail_bit };
    const out_of_range_only = [_]bitmap.Word{ 0, out_of_range_tail_bit };

    try std.testing.expect(bitmap.bitmap_equal(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&rhs, &lhs, nbits));
    try std.testing.expect(!bitmap.bitmap_intersects(&rhs, &out_of_range_only, nbits));
}
