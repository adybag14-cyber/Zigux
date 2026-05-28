const std = @import("std");
const find_bit = @import("find_bit");
const bitmap = @import("bitmap");

const iterations_bitmap_window: u64 = 20_000;

fn bitmapWindowBench() struct { checksum: u64 } {
    const nbits = find_bit.bits_per_long + 5;
    const lhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 8) };
    const rhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 9) };
    var checksum: u64 = 0;
    var idx: u64 = 0;
    while (idx < iterations_bitmap_window) : (idx += 1) {
        var dst = [_]find_bit.Word{ 0, 0 };
        checksum +%= @intCast(bitmap.weightedOr(&dst, &lhs, &rhs, nbits));
        checksum +%= @intCast(bitmap.weightedXor(&dst, &lhs, &rhs, nbits));
        checksum +%= @intCast(bitmap.weight(&dst, nbits));
    }
    return .{ .checksum = checksum };
}

test "phase1 bitmap-window bench replay keeps the helper packet stable" {
    const nbits = find_bit.bits_per_long + 5;
    const lhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 8) };
    const rhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 9) };

    var or_dst = [_]find_bit.Word{ 0, 0 };
    try std.testing.expectEqual(@as(usize, 2), bitmap.weightedOr(&or_dst, &lhs, &rhs, nbits));
    try std.testing.expectEqual(
        (@as(find_bit.Word, 1) << 1) |
            (@as(find_bit.Word, 1) << 3) |
            (@as(find_bit.Word, 1) << 8) |
            (@as(find_bit.Word, 1) << 9),
        or_dst[1],
    );
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&or_dst, nbits));

    var xor_dst = [_]find_bit.Word{ 0, 0 };
    try std.testing.expectEqual(@as(usize, 2), bitmap.weightedXor(&xor_dst, &lhs, &rhs, nbits));
    try std.testing.expectEqual(
        (@as(find_bit.Word, 1) << 1) |
            (@as(find_bit.Word, 1) << 3) |
            (@as(find_bit.Word, 1) << 8) |
            (@as(find_bit.Word, 1) << 9),
        xor_dst[1],
    );
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&xor_dst, nbits));
}

test "phase1 bitmap-window bench replay keeps the 20000-iteration checksum stable" {
    const result = bitmapWindowBench();
    try std.testing.expectEqual(@as(u64, 120_000), result.checksum);
}
