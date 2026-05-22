const std = @import("std");
const string = @import("string");

test "phase1 string cstring scan replay keeps counted scans and NUL stops aligned" {
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr("abcd", 4, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr("abcd", 1, 'b'));

    const cstr = [_]u8{ 'a', 'b', 0, 'c', 'b' };
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&cstr, cstr.len, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&cstr, cstr.len, 'c'));
    try std.testing.expectEqual(@as(?usize, 2), string.strnchr(&cstr, cstr.len, 0));
}

test "phase1 string cstring scan replay keeps copy and padding helpers aligned" {
    var dst = [_]u8{ 0, 0, 0, 0 };
    try std.testing.expectEqual(@as(usize, 5), string.strlcpy(&dst, "hello"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'e', 'l', 0 }, &dst);

    var truncated = [_]u8{ 0, 0, 0, 0 };
    try std.testing.expectEqual(@as(isize, -7), string.strscpy(&truncated, "hello"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'e', 'l', 0 }, &truncated);

    var padded = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa };
    try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(&padded, "hi"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'i', 0, 0, 0, 0 }, &padded);

    var padded_alias = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa };
    try std.testing.expectEqual(@as(isize, 2), string.strscpy_pad(&padded_alias, "hi"));
    try std.testing.expectEqualSlices(u8, &padded, &padded_alias);
}

test "phase1 string cstring scan replay keeps replacement and duplication helpers aligned" {
    var replace_buf = [_]u8{ 'a', 0, 'b', 'a' };
    try std.testing.expectEqual(@as(usize, 1), string.replaceChar(&replace_buf, 'a', 'z'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 0, 'b', 'a' }, &replace_buf);

    const dup = try string.memdup(std.testing.allocator, "zigux");
    defer std.testing.allocator.free(dup);
    try std.testing.expectEqualStrings("zigux", dup);
}
