const std = @import("std");
const hexdump = @import("hexdump");

test "hexToBin matches basic digit and alpha decoding" {
    try std.testing.expectEqual(@as(i32, 0), hexdump.hexToBin('0'));
    try std.testing.expectEqual(@as(i32, 10), hexdump.hexToBin('a'));
    try std.testing.expectEqual(@as(i32, 15), hexdump.hexToBin('F'));
    try std.testing.expectEqual(@as(i32, -1), hexdump.hexToBin('x'));
}

test "hex2bin decodes a bounded mixed-case fixture" {
    var decoded: [8]u8 = undefined;

    try hexdump.hex2bin(&decoded, "DeAdBEEF01234567");
    try std.testing.expectEqualSlices(
        u8,
        &.{ 0xde, 0xad, 0xbe, 0xef, 0x01, 0x23, 0x45, 0x67 },
        &decoded,
    );
}

test "bin2hex round-trips a bounded sample" {
    const source = [_]u8{ 0x00, 0x12, 0xab, 0xff, 0x34, 0x80 };
    var encoded: [source.len * 2]u8 = undefined;
    var decoded: [source.len]u8 = undefined;

    const written = try hexdump.bin2hex(&encoded, &source);
    try std.testing.expectEqualStrings("0012abff3480", written);

    try hexdump.hex2bin(&decoded, written);
    try std.testing.expectEqualSlices(u8, &source, &decoded);
}

test "hex helpers reject malformed inputs" {
    var decoded: [2]u8 = undefined;
    var short_encoded: [3]u8 = undefined;

    try std.testing.expectError(error.InvalidSourceLength, hexdump.hex2bin(&decoded, "abc"));
    try std.testing.expectError(error.InvalidHexDigit, hexdump.hex2bin(&decoded, "0x00"));
    try std.testing.expectError(error.DestinationTooSmall, hexdump.bin2hex(&short_encoded, &.{ 0xaa, 0xbb }));
}
