const std = @import("std");
const bitmap = @import("bitmap");

test "phase 1 bitmap review anchor replay keeps weighted tail counts clamped to the declared window" {
    const nbits = bitmap.bits_per_long + 5;
    const lhs = [_]bitmap.Word{
        0,
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 8),
    };
    const rhs = [_]bitmap.Word{
        0,
        (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 9),
    };
    var or_words = [_]bitmap.Word{ 0, 0 };
    var xor_words = [_]bitmap.Word{ 0, 0 };

    try std.testing.expectEqual(@as(usize, 3), bitmap.bitmap_weighted_or(&or_words, &lhs, &rhs, nbits));
    try std.testing.expectEqual(
        @as(bitmap.Word, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 8) | (@as(bitmap.Word, 1) << 9)),
        or_words[1],
    );
    try std.testing.expectEqual(@as(usize, 3), bitmap.weight(&or_words, nbits));

    try std.testing.expectEqual(@as(usize, 2), bitmap.bitmap_weighted_xor(&xor_words, &lhs, &rhs, nbits));
    try std.testing.expectEqual(
        @as(bitmap.Word, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 8) | (@as(bitmap.Word, 1) << 9)),
        xor_words[1],
    );
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&xor_words, nbits));

    try std.testing.expectEqual(@as(usize, 0), bitmap.weight(&[_]bitmap.Word{ 0, @as(bitmap.Word, 1) << 8 }, nbits));
}

test "phase 1 bitmap review anchor replay keeps cross-word formatting and tiny buffers review-visible" {
    const nbits = bitmap.bits_per_long + 8;
    var map = [_]bitmap.Word{ 0, 0 };
    bitmap.bitmap_set(&map, bitmap.bits_per_long - 2, 5);
    bitmap.bitmap_set(&map, bitmap.bits_per_long + 6, 1);

    var full_buffer: [64]u8 = undefined;
    const full_len = bitmap.bitmap_scnprintf(&map, nbits, &full_buffer);

    var expected: [32]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "{d}-{d},{d}",
        .{ bitmap.bits_per_long - 2, bitmap.bits_per_long + 2, bitmap.bits_per_long + 6 },
    );
    try std.testing.expectEqualStrings(expected_text, full_buffer[0..full_len]);

    var tiny_buffer = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa };
    const tiny_len = bitmap.bitmap_scnprintf(&map, nbits, &tiny_buffer);
    try std.testing.expectEqual(@as(usize, 3), tiny_len);
    try std.testing.expectEqualStrings(expected_text[0..3], tiny_buffer[0..tiny_len]);
    try std.testing.expectEqual(@as(u8, 0), tiny_buffer[tiny_len]);

    const empty_map = [_]bitmap.Word{ 0, 0 };
    var untouched = [_]u8{ 0xcc, 0xcc, 0xcc };
    const untouched_len = bitmap.bitmap_scnprintf(&empty_map, nbits, &untouched);
    try std.testing.expectEqual(@as(usize, 0), untouched_len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xcc, 0xcc, 0xcc }, &untouched);
}

test "phase 1 bitmap review anchor replay keeps copy-tail and extension aliases aligned" {
    const count = bitmap.bits_per_long + 5;
    const size = bitmap.bits_per_long * 3;
    const src = [_]bitmap.Word{ ~@as(bitmap.Word, 0), ~@as(bitmap.Word, 0), 0 };

    var direct_tail = [_]bitmap.Word{ 0, 0, 0 };
    var alias_tail = [_]bitmap.Word{ 0, 0, 0 };
    bitmap.copyClearTail(&direct_tail, src[0..2], count);
    bitmap.bitmap_copy_clear_tail(&alias_tail, src[0..2], count);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_tail, &alias_tail);
    try std.testing.expectEqual(bitmap.lastWordMask(count), direct_tail[1]);

    var direct_extend = [_]bitmap.Word{ 0xaa55, 0xaa55, 0xaa55 };
    var alias_extend = [_]bitmap.Word{ 0xaa55, 0xaa55, 0xaa55 };
    bitmap.copyAndExtend(&direct_extend, src[0..2], count, size);
    bitmap.bitmap_copy_and_extend(&alias_extend, src[0..2], count, size);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_extend, &alias_extend);
    try std.testing.expectEqual(bitmap.lastWordMask(count), direct_extend[1]);
    try std.testing.expectEqual(@as(bitmap.Word, 0), direct_extend[2]);
}
