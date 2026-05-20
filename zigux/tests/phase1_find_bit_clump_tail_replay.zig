const std = @import("std");
const find_bit = @import("find_bit");

test "phase1 find_bit replay keeps clump8 byte alignment explicit across a word boundary" {
    const nbits = find_bit.bits_per_long * 2;
    var bitmap = [_]find_bit.Word{ 0, 0 };
    bitmap[0] |= @as(find_bit.Word, 1) << @intCast(find_bit.bits_per_long - 2);
    bitmap[0] |= @as(find_bit.Word, 1) << @intCast(find_bit.bits_per_long - 1);
    bitmap[1] |= (@as(find_bit.Word, 1) << 0) | (@as(find_bit.Word, 1) << 6);

    var primary_first: u8 = 0;
    var alias_first: u8 = 0;
    var underscore_first: u8 = 0;

    const first_offset = find_bit.findFirstClump8(&primary_first, &bitmap, nbits);
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long - 8), first_offset);
    try std.testing.expectEqual(@as(u8, 0b1100_0000), primary_first);

    try std.testing.expectEqual(first_offset, find_bit.find_first_clump8(&alias_first, &bitmap, nbits));
    try std.testing.expectEqual(primary_first, alias_first);
    try std.testing.expectEqual(first_offset, find_bit._find_first_clump8(&underscore_first, &bitmap, nbits));
    try std.testing.expectEqual(primary_first, underscore_first);

    var next_primary: u8 = 0;
    var next_alias: u8 = 0;
    var next_underscore: u8 = 0;
    const second_offset = find_bit.findNextClump8(&next_primary, &bitmap, nbits, find_bit.bits_per_long);
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), second_offset);
    try std.testing.expectEqual(@as(u8, 0b0100_0001), next_primary);

    try std.testing.expectEqual(second_offset, find_bit.find_next_clump8(&next_alias, &bitmap, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(next_primary, next_alias);
    try std.testing.expectEqual(second_offset, find_bit._find_next_clump8(&next_underscore, &bitmap, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(next_primary, next_underscore);
}

test "phase1 find_bit replay masks tail clumps and keeps past-end scans side-effect free" {
    const nbits = find_bit.bits_per_long + 5;
    const clump_bitmap = [_]find_bit.Word{
        0,
        @as(find_bit.Word, 1) << 4,
    };
    const noisy_tail_bitmap = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9),
    };

    var clump: u8 = 0;
    const offset = find_bit.findFirstClump8(&clump, &clump_bitmap, nbits);
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), offset);
    try std.testing.expectEqual(@as(u8, 0b0001_0000), clump);

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findLastBit(&noisy_tail_bitmap, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findNextBit(&noisy_tail_bitmap, nbits, find_bit.bits_per_long + 4));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextBit(&noisy_tail_bitmap, nbits, find_bit.bits_per_long + 5));

    var alias_clump: u8 = 0;
    try std.testing.expectEqual(offset, find_bit.find_first_clump8(&alias_clump, &clump_bitmap, nbits));
    try std.testing.expectEqual(clump, alias_clump);

    var untouched: u8 = 0x5a;
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextClump8(&untouched, &clump_bitmap, nbits, nbits));
    try std.testing.expectEqual(@as(u8, 0x5a), untouched);
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_clump8(&untouched, &clump_bitmap, nbits, nbits + 4));
    try std.testing.expectEqual(@as(u8, 0x5a), untouched);
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_clump8(&untouched, &clump_bitmap, nbits, nbits + 9));
    try std.testing.expectEqual(@as(u8, 0x5a), untouched);
}
