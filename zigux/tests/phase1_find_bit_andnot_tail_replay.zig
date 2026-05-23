const std = @import("std");
const find_bit = @import("find_bit");

test "single-word andnot scans clamp out-of-range tail bits" {
    const nbits = 11;
    const boundary = nbits - 1;
    const lhs = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << 2) |
            (@as(find_bit.Word, 1) << @intCast(boundary)) |
            (@as(find_bit.Word, 1) << 13),
    };
    const rhs = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << 2) | (@as(find_bit.Word, 1) << 13),
    };

    try std.testing.expectEqual(@as(usize, boundary), find_bit.findFirstAndNotBit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, boundary), find_bit.findNextAndNotBit(&lhs, &rhs, nbits, boundary));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndNotBit(&lhs, &rhs, nbits, boundary + 1));
}

test "tail-word andnot scans skip earlier matches before clamping" {
    const nbits = find_bit.bits_per_long + 6;
    const lhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 1) |
            (@as(find_bit.Word, 1) << 4) |
            (@as(find_bit.Word, 1) << 9),
    };
    const rhs = [_]find_bit.Word{
        0,
        @as(find_bit.Word, 1) << 1,
    };

    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 4),
        find_bit.findFirstAndNotBit(&lhs, &rhs, nbits),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 4),
        find_bit.findNextAndNotBit(&lhs, &rhs, nbits, find_bit.bits_per_long + 2),
    );
    try std.testing.expectEqual(
        @as(usize, nbits),
        find_bit.findNextAndNotBit(&lhs, &rhs, nbits, find_bit.bits_per_long + 5),
    );
}

test "tail-word andnot inclusive boundary keeps the last in-range bit reachable" {
    const tail_bits: usize = 5;
    const boundary = find_bit.bits_per_long + tail_bits - 1;
    const nbits = boundary + 1;
    const lhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << @intCast(tail_bits - 1)) |
            (@as(find_bit.Word, 1) << @intCast(tail_bits + 2)),
    };
    const rhs = [_]find_bit.Word{
        0,
        @as(find_bit.Word, 1) << @intCast(tail_bits + 2),
    };

    try std.testing.expectEqual(@as(usize, boundary), find_bit.findFirstAndNotBit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, boundary), find_bit.findNextAndNotBit(&lhs, &rhs, nbits, boundary));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndNotBit(&lhs, &rhs, nbits, boundary + 1));
}
