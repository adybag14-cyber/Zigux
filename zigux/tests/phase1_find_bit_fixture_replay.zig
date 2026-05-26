const std = @import("std");
const find_bit = @import("find_bit");

const fixture_bytes = @embedFile("fixtures/phase1_helpers.json");

const Fixture = struct {
    find_bit: struct {
        bits_per_long: usize,
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
    },
};

fn loadFixture() !std.json.Parsed(Fixture) {
    return std.json.parseFromSlice(Fixture, std.testing.allocator, fixture_bytes, .{
        .ignore_unknown_fields = true,
    });
}

test "phase1 find_bit fixture replay covers inclusive boundaries and past-nbits exits" {
    var parsed = try loadFixture();
    defer parsed.deinit();
    const fixture = parsed.value;

    const word_bits = fixture.find_bit.bits_per_long;
    const exact_boundary = word_bits - 1;
    const exact_word_nbits = word_bits * 2;
    const exact_boundary_map = [_]find_bit.Word{
        @as(find_bit.Word, 1) << @intCast(exact_boundary),
        0,
    };
    const exact_boundary_zero_map = [_]find_bit.Word{
        ~(@as(find_bit.Word, 1) << @intCast(exact_boundary)),
        ~@as(find_bit.Word, 0),
    };

    try std.testing.expectEqual(
        fixture.find_bit.inclusive_boundary_next,
        find_bit.findNextBit(&exact_boundary_map, exact_word_nbits, exact_boundary),
    );
    try std.testing.expectEqual(
        fixture.find_bit.inclusive_boundary_zero,
        find_bit.findNextZeroBit(&exact_boundary_zero_map, exact_word_nbits, exact_boundary),
    );
    try std.testing.expectEqual(
        fixture.find_bit.inclusive_boundary_and,
        find_bit.findNextAndBit(&exact_boundary_map, &exact_boundary_map, exact_word_nbits, exact_boundary),
    );

    const tail_nbits = fixture.find_bit.tail_inclusive_boundary_and + 1;
    const tail_boundary = tail_nbits - 1;
    const tail_offset = tail_boundary - word_bits;
    const tail_boundary_map = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << @intCast(tail_offset)) |
            (@as(find_bit.Word, 1) << @intCast(tail_offset + 2)),
    };
    const tail_boundary_zero_map = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        find_bit.lastWordMask(tail_nbits) & ~(@as(find_bit.Word, 1) << @intCast(tail_offset)),
    };

    try std.testing.expectEqual(
        fixture.find_bit.tail_inclusive_boundary_next,
        find_bit.findNextBit(&tail_boundary_map, tail_nbits, tail_boundary),
    );
    try std.testing.expectEqual(
        fixture.find_bit.tail_inclusive_boundary_zero,
        find_bit.findNextZeroBit(&tail_boundary_zero_map, tail_nbits, tail_boundary),
    );
    try std.testing.expectEqual(
        fixture.find_bit.tail_inclusive_boundary_and,
        find_bit.findNextAndBit(&tail_boundary_map, &tail_boundary_map, tail_nbits, tail_boundary),
    );

    const empty = [_]find_bit.Word{};
    try std.testing.expectEqual(
        fixture.find_bit.past_nbits_next,
        find_bit.findNextBit(&empty, fixture.find_bit.past_nbits_next, fixture.find_bit.past_nbits_next),
    );
    try std.testing.expectEqual(
        fixture.find_bit.past_nbits_zero,
        find_bit.findNextZeroBit(&empty, fixture.find_bit.past_nbits_zero, fixture.find_bit.past_nbits_zero + 4),
    );
    try std.testing.expectEqual(
        fixture.find_bit.past_nbits_and,
        find_bit.findNextAndBit(&empty, &empty, fixture.find_bit.past_nbits_and, fixture.find_bit.past_nbits_and + 4),
    );
}

test "phase1 find_bit fixture replay covers tail-clamped first next zero and last edges" {
    var parsed = try loadFixture();
    defer parsed.deinit();
    const fixture = parsed.value;

    const word_bits = fixture.find_bit.bits_per_long;
    const tail_nbits = fixture.find_bit.tail_clamped_empty_last;

    var tail_set_map = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 10),
    };
    try std.testing.expectEqual(
        fixture.find_bit.tail_clamped_first,
        find_bit.findFirstBit(&tail_set_map, tail_nbits),
    );
    try std.testing.expectEqual(
        fixture.find_bit.tail_clamped_next,
        find_bit.findNextBit(&tail_set_map, tail_nbits, word_bits + 4),
    );
    try std.testing.expectEqual(
        fixture.find_bit.tail_clamped_last,
        find_bit.findLastBit(&tail_set_map, tail_nbits),
    );
    tail_set_map[1] &= ~(@as(find_bit.Word, 1) << 3);
    try std.testing.expectEqual(
        fixture.find_bit.tail_clamped_empty_last,
        find_bit.findLastBit(&tail_set_map, tail_nbits),
    );

    const tail_zero_map = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        find_bit.lastWordMask(tail_nbits),
    };
    try std.testing.expectEqual(
        fixture.find_bit.tail_zero_clamped_first,
        find_bit.findFirstZeroBit(&tail_zero_map, tail_nbits),
    );
    try std.testing.expectEqual(
        fixture.find_bit.tail_zero_clamped_next,
        find_bit.findNextZeroBit(&tail_zero_map, tail_nbits, word_bits + 4),
    );

    const tail_and_lhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 9),
    };
    const tail_and_rhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 9),
    };
    try std.testing.expectEqual(
        fixture.find_bit.tail_and_clamped_first,
        find_bit.findFirstAndBit(&tail_and_lhs, &tail_and_rhs, tail_nbits),
    );
    try std.testing.expectEqual(
        fixture.find_bit.tail_and_clamped_next,
        find_bit.findNextAndBit(&tail_and_lhs, &tail_and_rhs, tail_nbits, word_bits + 4),
    );
}
