const std = @import("std");
const bitmap = @import("bitmap");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "phase 1 bitmap range aliases preserve edges and tail-aware predicates" {
    const nbits = bits_per_long * 2 + 5;
    const start = bits_per_long - 3;
    const span = bits_per_long + 7;

    var direct = [_]Word{ 0, 0, 0 };
    var alias = [_]Word{ 0, 0, 0 };

    bitmap.setRange(&direct, start, span);
    bitmap.bitmap_set(&alias, start, span);
    try std.testing.expectEqualSlices(Word, &direct, &alias);

    bitmap.clearRange(&direct, start + 2, bits_per_long);
    bitmap.bitmap_clear(&alias, start + 2, bits_per_long);
    try std.testing.expectEqualSlices(Word, &direct, &alias);
    try std.testing.expectEqual(bitmap.weight(&direct, nbits), bitmap.weight(&alias, nbits));
    try std.testing.expectEqual(bitmap.empty(&direct, nbits), bitmap.empty(&alias, nbits));

    var with_tail_noise = direct;
    with_tail_noise[2] |= @as(Word, 1) << 9;
    const tail_only = [_]Word{ 0, 0, @as(Word, 1) << 9 };

    try std.testing.expect(bitmap.equal(&direct, &with_tail_noise, nbits));
    try std.testing.expect(bitmap.subset(&direct, &with_tail_noise, nbits));
    try std.testing.expect(bitmap.subset(&with_tail_noise, &direct, nbits));
    try std.testing.expect(!bitmap.intersects(&direct, &tail_only, nbits));
}

test "phase 1 bitmap scnprintf aliases keep merged cross-word ranges explicit" {
    const start = bits_per_long - 2;
    const run_len = 5;
    const later = bits_per_long + 6;
    const nbits = bits_per_long + 8;

    var map = [_]Word{ 0, 0 };
    bitmap.setRange(&map, start, run_len);
    bitmap.setRange(&map, later, 1);

    var expected_storage: [32]u8 = undefined;
    const expected = try std.fmt.bufPrint(
        &expected_storage,
        "{d}-{d},{d}",
        .{ start, start + run_len - 1, later },
    );

    var direct_buffer: [64]u8 = undefined;
    var alias_buffer: [64]u8 = undefined;
    const direct_len = bitmap.scnprintf(&map, nbits, &direct_buffer);
    const alias_len = bitmap.bitmap_scnprintf(&map, nbits, &alias_buffer);

    try std.testing.expectEqual(direct_len, alias_len);
    try std.testing.expectEqualStrings(expected, direct_buffer[0..direct_len]);
    try std.testing.expectEqualStrings(direct_buffer[0..direct_len], alias_buffer[0..alias_len]);

    var terminator_only_direct = [_]u8{0xaa};
    var terminator_only_alias = [_]u8{0xbb};
    try std.testing.expectEqual(@as(usize, 0), bitmap.scnprintf(&map, nbits, terminator_only_direct[0..1]));
    try std.testing.expectEqual(@as(usize, 0), bitmap.bitmap_scnprintf(&map, nbits, terminator_only_alias[0..1]));
    try std.testing.expectEqual(@as(u8, 0), terminator_only_direct[0]);
    try std.testing.expectEqual(@as(u8, 0), terminator_only_alias[0]);

    var zero_length_direct = [_]u8{0xcc};
    var zero_length_alias = [_]u8{0xdd};
    try std.testing.expectEqual(@as(usize, 0), bitmap.scnprintf(&map, nbits, zero_length_direct[0..0]));
    try std.testing.expectEqual(@as(usize, 0), bitmap.bitmap_scnprintf(&map, nbits, zero_length_alias[0..0]));
    try std.testing.expectEqual(@as(u8, 0xcc), zero_length_direct[0]);
    try std.testing.expectEqual(@as(u8, 0xdd), zero_length_alias[0]);
}
