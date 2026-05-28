const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");

const iterations_bitmap_weight: u64 = 20_000;

fn bitmapWeightBench() struct { checksum: u64 } {
    const nbits = find_bit.bits_per_long + 5;
    const map = [_]find_bit.Word{
        0b1111,
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 8),
    };
    var checksum: u64 = 0;
    var idx: u64 = 0;
    while (idx < iterations_bitmap_weight) : (idx += 1) {
        checksum +%= @intCast(bitmap.weight(&map, nbits));
    }
    return .{ .checksum = checksum };
}

test "phase1 bitmap weight bench replay keeps the helper packet stable" {
    const nbits = find_bit.bits_per_long + 5;
    const map = [_]find_bit.Word{
        0b1111,
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 8),
    };
    try std.testing.expectEqual(@as(usize, 5), bitmap.weight(&map, nbits));
}

test "phase1 bitmap weight bench replay keeps the 20000-iteration checksum stable" {
    const result = bitmapWeightBench();
    try std.testing.expectEqual(@as(u64, 100_000), result.checksum);
}
