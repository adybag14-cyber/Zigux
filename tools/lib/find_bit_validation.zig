const std = @import("std");
const find_bit = @import("find_bit.zig");

const Word = find_bit.Word;
const bits_per_long = find_bit.bits_per_long;

fn setBit(bitmap: []Word, bit: usize) void {
    const idx = bit / bits_per_long;
    const shift = bit & (bits_per_long - 1);
    bitmap[idx] |= @as(Word, 1) << @intCast(shift);
}

fn bitIsSet(bitmap: []const Word, bit: usize) bool {
    const idx = bit / bits_per_long;
    const shift = bit & (bits_per_long - 1);
    return ((bitmap[idx] >> @intCast(shift)) & 1) != 0;
}

fn fillPattern(bitmap: []Word, seed: u64) void {
    var state = seed;
    for (bitmap, 0..) |*word, idx| {
        state = state *% 0x9e3779b97f4a7c15 +% 0xbf58476d1ce4e5b9;
        const mixed = state ^ (state >> 23) ^ (@as(u64, idx) << 7);
        word.* = @as(Word, @truncate(mixed));
    }
}

fn refFindFirstBit(bitmap: []const Word, nbits: usize) usize {
    return refFindNextBit(bitmap, nbits, 0);
}

fn refFindNextBit(bitmap: []const Word, nbits: usize, start: usize) usize {
    var bit = start;
    while (bit < nbits) : (bit += 1) {
        if (bitIsSet(bitmap, bit)) {
            return bit;
        }
    }
    return nbits;
}

fn refFindFirstZeroBit(bitmap: []const Word, nbits: usize) usize {
    return refFindNextZeroBit(bitmap, nbits, 0);
}

fn refFindNextZeroBit(bitmap: []const Word, nbits: usize, start: usize) usize {
    var bit = start;
    while (bit < nbits) : (bit += 1) {
        if (!bitIsSet(bitmap, bit)) {
            return bit;
        }
    }
    return nbits;
}

fn refFindFirstAndBit(lhs: []const Word, rhs: []const Word, nbits: usize) usize {
    return refFindNextAndBit(lhs, rhs, nbits, 0);
}

fn refFindNextAndBit(lhs: []const Word, rhs: []const Word, nbits: usize, start: usize) usize {
    var bit = start;
    while (bit < nbits) : (bit += 1) {
        if (bitIsSet(lhs, bit) and bitIsSet(rhs, bit)) {
            return bit;
        }
    }
    return nbits;
}

fn refFindNextOrBit(lhs: []const Word, rhs: []const Word, nbits: usize, start: usize) usize {
    var bit = start;
    while (bit < nbits) : (bit += 1) {
        if (bitIsSet(lhs, bit) or bitIsSet(rhs, bit)) {
            return bit;
        }
    }
    return nbits;
}

fn refFindFirstAndNotBit(lhs: []const Word, rhs: []const Word, nbits: usize) usize {
    return refFindNextAndNotBit(lhs, rhs, nbits, 0);
}

fn refFindNextAndNotBit(lhs: []const Word, rhs: []const Word, nbits: usize, start: usize) usize {
    var bit = start;
    while (bit < nbits) : (bit += 1) {
        if (bitIsSet(lhs, bit) and !bitIsSet(rhs, bit)) {
            return bit;
        }
    }
    return nbits;
}

fn refFindLastBit(bitmap: []const Word, nbits: usize) usize {
    if (nbits == 0) {
        return 0;
    }

    var bit = nbits;
    while (bit > 0) {
        bit -= 1;
        if (bitIsSet(bitmap, bit)) {
            return bit;
        }
    }

    return nbits;
}

const RefClump = struct {
    offset: usize,
    value: u8,
};

fn refFindNextClump8(bitmap: []const Word, nbits: usize, start: usize) ?RefClump {
    const next = refFindNextBit(bitmap, nbits, start);
    if (next == nbits) {
        return null;
    }

    const clump_offset = next & ~@as(usize, 7);
    var value: u8 = 0;
    var bit: usize = 0;
    while (bit < 8 and clump_offset + bit < nbits) : (bit += 1) {
        if (bitIsSet(bitmap, clump_offset + bit)) {
            value |= @as(u8, 1) << @intCast(bit);
        }
    }

    return .{ .offset = clump_offset, .value = value };
}

