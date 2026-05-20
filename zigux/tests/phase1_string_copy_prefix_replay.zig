const std = @import("std");
const string = @import("string");

test "string copy helpers preserve C-string boundaries and padding" {
    const src_cstr = [_]u8{ 'o', 'k', 0, 'x', 'y' };

    var tiny = [_]u8{0xaa};
    try std.testing.expectEqual(@as(usize, 2), string.strlcpy(&tiny, &src_cstr));
    try std.testing.expectEqualSlices(u8, &[_]u8{0}, &tiny);

    var copied = [_]u8{0xaa} ** 4;
    try std.testing.expectEqual(@as(isize, 2), string.strscpy(&copied, &src_cstr));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0xaa }, &copied);

    var truncated = [_]u8{0xaa} ** 3;
    try std.testing.expectEqual(@as(isize, -7), string.strscpy(&truncated, "long"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'l', 'o', 0 }, &truncated);

    var padded = [_]u8{0xaa} ** 5;
    try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(&padded, &src_cstr));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0, 0 }, &padded);

    var alias_padded = [_]u8{0xaa} ** 5;
    try std.testing.expectEqual(@as(isize, 2), string.strscpy_pad(&alias_padded, "hi"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'i', 0, 0, 0 }, &alias_padded);
}

test "string prefix and suffix helpers ignore storage past embedded NUL" {
    const embedded = [_]u8{ 'n', 'o', 'd', 'e', 0, 'x', 'y' };
    const embedded_prefix = [_]u8{ 'n', 'o', 'd', 'e', 0, 'z' };
    const embedded_suffix = [_]u8{ 'd', 'e', 0, 'z' };

    try std.testing.expect(string.strEq(&embedded, "node"));
    try std.testing.expect(string.streq(&embedded, &embedded_prefix));
    try std.testing.expect(!string.strEq(&embedded, "nodes"));

    try std.testing.expectEqual(@as(usize, 4), string.strHasPrefix(&embedded, "node"));
    try std.testing.expectEqual(@as(usize, 4), string.str_has_prefix(&embedded, &embedded_prefix));
    try std.testing.expectEqual(@as(usize, 0), string.strHasPrefix(&embedded, "nodes"));
    try std.testing.expect(string.strstarts(&embedded, "node"));

    try std.testing.expect(string.strEndsWith(&embedded, "de"));
    try std.testing.expect(string.str_ends_with(&embedded, &embedded_suffix));
    try std.testing.expect(string.strEndsWith(&embedded, ""));
    try std.testing.expect(!string.strEndsWith(&embedded, "ode/"));
}
