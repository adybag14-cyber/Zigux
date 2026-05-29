const std = @import("std");
const find_bit = @import("find_bit.zig");

test "getValue8 reads aligned bytes at word edges" {
    const Word = find_bit.Word;
    const last_byte_offset = find_bit.bits_per_long - 8;
    var bitmap = [_]Word{ 0, 0 };

    bitmap[0] = @as(Word, 0xa5) << @intCast(last_byte_offset);
    bitmap[1] = @as(Word, 0x5a);

    try std.testing.expectEqual(@as(u8, 0xa5), find_bit.getValue8(&bitmap, last_byte_offset));
    try std.testing.expectEqual(@as(u8, 0x5a), find_bit.getValue8(&bitmap, find_bit.bits_per_long));
}
