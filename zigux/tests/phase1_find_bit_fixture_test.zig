const std = @import("std");
const find_bit = @import("find_bit");

const Word = find_bit.Word;

const FixtureEnvelope = struct {
    find_bit: FindBitFixture,
};

const FindBitFixture = struct {
    bits_per_long: usize,
    first: usize,
    next_after_6: usize,
    next_after_word: usize,
    first_zero: usize,
    next_zero: usize,
    first_and: usize,
    next_and: usize,
    last: usize,
    inclusive_boundary_next: usize,
    inclusive_boundary_zero: usize,
    inclusive_boundary_and: usize,
    tail_inclusive_boundary_next: usize,
    tail_inclusive_boundary_zero: usize,
    tail_inclusive_boundary_and: usize,
    past_nbits_next: usize,
    past_nbits_zero: usize,
    past_nbits_and: usize,
    tail_clamped_first: usize,
    tail_clamped_next: usize,
    tail_zero_clamped_first: usize,
    tail_zero_clamped_next: usize,
    tail_and_clamped_first: usize,
    tail_and_clamped_next: usize,
    tail_clamped_last: usize,
    tail_clamped_empty_last: usize,
};

fn loadFixture() !FindBitFixture {
    const parsed = try std.json.parseFromSlice(
        FixtureEnvelope,
        std.testing.allocator,
        @embedFile("fixtures/phase1_helpers.json"),
        .{ .ignore_unknown_fields = true },
    );
    defer parsed.deinit();
    return parsed.value.find_bit;
}

test "phase1 find_bit fixture stays aligned with boundary and tail clamp behavior" {
    const fixture = try loadFixture();
    try std.testing.expectEqual(find_bit.bits_per_long, fixture.bits_per_long);

    const three_word_nbits = find_bit.bits_per_long * 3;
    const first_and_last_map = [_]Word{
        @as(Word, 1) << 5,
        @as(Word, 1) << 3,
        @as(Word, 1) << 7,
    };
    try std.testing.expectEqual(fixture.first, find_bit.findFirstBit(&first_and_last_map, three_word_nbits));
    try std.testing.expectEqual(fixture.next_after_6, find_bit.findNextBit(&first_and_last_map, three_word_nbits, 6));
    try std.testing.expectEqual(fixture.next_after_word, find_bit.findNextBit(&first_and_last_map, three_word_nbits, find_bit.bits_per_long + 4));
    try std.testing.expectEqual(fixture.last, find_bit.findLastBit(&first_and_last_map, three_word_nbits));

    const zero_map = [_]Word{
        ~(@as(Word, 1) << 3),
        ~(@as(Word, 1) << 4),
        ~@as(Word, 0),
    };
    try std.testing.expectEqual(fixture.first_zero, find_bit.findFirstZeroBit(&zero_map, three_word_nbits));
    try std.testing.expectEqual(fixture.next_zero, find_bit.findNextZeroBit(&zero_map, three_word_nbits, find_bit.bits_per_long));

    const and_nbits = find_bit.bits_per_long * 2;
    const and_lhs = [_]Word{
        (@as(Word, 1) << 1) | (@as(Word, 1) << 9),
        (@as(Word, 1) << 2) | (@as(Word, 1) << 3),
    };
    const and_rhs = [_]Word{
        @as(Word, 1) << 9,
        @as(Word, 1) << 2,
    };
    try std.testing.expectEqual(fixture.first_and, find_bit.findFirstAndBit(&and_lhs, &and_rhs, and_nbits));
    try std.testing.expectEqual(fixture.next_and, find_bit.findNextAndBit(&and_lhs, &and_rhs, and_nbits, 10));

    const inclusive_boundary = find_bit.bits_per_long - 1;
    const inclusive_set = [_]Word{ @as(Word, 1) << @intCast(inclusive_boundary), 0 };
    const inclusive_zero = [_]Word{ ~(@as(Word, 1) << @intCast(inclusive_boundary)), ~@as(Word, 0) };
    try std.testing.expectEqual(fixture.inclusive_boundary_next, find_bit.findNextBit(&inclusive_set, and_nbits, inclusive_boundary));
    try std.testing.expectEqual(fixture.inclusive_boundary_zero, find_bit.findNextZeroBit(&inclusive_zero, and_nbits, inclusive_boundary));
    try std.testing.expectEqual(fixture.inclusive_boundary_and, find_bit.findNextAndBit(&inclusive_set, &inclusive_set, and_nbits, inclusive_boundary));

    const tail_nbits = find_bit.bits_per_long + 5;
    const tail_boundary = tail_nbits - 1;
    const tail_boundary_set = [_]Word{
        0,
        (@as(Word, 1) << 4) | (@as(Word, 1) << 7),
    };
    const tail_boundary_zero = [_]Word{
        ~@as(Word, 0),
        find_bit.lastWordMask(tail_nbits) & ~(@as(Word, 1) << 4),
    };
    try std.testing.expectEqual(fixture.tail_inclusive_boundary_next, find_bit.findNextBit(&tail_boundary_set, tail_nbits, tail_boundary));
    try std.testing.expectEqual(fixture.tail_inclusive_boundary_zero, find_bit.findNextZeroBit(&tail_boundary_zero, tail_nbits, tail_boundary));
    try std.testing.expectEqual(fixture.tail_inclusive_boundary_and, find_bit.findNextAndBit(&tail_boundary_set, &tail_boundary_set, tail_nbits, tail_boundary));

    const empty = [_]Word{};
    try std.testing.expectEqual(fixture.past_nbits_next, find_bit.findNextBit(&empty, 7, 11));
    try std.testing.expectEqual(fixture.past_nbits_zero, find_bit.findNextZeroBit(&empty, 7, 11));
    try std.testing.expectEqual(fixture.past_nbits_and, find_bit.findNextAndBit(&empty, &empty, 7, 11));

    const tail_clamp_map = [_]Word{
        0,
        (@as(Word, 1) << 3) | (@as(Word, 1) << 6),
    };
    try std.testing.expectEqual(fixture.tail_clamped_first, find_bit.findFirstBit(&tail_clamp_map, tail_nbits));
    try std.testing.expectEqual(fixture.tail_clamped_next, find_bit.findNextBit(&tail_clamp_map, tail_nbits, find_bit.bits_per_long + 4));
    try std.testing.expectEqual(fixture.tail_clamped_last, find_bit.findLastBit(&tail_clamp_map, tail_nbits));

    const tail_zero_map = [_]Word{
        ~@as(Word, 0),
        find_bit.lastWordMask(tail_nbits),
    };
    try std.testing.expectEqual(fixture.tail_zero_clamped_first, find_bit.findFirstZeroBit(&tail_zero_map, tail_nbits));
    try std.testing.expectEqual(fixture.tail_zero_clamped_next, find_bit.findNextZeroBit(&tail_zero_map, tail_nbits, find_bit.bits_per_long));

    const tail_and_rhs = [_]Word{
        0,
        (@as(Word, 1) << 3) | (@as(Word, 1) << 6),
    };
    try std.testing.expectEqual(fixture.tail_and_clamped_first, find_bit.findFirstAndBit(&tail_clamp_map, &tail_and_rhs, tail_nbits));
    try std.testing.expectEqual(fixture.tail_and_clamped_next, find_bit.findNextAndBit(&tail_clamp_map, &tail_and_rhs, tail_nbits, find_bit.bits_per_long + 4));

    const tail_empty_last = [_]Word{ 0, 0 };
    try std.testing.expectEqual(fixture.tail_clamped_empty_last, find_bit.findLastBit(&tail_empty_last, tail_nbits));
}
