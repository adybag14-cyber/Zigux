const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");

test "phase1 bitmap extend render replay keeps partial copy-and-extend aliases aligned" {
    const count = find_bit.bits_per_long + 5;
    const size = find_bit.bits_per_long * 3;
    const src = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9),
        ~@as(find_bit.Word, 0),
    };

    var direct = [_]find_bit.Word{ 0xaa55, 0xaa55, 0xaa55 };
    var alias = [_]find_bit.Word{ 0xaa55, 0xaa55, 0xaa55 };

    bitmap.copyAndExtend(&direct, &src, count, size);
    bitmap.bitmap_copy_and_extend(&alias, &src, count, size);

    try std.testing.expectEqualSlices(find_bit.Word, &direct, &alias);
    try std.testing.expectEqual(src[0], direct[0]);
    try std.testing.expectEqual((@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4), direct[1]);
    try std.testing.expectEqual(@as(find_bit.Word, 0), direct[2]);
}

test "phase1 bitmap extend render replay keeps exact-word extension aliases aligned" {
    const count = find_bit.bits_per_long * 2;
    const size = find_bit.bits_per_long * 3;
    const src = [_]find_bit.Word{ 0x55aa, 0xaa55, ~@as(find_bit.Word, 0) };

    var direct = [_]find_bit.Word{ ~@as(find_bit.Word, 0), ~@as(find_bit.Word, 0), ~@as(find_bit.Word, 0) };
    var alias = [_]find_bit.Word{ ~@as(find_bit.Word, 0), ~@as(find_bit.Word, 0), ~@as(find_bit.Word, 0) };

    bitmap.copyAndExtend(&direct, &src, count, size);
    bitmap.bitmap_copy_and_extend(&alias, &src, count, size);

    try std.testing.expectEqualSlices(find_bit.Word, &direct, &alias);
    try std.testing.expectEqual(src[0], direct[0]);
    try std.testing.expectEqual(src[1], direct[1]);
    try std.testing.expectEqual(@as(find_bit.Word, 0), direct[2]);
}

test "phase1 bitmap extend render replay keeps rendering aliases aligned" {
    const nbits = find_bit.bits_per_long * 2;
    var map = [_]find_bit.Word{ 0, 0 };
    bitmap.setRange(&map, 1, 3);
    bitmap.bitmap_set(&map, find_bit.bits_per_long + 2, 2);
    bitmap.bitmap_set(&map, find_bit.bits_per_long + 7, 1);

    var direct_buffer: [64]u8 = undefined;
    var alias_buffer: [64]u8 = undefined;
    const direct_len = bitmap.scnprintf(&map, nbits, &direct_buffer);
    const alias_len = bitmap.bitmap_scnprintf(&map, nbits, &alias_buffer);

    try std.testing.expectEqual(direct_len, alias_len);
    try std.testing.expectEqualStrings("1-3,66-67,71", direct_buffer[0..direct_len]);
    try std.testing.expectEqualStrings(direct_buffer[0..direct_len], alias_buffer[0..alias_len]);

    var empty_map = [_]find_bit.Word{0};
    var untouched = [_]u8{ 0xaa, 0xbb, 0xcc };
    const empty_len = bitmap.bitmap_scnprintf(&empty_map, 32, &untouched);
    try std.testing.expectEqual(@as(usize, 0), empty_len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xaa, 0xbb, 0xcc }, &untouched);
}
