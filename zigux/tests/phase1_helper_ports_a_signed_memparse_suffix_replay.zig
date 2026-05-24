const std = @import("std");
const string = @import("string");

test "phase1 helper ports A keeps signed hexadecimal memparse suffixes aligned with trailing rest" {
    const negative_hex = string.memparse("-0x10Ktail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -16384))), negative_hex.value);
    try std.testing.expectEqualStrings("tail", negative_hex.rest);

    const positive_hex = string.memparse("+0x20mrest");
    try std.testing.expectEqual(@as(u64, 0x20 << 20), positive_hex.value);
    try std.testing.expectEqualStrings("rest", positive_hex.rest);
}

test "phase1 helper ports A keeps signed octal memparse suffixes aligned with trailing rest" {
    const negative_octal = string.memparse("-010Ktail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -8192))), negative_octal.value);
    try std.testing.expectEqualStrings("tail", negative_octal.rest);

    const positive_octal = string.memparse("+077Mrest");
    try std.testing.expectEqual(@as(u64, 63 << 20), positive_octal.value);
    try std.testing.expectEqualStrings("rest", positive_octal.rest);
}
