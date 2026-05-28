const std = @import("std");
const find_bit = @import("find_bit");

const iterations_find_bit = 20_000;
const boundary = find_bit.bits_per_long - 1;
const head_nbits = find_bit.bits_per_long * 2;
const expected_checksum: u64 = boundary * iterations_find_bit;

fn boundarySet() [2]find_bit.Word {
    return .{
        @as(find_bit.Word, 1) << @intCast(boundary),
        (@as(find_bit.Word, 1) << 0) | (@as(find_bit.Word, 1) << 5),
    };
}

fn runFindNextAndBitReplay() u64 {
    const lhs = boundarySet();
    const rhs = boundarySet();
    var checksum: u64 = 0;
    var idx: usize = 0;
    while (idx < iterations_find_bit) : (idx += 1) {
        checksum +%= @intCast(find_bit.findNextAndBit(&lhs, &rhs, head_nbits, boundary));
    }
    return checksum;
}

test "phase1 find_next_and_bit bench replay keeps the shared boundary witnesses explicit" {
    const lhs = boundarySet();
    const rhs = boundarySet();

    try std.testing.expectEqual(boundary, find_bit.findNextAndBit(&lhs, &rhs, head_nbits, boundary));
    try std.testing.expectEqual(find_bit.bits_per_long, find_bit.findNextAndBit(&lhs, &rhs, head_nbits, boundary + 1));
    try std.testing.expectEqual(find_bit.bits_per_long + 5, find_bit.findNextAndBit(&lhs, &rhs, head_nbits, find_bit.bits_per_long + 1));
    try std.testing.expectEqual(head_nbits, find_bit.findNextAndBit(&lhs, &rhs, head_nbits, find_bit.bits_per_long + 6));
}

test "phase1 find_next_and_bit bench replay keeps the exact 20000-iteration checksum" {
    try std.testing.expectEqual(expected_checksum, runFindNextAndBitReplay());
}
