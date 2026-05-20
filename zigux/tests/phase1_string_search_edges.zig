const std = @import("std");
const string = @import("string");

test "phase1 string search helpers stop at C-string boundaries" {
    const slash_path = [_]u8{ '/', 't', 'm', 'p', '/', 'x', 0, '/', 'z' };
    try std.testing.expectEqual(@as(?usize, 0), string.strchr(&slash_path, '/'));
    try std.testing.expectEqual(@as(?usize, 4), string.strrchr(&slash_path, '/'));
    try std.testing.expectEqual(@as(?usize, null), string.strchr(&slash_path, 'z'));
    try std.testing.expectEqualStrings("x", string.kbasename(&slash_path));

    const accept = [_]u8{ 'x', 0, '/' };
    try std.testing.expectEqual(@as(?usize, 5), string.strpbrk(&slash_path, &accept));
    try std.testing.expectEqual(@as(?usize, null), string.strpbrk(&slash_path, ""));
}

test "phase1 string counted search helpers clamp to count or embedded NUL" {
    const counted = [_]u8{ 'a', 'b', 0, 'c', 'd' };
    try std.testing.expectEqual(@as(usize, 2), string.strnlen(&counted, counted.len));
    try std.testing.expectEqual(@as(usize, 1), string.strnlen(&counted, 1));
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&counted, counted.len, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&counted, counted.len, 'c'));
    try std.testing.expectEqual(@as(usize, 2), string.strnchrNul(&counted, counted.len, 'z'));
    try std.testing.expectEqual(@as(usize, 2), string.strnchrnul(&counted, counted.len, 'z'));
    try std.testing.expectEqual(@as(usize, 2), string.strchrNul(&counted, 'z'));
    try std.testing.expectEqual(@as(usize, 2), string.strchrnul(&counted, 'z'));
}

test "phase1 string span helpers keep accepted prefixes C-string aware" {
    try std.testing.expectEqual(@as(usize, 4), string.strspn("abba!", "ab"));
    try std.testing.expectEqual(@as(usize, 0), string.strspn("abba!", "xyz"));

    const truncated_accept = [_]u8{ 'a', 0, 'b' };
    try std.testing.expectEqual(@as(usize, 1), string.strspn("abba", &truncated_accept));

    const truncated_text = [_]u8{ 'a', 'b', 'a', 0, 'b' };
    try std.testing.expectEqual(@as(usize, 3), string.strspn(&truncated_text, "ab"));
}
