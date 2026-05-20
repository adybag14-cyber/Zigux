const std = @import("std");
const string = @import("string");

test "phase1 string basename helpers keep C-string path boundaries" {
    try std.testing.expectEqualStrings("file.txt", string.kbasename("/tmp/file.txt"));
    try std.testing.expectEqualStrings(
        "node",
        string.kbasename(&[_]u8{ '/', 'a', '/', 'n', 'o', 'd', 'e', 0, '/', 'x' }),
    );
    try std.testing.expectEqualStrings("", string.kbasename("/"));
}

test "phase1 string search helpers stop at embedded NUL and keep first or last matches" {
    try std.testing.expectEqual(@as(?usize, 1), string.strchr("abc", 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strchr(&[_]u8{ 'a', 0, 'b' }, 'b'));
    try std.testing.expectEqual(@as(?usize, 3), string.strrchr("abca", 'a'));
    try std.testing.expectEqual(@as(?usize, 0), string.strrchr(&[_]u8{ 'a', 0, 'a' }, 'a'));
}

test "phase1 string accept-set helpers honor C-string accept buffers" {
    try std.testing.expectEqual(@as(?usize, 1), string.strpbrk("kernel", "xyre"));
    try std.testing.expectEqual(@as(?usize, null), string.strpbrk(&[_]u8{ 'a', 0, 'b' }, "b"));
    try std.testing.expectEqual(@as(usize, 4), string.strspn("abba!", "ab"));
    try std.testing.expectEqual(@as(usize, 0), string.strspn("abba!", ""));

    const cstr = [_]u8{ 'a', 'b', 'a', 0, 'b' };
    try std.testing.expectEqual(@as(usize, 3), string.strspn(&cstr, "ab"));

    const accept_cstr = [_]u8{ 'a', 0, 'z' };
    try std.testing.expectEqual(@as(usize, 1), string.strspn("abca", &accept_cstr));
}

test "phase1 string counted search helpers return match NUL or count boundaries" {
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr("abc", 2, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr("abc", 1, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&[_]u8{ 'a', 0, 'b' }, 3, 'b'));
    try std.testing.expectEqual(@as(usize, 2), string.strnlen("abc", 2));
    try std.testing.expectEqual(@as(usize, 1), string.strnlen(&[_]u8{ 'a', 0, 'b' }, 3));
    try std.testing.expectEqual(@as(usize, 1), string.strnchrNul("abc", 3, 'b'));
    try std.testing.expectEqual(@as(usize, 2), string.strnchrNul("abc", 2, 'z'));
    try std.testing.expectEqual(@as(usize, 1), string.strnchrnul(&[_]u8{ 'a', 0, 'b' }, 3, 'z'));
    try std.testing.expectEqual(@as(usize, 3), string.strchrNul("abc", 'z'));
    try std.testing.expectEqual(@as(usize, 3), string.strchrnul("abc", 'z'));
}
