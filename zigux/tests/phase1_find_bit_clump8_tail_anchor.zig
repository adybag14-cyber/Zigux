const std = @import("std");
const find_bit = @import("../../tools/lib/find_bit.zig");

test "phase1 find_bit clump8 tail scans keep later in-range bits reachable from an interior start" {
    const nbits = find_bit.bits_per_long + 5;
    const start = find_bit.bits_per_long + 2;
    const bitmap = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 1) |
            (@as(find_bit.Word, 1) << 4) |
            (@as(find_bit.Word, 1) << 6),
    };
    var direct_clump: u8 = 0;
    var alias_clump: u8 = 0;

    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long),
        find_bit.findNextClump8(&direct_clump, &bitmap, nbits, start),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long),
        find_bit.find_next_clump8(&alias_clump, &bitmap, nbits, start),
    );
    try std.testing.expectEqual(@as(u8, 0b0001_0010), direct_clump);
    try std.testing.expectEqual(direct_clump, alias_clump);
}
