const std = @import("std");
const bitmap = @import("bitmap");

fn expectWordSlice(actual: []const bitmap.Word, expected: []const bitmap.Word) !void {
    try std.testing.expectEqual(expected.len, actual.len);
    for (actual, expected) |value, expected_value| {
        try std.testing.expectEqual(expected_value, value);
    }
}

test "phase 1 bitmap complement and replace clamp tail bits across aliases" {
    const nbits = bitmap.bits_per_long + 5;
    const tail_mask = bitmap.lastWordMask(nbits);

    const src = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << (bitmap.bits_per_long - 1)),
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 10),
    };

    var complemented = [_]bitmap.Word{ 0, 0 };
    bitmap.complement(&complemented, &src, nbits);
    try expectWordSlice(&complemented, &[_]bitmap.Word{
        ~src[0],
        (~src[1]) & tail_mask,
    });

    var complemented_alias = [_]bitmap.Word{ 0, 0 };
    bitmap.bitmap_complement(&complemented_alias, &src, nbits);
    try expectWordSlice(&complemented_alias, &complemented);

    var complemented_low_level = [_]bitmap.Word{ 0, 0 };
    bitmap.__bitmap_complement(&complemented_low_level, &src, nbits);
    try expectWordSlice(&complemented_low_level, &complemented);

    const old = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 0) | (@as(bitmap.Word, 1) << 5),
        (@as(bitmap.Word, 1) << 0) | (@as(bitmap.Word, 1) << 4),
    };
    const new = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 5),
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 9),
    };
    const mask = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 5),
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 9),
    };

    var replaced = [_]bitmap.Word{ 0, 0 };
    bitmap.replace(&replaced, &old, &new, &mask, nbits);
    try expectWordSlice(&replaced, &[_]bitmap.Word{
        (@as(bitmap.Word, 1) << 0) | (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 5),
        (@as(bitmap.Word, 1) << 0) | (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4),
    });

    var replaced_alias = [_]bitmap.Word{ 0, 0 };
    bitmap.bitmap_replace(&replaced_alias, &old, &new, &mask, nbits);
    try expectWordSlice(&replaced_alias, &replaced);

    var replaced_low_level = [_]bitmap.Word{ 0, 0 };
    bitmap.__bitmap_replace(&replaced_low_level, &old, &new, &mask, nbits);
    try expectWordSlice(&replaced_low_level, &replaced);
}

test "phase 1 bitmap weighted ops and predicates ignore tail bits beyond nbits" {
    const nbits = bitmap.bits_per_long + 3;

    const lhs = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 0) | (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << (bitmap.bits_per_long - 1)),
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 7),
    };
    const rhs = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << (bitmap.bits_per_long - 1)),
        (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << 9),
    };

    var weighted_or_dst = [_]bitmap.Word{ 0, 0 };
    try std.testing.expectEqual(@as(usize, 6), bitmap.weightedOr(&weighted_or_dst, &lhs, &rhs, nbits));
    try expectWordSlice(&weighted_or_dst, &[_]bitmap.Word{
        lhs[0] | rhs[0],
        lhs[1] | rhs[1],
    });
    try std.testing.expectEqual(@as(usize, 6), bitmap.bitmap_weighted_or(&weighted_or_dst, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 6), bitmap.__bitmap_weighted_or(&weighted_or_dst, &lhs, &rhs, nbits));

    var weighted_xor_dst = [_]bitmap.Word{ 0, 0 };
    try std.testing.expectEqual(@as(usize, 4), bitmap.weightedXor(&weighted_xor_dst, &lhs, &rhs, nbits));
    try expectWordSlice(&weighted_xor_dst, &[_]bitmap.Word{
        lhs[0] ^ rhs[0],
        lhs[1] ^ rhs[1],
    });
    try std.testing.expectEqual(@as(usize, 4), bitmap.bitmap_weighted_xor(&weighted_xor_dst, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 4), bitmap.__bitmap_weighted_xor(&weighted_xor_dst, &lhs, &rhs, nbits));

    const masked_a = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << (bitmap.bits_per_long - 1)),
        (@as(bitmap.Word, 1) << 0) | (@as(bitmap.Word, 1) << 6),
    };
    const masked_b = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << (bitmap.bits_per_long - 1)),
        (@as(bitmap.Word, 1) << 0) | (@as(bitmap.Word, 1) << 10),
    };
    const subset_superset = [_]bitmap.Word{
        masked_a[0],
        (@as(bitmap.Word, 1) << 0) | (@as(bitmap.Word, 1) << 2),
    };
    const disjoint_tail_noise = [_]bitmap.Word{
        @as(bitmap.Word, 1) << 5,
        (@as(bitmap.Word, 1) << 9) | (@as(bitmap.Word, 1) << 12),
    };

    try std.testing.expect(bitmap.equal(&masked_a, &masked_b, nbits));
    try std.testing.expect(bitmap.bitmap_equal(&masked_a, &masked_b, nbits));
    try std.testing.expect(bitmap.__bitmap_equal(&masked_a, &masked_b, nbits));

    try std.testing.expect(bitmap.subset(&masked_a, &subset_superset, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&masked_a, &subset_superset, nbits));
    try std.testing.expect(bitmap.__bitmap_subset(&masked_a, &subset_superset, nbits));

    try std.testing.expect(!bitmap.intersects(&masked_a, &disjoint_tail_noise, nbits));
    try std.testing.expect(!bitmap.bitmap_intersects(&masked_a, &disjoint_tail_noise, nbits));
    try std.testing.expect(!bitmap.__bitmap_intersects(&masked_a, &disjoint_tail_noise, nbits));
}
