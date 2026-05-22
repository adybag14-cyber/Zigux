const std = @import("std");
const bitmap = @import("bitmap");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "phase1 bitmap complement replay clamps the tail and mirrors the alias" {
    const nbits = bits_per_long + 5;
    const src = [_]Word{
        0b1010,
        (@as(Word, 1) << 1) | (@as(Word, 1) << 7) | (@as(Word, 1) << 10),
    };
    var direct = [_]Word{ 0, 0 };
    var alias = [_]Word{ 0, 0 };

    bitmap.complement(&direct, &src, nbits);
    bitmap.bitmap_complement(&alias, &src, nbits);

    try std.testing.expectEqualSlices(Word, &direct, &alias);
    try std.testing.expectEqual(~@as(Word, 0b1010), direct[0]);
    try std.testing.expectEqual((~src[1]) & bitmap.lastWordMask(nbits), direct[1]);

    var zero_src = [_]Word{~@as(Word, 0)};
    var zero_direct = [_]Word{0x1357};
    var zero_alias = [_]Word{0x2468};
    bitmap.complement(zero_direct[0..0], zero_src[0..0], 0);
    bitmap.bitmap_complement(zero_alias[0..0], zero_src[0..0], 0);
    try std.testing.expectEqual(@as(Word, 0x1357), zero_direct[0]);
    try std.testing.expectEqual(@as(Word, 0x2468), zero_alias[0]);
}

test "phase1 bitmap allocation and state aliases reset optionals" {
    const allocator = std.testing.allocator;
    const nbits = bits_per_long + 5;

    try std.testing.expectEqual(bitmap.bitmapSize(0), bitmap.bitmap_size(0));
    try std.testing.expectEqual(bitmap.bitmapSize(nbits), bitmap.bitmap_size(nbits));

    var direct = [_]Word{ 0xaa55, 0xaa55 };
    var alias = [_]Word{ 0xaa55, 0xaa55 };
    bitmap.zero(&direct, nbits);
    bitmap.bitmap_zero(&alias, nbits);
    try std.testing.expectEqualSlices(Word, &direct, &alias);
    try std.testing.expect(bitmap.empty(&direct, nbits));
    try std.testing.expect(bitmap.bitmap_empty(&alias, nbits));

    bitmap.fill(&direct, nbits);
    bitmap.bitmap_fill(&alias, nbits);
    try std.testing.expectEqualSlices(Word, &direct, &alias);
    try std.testing.expect(bitmap.full(&direct, nbits));
    try std.testing.expect(bitmap.bitmap_full(&alias, nbits));
    try std.testing.expectEqual(bitmap.weight(&direct, nbits), bitmap.bitmap_weight(&alias, nbits));

    var plain_direct: ?[]Word = try bitmap.bitmapAlloc(allocator, nbits);
    defer bitmap.bitmapFree(allocator, &plain_direct);
    var plain_alias: ?[]Word = try bitmap.bitmap_alloc(allocator, nbits);
    defer bitmap.bitmap_free(allocator, &plain_alias);
    try std.testing.expectEqual(plain_direct.?.len, plain_alias.?.len);
    try std.testing.expectEqual(@as(usize, bitmap.bitsToWords(nbits)), plain_direct.?.len);

    var zeroed_direct: ?[]Word = try bitmap.bitmapZalloc(allocator, nbits);
    defer bitmap.bitmapFree(allocator, &zeroed_direct);
    var zeroed_alias: ?[]Word = try bitmap.bitmap_zalloc(allocator, nbits);
    defer bitmap.bitmap_free(allocator, &zeroed_alias);
    try std.testing.expectEqual(zeroed_direct.?.len, zeroed_alias.?.len);
    for (zeroed_direct.?) |word| {
        try std.testing.expectEqual(@as(Word, 0), word);
    }
    for (zeroed_alias.?) |word| {
        try std.testing.expectEqual(@as(Word, 0), word);
    }

    bitmap.bitmapFree(allocator, &plain_direct);
    bitmap.bitmap_free(allocator, &plain_alias);
    bitmap.bitmapFree(allocator, &zeroed_direct);
    bitmap.bitmap_free(allocator, &zeroed_alias);
    try std.testing.expect(plain_direct == null);
    try std.testing.expect(plain_alias == null);
    try std.testing.expect(zeroed_direct == null);
    try std.testing.expect(zeroed_alias == null);
}
