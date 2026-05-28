const std = @import("std");
const find_bit = @import("find_bit");

test "phase1 find_bit replay keeps last-bit aliases tail-clamped" {
    const nbits = find_bit.bits_per_long + 5;
    var bitmap = [_]find_bit.Word{
        @as(find_bit.Word, 1) << 7,
        (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 9),
    };

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 3), find_bit.findLastBit(&bitmap, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 3), find_bit.find_last_bit(&bitmap, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 3), find_bit._find_last_bit(&bitmap, nbits));

    bitmap[1] &= ~(@as(find_bit.Word, 1) << 3);
    try std.testing.expectEqual(@as(usize, 7), find_bit.findLastBit(&bitmap, nbits));
    try std.testing.expectEqual(@as(usize, 7), find_bit.find_last_bit(&bitmap, nbits));
    try std.testing.expectEqual(@as(usize, 7), find_bit._find_last_bit(&bitmap, nbits));

    bitmap[0] = 0;
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findLastBit(&bitmap, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_last_bit(&bitmap, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_last_bit(&bitmap, nbits));
}

test "phase1 find_bit replay keeps clump aliases and caller-byte ownership aligned" {
    const nbits = find_bit.bits_per_long + 10;
    const bitmap = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << 9) | (@as(find_bit.Word, 1) << 14),
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 9),
    };

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 8), find_bit.findFirstClump8(&clump, &bitmap, nbits));
    try std.testing.expectEqual(@as(u8, 0b0100_0010), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findNextClump8(&clump, &bitmap, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(u8, 0b0000_0010), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, 8), find_bit.find_first_clump8(&clump, &bitmap, nbits));
    try std.testing.expectEqual(@as(u8, 0b0100_0010), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.find_next_clump8(&clump, &bitmap, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(u8, 0b0000_0010), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, 8), find_bit._find_first_clump8(&clump, &bitmap, nbits));
    try std.testing.expectEqual(@as(u8, 0b0100_0010), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit._find_next_clump8(&clump, &bitmap, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(u8, 0b0000_0010), clump);

    var untouched: u8 = 0x5a;
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextClump8(&untouched, &bitmap, nbits, nbits));
    try std.testing.expectEqual(@as(u8, 0x5a), untouched);
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_clump8(&untouched, &bitmap, nbits, nbits + 9));
    try std.testing.expectEqual(@as(u8, 0x5a), untouched);
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_clump8(&untouched, &bitmap, nbits, nbits + 17));
    try std.testing.expectEqual(@as(u8, 0x5a), untouched);
}

test "phase1 find_bit replay keeps partial-tail clumps and byte extraction aligned" {
    const nbits = find_bit.bits_per_long + 5;
    const tail_bitmap = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 6),
    };

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findFirstClump8(&clump, &tail_bitmap, nbits));
    try std.testing.expectEqual(@as(u8, 0b0100_1000), clump);

    const bytes = [_]find_bit.Word{
        (@as(find_bit.Word, 0x42) << 8) | (@as(find_bit.Word, 0xa5) << 24),
        @as(find_bit.Word, 0x11) << 8,
    };
    try std.testing.expectEqual(@as(u8, 0x42), find_bit.getValue8(&bytes, 8));
    try std.testing.expectEqual(@as(u8, 0xa5), find_bit.getValue8(&bytes, 24));
    try std.testing.expectEqual(@as(u8, 0x11), find_bit.getValue8(&bytes, find_bit.bits_per_long + 8));
}
