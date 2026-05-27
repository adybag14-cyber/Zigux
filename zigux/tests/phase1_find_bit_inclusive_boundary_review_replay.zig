const std = @import("std");
const find_bit = @import("find_bit");

const Word = find_bit.Word;
const bits_per_long = find_bit.bits_per_long;

test "phase1 find_bit inclusive-boundary replay keeps the last in-range bit reachable across public and alias scans" {
    const head_boundary = bits_per_long - 1;
    const head_nbits = bits_per_long * 2;
    const head_set = [_]Word{ @as(Word, 1) << @intCast(head_boundary), 0 };
    const head_zero = [_]Word{ ~(@as(Word, 1) << @intCast(head_boundary)), ~@as(Word, 0) };
    const head_andnot_lhs = [_]Word{ (@as(Word, 1) << 5) | (@as(Word, 1) << @intCast(head_boundary)), 0 };
    const head_andnot_rhs = [_]Word{ @as(Word, 1) << 5, 0 };

    try std.testing.expectEqual(head_boundary, find_bit.findNextBit(&head_set, head_nbits, head_boundary));
    try std.testing.expectEqual(head_boundary, find_bit.find_next_bit(&head_set, head_nbits, head_boundary));
    try std.testing.expectEqual(head_boundary, find_bit._find_next_bit(&head_set, head_nbits, head_boundary));
    try std.testing.expectEqual(head_boundary, find_bit.findNextZeroBit(&head_zero, head_nbits, head_boundary));
    try std.testing.expectEqual(head_boundary, find_bit.find_next_zero_bit(&head_zero, head_nbits, head_boundary));
    try std.testing.expectEqual(head_boundary, find_bit._find_next_zero_bit(&head_zero, head_nbits, head_boundary));
    try std.testing.expectEqual(head_boundary, find_bit.findNextAndNotBit(&head_andnot_lhs, &head_andnot_rhs, head_nbits, head_boundary));
    try std.testing.expectEqual(head_boundary, find_bit.find_next_andnot_bit(&head_andnot_lhs, &head_andnot_rhs, head_nbits, head_boundary));
    try std.testing.expectEqual(head_boundary, find_bit._find_next_andnot_bit(&head_andnot_lhs, &head_andnot_rhs, head_nbits, head_boundary));
    try std.testing.expectEqual(head_nbits, find_bit.findNextBit(&head_set, head_nbits, head_boundary + 1));
    try std.testing.expectEqual(head_nbits, find_bit.findNextZeroBit(&head_zero, head_nbits, head_boundary + 1));
    try std.testing.expectEqual(head_nbits, find_bit.findNextAndNotBit(&head_andnot_lhs, &head_andnot_rhs, head_nbits, head_boundary + 1));

    const tail_bits: usize = 5;
    const tail_boundary = bits_per_long + tail_bits - 1;
    const tail_nbits = tail_boundary + 1;
    const tail_set = [_]Word{ 0, (@as(Word, 1) << @intCast(tail_bits - 1)) | (@as(Word, 1) << @intCast(tail_bits + 3)) };
    const tail_zero = [_]Word{ ~@as(Word, 0), find_bit.lastWordMask(tail_nbits) & ~(@as(Word, 1) << @intCast(tail_bits - 1)) };
    const tail_and_lhs = [_]Word{ 0, (@as(Word, 1) << @intCast(tail_bits - 1)) | (@as(Word, 1) << @intCast(tail_bits + 3)) };
    const tail_and_rhs = [_]Word{ 0, (@as(Word, 1) << @intCast(tail_bits - 1)) | (@as(Word, 1) << @intCast(tail_bits + 3)) };

    try std.testing.expectEqual(tail_boundary, find_bit.findNextBit(&tail_set, tail_nbits, tail_boundary));
    try std.testing.expectEqual(tail_boundary, find_bit.findNextZeroBit(&tail_zero, tail_nbits, tail_boundary));
    try std.testing.expectEqual(tail_boundary, find_bit.findNextAndBit(&tail_and_lhs, &tail_and_rhs, tail_nbits, tail_boundary));
    try std.testing.expectEqual(tail_boundary, find_bit.find_next_and_bit(&tail_and_lhs, &tail_and_rhs, tail_nbits, tail_boundary));
    try std.testing.expectEqual(tail_boundary, find_bit._find_next_and_bit(&tail_and_lhs, &tail_and_rhs, tail_nbits, tail_boundary));
    try std.testing.expectEqual(tail_nbits, find_bit.findNextBit(&tail_set, tail_nbits, tail_boundary + 1));
    try std.testing.expectEqual(tail_nbits, find_bit.findNextZeroBit(&tail_zero, tail_nbits, tail_boundary + 1));
    try std.testing.expectEqual(tail_nbits, find_bit.findNextAndBit(&tail_and_lhs, &tail_and_rhs, tail_nbits, tail_boundary + 1));

    const single_nbits = 11;
    const single_boundary = single_nbits - 1;
    const single_set = [_]Word{(@as(Word, 1) << @intCast(single_boundary)) | (@as(Word, 1) << 13)};
    const single_and_lhs = [_]Word{(@as(Word, 1) << @intCast(single_boundary)) | (@as(Word, 1) << 13)};
    const single_and_rhs = [_]Word{(@as(Word, 1) << @intCast(single_boundary)) | (@as(Word, 1) << 13)};

    try std.testing.expectEqual(single_boundary, find_bit.findNextBit(&single_set, single_nbits, single_boundary));
    try std.testing.expectEqual(single_boundary, find_bit.findNextAndBit(&single_and_lhs, &single_and_rhs, single_nbits, single_boundary));
    try std.testing.expectEqual(single_boundary, find_bit.find_next_and_bit(&single_and_lhs, &single_and_rhs, single_nbits, single_boundary));
    try std.testing.expectEqual(single_boundary, find_bit._find_next_and_bit(&single_and_lhs, &single_and_rhs, single_nbits, single_boundary));
    try std.testing.expectEqual(single_nbits, find_bit.findNextBit(&single_set, single_nbits, single_boundary + 1));
    try std.testing.expectEqual(single_nbits, find_bit.findNextAndBit(&single_and_lhs, &single_and_rhs, single_nbits, single_boundary + 1));
}

