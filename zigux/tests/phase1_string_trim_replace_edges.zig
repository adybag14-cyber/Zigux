const std = @import("std");
const string = @import("string");

test "phase1 string trim helpers stop at the first embedded terminator and normalize all-space buffers" {
    var bounded = [_]u8{ ' ', '\t', 'o', 'k', ' ', 0, 'x', 'x' };
    try std.testing.expectEqualStrings("ok", string.trimSpaces(bounded[0..]));
    try std.testing.expectEqualStrings("ok", string.strim(bounded[0..]));
    try std.testing.expectEqualStrings("ok", string.strstrip(bounded[0..]));

    var spaces_only = [_]u8{ ' ', '\n', '\t', 0, 'x' };
    try std.testing.expectEqualStrings("", string.trimSpaces(spaces_only[0..]));
    try std.testing.expectEqual(@as(u8, 0), spaces_only[0]);
}

test "phase1 string remove helpers keep bytes after the first terminator untouched" {
    var remove_buf = [_]u8{ ' ', 'a', ' ', 'b', 0, ' ', 'c' };
    try std.testing.expectEqualStrings("ab", string.removeSpaces(remove_buf[0..]));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 0, 'b', 0, ' ', 'c' }, remove_buf[0..]);

    var alias_buf = [_]u8{ 'x', ' ', 'y', 0, ' ', 'z' };
    try std.testing.expectEqualStrings("xy", string.remove_spaces(alias_buf[0..]));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', 'y', 0, 0, ' ', 'z' }, alias_buf[0..]);
}

test "phase1 string replace helpers stop at the first terminator and report the visible length" {
    var replace_buf = [_]u8{ 'a', '-', 'b', 0, '-', 'c' };
    try std.testing.expectEqual(@as(usize, 3), string.replaceChar(replace_buf[0..], '-', '+'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', '+', 'b', 0, '-', 'c' }, replace_buf[0..]);

    var alias_buf = [_]u8{ 'm', '_', 'n', 0, '_', 'o' };
    try std.testing.expectEqual(@as(usize, 3), string.strreplace(alias_buf[0..], '_', '-'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'm', '-', 'n', 0, '_', 'o' }, alias_buf[0..]);
}

test "phase1 string prefix and suffix helpers honor embedded terminators and alias forms" {
    const bounded = [_]u8{ 'p', 'r', 'e', 'f', 'i', 'x', 0, '!' };
    const prefix = [_]u8{ 'p', 'r', 'e', 0, '?' };
    const suffix = [_]u8{ 'f', 'i', 'x', 0, '?' };

    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix(bounded[0..], prefix[0..]));
    try std.testing.expectEqual(@as(usize, 3), string.str_has_prefix(bounded[0..], "pre"));
    try std.testing.expect(string.strstarts(bounded[0..], "prefix"));
    try std.testing.expect(string.strEndsWith(bounded[0..], suffix[0..]));
    try std.testing.expect(string.str_ends_with(bounded[0..], "fix"));
    try std.testing.expect(!string.strEndsWith(bounded[0..], "fix!"));
}
