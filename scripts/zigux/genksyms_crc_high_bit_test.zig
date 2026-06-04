const std = @import("std");
const genksyms_crc = @import("genksyms_crc.zig");

test "crc32 treats high-bit bytes as byte values" {
    const high_bytes = [_]u8{ 0x80, 0xff, 0x7f };

    try std.testing.expectEqual(@as(u32, 0x3fba6cad), genksyms_crc.crc32(high_bytes[0..1]));
    try std.testing.expectEqual(@as(u32, 0xff000000), genksyms_crc.crc32(high_bytes[1..2]));
    try std.testing.expectEqual(@as(u32, 0x4dea534d), genksyms_crc.crc32(&high_bytes));
}

test "partialCrc32 composes across high-bit byte boundaries" {
    const payload = [_]u8{ 'p', 'r', 'e', 'f', 'i', 'x', 0x80, 0xff, 's', 'u', 'f', 'f', 'i', 'x' };

    const prefix_crc = genksyms_crc.partialCrc32(payload[0..6], 0xffff_ffff);
    const high_crc = genksyms_crc.partialCrc32(payload[6..8], prefix_crc);
    const final_crc = genksyms_crc.partialCrc32(payload[8..], high_crc) ^ 0xffff_ffff;

    try std.testing.expectEqual(@as(u32, 0x4a1ae3ce), genksyms_crc.crc32(&payload));
    try std.testing.expectEqual(genksyms_crc.crc32(&payload), final_crc);
}