test "phase1 find_bit inclusive-boundary replay keeps past-end and zero-sized windows explicit" {
    const past_end_nbits = 7;
    const empty = [_]Word{};
    const ones = [_]Word{};
    var clump: u8 = 0x5a;

    try std.testing.expectEqual(past_end_nbits, find_bit.findNextBit(&empty, past_end_nbits, past_end_nbits));
    try std.testing.expectEqual(past_end_nbits, find_bit.find_next_bit(&empty, past_end_nbits, past_end_nbits + 4));
    try std.testing.expectEqual(past_end_nbits, find_bit.findNextZeroBit(&empty, past_end_nbits, past_end_nbits));
    try std.testing.expectEqual(past_end_nbits, find_bit.find_next_zero_bit(&empty, past_end_nbits, past_end_nbits + 4));
    try std.testing.expectEqual(past_end_nbits, find_bit.findNextAndBit(&empty, &ones, past_end_nbits, past_end_nbits));
    try std.testing.expectEqual(past_end_nbits, find_bit.find_next_and_bit(&empty, &ones, past_end_nbits, past_end_nbits + 4));
    try std.testing.expectEqual(past_end_nbits, find_bit.findNextAndNotBit(&empty, &ones, past_end_nbits, past_end_nbits));
    try std.testing.expectEqual(past_end_nbits, find_bit.find_next_andnot_bit(&empty, &ones, past_end_nbits, past_end_nbits + 4));

    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstBit(&empty, 0));
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstZeroBit(&empty, 0));
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstAndBit(&empty, &ones, 0));
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstAndNotBit(&empty, &ones, 0));
    try std.testing.expectEqual(@as(usize, 0), find_bit.findLastBit(&empty, 0));

    try std.testing.expectEqual(past_end_nbits, find_bit.findNextClump8(&clump, &empty, past_end_nbits, past_end_nbits));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);
    try std.testing.expectEqual(past_end_nbits, find_bit.find_next_clump8(&clump, &empty, past_end_nbits, past_end_nbits + 9));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);
    try std.testing.expectEqual(past_end_nbits, find_bit._find_next_clump8(&clump, &empty, past_end_nbits, past_end_nbits + 17));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);
}