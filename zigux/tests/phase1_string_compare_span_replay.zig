const std = @import("std");
const string = @import("string");

test "phase1 string compare helpers keep C-string and case-fold boundaries aligned" {
    try std.testing.expectEqual(
        @as(i32, 0),
        string.strcmp(&[_]u8{ 'a', 0, 'x' }, &[_]u8{ 'a', 0, 'y' }),
    );
    try std.testing.expect(string.strcmp("abc", "abd") < 0);
    try std.testing.expect(string.strcmp("abd", "abc") > 0);

    try std.testing.expectEqual(
        @as(i32, 0),
        string.strncmp(&[_]u8{ 'a', 'b', 0, 'x' }, "abz", 2),
    );
    try std.testing.expect(string.strncmp(&[_]u8{ 'a', 'b', 0, 'x' }, "abz", 3) < 0);

    try std.testing.expectEqual(@as(i32, 0), string.strcasecmp("ZigUx", "zigux"));
    try std.testing.expectEqual(@as(i32, 0), string.strncasecmp("AlphaBeta", "ALPHAz", 5));
    try std.testing.expect(string.strncasecmp("Alpha", "alpi", 4) < 0);
}

test "phase1 string span helpers stop at the first blocked or missing byte" {
    try std.testing.expectEqual(@as(usize, 4), string.strspn("abba!", "ab"));
    try std.testing.expectEqual(@as(usize, 4), string.strcspn("path:/zigux", "/:"));
    try std.testing.expectEqual(@as(usize, 3), string.strspn("123abc", "0123456789"));
    try std.testing.expectEqual(@as(usize, 0), string.strcspn(":leading", "/:"));
}

test "phase1 string search helpers keep bounded and last-match semantics aligned" {
    const repeated = [_]u8{ 'b', 'a', 'n', 'a', 'n', 'a', 0, 'x' };
    try std.testing.expectEqual(@as(?usize, 1), string.strchr(&repeated, 'a'));
    try std.testing.expectEqual(@as(?usize, 5), string.strrchr(&repeated, 'a'));
    try std.testing.expectEqual(@as(?usize, 1), string.strpbrk("kernel", "zmre"));
    try std.testing.expectEqual(@as(?usize, 1), string.strstr(&repeated, "ana"));
    try std.testing.expectEqual(@as(?usize, 1), string.strnstr(&repeated, "ana", 6));
    try std.testing.expectEqual(@as(?usize, null), string.strnstr(&repeated, "ana", 3));
}

test "phase1 string bounded search aliases fall back to the visible C-string limit" {
    const bounded = [_]u8{ 'a', 'b', 0, 'c', 'd' };
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&bounded, bounded.len, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&bounded, bounded.len, 'c'));
    try std.testing.expectEqual(@as(usize, 2), string.strnchrNul(&bounded, bounded.len, 'z'));
    try std.testing.expectEqual(@as(usize, 2), string.strnchrnul(&bounded, bounded.len, 'z'));
    try std.testing.expectEqual(@as(usize, 2), string.strchrNul(&bounded, 'z'));
    try std.testing.expectEqual(@as(usize, 2), string.strchrnul(&bounded, 'z'));
}
