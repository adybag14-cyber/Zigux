const std = @import("std");
const bitmap = @import("bitmap");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "phase1 bitmap alloc/format replay keeps state aliases aligned on partial tails" {
    const nbits = bits_per_long + 5;

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
    try std.testing.expectEqual(@as(usize, nbits), bitmap.weight(&direct, nbits));
}

test "phase1 bitmap alloc/format replay keeps formatted range output and truncation stable" {
    const nbits = bits_per_long + 4;
    var ranged = [_]Word{ 0, 0 };

    bitmap.bitmap_set(&ranged, 1, 3);
    bitmap.bitmap_set(&ranged, bits_per_long, 2);

    var direct_buffer: [64]u8 = undefined;
    var alias_buffer: [64]u8 = undefined;

    const direct_len = bitmap.scnprintf(&ranged, nbits, &direct_buffer);
    const alias_len = bitmap.bitmap_scnprintf(&ranged, nbits, &alias_buffer);
    try std.testing.expectEqual(direct_len, alias_len);
    try std.testing.expectEqualStrings(direct_buffer[0..direct_len], alias_buffer[0..alias_len]);

    var truncated = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa };
    const truncated_len = bitmap.bitmap_scnprintf(&[_]Word{0b1110}, 8, &truncated);
    try std.testing.expectEqual(@as(usize, 3), truncated_len);
    try std.testing.expectEqualStrings("1-3", truncated[0..truncated_len]);
    try std.testing.expectEqual(@as(u8, 0), truncated[truncated_len]);
}

test "phase1 bitmap alloc/format replay keeps empty-format buffers untouched" {
    const empty_map = [_]Word{0};
    var buffer = [_]u8{ 0xcc, 0xcc, 0xcc, 0xcc };

    const len = bitmap.bitmap_scnprintf(&empty_map, 8, &buffer);
    try std.testing.expectEqual(@as(usize, 0), len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xcc, 0xcc, 0xcc, 0xcc }, &buffer);
}

test "phase1 bitmap alloc/format replay keeps allocation helpers zeroed and reset" {
    const allocator = std.testing.allocator;
    const nbits = bits_per_long + 9;
    const expected_words = bitmap.bitsToWords(nbits);

    var plain: ?[]Word = try bitmap.bitmap_alloc(allocator, nbits);
    try std.testing.expectEqual(@as(usize, expected_words), plain.?.len);
    bitmap.bitmap_free(allocator, &plain);
    try std.testing.expect(plain == null);

    var zeroed: ?[]Word = try bitmap.bitmap_zalloc(allocator, nbits);
    defer bitmap.bitmap_free(allocator, &zeroed);
    try std.testing.expectEqual(@as(usize, expected_words), zeroed.?.len);
    for (zeroed.?) |word| {
        try std.testing.expectEqual(@as(Word, 0), word);
    }

    try std.testing.expectEqual(@as(usize, expected_words * @sizeOf(Word)), bitmap.bitmap_size(nbits));
}
