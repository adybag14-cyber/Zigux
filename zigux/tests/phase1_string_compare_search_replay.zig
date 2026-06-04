const std = @import("std");
const string = @import("string");

test "phase1 string compare replay keeps counted and casefold fences" {
    const embedded_left = [_]u8{ 'A', 'b', 0, 'z' };
    const embedded_right = [_]u8{ 'a', 'B', 0, 'x' };

    try std.testing.expectEqual(@as(i32, 0), string.strcmp("same", "same"));
    try std.testing.expect(string.strcmp("same", "sane") < 0);
    try std.testing.expect(string.strcmp(&embedded_left, &embedded_right) < 0);

    try std.testing.expectEqual(@as(i32, 0), string.strncmp("prefix-old", "prefix-new", 6));
    try std.testing.expect(string.strncmp("prefix-old", "prefix-new", 8) > 0);
    try std.testing.expectEqual(@as(i32, 0), string.strncmp("anything", "different", 0));

    try std.testing.expectEqual(@as(i32, 0), string.strcasecmp("Kernel", "kernel"));
    try std.testing.expect(string.strcasecmp("Alpha", "alpHz") < 0);
    try std.testing.expectEqual(@as(i32, 0), string.strcasecmp(&embedded_left, &embedded_right));

    try std.testing.expectEqual(@as(i32, 0), string.strncasecmp("CaseFold", "caseZzzz", 4));
    try std.testing.expect(string.strncasecmp("CaseFold", "caseZzzz", 5) < 0);
    try std.testing.expectEqual(@as(i32, 0), string.strncasecmp("abc", "XYZ", 0));
}

test "phase1 string substring replay keeps C-string and count windows" {
    const embedded = [_]u8{ 'a', 'b', 0, 'c', 'd' };
    const nul_needle = [_]u8{ 'c', 0, 'd' };

    try std.testing.expectEqual(@as(?usize, 3), string.strstr("alphabet", "hab"));
    try std.testing.expectEqual(@as(?usize, null), string.strstr(&embedded, "cd"));
    try std.testing.expectEqual(@as(?usize, 2), string.strstr("abcdef", &nul_needle));
    try std.testing.expectEqual(@as(?usize, 0), string.strstr("abcdef", ""));

    try std.testing.expectEqual(@as(?usize, 2), string.strnstr("abcdef", "cd", 5));
    try std.testing.expectEqual(@as(?usize, null), string.strnstr("abcdef", "cd", 3));
    try std.testing.expectEqual(@as(?usize, null), string.strnstr(&embedded, "cd", embedded.len));
    try std.testing.expectEqual(@as(?usize, 0), string.strnstr("abcdef", "", 0));
}

test "phase1 string accepted rejected span replay stops at first terminator" {
    const embedded = [_]u8{ 'a', 'b', 0, 'c', 'd' };
    const accept_with_nul = [_]u8{ 'a', 'b', 0, 'c' };
    const reject_with_nul = [_]u8{ 'x', 0, 'b' };

    try std.testing.expectEqual(@as(?usize, 2), string.strpbrk("kernel", "rn"));
    try std.testing.expectEqual(@as(?usize, null), string.strpbrk(&embedded, "c"));
    try std.testing.expectEqual(@as(?usize, 1), string.strpbrk("cab", &accept_with_nul));

    try std.testing.expectEqual(@as(usize, 4), string.strspn("abba!", "ab"));
    try std.testing.expectEqual(@as(usize, 2), string.strspn(&embedded, "ab"));
    try std.testing.expectEqual(@as(usize, 2), string.strspn("abc", &accept_with_nul));

    try std.testing.expectEqual(@as(usize, 4), string.strcspn("path=/tmp", "="));
    try std.testing.expectEqual(@as(usize, 2), string.strcspn(&embedded, "c"));
    try std.testing.expectEqual(@as(usize, 3), string.strcspn("abc", &reject_with_nul));
}

test "phase1 string nul-search aliases keep match or boundary behavior" {
    const embedded = [_]u8{ 'a', 0, 'b', 'c' };

    try std.testing.expectEqual(@as(?usize, 1), string.strchr("abc", 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strchr(&embedded, 'b'));
    try std.testing.expectEqual(@as(?usize, 3), string.strchr("abc", 0));

    try std.testing.expectEqual(@as(?usize, 3), string.strrchr("abca", 'a'));
    try std.testing.expectEqual(@as(?usize, 0), string.strrchr(&embedded, 'a'));
    try std.testing.expectEqual(@as(?usize, 1), string.strrchr(&embedded, 0));

    try std.testing.expectEqual(@as(?usize, 1), string.strnchr("abc", 2, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr("abc", 1, 'b'));
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&embedded, embedded.len, 0));

    try std.testing.expectEqual(@as(usize, 1), string.strnchrNul("abc", 3, 'b'));
    try std.testing.expectEqual(@as(usize, 3), string.strnchrNul("abc", 3, 'z'));
    try std.testing.expectEqual(@as(usize, 1), string.strnchrnul(&embedded, embedded.len, 'z'));

    try std.testing.expectEqual(@as(usize, 1), string.strchrNul("abc", 'b'));
    try std.testing.expectEqual(@as(usize, 3), string.strchrNul("abc", 'z'));
    try std.testing.expectEqual(@as(usize, 1), string.strchrnul(&embedded, 'z'));
}
