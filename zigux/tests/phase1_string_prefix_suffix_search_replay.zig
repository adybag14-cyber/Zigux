const std = @import("std");
const string = @import("string");

test "phase1 string prefix suffix and bounded-search replay keeps helper aliases aligned" {
    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix("prefix-value", "pre"));
    try std.testing.expectEqual(@as(usize, 3), string.str_has_prefix("prefix-value", "pre"));
    try std.testing.expectEqual(@as(usize, 0), string.strHasPrefix("prefix-value", "suffix"));
    try std.testing.expect(string.strstarts("kernel", "ker"));
    try std.testing.expect(!string.strstarts("kernel", "ern"));
    try std.testing.expect(string.strEndsWith("kernel", "nel"));
    try std.testing.expect(string.str_ends_with("kernel", "nel"));
    try std.testing.expect(!string.strEndsWith("kernel", "ker"));
}

test "phase1 string prefix suffix and bounded-search replay keeps embedded-NUL boundaries explicit" {
    const cstr = [_]u8{ 'p', 'r', 'e', 'f', 'i', 'x', 0, 'x' };
    const suffix_cstr = [_]u8{ 'v', 'a', 'l', 'u', 'e', 0, 'x', 'x' };

    try std.testing.expectEqual(@as(usize, 6), string.strHasPrefix(&cstr, "prefix"));
    try std.testing.expect(string.strEndsWith(&suffix_cstr, "value"));
    try std.testing.expect(!string.strEndsWith(&suffix_cstr, "valued"));
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&[_]u8{ 'a', 'b', 0, 'c' }, 4, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&[_]u8{ 'a', 0, 'b', 'c' }, 4, 'b'));
}

test "phase1 string prefix suffix and bounded-search replay keeps bounded search helpers aligned" {
    try std.testing.expectEqual(@as(?usize, 0), string.strnchr("prefix-value", 1, 'p'));
    try std.testing.expectEqual(@as(?usize, 7), string.strnchr("prefix-value", 12, 'v'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr("prefix-value", 7, 'v'));
    try std.testing.expectEqual(@as(?usize, 2), string.strnchr(&[_]u8{ 'a', 'b', 0, 'c', 'd' }, 5, 0));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&[_]u8{ 'a', 'b', 0, 'c', 'd' }, 2, 0));
}
