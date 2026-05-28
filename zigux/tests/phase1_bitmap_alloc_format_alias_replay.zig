const std = @import("std");
const bitmap = @import("bitmap");

test "phase1 bitmap alloc-format alias replay keeps range formatting and truncation aligned" {
    const nbits = bitmap.bits_per_long + 12;
    var map = [_]bitmap.Word{ 0, 0 };

    bitmap.bitmap_set(&map, bitmap.bits_per_long - 2, 5);
    bitmap.bitmap_set(&map, bitmap.bits_per_long + 9, 1);
    bitmap.bitmap_clear(&map, bitmap.bits_per_long, 1);

    var direct_buffer: [64]u8 = undefined;
    var alias_buffer: [64]u8 = undefined;
    const direct_len = bitmap.scnprintf(&map, nbits, &direct_buffer);
    const alias_len = bitmap.bitmap_scnprintf(&map, nbits, &alias_buffer);

    try std.testing.expectEqual(direct_len, alias_len);
    try std.testing.expectEqualStrings(direct_buffer[0..direct_len], alias_buffer[0..alias_len]);

    var expected: [32]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "{d}-{d},{d}-{d},{d}",
        .{
            bitmap.bits_per_long - 2,
            bitmap.bits_per_long - 1,
            bitmap.bits_per_long + 1,
            bitmap.bits_per_long + 2,
            bitmap.bits_per_long + 9,
        },
    );
    try std.testing.expectEqualStrings(expected_text, alias_buffer[0..alias_len]);

    var direct_small = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa };
    var alias_small = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa };
    const direct_small_len = bitmap.scnprintf(&map, nbits, direct_small[0..1]);
    const alias_small_len = bitmap.bitmap_scnprintf(&map, nbits, alias_small[0..1]);
    try std.testing.expectEqual(direct_small_len, alias_small_len);
    try std.testing.expectEqual(@as(usize, 0), alias_small_len);
    try std.testing.expectEqual(@as(u8, 0), direct_small[0]);
    try std.testing.expectEqualSlices(u8, &direct_small, &alias_small);
}

test "phase1 bitmap alloc-format alias replay keeps allocation and state helpers aligned" {
    const allocator = std.testing.allocator;
    const nbits = bitmap.bits_per_long + 5;

    var filled = [_]bitmap.Word{ 0, 0 };
    bitmap.bitmap_fill(&filled, nbits);
    try std.testing.expect(bitmap.bitmap_full(&filled, nbits));
    try std.testing.expectEqual(@as(usize, nbits), bitmap.bitmap_weight(&filled, nbits));

    bitmap.bitmap_zero(&filled, nbits);
    try std.testing.expect(bitmap.bitmap_empty(&filled, nbits));
    try std.testing.expectEqual(@as(usize, 0), bitmap.bitmap_weight(&filled, nbits));

    var plain = try bitmap.bitmap_alloc(allocator, nbits);
    defer bitmap.bitmap_free(allocator, &plain);
    try std.testing.expect(plain != null);
    try std.testing.expectEqual(@as(usize, bitmap.bitsToWords(nbits)), plain.?.len);

    var zeroed = try bitmap.bitmap_zalloc(allocator, nbits);
    defer bitmap.bitmap_free(allocator, &zeroed);
    try std.testing.expect(zeroed != null);
    try std.testing.expectEqual(@as(usize, bitmap.bitsToWords(nbits)), zeroed.?.len);
    for (zeroed.?) |word| {
        try std.testing.expectEqual(@as(bitmap.Word, 0), word);
    }

    bitmap.bitmap_set(zeroed.?, 1, 3);
    bitmap.bitmap_set(zeroed.?, bitmap.bits_per_long + 1, 2);
    try std.testing.expectEqual(@as(usize, 5), bitmap.bitmap_weight(zeroed.?, nbits));
    try std.testing.expect(!bitmap.bitmap_empty(zeroed.?, nbits));
    try std.testing.expect(!bitmap.bitmap_full(zeroed.?, nbits));

    bitmap.bitmap_free(allocator, &plain);
    bitmap.bitmap_free(allocator, &zeroed);
    try std.testing.expect(plain == null);
    try std.testing.expect(zeroed == null);
}
