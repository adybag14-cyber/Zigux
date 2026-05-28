const std = @import("std");
const find_bit = @import("find_bit");

const iterations_find_bit = 20_000;
const expected_checksum: u64 = 15_621_472;

fn seedMap() [find_bit.bitsToWords(4096)]find_bit.Word {
    var map = std.mem.zeroes([find_bit.bitsToWords(4096)]find_bit.Word);
    map[0] |= (@as(find_bit.Word, 1) << 3);
    map[7] |= (@as(find_bit.Word, 1) << 9);
    map[15] |= (@as(find_bit.Word, 1) << 17);
    map[31] |= (@as(find_bit.Word, 1) << 1);
    return map;
}

fn runFindNextBitReplay() u64 {
    const map = seedMap();
    var checksum: u64 = 0;
    var idx: usize = 0;
    while (idx < iterations_find_bit) : (idx += 1) {
        checksum +%= @intCast(find_bit.findNextBit(&map, 4096, idx % 1024));
    }
    return checksum;
}

test "phase1 find_next_bit bench replay keeps the offset witnesses explicit" {
    const map = seedMap();
    try std.testing.expectEqual(@as(usize, 3), find_bit.findNextBit(&map, 4096, 0));
    try std.testing.expectEqual(@as(usize, 3), find_bit.findNextBit(&map, 4096, 3));
    try std.testing.expectEqual(@as(usize, 457), find_bit.findNextBit(&map, 4096, 4));
    try std.testing.expectEqual(@as(usize, 457), find_bit.findNextBit(&map, 4096, 457));
    try std.testing.expectEqual(@as(usize, 977), find_bit.findNextBit(&map, 4096, 458));
    try std.testing.expectEqual(@as(usize, 977), find_bit.findNextBit(&map, 4096, 977));
    try std.testing.expectEqual(@as(usize, 1985), find_bit.findNextBit(&map, 4096, 978));
    try std.testing.expectEqual(@as(usize, 1985), find_bit.findNextBit(&map, 4096, 1023));
}

test "phase1 find_next_bit bench replay keeps the exact 20000-iteration checksum" {
    try std.testing.expectEqual(expected_checksum, runFindNextBitReplay());
}
