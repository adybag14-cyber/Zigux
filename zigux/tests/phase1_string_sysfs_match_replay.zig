const std = @import("std");
const string = @import("string");

test "phase1 string sysfs helpers keep newline-aware first-match and count bounds" {
    const haystack = [_][]const u8{ "off\n", "auto", "auto\n", "on" };
    const empty = [_][]const u8{};

    try std.testing.expect(string.sysfsStreq("auto\n", "auto"));
    try std.testing.expect(!string.sysfsStreq("auto\n", "aux"));

    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(haystack[0..], "auto\n"));
    try std.testing.expectEqual(@as(?usize, 0), string.sysfs_match_string(haystack[0..], "off"));
    try std.testing.expectEqual(@as(?usize, null), string.sysfsMatchString(haystack[0..], "missing"));
    try std.testing.expectEqual(@as(?usize, null), string.sysfs_match_string(empty[0..], "off"));
}

test "phase1 string match helpers keep c-string first-match and nul boundaries" {
    const haystack = [_][]const u8{
        &[_]u8{ 'm', 'o', 'd', 'e', 0, 'x' },
        "mode",
        "model",
        "node",
    };
    const empty = [_][]const u8{};

    try std.testing.expect(string.strEq(&[_]u8{ 'm', 'o', 'd', 'e', 0, 'x' }, "mode"));
    try std.testing.expect(!string.strEq("mode", "model"));

    try std.testing.expectEqual(@as(?usize, 0), string.matchString(haystack[0..], "mode"));
    try std.testing.expectEqual(@as(?usize, 2), string.match_string(haystack[0..], "model"));
    try std.testing.expectEqual(@as(?usize, null), string.matchString(haystack[0..], "missing"));
    try std.testing.expectEqual(@as(?usize, null), string.match_string(empty[0..], "mode"));
}
