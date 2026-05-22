const std = @import("std");
const find_bit = @import("find_bit");

test "phase1 find_bit clump8 replay keeps aligned bytes inside their containing word" {
    const last_aligned_byte = find_bit.bits_per_long - 8;
    const bitmap = [_]find_bit.Word{
        @as(find_bit.Word, 0xA5) << @intCast(last_aligned_byte),
        @as(find_bit.Word, 0x11),
    };

    try std.testing.expectEqual(@as(u8, 0xA5), find_bit.getValue8(&bitmap, last_aligned_byte));
    try std.testing.expectEqual(@as(u8, 0x11), find_bit.getValue8(&bitmap, find_bit.bits_per_long));
}

test "phase1 find_bit clump8 replay masks partial tail bytes and keeps aliases aligned" {
    const nbits = find_bit.bits_per_long + 5;
    const bitmap = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 6),
    };

    var direct_first: u8 = 0;
    var linux_first: u8 = 0;
    var underscore_first: u8 = 0;

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findFirstClump8(&direct_first, &bitmap, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.find_first_clump8(&linux_first, &bitmap, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit._find_first_clump8(&underscore_first, &bitmap, nbits));

    try std.testing.expectEqual(@as(u8, 0b0000_1000), direct_first);
    try std.testing.expectEqual(direct_first, linux_first);
    try std.testing.expectEqual(direct_first, underscore_first);

    var direct_next: u8 = 0;
    var linux_next: u8 = 0;
    var underscore_next: u8 = 0;

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findNextClump8(&direct_next, &bitmap, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.find_next_clump8(&linux_next, &bitmap, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit._find_next_clump8(&underscore_next, &bitmap, nbits, find_bit.bits_per_long));

    try std.testing.expectEqual(direct_first, direct_next);
    try std.testing.expectEqual(direct_next, linux_next);
    try std.testing.expectEqual(direct_next, underscore_next);
}

test "phase1 find_bit clump8 replay leaves the caller byte untouched when no set bit remains" {
    const empty = [_]find_bit.Word{0};
    var clump: u8 = 0x5A;

    try std.testing.expectEqual(@as(usize, 8), find_bit.findFirstClump8(&clump, &empty, 8));
    try std.testing.expectEqual(@as(u8, 0x5A), clump);

    try std.testing.expectEqual(@as(usize, 8), find_bit.findNextClump8(&clump, &empty, 8, 4));
    try std.testing.expectEqual(@as(u8, 0x5A), clump);

    try std.testing.expectEqual(@as(usize, 8), find_bit.find_next_clump8(&clump, &empty, 8, 8));
    try std.testing.expectEqual(@as(u8, 0x5A), clump);

    try std.testing.expectEqual(@as(usize, 8), find_bit._find_next_clump8(&clump, &empty, 8, 12));
    try std.testing.expectEqual(@as(u8, 0x5A), clump);
}
