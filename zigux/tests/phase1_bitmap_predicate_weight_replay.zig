const std = @import("std");
const bitmap = @import("bitmap");

test "bitmap weighted aliases clamp counts to the declared tail window" {
    const nbits = bitmap.bits_per_long + 5;
    const lhs = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 8) };
    const rhs = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 9) };

    var direct_or = [_]bitmap.Word{ 0, 0 };
    var alias_or = [_]bitmap.Word{ 0, 0 };
    const direct_or_weight = bitmap.weightedOr(&direct_or, &lhs, &rhs, nbits);
    const alias_or_weight = bitmap.bitmap_weighted_or(&alias_or, &lhs, &rhs, nbits);
    try std.testing.expectEqual(@as(usize, 2), direct_or_weight);
    try std.testing.expectEqual(direct_or_weight, alias_or_weight);
    try std.testing.expectEqual(@as(bitmap.Word, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3)), direct_or[1] & bitmap.lastWordMask(nbits));
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&direct_or, nbits));
    try std.testing.expectEqualSlices(bitmap.Word, &direct_or, &alias_or);

    const xor_lhs = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 8) };
    const xor_rhs = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 9) };
    var direct_xor = [_]bitmap.Word{ 0, 0 };
    var alias_xor = [_]bitmap.Word{ 0, 0 };
    const direct_xor_weight = bitmap.weightedXor(&direct_xor, &xor_lhs, &xor_rhs, nbits);
    const alias_xor_weight = bitmap.bitmap_weighted_xor(&alias_xor, &xor_lhs, &xor_rhs, nbits);
    try std.testing.expectEqual(@as(usize, 2), direct_xor_weight);
    try std.testing.expectEqual(direct_xor_weight, alias_xor_weight);
    try std.testing.expectEqual(@as(bitmap.Word, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4)), direct_xor[1] & bitmap.lastWordMask(nbits));
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&direct_xor, nbits));
    try std.testing.expectEqualSlices(bitmap.Word, &direct_xor, &alias_xor);
}

test "bitmap predicates and complements ignore out-of-range tail differences" {
    const nbits = bitmap.bits_per_long + 5;
    const in_range = (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3);
    const lhs = [_]bitmap.Word{ 0b1010, in_range | (@as(bitmap.Word, 1) << 8) };
    const rhs = [_]bitmap.Word{ 0b1010, in_range | (@as(bitmap.Word, 1) << 10) };

    try std.testing.expect(bitmap.equal(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_equal(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.intersects(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.subset(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&lhs, &rhs, nbits));

    var and_dst = [_]bitmap.Word{ ~@as(bitmap.Word, 0), ~@as(bitmap.Word, 0) };
    try std.testing.expect(bitmap.andBits(&and_dst, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(bitmap.Word, 0b1010), and_dst[0]);
    try std.testing.expectEqual(in_range, and_dst[1]);

    var andnot_dst = [_]bitmap.Word{ ~@as(bitmap.Word, 0), ~@as(bitmap.Word, 0) };
    try std.testing.expect(!bitmap.andNotBits(&andnot_dst, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(bitmap.Word, 0), andnot_dst[0]);
    try std.testing.expectEqual(@as(bitmap.Word, 0), andnot_dst[1]);

    var direct_complement = [_]bitmap.Word{ 0, 0 };
    var alias_complement = [_]bitmap.Word{ 0, 0 };
    bitmap.complement(&direct_complement, &lhs, nbits);
    bitmap.bitmap_complement(&alias_complement, &lhs, nbits);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_complement, &alias_complement);
    try std.testing.expectEqual((~lhs[1]) & bitmap.lastWordMask(nbits), direct_complement[1]);
}

test "bitmap zero-bit views leave caller storage untouched" {
    const empty_words = [_]bitmap.Word{};

    var or_dst = [_]bitmap.Word{0x1357};
    var xor_dst = [_]bitmap.Word{0x2468};
    var and_dst = [_]bitmap.Word{0x55aa};
    var andnot_dst = [_]bitmap.Word{0xaa55};
    var complement_dst = [_]bitmap.Word{0xf0f0};
    var buffer = [_]u8{ 0xcc, 0xcc, 0xcc };

    bitmap.orBits(or_dst[0..0], empty_words[0..0], empty_words[0..0], 0);
    bitmap.xorBits(xor_dst[0..0], empty_words[0..0], empty_words[0..0], 0);
    try std.testing.expect(!bitmap.andBits(and_dst[0..0], empty_words[0..0], empty_words[0..0], 0));
    try std.testing.expect(!bitmap.andNotBits(andnot_dst[0..0], empty_words[0..0], empty_words[0..0], 0));
    bitmap.complement(complement_dst[0..0], empty_words[0..0], 0);

    try std.testing.expectEqual(@as(bitmap.Word, 0x1357), or_dst[0]);
    try std.testing.expectEqual(@as(bitmap.Word, 0x2468), xor_dst[0]);
    try std.testing.expectEqual(@as(bitmap.Word, 0x55aa), and_dst[0]);
    try std.testing.expectEqual(@as(bitmap.Word, 0xaa55), andnot_dst[0]);
    try std.testing.expectEqual(@as(bitmap.Word, 0xf0f0), complement_dst[0]);

    try std.testing.expectEqual(@as(usize, 0), bitmap.weightedOr(or_dst[0..0], empty_words[0..0], empty_words[0..0], 0));
    try std.testing.expectEqual(@as(usize, 0), bitmap.bitmap_weighted_or(or_dst[0..0], empty_words[0..0], empty_words[0..0], 0));
    try std.testing.expectEqual(@as(usize, 0), bitmap.weightedXor(xor_dst[0..0], empty_words[0..0], empty_words[0..0], 0));
    try std.testing.expectEqual(@as(usize, 0), bitmap.bitmap_weighted_xor(xor_dst[0..0], empty_words[0..0], empty_words[0..0], 0));

    try std.testing.expect(bitmap.empty(empty_words[0..0], 0));
    try std.testing.expect(bitmap.full(empty_words[0..0], 0));
    try std.testing.expectEqual(@as(usize, 0), bitmap.weight(empty_words[0..0], 0));
    try std.testing.expect(bitmap.equal(empty_words[0..0], empty_words[0..0], 0));
    try std.testing.expect(!bitmap.intersects(empty_words[0..0], empty_words[0..0], 0));
    try std.testing.expect(bitmap.subset(empty_words[0..0], empty_words[0..0], 0));

    const written = bitmap.scnprintf(empty_words[0..0], 0, &buffer);
    try std.testing.expectEqual(@as(usize, 0), written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xcc, 0xcc, 0xcc }, &buffer);
}
