const std = @import("std");
const string = @import("string");

test "phase1 string copy replay keeps C-string source length and truncation aligned" {
    var short_buf = [_]u8{ 9, 9, 9, 9, 9 };
    try std.testing.expectEqual(@as(usize, 2), string.strlcpy(short_buf[0..], &[_]u8{ 'h', 'i', 0, 'x' }));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'i', 0, 9, 9 }, short_buf[0..]);

    var truncated = [_]u8{ 7, 7, 7, 7 };
    try std.testing.expectEqual(@as(usize, 5), string.strlcpy(truncated[0..], "hello"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'e', 'l', 0 }, truncated[0..]);

    var empty = [_]u8{};
    try std.testing.expectEqual(@as(usize, 3), string.strlcpy(empty[0..], "zig"));
}

test "phase1 string append replay keeps attempted length and full-destination behavior aligned" {
    var appended = [_]u8{ 'a', 'b', 0, 0, 0 };
    try std.testing.expectEqual(@as(usize, 4), string.strlcat(appended[0..], &[_]u8{ 'c', 'd', 0, 'x' }));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 'c', 'd', 0 }, appended[0..]);

    var truncated = [_]u8{ 'a', 'b', 0, 'x' };
    try std.testing.expectEqual(@as(usize, 6), string.strlcat(truncated[0..], "cdef"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 'c', 0 }, truncated[0..]);

    var full = [_]u8{ 'a', 'b', 'c' };
    try std.testing.expectEqual(@as(usize, 6), string.strlcat(full[0..], "xyz"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 'c' }, full[0..]);
}

test "phase1 string strscpy replay keeps one-byte, truncation, and padding alias rules aligned" {
    var copied = [_]u8{ 1, 1, 1, 1, 1, 1 };
    try std.testing.expectEqual(@as(isize, 2), string.strscpy(copied[0..], &[_]u8{ 'o', 'k', 0, 'x' }));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 1, 1, 1 }, copied[0..]);

    var clipped = [_]u8{ 8, 8, 8 };
    try std.testing.expectEqual(@as(isize, -7), string.strscpy(clipped[0..], "abcd"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 0 }, clipped[0..]);

    var padded = [_]u8{ 3, 3, 3, 3, 3 };
    try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(padded[0..], "hi"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'i', 0, 0, 0 }, padded[0..]);

    var alias_padded = [_]u8{ 4, 4, 4, 4 };
    try std.testing.expectEqual(@as(isize, 2), string.strscpy_pad(alias_padded[0..], &[_]u8{ 'o', 'k', 0, 'x' }));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0 }, alias_padded[0..]);

    var single = [_]u8{9};
    try std.testing.expectEqual(@as(isize, -7), string.strscpy(single[0..], "x"));
    try std.testing.expectEqual(@as(u8, 0), single[0]);
}
