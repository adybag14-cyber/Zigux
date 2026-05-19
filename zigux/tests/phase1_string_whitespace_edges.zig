const std = @import("std");
const string = @import("string");

test "phase1 string whitespace edges keep prefix skipping aligned with embedded NUL boundaries" {
    try std.testing.expectEqualStrings("hello", string.skipSpaces(" \t\nhello"));
    try std.testing.expectEqualStrings("hello", string.skip_spaces(" \t\nhello"));

    const nul_prefixed = [_]u8{ ' ', '\t', 0, 'x', 'y' };
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 'x', 'y' }, string.skipSpaces(&nul_prefixed));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 'x', 'y' }, string.skip_spaces(&nul_prefixed));
}

test "phase1 string whitespace edges trim in place without disturbing bytes beyond the C-string" {
    var trim_buf = [_]u8{ ' ', '\t', 'h', 'i', ' ', '\n' };
    try std.testing.expectEqualStrings("hi", string.trimSpaces(&trim_buf));

    var whitespace_only = [_]u8{ ' ', '\t', '\n', 0, 'x' };
    try std.testing.expectEqualStrings("", string.trimSpaces(&whitespace_only));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, '\t', '\n', 0, 'x' }, &whitespace_only);

    var strim_buf = [_]u8{ ' ', 'o', 'k', ' ', '\n', 0, 'x' };
    try std.testing.expectEqualStrings("ok", string.strim(&strim_buf));
    try std.testing.expectEqualSlices(u8, &[_]u8{ ' ', 'o', 'k', 0, '\n', 0, 'x' }, &strim_buf);

    var strstrip_buf = [_]u8{ ' ', 'a', 'b', 0, ' ', '\n', 'z' };
    try std.testing.expectEqualStrings("ab", string.strstrip(&strstrip_buf));
    try std.testing.expectEqualSlices(u8, &[_]u8{ ' ', 'a', 'b', 0, ' ', '\n', 'z' }, &strstrip_buf);
}

test "phase1 string whitespace edges only remove literal spaces and preserve other separators" {
    var remove_buf = [_]u8{ ' ', 'a', '\t', ' ', 'b', '\n', ' ', 'c', 0, 'x' };
    try std.testing.expectEqualStrings("a\tb\nc", string.removeSpaces(&remove_buf));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', '\t', 'b', '\n', 'c', 0, ' ', 'c', 0, 'x' }, &remove_buf);

    var alias_buf = [_]u8{ ' ', 'a', ' ', 'b', 0, 'x' };
    try std.testing.expectEqualStrings("ab", string.remove_spaces(&alias_buf));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 0, 'b', 0, 'x' }, &alias_buf);
}

test "phase1 string whitespace edges keep earliest dirty byte across long memchrInv scans" {
    var zero_scan = [_]u8{0} ** 96;
    zero_scan[17] = 0x7f;
    zero_scan[44] = 0x33;
    try std.testing.expectEqual(@as(?usize, 17), string.memchrInv(&zero_scan, 0));
    try std.testing.expectEqual(@as(?usize, 17), string.memchr_inv(&zero_scan, 0));

    var non_zero_scan = [_]u8{'a'} ** 96;
    non_zero_scan[40] = 'X';
    non_zero_scan[71] = 'Y';
    try std.testing.expectEqual(@as(?usize, 40), string.memchrInv(&non_zero_scan, 'a'));
    non_zero_scan[40] = 'a';
    try std.testing.expectEqual(@as(?usize, 71), string.memchrInv(&non_zero_scan, 'a'));
}

test "phase1 string whitespace edges keep sysfs newline equivalence without hiding extra payload" {
    try std.testing.expect(string.sysfsStreq("zigux\n", "zigux"));
    try std.testing.expect(string.sysfs_streq("zigux", "zigux\n"));
    try std.testing.expect(!string.sysfsStreq("zigux\nmore", "zigux"));

    const newline = [_]u8{ 'o', 'k', '\n', 0, 'x' };
    const nul = [_]u8{ 'o', 'k', 0, 'y' };
    try std.testing.expect(string.sysfsStreq(&newline, &nul));
}
