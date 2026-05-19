const std = @import("std");
const find_bit = @import("find_bit");

const Word = find_bit.Word;
const bits_per_long = find_bit.bits_per_long;

test "phase1 find_bit replay keeps the last aligned byte of a word visible" {
    const boundary_offset = bits_per_long - 8;
    const nbits = bits_per_long * 2;
    const bitmap = [_]Word{
        @as(Word, 0x80) << @intCast(boundary_offset),
        (@as(Word, 1) << 0) | (@as(Word, 1) << 5),
    };

    try std.testing.expectEqual(@as(u8, 0x80), find_bit.getValue8(&bitmap, boundary_offset));

    var clump: u8 = 0;
    try std.testing.expectEqual(boundary_offset, find_bit.findNextClump8(&clump, &bitmap, nbits, boundary_offset));
    try std.testing.expectEqual(@as(u8, 0x80), clump);

    clump = 0;
    try std.testing.expectEqual(boundary_offset, find_bit.findNextClump8(&clump, &bitmap, nbits, boundary_offset + 1));
    try std.testing.expectEqual(@as(u8, 0x80), clump);

    clump = 0;
    try std.testing.expectEqual(bits_per_long, find_bit.findNextClump8(&clump, &bitmap, nbits, bits_per_long));
    try std.testing.expectEqual(@as(u8, 0b0010_0001), clump);
}

test "phase1 find_bit replay ignores out-of-range tail bits once the in-range tail bit is behind start" {
    const nbits = bits_per_long + 5;
    const bitmap = [_]Word{ 0, (@as(Word, 1) << 3) | (@as(Word, 1) << 6) };

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, bits_per_long), find_bit.findFirstClump8(&clump, &bitmap, nbits));
    try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, bits_per_long), find_bit.findNextClump8(&clump, &bitmap, nbits, bits_per_long + 2));
    try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);

    clump = 0x5a;
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextClump8(&clump, &bitmap, nbits, bits_per_long + 4));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);
}
