const std = @import("std");
const genksyms_crc = @import("genksyms_crc.zig");

fn byteSweepPayload() [256]u8 {
    var payload: [256]u8 = undefined;
    for (&payload, 0..) |*byte, index| {
        byte.* = @intCast(index);
    }
    return payload;
}

test "crc32 covers the complete byte-value sweep" {
    const payload = byteSweepPayload();

    try std.testing.expectEqual(@as(u32, 0x29058c73), genksyms_crc.crc32(&payload));

    var state: u32 = 0xffff_ffff;
    state = genksyms_crc.partialCrc32(payload[0..64], state);
    state = genksyms_crc.partialCrc32(payload[64..129], state);
    state = genksyms_crc.partialCrc32(payload[129..], state);

    try std.testing.expectEqual(@as(u32, 0x29058c73), state ^ 0xffff_ffff);
}

test "partialCrc32One matches slice replay for every byte and seed" {
    const seeds = [_]u32{
        0x0000_0000,
        0xffff_ffff,
        0x1234_5678,
        0xa5a5_5a5a,
    };

    for (seeds) |seed| {
        for (0..256) |index| {
            const byte: u8 = @intCast(index);
            const single = [_]u8{byte};
            try std.testing.expectEqual(
                genksyms_crc.partialCrc32(single[0..], seed),
                genksyms_crc.partialCrc32One(byte, seed),
            );
        }
    }
}
