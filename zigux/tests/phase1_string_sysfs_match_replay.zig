const std = @import("std");
const string = @import("string");

test "phase1 string sysfs replay keeps newline-aware first-match order under count limits" {
    const haystack = [_][]const u8{ "off", "auto\n", "auto", "on" };
    const limited = haystack[0..3];

    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(limited, "auto"));
    try std.testing.expectEqual(@as(?usize, null), string.sysfsMatchString(haystack[0..1], "auto"));
}

test "phase1 string sysfs replay keeps alias behavior for empty and matched lists" {
    const haystack = [_][]const u8{ "mode\n", "manual", "mode" };
    const empty = [_][]const u8{};

    try std.testing.expectEqual(@as(?usize, 0), string.sysfs_match_string(haystack[0..], "mode"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(haystack[0..], "manual"));
    try std.testing.expectEqual(@as(?usize, null), string.sysfs_match_string(empty[0..], "mode"));
}

test "phase1 string match replay keeps C-string boundaries and first-match order" {
    const haystack = [_][]const u8{
        &[_]u8{ 'a', 0, 'x' },
        "alpha",
        &[_]u8{ 'a', 'l', 'p', 'h', 'a', 0, 'z' },
    };
    const empty = [_][]const u8{};

    try std.testing.expectEqual(@as(?usize, 0), string.matchString(haystack[0..], "a"));
    try std.testing.expectEqual(@as(?usize, 1), string.match_string(haystack[0..], "alpha"));
    try std.testing.expectEqual(@as(?usize, null), string.matchString(haystack[0..], "alphabet"));
    try std.testing.expectEqual(@as(?usize, null), string.match_string(empty[0..], "alpha"));
}
