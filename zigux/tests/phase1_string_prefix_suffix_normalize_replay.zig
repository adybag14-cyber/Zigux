const std = @import("std");
const string = @import("string");

test "phase1 string prefix and suffix aliases stay aligned on C-string boundaries" {
    const cstr = [_]u8{ 'k', 'e', 'r', 'n', 'e', 'l', 0, 'x', 'y' };
    const prefix = [_]u8{ 'k', 'e', 'r', 0, 'z' };
    const suffix = [_]u8{ 'n', 'e', 'l', 0, 'z' };
    const miss = [_]u8{ 'e', 'l', 'f', 0, 'z' };

    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix(&cstr, &prefix));
    try std.testing.expectEqual(@as(usize, 3), string.str_has_prefix(&cstr, &prefix));
    try std.testing.expect(string.strstarts(&cstr, &prefix));

    try std.testing.expect(string.strEndsWith(&cstr, &suffix));
    try std.testing.expect(string.str_ends_with(&cstr, &suffix));
    try std.testing.expect(!string.strEndsWith(&cstr, &miss));

    try std.testing.expectEqual(@as(usize, 0), string.strHasPrefix("kernel", ""));
    try std.testing.expect(string.strstarts("kernel", ""));
    try std.testing.expect(string.strEndsWith("kernel", ""));
}

test "phase1 string in-place normalization stays bounded by the first NUL" {
    var spaced = [_]u8{ ' ', 'a', ' ', 'b', 0, ' ', 'c' };
    const trimmed = string.skipSpaces(&spaced);
    try std.testing.expectEqualStrings("a b", std.mem.sliceTo(trimmed, 0));
    try std.testing.expectEqual(@as(u8, 0), trimmed[3]);
    try std.testing.expectEqual(@as(u8, ' '), trimmed[4]);

    var removed = [_]u8{ 'a', ' ', 'b', 0, ' ', 'c' };
    try std.testing.expectEqualStrings("ab", string.removeSpaces(&removed));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 0, 0, ' ', 'c' }, &removed);

    var replaced = [_]u8{ 'a', '-', 'b', 0, '-', 'c' };
    try std.testing.expectEqual(@as(usize, 3), string.replaceChar(&replaced, '-', '_'));
    try std.testing.expectEqual(@as(usize, 3), string.strreplace(&replaced, '_', '-'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', '-', 'b', 0, '-', 'c' }, &replaced);
}
