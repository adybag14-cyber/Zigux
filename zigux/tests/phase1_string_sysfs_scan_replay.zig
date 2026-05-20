const std = @import("std");
const string = @import("string");

test "phase 1 string sysfs helpers keep newline-aware first-match semantics" {
    const haystack = [_][]const u8{
        "disabled",
        "auto\n",
        "auto",
        "enabled",
    };

    try std.testing.expect(string.sysfsStreq("auto\n", "auto"));
    try std.testing.expect(string.sysfs_streq("enabled\n", "enabled"));
    try std.testing.expect(!string.sysfsStreq("auto\n", "enabled"));

    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, null), string.sysfsMatchString(haystack[0..], "missing"));
}

test "phase 1 string match helpers keep C-string first-match semantics" {
    const haystack = [_][]const u8{
        &[_]u8{ 'a', 'l', 'p', 'h', 'a', 0, 'x' },
        "beta",
        "alpha",
    };

    try std.testing.expectEqual(@as(?usize, 0), string.matchString(haystack[0..], "alpha"));
    try std.testing.expectEqual(@as(?usize, 0), string.match_string(haystack[0..], "alpha"));
    try std.testing.expectEqual(@as(?usize, null), string.matchString(haystack[0..], "gamma"));
}

test "phase 1 string strnchr stays bounded by count and embedded NUL" {
    const cstr = [_]u8{ 'a', 'b', 0, 'c', 'b' };

    try std.testing.expectEqual(@as(?usize, 1), string.strnchr("abcd", 4, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr("abcd", 1, 'b'));
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&cstr, cstr.len, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&cstr, cstr.len, 'c'));
    try std.testing.expectEqual(@as(?usize, 2), string.strnchr(&cstr, cstr.len, 0));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&cstr, 2, 0));
}
