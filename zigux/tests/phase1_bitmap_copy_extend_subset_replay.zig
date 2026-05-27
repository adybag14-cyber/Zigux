const std = @import("std");
const bitmap = @import("bitmap");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "bitmap copyAndExtend masks copied tail bits and clears extension words" {
    const count = bits_per_long + 5;
    const size = bits_per_long * 3 + 9;

    const src = [_]Word{
        ~@as(Word, 0),
        (@as(Word, 1) << 2) | (@as(Word, 1) << 4) | (@as(Word, 1) << 11) | (@as(Word, 1) << 17),
    };
    var dst = [_]Word{
        ~@as(Word, 0),
        ~@as(Word, 0),
        ~@as(Word, 0),
        ~@as(Word, 0),
    };

    bitmap.copyAndExtend(&dst, &src, count, size);

    try std.testing.expectEqual(src[0], dst[0]);
    try std.testing.expectEqual(src[1] & bitmap.lastWordMask(count), dst[1]);
    try std.testing.expectEqual(@as(Word, 0), dst[2]);
    try std.testing.expectEqual(@as(Word, 0), dst[3]);
    try std.testing.expectEqual(@as(usize, bits_per_long + 2), bitmap.weight(&dst, size));
    try std.testing.expect(bitmap.empty(dst[2..], bits_per_long * 2));

    var alias_dst = [_]Word{
        ~@as(Word, 0),
        ~@as(Word, 0),
        ~@as(Word, 0),
        ~@as(Word, 0),
    };
    bitmap.bitmap_copy_and_extend(&alias_dst, &src, count, size);
    try std.testing.expectEqualSlices(Word, &dst, &alias_dst);
}

test "bitmap equal subset and intersects ignore bits beyond nbits" {
    const nbits = bits_per_long + 5;

    const equal_lhs = [_]Word{
        (@as(Word, 1) << 1) | (@as(Word, 1) << 9),
        (@as(Word, 1) << 2) | (@as(Word, 1) << 17),
    };
    const equal_rhs = [_]Word{
        (@as(Word, 1) << 1) | (@as(Word, 1) << 9),
        (@as(Word, 1) << 2) | (@as(Word, 1) << 29),
    };
    try std.testing.expect(bitmap.equal(&equal_lhs, &equal_rhs, nbits));
    try std.testing.expect(bitmap.bitmap_equal(&equal_lhs, &equal_rhs, nbits));

    const subset_lhs = [_]Word{
        (@as(Word, 1) << 4),
        (@as(Word, 1) << 1) | (@as(Word, 1) << 20),
    };
    const subset_rhs = [_]Word{
        (@as(Word, 1) << 4) | (@as(Word, 1) << 12),
        (@as(Word, 1) << 1) | (@as(Word, 1) << 27),
    };
    try std.testing.expect(bitmap.subset(&subset_lhs, &subset_rhs, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&subset_lhs, &subset_rhs, nbits));

    const outside_only_lhs = [_]Word{ 0, @as(Word, 1) << 12 };
    const outside_only_rhs = [_]Word{ 0, @as(Word, 1) << 18 };
    try std.testing.expect(!bitmap.intersects(&outside_only_lhs, &outside_only_rhs, nbits));
    try std.testing.expect(!bitmap.bitmap_intersects(&outside_only_lhs, &outside_only_rhs, nbits));

    const valid_overlap_rhs = [_]Word{ 0, @as(Word, 1) << 3 };
    const valid_overlap_lhs = [_]Word{ 0, (@as(Word, 1) << 3) | (@as(Word, 1) << 18) };
    try std.testing.expect(bitmap.intersects(&valid_overlap_lhs, &valid_overlap_rhs, nbits));
}
