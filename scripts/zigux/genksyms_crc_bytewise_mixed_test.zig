const std = @import("std");
const genksyms_crc = @import("genksyms_crc.zig");

test "partialCrc32One replays mixed bytes identically to crc32" {
    const payload = [_]u8{ 'm', 'o', 'd', 0, 'v', 'e', 'r', '\r', 0x80, 0xff, 's', 'y', 'm' };

    var bytewise_state: u32 = 0xffff_ffff;
    for (&payload) |byte| {
        bytewise_state = genksyms_crc.partialCrc32One(byte, bytewise_state);
    }

    try std.testing.expectEqual(@as(u32, 0xd411930d), genksyms_crc.crc32(&payload));
    try std.testing.expectEqual(genksyms_crc.crc32(&payload), bytewise_state ^ 0xffff_ffff);
}

test "partialCrc32 composes across mixed NUL carriage return and high-bit chunks" {
    const payload = [_]u8{ 'm', 'o', 'd', 0, 'v', 'e', 'r', '\r', 0x80, 0xff, 's', 'y', 'm' };

    const prefix_state = genksyms_crc.partialCrc32(payload[0..4], 0xffff_ffff);
    const cr_state = genksyms_crc.partialCrc32(payload[4..8], prefix_state);
    const high_state = genksyms_crc.partialCrc32(payload[8..10], cr_state);
    const final_crc = genksyms_crc.partialCrc32(payload[10..], high_state) ^ 0xffff_ffff;

    try std.testing.expectEqual(@as(u32, 0xaa12d27c), prefix_state ^ 0xffff_ffff);
    try std.testing.expectEqual(@as(u32, 0xa3a78a01), cr_state ^ 0xffff_ffff);
    try std.testing.expectEqual(genksyms_crc.crc32(&payload), final_crc);
}
