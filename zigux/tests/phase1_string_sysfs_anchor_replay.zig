const std = @import("std");
const string = @import("string");

test "phase1 string sysfs replay keeps newline-aware lookup ahead of plain matchString" {
    const haystack = [_][]const u8{
        "mode\n",
        "mode",
        "manual",
    };

    try std.testing.expectEqual(@as(?usize, 0), string.sysfsMatchString(haystack[0..], "mode"));
    try std.testing.expectEqual(@as(?usize, 0), string.sysfs_match_string(haystack[0..], "mode"));
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(haystack[0..], "mode"));
    try std.testing.expectEqual(@as(?usize, 1), string.match_string(haystack[0..], "mode"));
}

test "phase1 string sysfs replay keeps trailing newline equivalence scoped to sysfs helpers" {
    const newline_terminated = [_]u8{ 'a', 'u', 't', 'o', '\n', 0 };
    const nul_terminated = [_]u8{ 'a', 'u', 't', 'o', 0 };
    const haystack = [_][]const u8{
        &newline_terminated,
        &nul_terminated,
        "other",
    };

    try std.testing.expect(string.sysfsStreq(&newline_terminated, &nul_terminated));
    try std.testing.expect(string.sysfs_streq(&newline_terminated, &nul_terminated));
    try std.testing.expect(!string.streq(&newline_terminated, &nul_terminated));

    try std.testing.expectEqual(@as(?usize, 0), string.sysfsMatchString(haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(haystack[0..], "auto"));
}

test "phase1 string sysfs replay keeps first-match order stable across repeated newline variants" {
    const haystack = [_][]const u8{
        "off",
        "auto\n",
        "auto",
        "auto\n",
        "on",
    };

    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 2), string.matchString(haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, null), string.sysfsMatchString(haystack[0..], "missing"));
    try std.testing.expectEqual(@as(?usize, null), string.matchString(haystack[0..], "missing"));
}
