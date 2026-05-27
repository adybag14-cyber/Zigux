const std = @import("std");
const bitmap = @import("bitmap");

test "phase 1 bitmap predicate-range replay keeps cross-word range edits aligned" {
    const start = bitmap.bits_per_long - 2;
    const len = bitmap.bits_per_long + 5;
    var map = [_]bitmap.Word{ 0, 0, 0, 0 };

    bitmap.bitmap_set(&map, start, len);
    try std.testing.expectEqual(bitmap.firstWordMask(start), map[0]);
    try std.testing.expectEqual(~@as(bitmap.Word, 0), map[1]);
    try std.testing.expectEqual(bitmap.lastWordMask(start + len), map[2]);
    try std.testing.expectEqual(@as(bitmap.Word, 0), map[3]);

    bitmap.bitmap_clear(&map, start, len);
    try std.testing.expectEqualSlices(bitmap.Word, &[_]bitmap.Word{ 0, 0, 0, 0 }, &map);
}

test "phase 1 bitmap predicate-range replay keeps tail-masked predicates and results explicit" {
    const nbits = bitmap.bits_per_long + 5;
    const equal_lhs = [_]bitmap.Word{ 0b1010, (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << 9) };
    const equal_rhs = [_]bitmap.Word{ 0b1010, (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << 11) };
    const outside_only = [_]bitmap.Word{ 0, @as(bitmap.Word, 1) << 9 };
    const and_lhs = [_]bitmap.Word{ 0b1010, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 9) };
    const and_rhs = [_]bitmap.Word{ 0b1010, (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 11) };
    var and_words = [_]bitmap.Word{ ~@as(bitmap.Word, 0), ~@as(bitmap.Word, 0) };
    var andnot_words = [_]bitmap.Word{ ~@as(bitmap.Word, 0), ~@as(bitmap.Word, 0) };

    try std.testing.expect(bitmap.bitmap_equal(&equal_lhs, &equal_rhs, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&equal_lhs, &equal_rhs, nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&equal_lhs, &equal_rhs, nbits));
    try std.testing.expect(bitmap.bitmap_equal(&outside_only, &[_]bitmap.Word{ 0, 0 }, nbits));
    try std.testing.expect(!bitmap.bitmap_intersects(&outside_only, &outside_only, nbits));

    try std.testing.expect(bitmap.bitmap_and(&and_words, &and_lhs, &and_rhs, nbits));
    try std.testing.expectEqualSlices(
        bitmap.Word,
        &[_]bitmap.Word{ 0b1010, @as(bitmap.Word, 1) << 3 },
        &and_words,
    );
    try std.testing.expectEqual(@as(usize, 3), bitmap.weight(&and_words, nbits));

    try std.testing.expect(bitmap.bitmap_andnot(&andnot_words, &and_lhs, &and_rhs, nbits));
    try std.testing.expectEqualSlices(
        bitmap.Word,
        &[_]bitmap.Word{ 0, @as(bitmap.Word, 1) << 1 },
        &andnot_words,
    );
    try std.testing.expectEqual(@as(usize, 1), bitmap.weight(&andnot_words, nbits));
}

test "phase 1 bitmap predicate-range replay keeps alias state helpers stable around tail noise" {
    const nbits = bitmap.bits_per_long + 5;
    const out_of_range_noise = (@as(bitmap.Word, 1) << 8) | (@as(bitmap.Word, 1) << 11);
    var map = [_]bitmap.Word{ 0, out_of_range_noise };

    try std.testing.expect(bitmap.bitmap_empty(&map, nbits));
    try std.testing.expect(!bitmap.bitmap_full(&map, nbits));
    try std.testing.expectEqual(@as(usize, 0), bitmap.bitmap_weight(&map, nbits));

    bitmap.bitmap_fill(&map, nbits);
    try std.testing.expect(bitmap.bitmap_full(&map, nbits));
    try std.testing.expectEqual(nbits, bitmap.bitmap_weight(&map, nbits));

    bitmap.bitmap_zero(&map, nbits);
    try std.testing.expect(bitmap.bitmap_empty(&map, nbits));
    try std.testing.expectEqual(@as(bitmap.Word, 0), map[0]);
    try std.testing.expectEqual(@as(bitmap.Word, 0), map[1]);
}