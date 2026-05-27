const std = @import("std");
const cmdline = @import("cmdline");

test "cmdline shared replay probe keeps signed and blank edge cases aligned" {
    const negative_invalid = cmdline.memparse("-xyz");
    try std.testing.expectEqual(@as(u64, 0), negative_invalid.value);
    try std.testing.expectEqualStrings("-xyz", negative_invalid.rest);

    const positive_invalid = cmdline.memparse("+nope");
    try std.testing.expectEqual(@as(u64, 0), positive_invalid.value);
    try std.testing.expectEqualStrings("+nope", positive_invalid.rest);

    const negative_hex = cmdline.memparse("-0x2Ktail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -2048))), negative_hex.value);
    try std.testing.expectEqualStrings("tail", negative_hex.rest);

    const positive_octal = cmdline.memparse("+010Mmore");
    try std.testing.expectEqual(@as(u64, 8 << 20), positive_octal.value);
    try std.testing.expectEqualStrings("more", positive_octal.rest);

    try std.testing.expect(cmdline.nextArg(" \t \n") == null);

    const empty = cmdline.nextArg("root=\"\" quiet") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("root", empty.param);
    try std.testing.expectEqualStrings("", empty.value.?);
    try std.testing.expectEqualStrings("quiet", empty.remaining);
}
