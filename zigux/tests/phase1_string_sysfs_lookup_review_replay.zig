const std = @import("std");
const string = @import("string");

test "phase1 string sysfs lookup replay keeps newline-aware first-match order stable" {
    const haystack = [_][]const u8{
        "off",
        "auto\n",
        "auto",
        "on",
    };

    try std.testing.expect(string.sysfsStreq("auto\n", "auto"));
    try std.testing.expect(string.sysfs_streq("auto\n", "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(haystack[0..3], "auto"));
    try std.testing.expectEqual(@as(?usize, null), string.sysfsMatchString(haystack[0..1], "auto"));
}

test "phase1 string lookup replay keeps C-string first-match order separate from sysfs matching" {
    const c_string_haystack = [_][]const u8{
        &[_]u8{ 'a', 0, 'x' },
        "alpha",
        "alpha",
    };
    const sysfs_haystack = [_][]const u8{
        "alpha\n",
        "alpha",
    };

    try std.testing.expectEqual(@as(?usize, 0), string.matchString(c_string_haystack[0..], "a"));
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(c_string_haystack[0..], "alpha"));
    try std.testing.expectEqual(@as(?usize, 1), string.match_string(c_string_haystack[0..], "alpha"));
    try std.testing.expectEqual(@as(?usize, 0), string.sysfsMatchString(sysfs_haystack[0..], "alpha"));
    try std.testing.expectEqual(@as(?usize, 0), string.sysfs_match_string(sysfs_haystack[0..], "alpha"));
}

test "phase1 string sysfs lookup replay keeps empty and limited scans parked at null" {
    const empty = [_][]const u8{};
    const haystack = [_][]const u8{
        "mode\n",
        "value",
    };

    try std.testing.expectEqual(@as(?usize, null), string.sysfsMatchString(empty[0..], "mode"));
    try std.testing.expectEqual(@as(?usize, null), string.match_string(empty[0..], "mode"));
    try std.testing.expectEqual(@as(?usize, 0), string.sysfsMatchString(haystack[0..1], "mode"));
    try std.testing.expectEqual(@as(?usize, null), string.sysfsMatchString(haystack[0..1], "value"));
    try std.testing.expectEqual(@as(?usize, null), string.matchString(haystack[0..], "missing"));
}