test "find_bit helpers match naive reference scans across bounded patterned inputs" {
    const max_words = 3;
    const max_nbits = bits_per_long * 2 + 9;
    const case_count = 24;

    var lhs_storage = [_]Word{0} ** max_words;
    var rhs_storage = [_]Word{0} ** max_words;

    for (0..max_nbits + 1) |nbits| {
        const nwords = find_bit.bitsToWords(nbits);
        const lhs = lhs_storage[0..nwords];
        const rhs = rhs_storage[0..nwords];

        for (0..case_count) |case_id| {
            @memset(lhs_storage[0..], 0);
            @memset(rhs_storage[0..], 0);
            fillPattern(lhs_storage[0..], 0x1357_2468_ace0_ff11 ^ @as(u64, case_id) ^ @as(u64, nbits));
            fillPattern(rhs_storage[0..], 0xfedc_ba98_7654_3210 ^ (@as(u64, case_id) << 11) ^ @as(u64, nbits));

            if (nbits != 0) {
                setBit(lhs_storage[0..], 0);
                setBit(rhs_storage[0..], nbits - 1);
                if (nbits > bits_per_long) {
                    setBit(lhs_storage[0..], bits_per_long);
                    setBit(rhs_storage[0..], bits_per_long - 1);
                }
            }

            try std.testing.expectEqual(refFindFirstBit(lhs, nbits), find_bit.findFirstBit(lhs, nbits));
            try std.testing.expectEqual(refFindFirstZeroBit(lhs, nbits), find_bit.findFirstZeroBit(lhs, nbits));
            try std.testing.expectEqual(refFindFirstAndBit(lhs, rhs, nbits), find_bit.findFirstAndBit(lhs, rhs, nbits));
            try std.testing.expectEqual(refFindFirstAndNotBit(lhs, rhs, nbits), find_bit.findFirstAndNotBit(lhs, rhs, nbits));
            try std.testing.expectEqual(refFindLastBit(lhs, nbits), find_bit.findLastBit(lhs, nbits));

            for (0..nbits + 2) |start| {
                try std.testing.expectEqual(refFindNextBit(lhs, nbits, start), find_bit.findNextBit(lhs, nbits, start));
                try std.testing.expectEqual(refFindNextZeroBit(lhs, nbits, start), find_bit.findNextZeroBit(lhs, nbits, start));
                try std.testing.expectEqual(refFindNextAndBit(lhs, rhs, nbits, start), find_bit.findNextAndBit(lhs, rhs, nbits, start));
                try std.testing.expectEqual(refFindNextOrBit(lhs, rhs, nbits, start), find_bit.findNextOrBit(lhs, rhs, nbits, start));
                try std.testing.expectEqual(refFindNextAndNotBit(lhs, rhs, nbits, start), find_bit.findNextAndNotBit(lhs, rhs, nbits, start));
            }
        }
    }
}

test "clump8 helpers match a byte-wise reference and preserve caller state on misses" {
    const max_words = 3;
    const max_nbits = bits_per_long * 2 + 9;
    const case_count = 24;

    var storage = [_]Word{0} ** max_words;

    for (0..max_nbits + 1) |nbits| {
        const nwords = find_bit.bitsToWords(nbits);
        const bitmap = storage[0..nwords];

        for (0..case_count) |case_id| {
            @memset(storage[0..], 0);
            fillPattern(storage[0..], 0x0123_4567_89ab_cdef ^ (@as(u64, case_id) << 9) ^ @as(u64, nbits));

            if (nbits != 0) {
                setBit(storage[0..], 0);
                setBit(storage[0..], nbits - 1);
            }

            var first_clump: u8 = 0xaa;
            if (refFindNextClump8(bitmap, nbits, 0)) |expected| {
                try std.testing.expectEqual(expected.offset, find_bit.findFirstClump8(&first_clump, bitmap, nbits));
                try std.testing.expectEqual(expected.value, first_clump);
            } else {
                try std.testing.expectEqual(nbits, find_bit.findFirstClump8(&first_clump, bitmap, nbits));
                try std.testing.expectEqual(@as(u8, 0xaa), first_clump);
            }

            for (0..nbits + 3) |start| {
                var clump: u8 = 0x5a;
                if (refFindNextClump8(bitmap, nbits, start)) |expected| {
                    try std.testing.expectEqual(expected.offset, find_bit.findNextClump8(&clump, bitmap, nbits, start));
                    try std.testing.expectEqual(expected.value, clump);
                } else {
                    try std.testing.expectEqual(nbits, find_bit.findNextClump8(&clump, bitmap, nbits, start));
                    try std.testing.expectEqual(@as(u8, 0x5a), clump);
                }
            }
        }
    }
}

