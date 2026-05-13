const std = @import("std");
const string_helpers = @import("string_helpers");

test "phase 7 string helpers starter covers whitespace trimming and prefix skipping" {
    try std.testing.expectEqualStrings("hello", string_helpers.skipSpaces("   hello"));
    try std.testing.expectEqualStrings("world", string_helpers.skip_spaces("\t\nworld"));

    var trim_buf = [_]u8{ ' ', '\t', 'h', 'i', ' ', '\n' };
    try std.testing.expectEqualStrings("hi", string_helpers.trimSpaces(&trim_buf));

    var strim_buf = [_]u8{ ' ', 'h', 'i', ' ', '\n', 0, 'x', 'y' };
    try std.testing.expectEqualStrings("hi", string_helpers.strim(&strim_buf));
    try std.testing.expectEqualSlices(u8, &[_]u8{ ' ', 'h', 'i', 0, '\n', 0, 'x', 'y' }, &strim_buf);
}

test "phase 7 string helpers starter keeps sysfs matching newline aware" {
    try std.testing.expect(string_helpers.sysfsStreq("zigux\n", "zigux"));
    try std.testing.expect(string_helpers.sysfs_streq("zigux", "zigux\n"));
    try std.testing.expect(!string_helpers.sysfsStreq("zigux\nmore", "zigux"));

    const newline = [_]u8{ 'o', 'k', '\n', 0, 'x' };
    const nul = [_]u8{ 'o', 'k', 0, 'y' };
    try std.testing.expect(string_helpers.sysfsStreq(&newline, &nul));
}

test "phase 7 string helpers starter matches tables through the first null entry" {
    const values = [_]?[]const u8{
        "disabled",
        "auto\n",
        "manual",
        null,
        "ignored",
    };

    try std.testing.expectEqual(@as(?usize, 2), string_helpers.matchString(&values, "manual"));
    try std.testing.expectEqual(@as(?usize, 2), string_helpers.match_string(&values, "manual"));
    try std.testing.expectEqual(@as(?usize, 1), string_helpers.sysfsMatchString(&values, "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string_helpers.__sysfs_match_string(&values, "auto\n"));
    try std.testing.expectEqual(@as(?usize, null), string_helpers.matchString(&values, "ignored"));
}

test "phase 7 string helpers starter replaces bytes only inside the exported c-string prefix" {
    var replace_buf = [_]u8{ 'a', '-', 'b', 0, '-' };
    try std.testing.expectEqual(@as(usize, 3), string_helpers.strreplace(&replace_buf, '-', '_'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', '_', 'b', 0, '-' }, &replace_buf);
}
