const std = @import("std");
const bitmap = @import("bitmap");

const Word = bitmap.Word;

test "phase1 bitmap range replay keeps boundary ranges and alias rendering aligned" {
    const nbits = bitmap.bits_per_long * 2 + 8;
    var direct = [_]Word{ 0, 0, 0 };
    var alias = [_]Word{ 0, 0, 0 };

    bitmap.setRange(&direct, bitmap.bits_per_long - 2, 5);
    bitmap.bitmap_set(&alias, bitmap.bits_per_long - 2, 5);
    bitmap.setRange(&direct, bitmap.bits_per_long * 2 + 1, 3);
    bitmap.bitmap_set(&alias, bitmap.bits_per_long * 2 + 1, 3);
    try std.testing.expectEqualSlices(Word, &direct, &alias);

    var direct_buffer: [64]u8 = undefined;
    var alias_buffer: [64]u8 = undefined;
    const direct_len = bitmap.scnprintf(&direct, nbits, &direct_buffer);
    const alias_len = bitmap.bitmap_scnprintf(&alias, nbits, &alias_buffer);
    try std.testing.expectEqual(direct_len, alias_len);
    try std.testing.expectEqualStrings(direct_buffer[0..direct_len], alias_buffer[0..alias_len]);

    var expected: [32]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "{d}-{d},{d}-{d}",
        .{
            bitmap.bits_per_long - 2,
            bitmap.bits_per_long + 2,
            bitmap.bits_per_long * 2 + 1,
            bitmap.bits_per_long * 2 + 3,
        },
    );
    try std.testing.expectEqualStrings(expected_text, direct_buffer[0..direct_len]);

    bitmap.clearRange(&direct, bitmap.bits_per_long - 1, 3);
    bitmap.bitmap_clear(&alias, bitmap.bits_per_long - 1, 3);
    try std.testing.expectEqualSlices(Word, &direct, &alias);

    const trimmed_len = bitmap.scnprintf(&direct, nbits, &direct_buffer);
    const trimmed_expected = try std.fmt.bufPrint(
        &expected,
        "{d},{d},{d}-{d}",
        .{
            bitmap.bits_per_long - 2,
            bitmap.bits_per_long + 2,
            bitmap.bits_per_long * 2 + 1,
            bitmap.bits_per_long * 2 + 3,
        },
    );
    try std.testing.expectEqualStrings(trimmed_expected, direct_buffer[0..trimmed_len]);
}

test "phase1 bitmap range replay leaves zero-sized caller views untouched" {
    var direct = [_]Word{0x55aa};
    var alias = [_]Word{0x55aa};

    bitmap.setRange(direct[0..0], 0, 0);
    bitmap.bitmap_set(alias[0..0], 0, 0);
    try std.testing.expectEqualSlices(Word, &direct, &alias);

    bitmap.clearRange(direct[0..0], 0, 0);
    bitmap.bitmap_clear(alias[0..0], 0, 0);
    try std.testing.expectEqualSlices(Word, &direct, &alias);
    try std.testing.expectEqual(@as(Word, 0x55aa), direct[0]);
}

test "phase1 bitmap range replay truncates rendering while preserving a terminator slot" {
    const nbits = bitmap.bits_per_long + 4;
    var direct = [_]Word{ 0, 0 };
    var alias = [_]Word{ 0, 0 };

    bitmap.setRange(&direct, 1, 3);
    bitmap.bitmap_set(&alias, 1, 3);
    bitmap.setRange(&direct, bitmap.bits_per_long - 1, 3);
    bitmap.bitmap_set(&alias, bitmap.bits_per_long - 1, 3);

    var direct_buffer = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa };
    var alias_buffer = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa };
    const direct_len = bitmap.scnprintf(&direct, nbits, &direct_buffer);
    const alias_len = bitmap.bitmap_scnprintf(&alias, nbits, &alias_buffer);

    try std.testing.expectEqual(direct_len, alias_len);
    try std.testing.expectEqualSlices(u8, direct_buffer[0 .. direct_len + 1], alias_buffer[0 .. alias_len + 1]);
    try std.testing.expectEqual(@as(u8, 0), direct_buffer[direct_len]);
    try std.testing.expectEqualStrings("1-3,6", direct_buffer[0..direct_len]);
}
