const std = @import("std");
const find_bit = @import("find_bit");

const iterations_find_bit: u64 = 20_000;

fn findBitBench() struct { checksum: u64 } {
    const head_nbits = find_bit.bits_per_long * 2;
    const boundary = find_bit.bits_per_long - 1;
    const boundary_set = [_]find_bit.Word{
        @as(find_bit.Word, 1) << @intCast(boundary),
        (@as(find_bit.Word, 1) << 0) | (@as(find_bit.Word, 1) << 5),
    };
    const boundary_zero = [_]find_bit.Word{
        0,
        ~((@as(find_bit.Word, 1) << 0) | (@as(find_bit.Word, 1) << 5)),
    };
    var checksum: u64 = 0;
    var idx: u64 = 0;
    while (idx < iterations_find_bit) : (idx += 1) {
        checksum +%= @intCast(find_bit.findNextBit(&boundary_set, head_nbits, boundary));
        checksum +%= @intCast(find_bit.findNextAndBit(&boundary_set, &boundary_set, head_nbits, boundary));
        checksum +%= @intCast(find_bit.findNextZeroBit(&boundary_zero, head_nbits, boundary));
    }
    return .{ .checksum = checksum };
}

test "phase1 find_bit bench replay keeps the boundary packet stable" {
    const head_nbits = find_bit.bits_per_long * 2;
    const boundary = find_bit.bits_per_long - 1;
    const boundary_set = [_]find_bit.Word{
        @as(find_bit.Word, 1) << @intCast(boundary),
        (@as(find_bit.Word, 1) << 0) | (@as(find_bit.Word, 1) << 5),
    };
    const boundary_zero = [_]find_bit.Word{
        0,
        ~((@as(find_bit.Word, 1) << 0) | (@as(find_bit.Word, 1) << 5)),
    };

    try std.testing.expectEqual(boundary, find_bit.findNextBit(&boundary_set, head_nbits, boundary));
    try std.testing.expectEqual(
        boundary,
        find_bit.findNextAndBit(&boundary_set, &boundary_set, head_nbits, boundary),
    );
    try std.testing.expectEqual(
        boundary,
        find_bit.findNextZeroBit(&boundary_zero, head_nbits, boundary),
    );
}

test "phase1 find_bit bench replay keeps the 20000-iteration checksum stable" {
    const result = findBitBench();
    try std.testing.expectEqual(@as(u64, 3_780_000), result.checksum);
}
