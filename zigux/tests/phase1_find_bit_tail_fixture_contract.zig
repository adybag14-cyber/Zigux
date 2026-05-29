const std = @import("std");

const fixture_bytes = @embedFile("fixtures/phase1_helpers.json");

const Fixture = struct {
    find_bit: struct {
        bits_per_long: usize,
        tail_clamped_first: usize,
        tail_clamped_next: usize,
        tail_zero_clamped_first: usize,
        tail_zero_clamped_next: usize,
        tail_and_clamped_first: usize,
        tail_and_clamped_next: usize,
        tail_clamped_last: usize,
        tail_clamped_empty_last: usize,
        tail_inclusive_boundary_next: usize,
        tail_inclusive_boundary_zero: usize,
        tail_inclusive_boundary_and: usize,
    },
};

fn loadFixture() !std.json.Parsed(Fixture) {
    return std.json.parseFromSlice(Fixture, std.testing.allocator, fixture_bytes, .{
        .ignore_unknown_fields = true,
    });
}

test "phase1 find_bit fixture keeps declared tail-window packet" {
    var parsed = try loadFixture();
    defer parsed.deinit();
    const packet = parsed.value.find_bit;

    try std.testing.expectEqual(@as(usize, 64), packet.bits_per_long);

    const tail_nbits = packet.bits_per_long + 5;
    try std.testing.expectEqual(packet.bits_per_long + 3, packet.tail_clamped_first);
    try std.testing.expectEqual(tail_nbits, packet.tail_clamped_next);
    try std.testing.expectEqual(tail_nbits, packet.tail_zero_clamped_first);
    try std.testing.expectEqual(tail_nbits, packet.tail_zero_clamped_next);
    try std.testing.expectEqual(packet.bits_per_long + 3, packet.tail_and_clamped_first);
    try std.testing.expectEqual(tail_nbits, packet.tail_and_clamped_next);
    try std.testing.expectEqual(packet.bits_per_long + 3, packet.tail_clamped_last);
    try std.testing.expectEqual(tail_nbits, packet.tail_clamped_empty_last);
}

test "phase1 find_bit fixture keeps inclusive tail-boundary packet" {
    var parsed = try loadFixture();
    defer parsed.deinit();
    const packet = parsed.value.find_bit;

    const final_inclusive_bit = packet.bits_per_long + 4;
    try std.testing.expectEqual(final_inclusive_bit, packet.tail_inclusive_boundary_next);
    try std.testing.expectEqual(final_inclusive_bit, packet.tail_inclusive_boundary_zero);
    try std.testing.expectEqual(final_inclusive_bit, packet.tail_inclusive_boundary_and);
}
