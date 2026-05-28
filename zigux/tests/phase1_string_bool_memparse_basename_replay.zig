const std = @import("std");
const string = @import("string");

test "strtobool accepts Linux-style truthy and falsy aliases and rejects empty inputs" {
    try std.testing.expect(try string.strtobool("enable") == true);
    try std.testing.expect(try string.strtobool("true") == true);
    try std.testing.expect(try string.strtobool("1") == true);
    try std.testing.expect(try string.strtobool("disable") == false);
    try std.testing.expect(try string.strtobool("False") == false);
    try std.testing.expect(try string.strtobool("0") == false);
    try std.testing.expectError(error.Invalid, string.strtobool(""));
    try std.testing.expectError(error.Invalid, string.strtobool(null));
    try std.testing.expectError(error.Invalid, string.strtobool("maybe"));
}

test "memparse keeps signed suffixes and unchanged rest aligned" {
    const negative_hex = string.memparse("-0x2Ktail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -2048))), negative_hex.value);
    try std.testing.expectEqualStrings("tail", negative_hex.rest);

    const positive_octal = string.memparse("+010Mmore");
    try std.testing.expectEqual(@as(u64, 8 << 20), positive_octal.value);
    try std.testing.expectEqualStrings("more", positive_octal.rest);

    const invalid = string.memparse("+nope");
    try std.testing.expectEqual(@as(u64, 0), invalid.value);
    try std.testing.expectEqualStrings("+nope", invalid.rest);
}

test "kbasename stops at the C-string boundary and returns the final path component" {
    try std.testing.expectEqualStrings("console", string.kbasename("/sys/devices/console"));
    try std.testing.expectEqualStrings(
        "node",
        string.kbasename(&[_]u8{ '/', 'a', '/', 'n', 'o', 'd', 'e', 0, '/', 'x' }),
    );
    try std.testing.expectEqualStrings("", string.kbasename("/tmp/"));
}
