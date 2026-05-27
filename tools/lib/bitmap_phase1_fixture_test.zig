const std = @import("std");
const bitmap = @import("bitmap.zig");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "phase1 bitmap copy_clear_tail masks bits outside the declared tail" {
    const nbits = bits_per_long + 5;
    const src = [_]Word{ ~@as(Word, 0), ~@as(Word, 0), 0 };
    var dst = [_]Word{ 0, 0, 0 };

    bitmap.bitmap_copy_clear_tail(&dst, src[0..2], nbits);

    try std.testing.expectEqual(src[0], dst[0]);
    try std.testing.expectEqual(bitmap.lastWordMask(nbits), dst[1]);
    try std.testing.expectEqual(@as(Word, 0), dst[2]);
}

test "phase1 bitmap scnprintf keeps cross-word ranges collapsed" {
    const nbits = bits_per_long + 8;
    var map = [_]Word{ 0, 0 };
    bitmap.bitmap_set(&map, bits_per_long - 2, 5);
    bitmap.bitmap_set(&map, bits_per_long + 6, 1);

    var buffer: [64]u8 = undefined;
    const len = bitmap.bitmap_scnprintf(&map, nbits, &buffer);

    var expected: [32]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "{d}-{d},{d}",
        .{ bits_per_long - 2, bits_per_long + 2, bits_per_long + 6 },
    );
    try std.testing.expectEqualStrings(expected_text, buffer[0..len]);
}

test "phase1 bitmap scnprintf preserves zero-sized caller buffer expectations" {
    var map = [_]Word{0};
    bitmap.bitmap_set(&map, 1, 3);

    var terminator_only = [_]u8{0xaa};
    const terminator_only_len = bitmap.bitmap_scnprintf(&map, 8, terminator_only[0..1]);
    try std.testing.expectEqual(@as(usize, 0), terminator_only_len);
    try std.testing.expectEqual(@as(u8, 0), terminator_only[0]);

    var zero_length_backing = [_]u8{0xbb};
    const zero_length_len = bitmap.bitmap_scnprintf(&map, 8, zero_length_backing[0..0]);
    try std.testing.expectEqual(@as(usize, 0), zero_length_len);
    try std.testing.expectEqual(@as(u8, 0xbb), zero_length_backing[0]);
}

test "phase1 bitmap copy aliases keep zero-sized caller views untouched" {
    var src = [_]Word{~@as(Word, 0)};
    var copy_dst = [_]Word{0x55aa};
    var clear_dst = [_]Word{0xaa55};
    var extend_dst = [_]Word{0xf0f0};

    bitmap.bitmap_copy(copy_dst[0..0], src[0..0], 0);
    try std.testing.expectEqual(@as(Word, 0x55aa), copy_dst[0]);

    bitmap.bitmap_copy_clear_tail(clear_dst[0..0], src[0..0], 0);
    try std.testing.expectEqual(@as(Word, 0xaa55), clear_dst[0]);

    bitmap.bitmap_copy_and_extend(extend_dst[0..0], src[0..0], 0, 0);
    try std.testing.expectEqual(@as(Word, 0xf0f0), extend_dst[0]);
}
