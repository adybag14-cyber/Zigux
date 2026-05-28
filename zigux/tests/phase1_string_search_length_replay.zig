const std = @import("std");
const string = @import("string");

test "phase1 string search helpers keep C-string search boundaries stable" {
    try std.testing.expectEqual(@as(?usize, 1), string.strchr("abc", 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strchr(&[_]u8{ 'a', 0, 'b' }, 'b'));
    try std.testing.expectEqual(@as(?usize, 3), string.strchr("abc", 0));

    try std.testing.expectEqual(@as(?usize, 3), string.strrchr("abca", 'a'));
    try std.testing.expectEqual(@as(?usize, 0), string.strrchr(&[_]u8{ 'a', 0, 'a' }, 'a'));
    try std.testing.expectEqual(@as(?usize, 1), string.strrchr(&[_]u8{ 'a', 0, 'b' }, 0));

    try std.testing.expectEqual(@as(?usize, 1), string.strpbrk("kernel", "xyre"));
    try std.testing.expectEqual(@as(?usize, null), string.strpbrk(&[_]u8{ 'a', 0, 'b' }, "b"));
}

test "phase1 string span helpers stop at accept and reject C-string boundaries" {
    try std.testing.expectEqual(@as(usize, 4), string.strspn("abba!", "ab"));
    try std.testing.expectEqual(@as(usize, 0), string.strspn("abba!", ""));

    const accept_cstr = [_]u8{ 'a', 0, 'z' };
    try std.testing.expectEqual(@as(usize, 1), string.strspn("abca", &accept_cstr));

    try std.testing.expectEqual(@as(usize, 4), string.strcspn("path=/tmp", "="));
    try std.testing.expectEqual(@as(usize, 4), string.strcspn("keep", ""));

    const reject_cstr = [_]u8{ 'x', 0, 'y' };
    try std.testing.expectEqual(@as(usize, 2), string.strcspn("abxc", &reject_cstr));
}

test "phase1 string length helpers keep count-limited NUL behavior stable" {
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr("abc", 2, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr("abc", 1, 'b'));
    try std.testing.expectEqual(@as(?usize, 3), string.strnchr("abc", 4, 0));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr("abc", 3, 0));

    try std.testing.expectEqual(@as(usize, 3), string.strlen("abc"));
    try std.testing.expectEqual(@as(usize, 1), string.strlen(&[_]u8{ 'a', 0, 'b' }));
    try std.testing.expectEqual(@as(usize, 2), string.strnlen("abc", 2));
    try std.testing.expectEqual(@as(usize, 1), string.strnlen(&[_]u8{ 'a', 0, 'b' }, 3));

    try std.testing.expectEqual(@as(usize, 1), string.strnchrNul("abc", 3, 'b'));
    try std.testing.expectEqual(@as(usize, 3), string.strnchrNul("abc", 3, 'z'));
    try std.testing.expectEqual(@as(usize, 1), string.strnchrNul(&[_]u8{ 'a', 0, 'b' }, 3, 'z'));
    try std.testing.expectEqual(@as(usize, 1), string.strnchrnul(&[_]u8{ 'a', 'b', 0 }, 3, 'b'));

    try std.testing.expectEqual(@as(usize, 1), string.strchrNul("abc", 'b'));
    try std.testing.expectEqual(@as(usize, 3), string.strchrNul("abc", 'z'));
    try std.testing.expectEqual(@as(usize, 1), string.strchrNul(&[_]u8{ 'a', 0, 'b' }, 'z'));
    try std.testing.expectEqual(@as(usize, 1), string.strchrnul(&[_]u8{ 'a', 'b', 0 }, 'b'));
}
