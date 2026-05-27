const std = @import("std");
const find_bit = @import("find_bit.zig");

pub const Word = find_bit.Word;

pub fn findNextBitWrap(addr: []const Word, nbits: usize, start: usize) usize {
    const bit = find_bit.findNextBit(addr, nbits, start);
    if (bit < nbits or start == 0) {
        return bit;
    }

    const wrapped = find_bit.findFirstBit(addr, start);
    return if (wrapped < start) wrapped else nbits;
}

pub fn find_next_bit_wrap(addr: []const Word, nbits: usize, start: usize) usize {
    return findNextBitWrap(addr, nbits, start);
}

pub fn findNextAndBitWrap(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {
    const bit = find_bit.findNextAndBit(addr1, addr2, nbits, start);
    if (bit < nbits or start == 0) {
        return bit;
    }

    const wrapped = find_bit.findFirstAndBit(addr1, addr2, start);
    return if (wrapped < start) wrapped else nbits;
}

pub fn find_next_and_bit_wrap(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {
    return findNextAndBitWrap(addr1, addr2, nbits, start);
}

test "findNextBitWrap returns in-range matches before wrapping" {
    const nbits = find_bit.bits_per_long * 2;
    const bitmap = [_]Word{
        (@as(Word, 1) << 2) | (@as(Word, 1) << 9),
        (@as(Word, 1) << 1) | (@as(Word, 1) << 5),
    };

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 1), findNextBitWrap(&bitmap, nbits, 10));
    try std.testing.expectEqual(@as(usize, 2), findNextBitWrap(&bitmap, nbits, find_bit.bits_per_long + 6));
}

test "findNextBitWrap keeps zero and exhausted windows explicit" {
    const empty = [_]Word{0};

    try std.testing.expectEqual(@as(usize, 0), findNextBitWrap(&empty, 0, 0));
    try std.testing.expectEqual(@as(usize, 8), findNextBitWrap(&empty, 8, 0));
    try std.testing.expectEqual(@as(usize, 8), findNextBitWrap(&empty, 8, 7));
    try std.testing.expectEqual(@as(usize, 8), findNextBitWrap(&empty, 8, 8));
}

test "findNextAndBitWrap replays shared matches before wrapping" {
    const nbits = find_bit.bits_per_long * 2;
    const lhs = [_]Word{
        (@as(Word, 1) << 2) | (@as(Word, 1) << 9),
        (@as(Word, 1) << 1) | (@as(Word, 1) << 5),
    };
    const rhs = [_]Word{
        (@as(Word, 1) << 2),
        (@as(Word, 1) << 1) | (@as(Word, 1) << 5),
    };

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 1), findNextAndBitWrap(&lhs, &rhs, nbits, 10));
    try std.testing.expectEqual(@as(usize, 2), findNextAndBitWrap(&lhs, &rhs, nbits, find_bit.bits_per_long + 6));
}

test "Linux-style wrap aliases mirror the primary helpers" {
    const nbits = find_bit.bits_per_long * 2;
    const bitmap = [_]Word{
        (@as(Word, 1) << 3),
        (@as(Word, 1) << 2),
    };
    const rhs = [_]Word{
        (@as(Word, 1) << 3),
        (@as(Word, 1) << 2),
    };

    try std.testing.expectEqual(findNextBitWrap(&bitmap, nbits, find_bit.bits_per_long + 3), find_next_bit_wrap(&bitmap, nbits, find_bit.bits_per_long + 3));
    try std.testing.expectEqual(findNextAndBitWrap(&bitmap, &rhs, nbits, find_bit.bits_per_long + 3), find_next_and_bit_wrap(&bitmap, &rhs, nbits, find_bit.bits_per_long + 3));
}
