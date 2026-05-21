const std = @import("std");
const bitmap = @import("bitmap");

const Word = bitmap.Word;

test "phase1 bitmap zero-bit replay keeps primary helpers as explicit no-ops" {
    var dst = [_]Word{0x55aa55aa55aa55aa};
    const src1 = [_]Word{0xffff0000ffff0000};
    const src2 = [_]Word{0x0000ffff0000ffff};
    const copy_src = [_]Word{0x0123456789abcdef};
    const before = dst[0];

    bitmap.zero(dst[0..0], 0);
    try std.testing.expectEqual(before, dst[0]);

    bitmap.orBits(dst[0..0], src1[0..0], src2[0..0], 0);
    try std.testing.expectEqual(before, dst[0]);

    bitmap.xorBits(dst[0..0], src1[0..0], src2[0..0], 0);
    try std.testing.expectEqual(before, dst[0]);

    bitmap.copy(dst[0..0], copy_src[0..0], 0);
    try std.testing.expectEqual(before, dst[0]);

    try std.testing.expect(bitmap.empty(&[_]Word{}, 0));
    try std.testing.expect(bitmap.full(&[_]Word{}, 0));
    try std.testing.expectEqual(@as(usize, 0), bitmap.weight(&[_]Word{}, 0));

    var buffer = [_]u8{0xaa};
    const rendered = bitmap.scnprintf(&[_]Word{}, 0, &buffer);
    try std.testing.expectEqual(@as(usize, 0), rendered);
    try std.testing.expectEqual(@as(u8, 0xaa), buffer[0]);
}

test "phase1 bitmap zero-bit replay keeps binary helpers and relations stable" {
    const lhs = [_]Word{0xffff_0000_ffff_0000};
    const rhs = [_]Word{0x0000_ffff_0000_ffff};
    const mask = [_]Word{~@as(Word, 0)};

    var primary_dst = [_]Word{0x55aa_55aa_55aa_55aa};
    var alias_dst = [_]Word{0x55aa_55aa_55aa_55aa};
    const before = primary_dst[0];

    try std.testing.expectEqual(
        bitmap.andBits(primary_dst[0..0], lhs[0..0], rhs[0..0], 0),
        bitmap.bitmap_and(alias_dst[0..0], lhs[0..0], rhs[0..0], 0),
    );
    try std.testing.expectEqual(@as(bool, false), bitmap.andBits(primary_dst[0..0], lhs[0..0], rhs[0..0], 0));
    try std.testing.expectEqual(before, primary_dst[0]);
    try std.testing.expectEqual(before, alias_dst[0]);

    try std.testing.expectEqual(
        bitmap.andNotBits(primary_dst[0..0], lhs[0..0], rhs[0..0], 0),
        bitmap.bitmap_andnot(alias_dst[0..0], lhs[0..0], rhs[0..0], 0),
    );
    try std.testing.expectEqual(@as(bool, false), bitmap.andNotBits(primary_dst[0..0], lhs[0..0], rhs[0..0], 0));
    try std.testing.expectEqual(before, primary_dst[0]);
    try std.testing.expectEqual(before, alias_dst[0]);

    bitmap.complement(primary_dst[0..0], lhs[0..0], 0);
    bitmap.bitmap_complement(alias_dst[0..0], lhs[0..0], 0);
    try std.testing.expectEqual(before, primary_dst[0]);
    try std.testing.expectEqual(before, alias_dst[0]);

    bitmap.replace(primary_dst[0..0], lhs[0..0], rhs[0..0], mask[0..0], 0);
    bitmap.bitmap_replace(alias_dst[0..0], lhs[0..0], rhs[0..0], mask[0..0], 0);
    try std.testing.expectEqual(before, primary_dst[0]);
    try std.testing.expectEqual(before, alias_dst[0]);

    try std.testing.expect(bitmap.equal(lhs[0..0], rhs[0..0], 0));
    try std.testing.expect(bitmap.bitmap_equal(lhs[0..0], rhs[0..0], 0));
    try std.testing.expect(!bitmap.intersects(lhs[0..0], rhs[0..0], 0));
    try std.testing.expect(!bitmap.bitmap_intersects(lhs[0..0], rhs[0..0], 0));
    try std.testing.expect(bitmap.subset(lhs[0..0], rhs[0..0], 0));
    try std.testing.expect(bitmap.bitmap_subset(lhs[0..0], rhs[0..0], 0));
}

test "phase1 bitmap zero-bit replay keeps Linux-style aliases as explicit no-ops" {
    const allocator = std.testing.allocator;
    const lhs = [_]Word{0xffff_0000_ffff_0000};
    const rhs = [_]Word{0x0000_ffff_0000_ffff};
    const copy_src = [_]Word{0x0123_4567_89ab_cdef};

    var empty_alloc = try bitmap.bitmap_alloc(allocator, 0);
    try std.testing.expect(empty_alloc == null);
    bitmap.bitmap_free(allocator, &empty_alloc);
    try std.testing.expect(empty_alloc == null);

    var empty_zalloc = try bitmap.bitmap_zalloc(allocator, 0);
    try std.testing.expect(empty_zalloc == null);
    bitmap.bitmap_free(allocator, &empty_zalloc);
    try std.testing.expect(empty_zalloc == null);

    var zero_dst = [_]Word{0x55aa_55aa_55aa_55aa};
    const before = zero_dst[0];

    bitmap.bitmap_zero(zero_dst[0..0], 0);
    try std.testing.expectEqual(before, zero_dst[0]);

    bitmap.bitmap_or(zero_dst[0..0], lhs[0..0], rhs[0..0], 0);
    try std.testing.expectEqual(before, zero_dst[0]);

    bitmap.bitmap_xor(zero_dst[0..0], lhs[0..0], rhs[0..0], 0);
    try std.testing.expectEqual(before, zero_dst[0]);

    try std.testing.expectEqual(@as(usize, 0), bitmap.weightedOr(zero_dst[0..0], lhs[0..0], rhs[0..0], 0));
    try std.testing.expectEqual(before, zero_dst[0]);
    try std.testing.expectEqual(@as(usize, 0), bitmap.bitmap_weighted_or(zero_dst[0..0], lhs[0..0], rhs[0..0], 0));
    try std.testing.expectEqual(before, zero_dst[0]);

    try std.testing.expectEqual(@as(usize, 0), bitmap.weightedXor(zero_dst[0..0], lhs[0..0], rhs[0..0], 0));
    try std.testing.expectEqual(before, zero_dst[0]);
    try std.testing.expectEqual(@as(usize, 0), bitmap.bitmap_weighted_xor(zero_dst[0..0], lhs[0..0], rhs[0..0], 0));
    try std.testing.expectEqual(before, zero_dst[0]);

    bitmap.bitmap_copy(zero_dst[0..0], copy_src[0..0], 0);
    try std.testing.expectEqual(before, zero_dst[0]);

    var buffer = [_]u8{0xaa};
    const rendered = bitmap.bitmap_scnprintf(&[_]Word{}, 0, &buffer);
    try std.testing.expectEqual(@as(usize, 0), rendered);
    try std.testing.expectEqual(@as(u8, 0xaa), buffer[0]);
}
