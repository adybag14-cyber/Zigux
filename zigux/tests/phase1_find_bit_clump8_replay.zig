const std = @import("std");
const find_bit = @import("find_bit");

test "phase1 find_bit clump8 replay preserves aligned byte scans across words" {
    const bitmap = [_]find_bit.Word{
        (@as(find_bit.Word, 0x42) << 8) | (@as(find_bit.Word, 0xa5) << 24),
        @as(find_bit.Word, 0x01) << 8,
    };
    const nbits = find_bit.bits_per_long * 2;

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 8), find_bit.findFirstClump8(&clump, &bitmap, nbits));
    try std.testing.expectEqual(@as(u8, 0x42), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, 8), find_bit.findNextClump8(&clump, &bitmap, nbits, 10));
    try std.testing.expectEqual(@as(u8, 0x42), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 8), find_bit.findNextClump8(&clump, &bitmap, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(u8, 0x01), clump);
}

test "phase1 find_bit clump8 replay keeps partial tail bytes reachable and masked" {
    const nbits = find_bit.bits_per_long + 5;
    const reachable_tail = [_]find_bit.Word{ 0, @as(find_bit.Word, 1) << 3 };
    const masked_tail = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 6) };

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findFirstClump8(&clump, &reachable_tail, nbits));
    try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findFirstClump8(&clump, &masked_tail, nbits));
    try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);
}

test "phase1 find_bit clump8 replay leaves caller byte untouched for empty windows" {
    const empty = [_]find_bit.Word{0};
    const populated = [_]find_bit.Word{@as(find_bit.Word, 1) << 3};

    var clump: u8 = 0xaa;
    try std.testing.expectEqual(@as(usize, 8), find_bit.findFirstClump8(&clump, &empty, 8));
    try std.testing.expectEqual(@as(u8, 0xaa), clump);

    try std.testing.expectEqual(@as(usize, 8), find_bit.findNextClump8(&clump, &empty, 8, 4));
    try std.testing.expectEqual(@as(u8, 0xaa), clump);

    clump = 0x5a;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstClump8(&clump, &populated, 0));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);

    try std.testing.expectEqual(@as(usize, 8), find_bit.findNextClump8(&clump, &populated, 8, 8));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);
    try std.testing.expectEqual(@as(usize, 8), find_bit.findNextClump8(&clump, &populated, 8, 12));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);
}

test "phase1 find_bit clump8 replay keeps wrapper variants aligned with the direct entrypoints" {
    const bitmap = [_]find_bit.Word{@as(find_bit.Word, 1) << 3};
    var clump: u8 = 0;

    try std.testing.expectEqual(@as(usize, 0), find_bit.find_first_clump8(&clump, &bitmap, 8));
    try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit._find_first_clump8(&clump, &bitmap, 8));
    try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.find_next_clump8(&clump, &bitmap, 8, 0));
    try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit._find_next_clump8(&clump, &bitmap, 8, 0));
    try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);
}
