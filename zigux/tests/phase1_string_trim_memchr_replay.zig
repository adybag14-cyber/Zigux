const std = @import("std");
const string = @import("string");

test "phase1 string trim and replace helpers stop at the visible C-string boundary" {
    const skip_buf = [_]u8{ ' ', '\t', 'o', 'k', ' ', 0, 'x' };
    var trim_buf = [_]u8{ ' ', '\t', 'o', 'k', ' ', 0, 'x' };
    var remove_buf = [_]u8{ 'a', ' ', 'b', ' ', 0, 'x' };
    var replace_buf = [_]u8{ 'a', '-', 'b', 0, '-' };

    const skipped = string.skipSpaces(&skip_buf);
    try std.testing.expectEqualStrings("ok \x00x", skipped);
    try std.testing.expectEqualStrings("ok", string.trimSpaces(&trim_buf));
    try std.testing.expectEqualStrings("ok", string.strim(&trim_buf));
    try std.testing.expectEqualStrings("ok", string.strstrip(&trim_buf));

    try std.testing.expectEqualStrings("ab", string.removeSpaces(&remove_buf));
    try std.testing.expectEqualStrings("ab", string.remove_spaces(&remove_buf));

    try std.testing.expectEqual(@as(usize, 3), string.replaceChar(&replace_buf, '-', '+'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', '+', 'b', 0, '-' }, &replace_buf);

    replace_buf = .{ 'a', '-', 'b', 0, '-' };
    try std.testing.expectEqual(@as(usize, 3), string.strreplace(&replace_buf, '-', '+'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', '+', 'b', 0, '-' }, &replace_buf);
}

test "phase1 string memchr helpers keep the earliest dirty byte across alignment shifts" {
    for (0..@sizeOf(usize)) |offset| {
        var zero_backing = [_]u8{0} ** 40;
        zero_backing[offset + 13] = 4;
        try std.testing.expectEqual(@as(?usize, 13), string.memchrInv(zero_backing[offset .. offset + 32], 0));
        try std.testing.expectEqual(@as(?usize, 13), string.memchr_inv(zero_backing[offset .. offset + 32], 0));

        var nonzero_backing = [_]u8{7} ** 40;
        nonzero_backing[offset + 11] = 5;
        try std.testing.expectEqual(@as(?usize, 11), string.memchrInv(nonzero_backing[offset .. offset + 32], 7));
        try std.testing.expectEqual(@as(?usize, 11), string.memchr_inv(nonzero_backing[offset .. offset + 32], 7));
    }
}
