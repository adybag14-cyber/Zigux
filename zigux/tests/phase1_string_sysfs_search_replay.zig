const std = @import("std");
const string = @import("string");

test "phase1 string replay keeps sysfs matching distinct from plain C-string matching" {
    const sysfs_haystack = [_][]const u8{
        "manual\n",
        "manual",
        "manual\n",
        "auto",
    };
    const plain_haystack = [_][]const u8{
        "manual\n",
        "manual",
        &[_]u8{ 'm', 'a', 'n', 'u', 'a', 'l', 0, 'x' },
        "auto",
    };

    try std.testing.expect(string.sysfsStreq("manual\n", "manual"));
    try std.testing.expect(!string.sysfsStreq("manual\n", "manuals"));
    try std.testing.expectEqual(@as(?usize, 0), string.sysfsMatchString(sysfs_haystack[0..], "manual"));
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(plain_haystack[0..], "manual"));
    try std.testing.expectEqual(@as(?usize, 1), string.match_string(plain_haystack[0..], "manual"));
    try std.testing.expectEqual(@as(?usize, null), string.sysfs_match_string(sysfs_haystack[0..], "missing"));
}

test "phase1 string replay keeps prefix suffix and counted scans inside C-string bounds" {
    const cstr = [_]u8{ 'm', 'o', 'd', 'e', '-', 'a', 0, 'x', 'x' };
    const prefixed = [_]u8{ 'm', 'o', 'd', 'e', 0, '-', 'x' };
    const suffixed = [_]u8{ 'a', 'u', 't', 'o', '\n', 0, 'x' };

    try std.testing.expectEqual(@as(usize, 4), string.strHasPrefix(prefixed[0..], "mode"));
    try std.testing.expect(string.strstarts(prefixed[0..], "mod"));
    try std.testing.expect(!string.strstarts(prefixed[0..], "node"));
    try std.testing.expect(string.strEndsWith(suffixed[0..], "o\n"));
    try std.testing.expect(!string.str_ends_with(suffixed[0..], "ox"));
    try std.testing.expectEqual(@as(?usize, 4), string.strnchr(cstr[0..], cstr.len, '-'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(cstr[0..], 4, '-'));
    try std.testing.expectEqual(@as(?usize, 6), string.strnchr(cstr[0..], cstr.len, 0));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(cstr[0..], 6, 0));
}
