const std = @import("std");
const genksyms_crc = @import("genksyms_crc.zig");

test "genksyms CRC32 matches the standard check vector" {
    const vector = "123456789";

    try std.testing.expectEqual(@as(u32, 0xcbf4_3926), genksyms_crc.crc32(vector));
}

test "genksyms partial CRC32 composes the standard check vector" {
    const vector = "123456789";
    const prefix = genksyms_crc.partialCrc32(vector[0..3], 0xffff_ffff);
    const middle = genksyms_crc.partialCrc32(vector[3..6], prefix);
    const combined = genksyms_crc.partialCrc32(vector[6..], middle) ^ 0xffff_ffff;

    try std.testing.expectEqual(genksyms_crc.crc32(vector), combined);
    try std.testing.expectEqual(@as(u32, 0xcbf4_3926), combined);
}

test "genksyms bytewise CRC32 agrees with slice CRC32" {
    const vector = "123456789";
    var crc: u32 = 0xffff_ffff;
    for (vector) |byte| {
        crc = genksyms_crc.partialCrc32One(byte, crc);
    }

    const bytewise = crc ^ 0xffff_ffff;
    try std.testing.expectEqual(genksyms_crc.crc32(vector), bytewise);
}
