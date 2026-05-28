const std = @import("std");
const string = @import("string");

test "phase1 string prefix helpers keep C-string prefix length and alias rules aligned" {
    const prefix_cstr = [_]u8{ 'k', 'e', 'r', 'n', 'e', 'l', 0, 'x' };

    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix(&prefix_cstr, "ker"));
    try std.testing.expectEqual(@as(usize, 3), string.str_has_prefix("kernel", "ker"));
    try std.testing.expectEqual(@as(usize, 0), string.strHasPrefix("kernel", "xyz"));
    try std.testing.expect(string.strstarts("kernel", "ker"));
    try std.testing.expect(!string.strstarts("kernel", "ern"));
}

test "phase1 string suffix helpers keep C-string suffix length and alias rules aligned" {
    const suffix_cstr = [_]u8{ 'k', 'e', 'r', 'n', 'e', 'l', 0, 'y' };

    try std.testing.expectEqual(@as(usize, 3), string.strHasSuffix(&suffix_cstr, "nel"));
    try std.testing.expectEqual(@as(usize, 3), string.str_has_suffix("kernel", "nel"));
    try std.testing.expectEqual(@as(usize, 0), string.strHasSuffix("kernel", "xyz"));
    try std.testing.expect(string.strEndsWith(&suffix_cstr, "nel"));
    try std.testing.expect(string.str_ends_with("kernel", "nel"));
    try std.testing.expect(string.strends("kernel", "nel"));
    try std.testing.expect(!string.strEndsWith("kernel", "xyz"));
}

test "phase1 string prefix and suffix helpers stop at embedded NUL boundaries" {
    const prefixed = [_]u8{ 'a', 'b', 'c', 0, 'x', 'y', 'z' };
    const suffixed = [_]u8{ 'a', 'b', 'c', 0, 'x', 'y', 'z' };

    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix(&prefixed, "abc"));
    try std.testing.expectEqual(@as(usize, 0), string.strHasSuffix(&suffixed, "xyz"));
    try std.testing.expect(string.strEndsWith(&suffixed, "bc"));
    try std.testing.expectEqual(@as(usize, 0), string.strHasPrefix(&prefixed, "abcd"));
}