test "alias entry points stay in lockstep with the primary helper APIs" {
    const nbits = bits_per_long + 5;
    const lhs = [_]Word{ (@as(Word, 1) << 2) | (@as(Word, 1) << 7), (@as(Word, 1) << 3) | (@as(Word, 1) << 9) };
    const rhs = [_]Word{ (@as(Word, 1) << 7), @as(Word, 1) << 3 };

    try std.testing.expectEqual(find_bit.findFirstBit(&lhs, nbits), find_bit.find_first_bit(&lhs, nbits));
    try std.testing.expectEqual(find_bit.findFirstBit(&lhs, nbits), find_bit._find_first_bit(&lhs, nbits));
    try std.testing.expectEqual(find_bit.findFirstZeroBit(&lhs, nbits), find_bit.find_first_zero_bit(&lhs, nbits));
    try std.testing.expectEqual(find_bit.findFirstZeroBit(&lhs, nbits), find_bit._find_first_zero_bit(&lhs, nbits));
    try std.testing.expectEqual(find_bit.findFirstAndBit(&lhs, &rhs, nbits), find_bit.find_first_and_bit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(find_bit.findFirstAndBit(&lhs, &rhs, nbits), find_bit._find_first_and_bit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(find_bit.findFirstAndNotBit(&lhs, &rhs, nbits), find_bit.find_first_andnot_bit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(find_bit.findFirstAndNotBit(&lhs, &rhs, nbits), find_bit._find_first_andnot_bit(&lhs, &rhs, nbits));

    try std.testing.expectEqual(find_bit.findNextBit(&lhs, nbits, 3), find_bit.find_next_bit(&lhs, nbits, 3));
    try std.testing.expectEqual(find_bit.findNextBit(&lhs, nbits, 3), find_bit._find_next_bit(&lhs, nbits, 3));
    try std.testing.expectEqual(find_bit.findNextZeroBit(&lhs, nbits, 1), find_bit.find_next_zero_bit(&lhs, nbits, 1));
    try std.testing.expectEqual(find_bit.findNextZeroBit(&lhs, nbits, 1), find_bit._find_next_zero_bit(&lhs, nbits, 1));
    try std.testing.expectEqual(find_bit.findNextAndBit(&lhs, &rhs, nbits, 0), find_bit.find_next_and_bit(&lhs, &rhs, nbits, 0));
    try std.testing.expectEqual(find_bit.findNextAndBit(&lhs, &rhs, nbits, 0), find_bit._find_next_and_bit(&lhs, &rhs, nbits, 0));
    try std.testing.expectEqual(find_bit.findNextOrBit(&lhs, &rhs, nbits, 0), find_bit.find_next_or_bit(&lhs, &rhs, nbits, 0));
    try std.testing.expectEqual(find_bit.findNextOrBit(&lhs, &rhs, nbits, 0), find_bit._find_next_or_bit(&lhs, &rhs, nbits, 0));
    try std.testing.expectEqual(find_bit.findNextAndNotBit(&lhs, &rhs, nbits, 0), find_bit.find_next_andnot_bit(&lhs, &rhs, nbits, 0));
    try std.testing.expectEqual(find_bit.findNextAndNotBit(&lhs, &rhs, nbits, 0), find_bit._find_next_andnot_bit(&lhs, &rhs, nbits, 0));
    try std.testing.expectEqual(find_bit.findLastBit(&lhs, nbits), find_bit.find_last_bit(&lhs, nbits));
    try std.testing.expectEqual(find_bit.findLastBit(&lhs, nbits), find_bit._find_last_bit(&lhs, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(find_bit.findFirstClump8(&clump, &lhs, nbits), find_bit.find_first_clump8(&clump, &lhs, nbits));
    try std.testing.expectEqual(find_bit.findNextClump8(&clump, &lhs, nbits, 0), find_bit._find_next_clump8(&clump, &lhs, nbits, 0));
}
