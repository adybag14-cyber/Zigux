const std = @import("std");
const find_bit = @import("find_bit");

test "phase 1 find_bit tail clamp and boundary replay stays explicit" {
    const boundary = find_bit.bits_per_long - 1;
    const head_nbits = find_bit.bits_per_long * 2;
    const tail_nbits = find_bit.bits_per_long + 5;
    const past_nbits = 7;

    const boundary_set = [_]find_bit.Word{ (@as(find_bit.Word, 1) << @intCast(boundary)), 0 };
    const boundary_zero = [_]find_bit.Word{ ~(@as(find_bit.Word, 1) << @intCast(boundary)), ~@as(find_bit.Word, 0) };
    const tail_only = [_]find_bit.Word{ 0, @as(find_bit.Word, 1) << 9 };
    const tail_full = [_]find_bit.Word{ ~@as(find_bit.Word, 0), find_bit.lastWordMask(tail_nbits) };
    const empty = [_]find_bit.Word{};

    try std.testing.expectEqual(boundary, find_bit.findNextBit(&boundary_set, head_nbits, boundary));
    try std.testing.expectEqual(boundary, find_bit.findNextZeroBit(&boundary_zero, head_nbits, boundary));
    try std.testing.expectEqual(boundary, find_bit.findNextAndBit(&boundary_set, &boundary_set, head_nbits, boundary));

    try std.testing.expectEqual(boundary, find_bit._find_next_bit(&boundary_set, head_nbits, boundary));
    try std.testing.expectEqual(boundary, find_bit._find_next_zero_bit(&boundary_zero, head_nbits, boundary));
    try std.testing.expectEqual(boundary, find_bit._find_next_and_bit(&boundary_set, &boundary_set, head_nbits, boundary));

    try std.testing.expectEqual(tail_nbits, find_bit.findFirstBit(&tail_only, tail_nbits));
    try std.testing.expectEqual(tail_nbits, find_bit.findNextBit(&tail_only, tail_nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(tail_nbits, find_bit.findFirstZeroBit(&tail_full, tail_nbits));
    try std.testing.expectEqual(tail_nbits, find_bit.findNextZeroBit(&tail_full, tail_nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(tail_nbits, find_bit.findFirstAndBit(&tail_only, &tail_only, tail_nbits));
    try std.testing.expectEqual(tail_nbits, find_bit.findNextAndBit(&tail_only, &tail_only, tail_nbits, find_bit.bits_per_long));

    try std.testing.expectEqual(tail_nbits, find_bit._find_first_bit(&tail_only, tail_nbits));
    try std.testing.expectEqual(tail_nbits, find_bit._find_first_zero_bit(&tail_full, tail_nbits));
    try std.testing.expectEqual(tail_nbits, find_bit._find_first_and_bit(&tail_only, &tail_only, tail_nbits));

    var tail_window = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 9) };
    try std.testing.expectEqual(find_bit.bits_per_long + 3, find_bit.findFirstBit(&tail_window, tail_nbits));
    try std.testing.expectEqual(tail_nbits, find_bit.findNextBit(&tail_window, tail_nbits, find_bit.bits_per_long + 4));
    try std.testing.expectEqual(find_bit.bits_per_long + 3, find_bit.findLastBit(&tail_window, tail_nbits));
    try std.testing.expectEqual(find_bit.bits_per_long + 3, find_bit._find_last_bit(&tail_window, tail_nbits));

    tail_window[1] &= ~(@as(find_bit.Word, 1) << 3);
    try std.testing.expectEqual(tail_nbits, find_bit.findFirstBit(&tail_window, tail_nbits));
    try std.testing.expectEqual(tail_nbits, find_bit.findLastBit(&tail_window, tail_nbits));

    var tail_zero_window = tail_full;
    tail_zero_window[1] &= ~(@as(find_bit.Word, 1) << 2);
    try std.testing.expectEqual(find_bit.bits_per_long + 2, find_bit.findFirstZeroBit(&tail_zero_window, tail_nbits));
    try std.testing.expectEqual(find_bit.bits_per_long + 2, find_bit.findNextZeroBit(&tail_zero_window, tail_nbits, find_bit.bits_per_long));

    try std.testing.expectEqual(past_nbits, find_bit.findNextBit(&empty, past_nbits, past_nbits));
    try std.testing.expectEqual(past_nbits, find_bit.findNextBit(&empty, past_nbits, past_nbits + 4));
    try std.testing.expectEqual(past_nbits, find_bit.findNextZeroBit(&empty, past_nbits, past_nbits));
    try std.testing.expectEqual(past_nbits, find_bit.findNextZeroBit(&empty, past_nbits, past_nbits + 4));
    try std.testing.expectEqual(past_nbits, find_bit.findNextAndBit(&empty, &empty, past_nbits, past_nbits));
    try std.testing.expectEqual(past_nbits, find_bit.findNextAndBit(&empty, &empty, past_nbits, past_nbits + 4));
}
