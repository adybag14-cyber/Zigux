const std = @import("std");
const find_bit = @import("find_bit");

const Word = find_bit.Word;
const bits_per_long = find_bit.bits_per_long;

test "phase 1 findLastBit clamps a partial tail word to in-range bits" {
    const nbits = bits_per_long + 5;
    const in_range_tail = bits_per_long + 4;
    const masked_tail = bits_per_long + 8;
    const map = [_]Word{
        @as(Word, 1) << 7,
        (@as(Word, 1) << 4) | (@as(Word, 1) << 8),
    };

    try std.testing.expectEqual(in_range_tail, find_bit.findLastBit(&map, nbits));
    try std.testing.expectEqual(in_range_tail, find_bit.find_last_bit(&map, nbits));
    try std.testing.expectEqual(in_range_tail, find_bit._find_last_bit(&map, nbits));
    try std.testing.expect(masked_tail >= nbits);
}

test "phase 1 findLastBit returns nbits when only masked tail storage remains" {
    const nbits = bits_per_long + 5;
    const map = [_]Word{
        0,
        @as(Word, 1) << 8,
    };

    try std.testing.expectEqual(nbits, find_bit.findLastBit(&map, nbits));
    try std.testing.expectEqual(nbits, find_bit.find_last_bit(&map, nbits));
    try std.testing.expectEqual(nbits, find_bit._find_last_bit(&map, nbits));
}

test "phase 1 findLastBit keeps exact-word windows fenced from later storage" {
    const nbits = bits_per_long;
    const map = [_]Word{
        (@as(Word, 1) << 2) | (@as(Word, 1) << @intCast(bits_per_long - 1)),
        ~@as(Word, 0),
    };

    try std.testing.expectEqual(bits_per_long - 1, find_bit.findLastBit(map[0..1], nbits));
    try std.testing.expectEqual(bits_per_long - 1, find_bit.find_last_bit(map[0..1], nbits));
    try std.testing.expectEqual(bits_per_long - 1, find_bit._find_last_bit(map[0..1], nbits));
}
