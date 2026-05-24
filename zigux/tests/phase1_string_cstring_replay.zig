const std = @import("std");
const string = @import("string");

test "phase1 string replay keeps c-string boundary helpers aligned" {
    var trim_buf = [_]u8{ ' ', 'a', ' ', 'b', ' ', 0, 'x' };
    const trimmed = string.trimSpaces(trim_buf[0..]);
    try std.testing.expectEqualStrings("a b", trimmed);
    try std.testing.expectEqualStrings("a b", string.strstrip(trim_buf[0..]));

    var remove_buf = [_]u8{ 'a', ' ', 'b', ' ', 0, 'x' };
    const removed = string.removeSpaces(remove_buf[0..]);
    try std.testing.expectEqualStrings("ab", removed);

    var replace_buf = [_]u8{ 'a', '-', 'b', 0, '-' };
    try std.testing.expectEqual(@as(usize, 3), string.replaceChar(replace_buf[0..], '-', '+'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', '+', 'b', 0, '-' }, replace_buf[0..]);

    try std.testing.expectEqualStrings("lead", string.skipSpaces("  \tlead"));
    try std.testing.expect(string.streq(&[_]u8{ 'a', 0, 'x' }, &[_]u8{ 'a', 0, 'y' }));
    try std.testing.expect(!string.streq("abc", "abd"));
}

test "phase1 string replay keeps memparse signed suffix handling aligned" {
    const decimal = string.memparse("64K rest");
    try std.testing.expectEqual(@as(u64, 64 << 10), decimal.value);
    try std.testing.expectEqualStrings(" rest", decimal.rest);

    const negative = string.memparse("-2Ktail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -2048))), negative.value);
    try std.testing.expectEqualStrings("tail", negative.rest);

    const invalid = string.memparse("+nope");
    try std.testing.expectEqual(@as(u64, 0), invalid.value);
    try std.testing.expectEqualStrings("+nope", invalid.rest);
}

test "phase1 string replay keeps prefix and inverse-byte helpers aligned" {
    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix(&[_]u8{ 'a', 'b', 'c', 0, 'x' }, "abc"));
    try std.testing.expectEqual(@as(usize, 3), string.str_has_prefix("abcdef", "abc"));
    try std.testing.expectEqual(@as(usize, 0), string.strHasPrefix("abcdef", "abd"));

    try std.testing.expectEqual(@as(?usize, 2), string.memchrInv(&[_]u8{ 'x', 'x', 'y' }, 'x'));
    try std.testing.expectEqual(@as(?usize, null), string.memchrInv(&[_]u8{ 'x', 'x', 'x' }, 'x'));

    var long_buf = [_]u8{0} ** 32;
    long_buf[19] = 1;
    try std.testing.expectEqual(@as(?usize, 19), string.memchrInv(long_buf[0..], 0));
}

test "phase1 string replay keeps sysfs and match-string order aligned" {
    const sysfs_haystack = [_][]const u8{ "off", "auto\n", "auto", "on" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs_haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(sysfs_haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, null), string.sysfsMatchString(sysfs_haystack[0..], "missing"));

    const match_haystack = [_][]const u8{
        &[_]u8{ 'a', 0, 'x' },
        "beta",
        "alpha",
    };
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(match_haystack[0..], "a"));
    try std.testing.expectEqual(@as(?usize, 0), string.match_string(match_haystack[0..], "a"));
    try std.testing.expectEqual(@as(?usize, null), string.matchString(match_haystack[0..], "gamma"));
}
