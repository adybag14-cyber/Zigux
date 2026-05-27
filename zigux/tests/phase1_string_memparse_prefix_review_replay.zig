const std = @import("std");
const string = @import("string");

test "phase 1 string memparse replay keeps signed saturation and suffix rest aligned" {
    const signed_negative = string.memparse("-9000000000000Ktail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -9216000000000000))), signed_negative.value);
    try std.testing.expectEqualStrings("tail", signed_negative.rest);

    const signed_positive = string.memparse("+9223372036854775808more");
    try std.testing.expectEqual(@as(u64, @intCast(std.math.maxInt(i64))), signed_positive.value);
    try std.testing.expectEqualStrings("ore", signed_positive.rest);

    const invalid = string.memparse("-xyz");
    try std.testing.expectEqual(@as(u64, 0), invalid.value);
    try std.testing.expectEqualStrings("-xyz", invalid.rest);
}

test "phase 1 string prefix and suffix replay stops at the exported C-string boundary" {
    const prefix_cstr = [_]u8{ 'k', 'e', 'r', 'n', 'e', 'l', 0, 'x' };
    const suffix_cstr = [_]u8{ 'k', 'e', 'r', 'n', 'e', 'l', 0, 'y' };

    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix(&prefix_cstr, "ker"));
    try std.testing.expectEqual(@as(usize, 3), string.str_has_prefix(&prefix_cstr, "ker"));
    try std.testing.expect(string.strstarts(&prefix_cstr, "ker"));
    try std.testing.expectEqual(@as(usize, 0), string.strHasPrefix(&prefix_cstr, "kernelx"));

    try std.testing.expect(string.strEndsWith(&suffix_cstr, "nel"));
    try std.testing.expect(string.str_ends_with(&suffix_cstr, "nel"));
    try std.testing.expect(!string.strEndsWith(&suffix_cstr, "ely"));
}
