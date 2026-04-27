const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;
const bitmap_nbits: usize = 1024;
const word_count: usize = bitmap.bitsToWords(bitmap_nbits);

fn expectSet(map: []const Word, bit: usize) !void {
    try std.testing.expect(((map[bit / bits_per_long] >> @intCast(bit % bits_per_long)) & 1) == 1);
}

fn expectClear(map: []const Word, bit: usize) !void {
    try std.testing.expect(((map[bit / bits_per_long] >> @intCast(bit % bits_per_long)) & 1) == 0);
}

test "bitmap diff gate records exact partial fill and zero checks" {
    var map = [_]Word{0} ** word_count;

    bitmap.fill(map[0..bitmap.bitsToWords(35)], 35);
    try std.testing.expectEqual(@as(usize, 35), bitmap.weight(&map, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstBit(&map, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, 35), find_bit.findFirstZeroBit(&map, bitmap_nbits));
    try expectSet(&map, 34);
    try expectClear(&map, 35);
    try expectClear(&map, bits_per_long);

    bitmap.fill(&map, bitmap_nbits);
    bitmap.zero(map[0..bitmap.bitsToWords(35)], 35);
    try std.testing.expectEqual(@as(usize, bits_per_long), find_bit.findFirstBit(&map, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstZeroBit(&map, bitmap_nbits));
    try expectClear(&map, bits_per_long - 1);
    try expectSet(&map, bits_per_long);
}

test "bitmap diff gate records exact copy and copyClearTail checks" {
    const nbits = bits_per_long + 5;
    const src = [_]Word{ ~@as(Word, 0), ~@as(Word, 0), 0 };
    var dst = [_]Word{ ~@as(Word, 0), ~@as(Word, 0), ~@as(Word, 0) };

    bitmap.copy(&dst, &src, nbits);
    try std.testing.expectEqual(~@as(Word, 0), dst[0]);
    try std.testing.expectEqual(~@as(Word, 0), dst[1]);
    try std.testing.expectEqual(~@as(Word, 0), dst[2]);

    bitmap.fill(&dst, bits_per_long * 3);
    bitmap.copyClearTail(&dst, &src, nbits);
    try std.testing.expectEqual(~@as(Word, 0), dst[0]);
    try std.testing.expectEqual(bitmap.lastWordMask(nbits), dst[1]);
    try std.testing.expectEqual(~@as(Word, 0), dst[2]);
    try std.testing.expectEqual(@as(usize, nbits), bitmap.weight(dst[0..2], nbits));
}

test "bitmap diff gate records exact scnprintf and masked xor checks" {
    var map = [_]Word{ 0, 0 };
    bitmap.setRange(&map, 1, 3);
    bitmap.setRange(&map, 7, 1);
    bitmap.setRange(&map, 10, 2);

    var buffer: [64]u8 = undefined;
    const len = bitmap.scnprintf(&map, 32, &buffer);
    try std.testing.expectEqualStrings("1-3,7,10-11", buffer[0..len]);

    var trunc_buffer = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa };
    const trunc_len = bitmap.scnprintf(&map, 8, &trunc_buffer);
    try std.testing.expectEqual(@as(usize, 3), trunc_len);
    try std.testing.expectEqualStrings("1-3", trunc_buffer[0..trunc_len]);
    try std.testing.expectEqual(@as(u8, 0), trunc_buffer[trunc_len]);

    const lhs = [_]Word{0b1_1111};
    const rhs = [_]Word{0b1_0001};
    var dst = [_]Word{0};
    bitmap.xorBits(&dst, &lhs, &rhs, 4);
    try std.testing.expectEqual(@as(Word, 0b1110), dst[0] & bitmap.lastWordMask(4));
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstZeroBit(&dst, 4));
}
