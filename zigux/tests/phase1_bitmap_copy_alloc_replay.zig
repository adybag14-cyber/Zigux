const std = @import("std");
const bitmap = @import("bitmap");

fn maskedWord(value: bitmap.Word, nbits: usize) bitmap.Word {
    return value & bitmap.lastWordMask(nbits);
}

test "phase1 bitmap copy alloc replay keeps bounded copy tails and extension explicit" {
    const count = bitmap.bits_per_long + 5;
    const size = bitmap.bits_per_long * 3 + 2;
    const src = [_]bitmap.Word{ ~@as(bitmap.Word, 0), ~@as(bitmap.Word, 0), 0, 0 };

    var direct_tail = [_]bitmap.Word{ 0, 0, 0 };
    var alias_tail = [_]bitmap.Word{ 0, 0, 0 };
    bitmap.copyClearTail(&direct_tail, src[0..2], count);
    bitmap.bitmap_copy_clear_tail(&alias_tail, src[0..2], count);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_tail, &alias_tail);
    try std.testing.expectEqual(~@as(bitmap.Word, 0), alias_tail[0]);
    try std.testing.expectEqual(bitmap.lastWordMask(count), alias_tail[1]);
    try std.testing.expectEqual(@as(bitmap.Word, 0), alias_tail[2]);

    var direct_extend = [_]bitmap.Word{
        0xaa55,
        0xaa55,
        0xaa55,
        0xaa55,
    };
    var alias_extend = [_]bitmap.Word{
        0xaa55,
        0xaa55,
        0xaa55,
        0xaa55,
    };
    bitmap.copyAndExtend(&direct_extend, src[0..2], count, size);
    bitmap.bitmap_copy_and_extend(&alias_extend, src[0..2], count, size);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_extend, &alias_extend);
    try std.testing.expectEqual(~@as(bitmap.Word, 0), alias_extend[0]);
    try std.testing.expectEqual(bitmap.lastWordMask(count), alias_extend[1]);
    try std.testing.expectEqual(@as(bitmap.Word, 0), alias_extend[2]);
    try std.testing.expectEqual(@as(bitmap.Word, 0), maskedWord(alias_extend[3], size));

    var zero_copy = [_]bitmap.Word{0x55aa};
    var zero_clear = [_]bitmap.Word{0xaa55};
    var zero_extend = [_]bitmap.Word{0xf0f0};
    bitmap.bitmap_copy(zero_copy[0..0], src[0..0], 0);
    bitmap.bitmap_copy_clear_tail(zero_clear[0..0], src[0..0], 0);
    bitmap.bitmap_copy_and_extend(zero_extend[0..0], src[0..0], 0, 0);
    try std.testing.expectEqual(@as(bitmap.Word, 0x55aa), zero_copy[0]);
    try std.testing.expectEqual(@as(bitmap.Word, 0xaa55), zero_clear[0]);
    try std.testing.expectEqual(@as(bitmap.Word, 0xf0f0), zero_extend[0]);
}

test "phase1 bitmap copy alloc replay keeps alias alloc fill zero and free behavior aligned" {
    const allocator = std.testing.allocator;
    const nbits = bitmap.bits_per_long + 5;

    try std.testing.expectEqual(@as(usize, @sizeOf(bitmap.Word) * 2), bitmap.bitmap_size(nbits));

    var plain: ?[]bitmap.Word = try bitmap.bitmap_alloc(allocator, nbits);
    defer bitmap.bitmap_free(allocator, &plain);
    var zeroed: ?[]bitmap.Word = try bitmap.bitmap_zalloc(allocator, nbits);
    defer bitmap.bitmap_free(allocator, &zeroed);

    try std.testing.expectEqual(@as(usize, bitmap.bitsToWords(nbits)), plain.?.len);
    try std.testing.expectEqual(plain.?.len, zeroed.?.len);
    for (zeroed.?) |word| {
        try std.testing.expectEqual(@as(bitmap.Word, 0), word);
    }
    try std.testing.expect(bitmap.bitmap_empty(zeroed.?, nbits));

    bitmap.bitmap_fill(plain.?, nbits);
    try std.testing.expect(bitmap.bitmap_full(plain.?, nbits));
    try std.testing.expectEqual(nbits, bitmap.bitmap_weight(plain.?, nbits));

    bitmap.bitmap_zero(plain.?, nbits);
    try std.testing.expect(bitmap.bitmap_empty(plain.?, nbits));
    try std.testing.expectEqual(@as(usize, 0), bitmap.bitmap_weight(plain.?, nbits));

    bitmap.bitmap_free(allocator, &zeroed);
    try std.testing.expect(zeroed == null);
}
