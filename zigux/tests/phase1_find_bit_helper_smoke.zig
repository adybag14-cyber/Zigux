const std = @import("std");
const find_bit = @import("find_bit");

fn word(bit: usize) find_bit.Word {
    return @as(find_bit.Word, 1) << @intCast(bit);
}

test "phase1 find_bit helper smoke keeps alias scans aligned" {
    const nbits = find_bit.bits_per_long * 2;
    const set_map = [_]find_bit.Word{
        word(5) | word(11),
        word(2) | word(7),
    };
    const zero_map = [_]find_bit.Word{
        ~word(9),
        ~word(1),
    };
    const and_lhs = [_]find_bit.Word{
        word(4) | word(9),
        word(0) | word(7),
    };
    const and_rhs = [_]find_bit.Word{
        word(9),
        word(0) | word(7),
    };
    const andnot_lhs = [_]find_bit.Word{
        word(3) | word(11),
        word(1) | word(6),
    };
    const andnot_rhs = [_]find_bit.Word{
        word(11),
        word(6),
    };

    try std.testing.expectEqual(
        find_bit.findFirstBit(&set_map, nbits),
        find_bit.find_first_bit(&set_map, nbits),
    );
    try std.testing.expectEqual(
        find_bit.findFirstBit(&set_map, nbits),
        find_bit._find_first_bit(&set_map, nbits),
    );
    try std.testing.expectEqual(
        find_bit.findFirstAndBit(&and_lhs, &and_rhs, nbits),
        find_bit.find_first_and_bit(&and_lhs, &and_rhs, nbits),
    );
    try std.testing.expectEqual(
        find_bit.findFirstAndNotBit(&andnot_lhs, &andnot_rhs, nbits),
        find_bit.find_first_andnot_bit(&andnot_lhs, &andnot_rhs, nbits),
    );
    try std.testing.expectEqual(
        find_bit.findFirstZeroBit(&zero_map, nbits),
        find_bit.find_first_zero_bit(&zero_map, nbits),
    );
    try std.testing.expectEqual(
        find_bit.findNextBit(&set_map, nbits, 6),
        find_bit.find_next_bit(&set_map, nbits, 6),
    );
    try std.testing.expectEqual(
        find_bit.findNextAndBit(&and_lhs, &and_rhs, nbits, 10),
        find_bit.find_next_and_bit(&and_lhs, &and_rhs, nbits, 10),
    );
    try std.testing.expectEqual(
        find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, 4),
        find_bit.find_next_andnot_bit(&andnot_lhs, &andnot_rhs, nbits, 4),
    );
    try std.testing.expectEqual(
        find_bit.findNextZeroBit(&zero_map, nbits, 10),
        find_bit.find_next_zero_bit(&zero_map, nbits, 10),
    );
    try std.testing.expectEqual(
        find_bit.findLastBit(&set_map, nbits),
        find_bit.find_last_bit(&set_map, nbits),
    );
}

test "phase1 find_bit helper smoke keeps tail and clump routes reviewable" {
    const nbits = find_bit.bits_per_long + 5;
    const tail_map = [_]find_bit.Word{
        0,
        word(1) | word(4) | word(9),
    };
    const tail_andnot_lhs = [_]find_bit.Word{
        0,
        word(1) | word(4) | word(9),
    };
    const tail_andnot_rhs = [_]find_bit.Word{
        0,
        word(1),
    };
    const full_tail = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        find_bit.lastWordMask(nbits),
    };

    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 1),
        find_bit.findNextBit(&tail_map, nbits, find_bit.bits_per_long),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 4),
        find_bit.findNextAndNotBit(&tail_andnot_lhs, &tail_andnot_rhs, nbits, find_bit.bits_per_long + 2),
    );
    try std.testing.expectEqual(
        @as(usize, nbits),
        find_bit.findNextBit(&tail_map, nbits, find_bit.bits_per_long + 5),
    );
    try std.testing.expectEqual(
        @as(usize, nbits),
        find_bit.findFirstZeroBit(&full_tail, nbits),
    );

    var clump: u8 = 0;
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long),
        find_bit.findFirstClump8(&clump, &tail_map, nbits),
    );
    try std.testing.expectEqual(@as(u8, 0b0001_0010), clump);
    try std.testing.expectEqual(
        clump,
        blk: {
            var alias_clump: u8 = 0;
            _ = find_bit.find_first_clump8(&alias_clump, &tail_map, nbits);
            break :blk alias_clump;
        },
    );
    try std.testing.expectEqual(
        @as(u8, 0x12),
        find_bit.getValue8(&[_]find_bit.Word{
            0,
            @as(find_bit.Word, 0x12),
        }, find_bit.bits_per_long),
    );
}
