const std = @import("std");
const string = @import("string");

test "phase1 string compare and basename helpers keep C-string boundaries exact" {
    try std.testing.expect(string.strcmp("alpha", "alpha") == 0);
    try std.testing.expect(string.strcmp("alphabet", "alpha") > 0);
    try std.testing.expect(string.strcmp("alpha", "alphabet") < 0);
    try std.testing.expect(string.strcmp(&[_]u8{ 'a', 0, 'z' }, &[_]u8{ 'a', 0, 'x' }) == 0);

    try std.testing.expectEqual(@as(?usize, 1), string.strchr("kernel", 'e'));
    try std.testing.expectEqual(@as(?usize, 4), string.strrchr("level", 'l'));
    try std.testing.expectEqual(@as(?usize, 6), string.strchr("/tmp/x", 0));
    try std.testing.expectEqual(@as(?usize, 2), string.strrchr(&[_]u8{ 'o', 'k', 0, 'x' }, 0));

    try std.testing.expectEqualStrings("leaf", string.kbasename("/root/branch/leaf"));
    try std.testing.expectEqualStrings("node", string.kbasename(&[_]u8{ '/', 'a', '/', 'n', 'o', 'd', 'e', 0, '/', 'x' }));
}

test "phase1 string span and bounded search helpers stop at the same visible edge" {
    try std.testing.expectEqual(@as(?usize, 1), string.strpbrk("trace", "xyra"));
    try std.testing.expectEqual(@as(?usize, null), string.strpbrk(&[_]u8{ 'a', 0, 'b' }, "b"));

    try std.testing.expectEqual(@as(usize, 4), string.strspn("abba!", "ab"));
    try std.testing.expectEqual(@as(usize, 4), string.strcspn("path=/tmp", "="));
    try std.testing.expectEqual(@as(usize, 3), string.strspn(&[_]u8{ 'a', 'b', 'a', 0, 'b' }, "ab"));

    try std.testing.expectEqual(@as(?usize, 1), string.strnchr("abcd", 2, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&[_]u8{ 'a', 0, 'b' }, 3, 'b'));
    try std.testing.expectEqual(@as(usize, 2), string.strnchrNul("abc", 2, 'z'));
    try std.testing.expectEqual(@as(usize, 1), string.strnchrnul(&[_]u8{ 'a', 0, 'b' }, 3, 'z'));
    try std.testing.expectEqual(@as(usize, 3), string.strchrNul("abc", 'z'));
    try std.testing.expectEqual(@as(usize, 3), string.strchrnul("abc", 'z'));
}
