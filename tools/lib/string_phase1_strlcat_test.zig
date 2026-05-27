const std = @import("std");
const string = @import("string.zig");

test "phase1 string strlcat stops at the first source terminator" {
    var buf = [_]u8{ 'o', 'k', 0, 'x', 'x' };
    const src = [_]u8{ '!', '!', 0, '?', '?' };

    try std.testing.expectEqual(@as(usize, 4), string.strlcat(buf[0..], &src));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', '!', '!', 0 }, buf[0..]);
}

test "phase1 string strlcat leaves the destination stable for an empty C-string source" {
    var buf = [_]u8{ 'o', 'k', 0, 'x' };
    const src = [_]u8{ 0, '!', '!' };

    try std.testing.expectEqual(@as(usize, 2), string.strlcat(buf[0..], &src));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 'x' }, buf[0..]);
}

test "phase1 string strlcat treats an unterminated destination as full" {
    var buf = [_]u8{ 'a', 'b', 'c' };

    try std.testing.expectEqual(@as(usize, 6), string.strlcat(buf[0..], "xyz"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 'c' }, buf[0..]);
}

test "phase1 string strlcat handles a zero-length destination buffer" {
    var empty = [_]u8{};

    try std.testing.expectEqual(@as(usize, 3), string.strlcat(empty[0..], "zig"));
}
