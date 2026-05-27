const std = @import("std");
const find_bit = @import("../../tools/lib/find_bit.zig");

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

test "find_bit fixture covers boundary and tail clamp behavior" {
    var parsed = try loadFixture();
    defer parsed.deinit();
    const fixture = parsed.value.find_bit;

    const bits_per_long = fixture.bits_per_long;
    try std.testing.expectEqual(find_bit.bits_per_long, bits_per_long);

    const boundary = bits_per_long - 1;
    const boundary_nbits = bits_per_long * 2;
    const boundary_set_map = [_]find_bit.Word{
        @as(find_bit.Word, 1) << @intCast(boundary),
        0,
    };
    const boundary_zero_map = [_]find_bit.Word{
        ~(@as(find_bit.Word, 1) << @intCast(boundary)),
        ~@as(find_bit.Word, 0),
    };
    try std.testing.expectEqual(
        fixture.inclusive_boundary_next,
        find_bit.findNextBit(&boundary_set_map, boundary_nbits, boundary),
    );
    try std.testing.expectEqual(
        fixture.inclusive_boundary_zero,
        find_bit.findNextZeroBit(&boundary_zero_map, boundary_nbits, boundary),
    );
    try std.testing.expectEqual(
        fixture.inclusive_boundary_and,
        find_bit.findNextAndBit(&boundary_set_map, &boundary_set_map, boundary_nbits, boundary),
    );

    const tail_nbits = bits_per_long + 5;
    const tail_boundary = tail_nbits - 1;
    const tail_set_map = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 7),
    };
    const tail_zero_map = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        find_bit.lastWordMask(tail_nbits) & ~(@as(find_bit.Word, 1) << 4),
    };
    try std.testing.expectEqual(
        fixture.tail_inclusive_boundary_next,
        find_bit.findNextBit(&tail_set_map, tail_nbits, tail_boundary),
    );
    try std.testing.expectEqual(
        fixture.tail_inclusive_boundary_zero,
        find_bit.findNextZeroBit(&tail_zero_map, tail_nbits, tail_boundary),
    );
    try std.testing.expectEqual(
        fixture.tail_inclusive_boundary_and,
        find_bit.findNextAndBit(&tail_set_map, &tail_set_map, tail_nbits, tail_boundary),
    );

    const empty = [_]find_bit.Word{};
    try std.testing.expectEqual(
        fixture.past_nbits_next,
        find_bit.findNextBit(&empty, 7, 11),
    );
    try std.testing.expectEqual(
        fixture.past_nbits_zero,
        find_bit.findNextZeroBit(&empty, 7, 11),
    );
    try std.testing.expectEqual(
        fixture.past_nbits_and,
        find_bit.findNextAndBit(&empty, &empty, 7, 11),
    );

    const tail_clamp_map = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 10),
    };
    const tail_clamp_zero_map = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        find_bit.lastWordMask(tail_nbits) & ~(@as(find_bit.Word, 1) << 4),
    };
    const tail_empty_last_map = [_]find_bit.Word{
        0,
        @as(find_bit.Word, 1) << 10,
    };
    try std.testing.expectEqual(
        fixture.tail_clamped_first,
        find_bit.findFirstBit(&tail_clamp_map, tail_nbits),
    );
    try std.testing.expectEqual(
        fixture.tail_clamped_next,
        find_bit.findNextBit(&tail_clamp_map, tail_nbits, bits_per_long + 4),
    );
    try std.testing.expectEqual(
        fixture.tail_zero_clamped_first,
        find_bit.findFirstZeroBit(&tail_clamp_zero_map, tail_nbits),
    );
    try std.testing.expectEqual(
        fixture.tail_zero_clamped_next,
        find_bit.findNextZeroBit(&tail_clamp_zero_map, tail_nbits, tail_nbits),
    );
    try std.testing.expectEqual(
        fixture.tail_and_clamped_first,
        find_bit.findFirstAndBit(&tail_clamp_map, &tail_clamp_map, tail_nbits),
    );
    try std.testing.expectEqual(
        fixture.tail_and_clamped_next,
        find_bit.findNextAndBit(&tail_clamp_map, &tail_clamp_map, tail_nbits, bits_per_long + 4),
    );
    try std.testing.expectEqual(
        fixture.tail_clamped_last,
        find_bit.findLastBit(&tail_clamp_map, tail_nbits),
    );
    try std.testing.expectEqual(
        fixture.tail_clamped_empty_last,
        find_bit.findLastBit(&tail_empty_last_map, tail_nbits),
    );
}
