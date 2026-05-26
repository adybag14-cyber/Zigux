const std = @import("std");
const string = @import("string");

test "phase1 string compare replay keeps lexical and count boundaries aligned" {
    try std.testing.expect(string.strcmp("abc", "abc") == 0);
    try std.testing.expect(string.strcmp("abd", "abc") > 0);
    try std.testing.expect(string.strcmp("abc", "abd") < 0);

    try std.testing.expect(string.strcmp(&[_]u8{ 'a', 0, 'z' }, &[_]u8{ 'a', 0, 'x' }) == 0);
    try std.testing.expect(string.strcmp(&[_]u8{ 'a', 0, 'z' }, "ab") < 0);
    try std.testing.expect(string.strcmp("ab", &[_]u8{ 'a', 0, 'z' }) > 0);

    try std.testing.expect(string.strncmp("abcdef", "abcxyz", 3) == 0);
    try std.testing.expect(string.strncmp("abcdef", "abcxyz", 4) < 0);
    try std.testing.expect(string.strncmp("abcxyz", "abcdef", 4) > 0);
    try std.testing.expect(string.strncmp("abcdef", "abcxyz", 0) == 0);
    try std.testing.expect(string.strncmp("ab", "abc", 2) == 0);
}

test "phase1 string substring replay keeps C-string and count clamps aligned" {
    try std.testing.expectEqual(@as(?usize, 1), string.strstr("abc", "bc"));
    try std.testing.expectEqual(@as(?usize, null), string.strstr(&[_]u8{ 'a', 0, 'b', 'c' }, "bc"));
    try std.testing.expectEqual(@as(?usize, 1), string.strstr("abc", &[_]u8{ 'b', 0, 'x' }));
    try std.testing.expectEqual(@as(?usize, 0), string.strstr("abc", ""));

    try std.testing.expectEqual(@as(?usize, 1), string.strnstr("abc", "bc", 3));
    try std.testing.expectEqual(@as(?usize, null), string.strnstr("abc", "bc", 1));
    try std.testing.expectEqual(@as(?usize, null), string.strnstr(&[_]u8{ 'a', 0, 'b', 'c' }, "bc", 4));
    try std.testing.expectEqual(@as(?usize, 1), string.strnstr("abc", &[_]u8{ 'b', 0, 'x' }, 3));
    try std.testing.expectEqual(@as(?usize, 0), string.strnstr("abc", "", 0));
}

test "phase1 string search-span replay keeps terminator and counted edges aligned" {
    try std.testing.expectEqual(@as(?usize, 1), string.strchr("abc", 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strchr(&[_]u8{ 'a', 0, 'b' }, 'b'));
    try std.testing.expectEqual(@as(?usize, 3), string.strchr("abc", 0));
    try std.testing.expectEqual(@as(?usize, 3), string.strrchr("abca", 'a'));
    try std.testing.expectEqual(@as(?usize, 1), string.strrchr(&[_]u8{ 'a', 0, 'b' }, 0));

    try std.testing.expectEqual(@as(?usize, 1), string.strpbrk("kernel", "xyre"));
    try std.testing.expectEqual(@as(?usize, null), string.strpbrk(&[_]u8{ 'a', 0, 'b' }, "b"));
    try std.testing.expectEqual(@as(usize, 4), string.strspn("abba!", "ab"));
    try std.testing.expectEqual(@as(usize, 4), string.strcspn("path=/tmp", "="));

    try std.testing.expectEqual(@as(?usize, 1), string.strnchr("abc", 2, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&[_]u8{ 'a', 0, 'b' }, 3, 'b'));
    try std.testing.expectEqual(@as(usize, 2), string.strnlen("abc", 2));
    try std.testing.expectEqual(@as(usize, 3), string.strnchrNul("abc", 3, 'z'));
    try std.testing.expectEqual(@as(usize, 1), string.strnchrnul(&[_]u8{ 'a', 'b', 0 }, 3, 'b'));
    try std.testing.expectEqual(@as(usize, 3), string.strchrNul("abc", 'z'));
    try std.testing.expectEqual(@as(usize, 1), string.strchrnul(&[_]u8{ 'a', 0, 'b' }, 'z'));
}
