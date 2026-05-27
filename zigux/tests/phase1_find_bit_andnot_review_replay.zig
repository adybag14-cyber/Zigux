const std = @import("std");
const find_bit = @import("find_bit");

const fixture_bytes = @embedFile("fixtures/phase1_helpers.json");

const Fixture = struct {
    find_bit: struct {
        tail_clamped_first: usize,
        tail_clamped_next: usize,
        tail_zero_clamped_first: usize,
        tail_zero_clamped_next: usize,
        tail_and_clamped_first: usize,
        tail_and_clamped_next: usize,
    },
};

fn loadFixture() !std.json.Parsed(Fixture) {
    return std.json.parseFromSlice(Fixture, std.testing.allocator, fixture_bytes, .{
        .ignore_unknown_fields = true,
    });
}

test "phase1 find_bit tail clamp fixture fields stay aligned" {
    var parsed = try loadFixture();
    defer parsed.deinit();
    const fixture = parsed.value.find_bit;

    const nbits = find_bit.bits_per_long + 5;

    var bitmap = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 10) };
    try std.testing.expectEqual(fixture.tail_clamped_first, find_bit.findFirstBit(&bitmap, nbits));
    try std.testing.expectEqual(fixture.tail_clamped_next, find_bit.findNextBit(&bitmap, nbits, find_bit.bits_per_long + 4));

    const zero_bitmap = [_]find_bit.Word{ ~@as(find_bit.Word, 0), find_bit.lastWordMask(nbits) };
    try std.testing.expectEqual(fixture.tail_zero_clamped_first, find_bit.findFirstZeroBit(&zero_bitmap, nbits));
    try std.testing.expectEqual(fixture.tail_zero_clamped_next, find_bit.findNextZeroBit(&zero_bitmap, nbits, find_bit.bits_per_long));

    const and_lhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 9) };
    const and_rhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 9) };
    try std.testing.expectEqual(fixture.tail_and_clamped_first, find_bit.findFirstAndBit(&and_lhs, &and_rhs, nbits));
    try std.testing.expectEqual(fixture.tail_and_clamped_next, find_bit.findNextAndBit(&and_lhs, &and_rhs, nbits, find_bit.bits_per_long + 4));

    bitmap[1] &= ~(@as(find_bit.Word, 1) << 3);
    try std.testing.expectEqual(nbits, find_bit.findFirstBit(&bitmap, nbits));
}

test "phase1 find_bit andnot aliases stay aligned on tail windows" {
    const nbits = find_bit.bits_per_long + 6;
    const lhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9) };
    const rhs = [_]find_bit.Word{ 0, @as(find_bit.Word, 1) << 1 };

    const first = find_bit.findFirstAndNotBit(&lhs, &rhs, nbits);
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), first);
    try std.testing.expectEqual(first, find_bit.find_first_andnot_bit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(first, find_bit._find_first_andnot_bit(&lhs, &rhs, nbits));

    const next = find_bit.findNextAndNotBit(&lhs, &rhs, nbits, find_bit.bits_per_long + 2);
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), next);
    try std.testing.expectEqual(next, find_bit.find_next_andnot_bit(&lhs, &rhs, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(next, find_bit._find_next_andnot_bit(&lhs, &rhs, nbits, find_bit.bits_per_long + 2));

    const exhausted = find_bit.findNextAndNotBit(&lhs, &rhs, nbits, find_bit.bits_per_long + 5);
    try std.testing.expectEqual(nbits, exhausted);
    try std.testing.expectEqual(exhausted, find_bit.find_next_andnot_bit(&lhs, &rhs, nbits, find_bit.bits_per_long + 5));
    try std.testing.expectEqual(exhausted, find_bit._find_next_andnot_bit(&lhs, &rhs, nbits, find_bit.bits_per_long + 5));
}
