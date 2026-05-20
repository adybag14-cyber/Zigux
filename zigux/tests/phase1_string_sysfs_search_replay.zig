const std = @import("std");
const string = @import("string");

test "phase1 string sysfs replay keeps newline-aware equality and first-match order" {
    const haystack = [_][]const u8{ "off", "auto\n", "auto", "auto\n", "on" };

    try std.testing.expect(string.sysfsStreq("auto\n", "auto"));
    try std.testing.expect(string.sysfs_streq("mode\n", "mode"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.__sysfs_match_string(haystack[0..], 3, "auto"));
    try std.testing.expectEqual(@as(?usize, null), string.__sysfs_match_string(haystack[0..], 1, "auto"));
}

test "phase1 string search replay keeps counted and C-string boundaries aligned" {
    const c_lookup = [_][]const u8{
        &[_]u8{ 'a', 0, 'x' },
        "beta",
        "alpha",
    };
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(c_lookup[0..], "a"));
    try std.testing.expectEqual(@as(?usize, 1), string.match_string(&[_][]const u8{ "skip", "keep" }, "keep"));

    const counted = [_]u8{ 'a', 'b', 0, 'c', 'd' };
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&counted, counted.len, 'c'));
    try std.testing.expectEqual(@as(usize, 2), string.strnchrNul(&counted, counted.len, 'z'));
    try std.testing.expectEqual(@as(usize, 2), string.strnlen(&counted, counted.len));
    try std.testing.expectEqual(@as(?usize, 1), string.strpbrk("kernel", "xyre"));
    try std.testing.expectEqual(@as(usize, 4), string.strspn("abba!", "ab"));
    try std.testing.expectEqual(@as(usize, 1), string.strspn(&[_]u8{ 'a', 0, 'b' }, "ab"));
    try std.testing.expectEqual(@as(usize, 1), string.strchrNul("abc", 'b'));
    try std.testing.expectEqual(@as(usize, 3), string.strchrnul("abc", 'z'));
}
