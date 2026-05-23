const std = @import("std");
const find_bit = @import("find_bit");

fn word(bit: usize) find_bit.Word {
    return @as(find_bit.Word, 1) << @intCast(bit);
}

test "phase1 find_bit boundary smoke keeps inclusive starts reachable" {
    const head_boundary = find_bit.bits_per_long - 1;
    const head_nbits = find_bit.bits_per_long * 2;
    const head_set_map = [_]find_bit.Word{ word(head_boundary), 0 };
    const head_and_lhs = [_]find_bit.Word{ word(head_boundary), 0 };
    const head_and_rhs = [_]find_bit.Word{ word(head_boundary), 0 };
    const head_andnot_lhs = [_]find_bit.Word{ word(5) | word(head_boundary), 0 };
    const head_andnot_rhs = [_]find_bit.Word{ word(5), 0 };
    const head_zero_map = [_]find_bit.Word{ ~word(head_boundary), ~@as(find_bit.Word, 0) };

    try std.testing.expectEqual(@as(usize, head_boundary), find_bit.findNextBit(&head_set_map, head_nbits, head_boundary));
    try std.testing.expectEqual(@as(usize, head_boundary), find_bit.find_next_and_bit(&head_and_lhs, &head_and_rhs, head_nbits, head_boundary));
    try std.testing.expectEqual(@as(usize, head_boundary), find_bit._find_next_andnot_bit(&head_andnot_lhs, &head_andnot_rhs, head_nbits, head_boundary));
    try std.testing.expectEqual(@as(usize, head_boundary), find_bit.findNextZeroBit(&head_zero_map, head_nbits, head_boundary));

    const tail_bits: usize = 5;
    const tail_boundary = find_bit.bits_per_long + tail_bits - 1;
    const tail_nbits = tail_boundary + 1;
    const tail_set_map = [_]find_bit.Word{ 0, word(tail_bits - 1) | word(tail_bits + 2) };
    const tail_and_lhs = [_]find_bit.Word{ 0, word(tail_bits - 1) | word(tail_bits + 2) };
    const tail_and_rhs = [_]find_bit.Word{ 0, word(tail_bits - 1) | word(tail_bits + 2) };
    const tail_andnot_lhs = [_]find_bit.Word{ 0, word(tail_bits - 1) | word(tail_bits + 2) };
    const tail_andnot_rhs = [_]find_bit.Word{ 0, word(tail_bits + 2) };
    const tail_zero_map = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        find_bit.lastWordMask(tail_nbits) & ~word(tail_bits - 1),
    };

    try std.testing.expectEqual(@as(usize, tail_boundary), find_bit.find_next_bit(&tail_set_map, tail_nbits, tail_boundary));
    try std.testing.expectEqual(@as(usize, tail_boundary), find_bit._find_next_and_bit(&tail_and_lhs, &tail_and_rhs, tail_nbits, tail_boundary));
    try std.testing.expectEqual(@as(usize, tail_boundary), find_bit.findNextAndNotBit(&tail_andnot_lhs, &tail_andnot_rhs, tail_nbits, tail_boundary));
    try std.testing.expectEqual(@as(usize, tail_boundary), find_bit.find_next_zero_bit(&tail_zero_map, tail_nbits, tail_boundary));

    const single_word_nbits = 11;
    const single_boundary = single_word_nbits - 1;
    const single_set_map = [_]find_bit.Word{word(single_boundary) | word(13)};
    const single_and_lhs = [_]find_bit.Word{word(single_boundary) | word(13)};
    const single_and_rhs = [_]find_bit.Word{word(single_boundary) | word(13)};
    const single_andnot_lhs = [_]find_bit.Word{word(2) | word(single_boundary) | word(13)};
    const single_andnot_rhs = [_]find_bit.Word{word(2) | word(13)};
    const single_zero_map = [_]find_bit.Word{find_bit.lastWordMask(single_word_nbits) & ~word(single_boundary)};

    try std.testing.expectEqual(@as(usize, single_boundary), find_bit.findNextBit(&single_set_map, single_word_nbits, single_boundary));
    try std.testing.expectEqual(@as(usize, single_boundary), find_bit.find_next_and_bit(&single_and_lhs, &single_and_rhs, single_word_nbits, single_boundary));
    try std.testing.expectEqual(@as(usize, single_boundary), find_bit._find_next_andnot_bit(&single_andnot_lhs, &single_andnot_rhs, single_word_nbits, single_boundary));
    try std.testing.expectEqual(@as(usize, single_boundary), find_bit.findNextZeroBit(&single_zero_map, single_word_nbits, single_boundary));
}

test "phase1 find_bit boundary smoke keeps empty-window and clump routes fail-closed" {
    const empty = [_]find_bit.Word{};

    try std.testing.expectEqual(@as(usize, 7), find_bit.findNextBit(&empty, 7, 7));
    try std.testing.expectEqual(@as(usize, 7), find_bit.find_next_bit(&empty, 7, 12));
    try std.testing.expectEqual(@as(usize, 7), find_bit.findNextZeroBit(&empty, 7, 7));
    try std.testing.expectEqual(@as(usize, 7), find_bit.find_next_zero_bit(&empty, 7, 12));
    try std.testing.expectEqual(@as(usize, 7), find_bit.findNextAndBit(&empty, &empty, 7, 7));
    try std.testing.expectEqual(@as(usize, 7), find_bit._find_next_and_bit(&empty, &empty, 7, 12));
    try std.testing.expectEqual(@as(usize, 7), find_bit.findNextAndNotBit(&empty, &empty, 7, 7));
    try std.testing.expectEqual(@as(usize, 7), find_bit._find_next_andnot_bit(&empty, &empty, 7, 12));

    const exact_tail_nbits = find_bit.bits_per_long + 5;
    const exact_tail_map = [_]find_bit.Word{ 0, word(3) };
    var clump: u8 = 0x5a;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findFirstClump8(&clump, &exact_tail_map, exact_tail_nbits));
    try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);

    const masked_tail_map = [_]find_bit.Word{ 0, word(3) | word(6) };
    var alias_clump: u8 = 0;
    try std.testing.expectEqual(
        find_bit.findFirstClump8(&clump, &masked_tail_map, exact_tail_nbits),
        find_bit.find_first_clump8(&alias_clump, &masked_tail_map, exact_tail_nbits),
    );
    try std.testing.expectEqual(clump, alias_clump);

    clump = 0x33;
    try std.testing.expectEqual(@as(usize, 8), find_bit.findFirstClump8(&clump, &[_]find_bit.Word{0}, 8));
    try std.testing.expectEqual(@as(u8, 0x33), clump);

    clump = 0x44;
    try std.testing.expectEqual(@as(usize, 8), find_bit.find_next_clump8(&clump, &empty, 8, 12));
    try std.testing.expectEqual(@as(u8, 0x44), clump);

    clump = 0x55;
    try std.testing.expectEqual(@as(usize, 8), find_bit._find_next_clump8(&clump, &empty, 8, 20));
    try std.testing.expectEqual(@as(u8, 0x55), clump);
}
