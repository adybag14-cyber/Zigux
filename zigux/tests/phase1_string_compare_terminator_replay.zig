const std = @import("std");
const string = @import("string");

test "phase1 string compare replay clamps equality at embedded terminators" {
    try std.testing.expectEqual(@as(i32, 0), string.strcmp("alpha\x00left", "alpha\x00right"));
    try std.testing.expectEqual(@as(i32, 0), string.strncmp("alpha\x00left", "alpha\x00right", 16));
    try std.testing.expectEqual(@as(i32, 0), string.strcasecmp("Alpha\x00left", "aLPHA\x00right"));
    try std.testing.expectEqual(@as(i32, 0), string.strncasecmp("Alpha\x00left", "aLPHA\x00right", 16));

    try std.testing.expect(string.strEq("module\x00debug", "module\x00release"));
    try std.testing.expectEqual(@as(usize, 6), string.strHasPrefix("module\x00debug", "module"));
    try std.testing.expectEqual(@as(usize, 0), string.strHasPrefix("mod\x00ule", "module"));
    try std.testing.expectEqual(@as(usize, 3), string.strHasSuffix("driver.ko\x00.tmp", ".ko"));
    try std.testing.expectEqual(@as(usize, 0), string.strHasSuffix("driver\x00.ko", ".ko"));
}

test "phase1 string compare replay preserves first differing byte signs" {
    try std.testing.expect(string.strcmp("abc", "abd") < 0);
    try std.testing.expect(string.strcmp("abd", "abc") > 0);
    try std.testing.expect(string.strcmp("abc", "abc\x01") < 0);
    try std.testing.expect(string.strcmp("abc\x7f", "abc\x80") < 0);

    try std.testing.expect(string.strcasecmp("az", "aA") > 0);
    try std.testing.expect(string.strcasecmp("aA", "az") < 0);
    try std.testing.expectEqual(@as(i32, 0), string.strncasecmp("same-tail", "SAME-next", 4));
    try std.testing.expect(string.strncmp("same-tail", "same-next", 6) > 0);
}

test "phase1 string search replay stops at the visible C string window" {
    try std.testing.expectEqual(@as(?usize, 2), string.strchr("abca\x00tail", 'c'));
    try std.testing.expectEqual(@as(?usize, 4), string.strchr("abca\x00tail", 0));
    try std.testing.expectEqual(@as(?usize, 3), string.strrchr("abca\x00tail", 'a'));
    try std.testing.expectEqual(@as(?usize, 4), string.strrchr("abca\x00tail", 0));
    try std.testing.expectEqual(@as(?usize, null), string.strchr("abca\x00tail", 't'));
    try std.testing.expectEqual(@as(?usize, null), string.strrchr("abca\x00tail", 't'));

    try std.testing.expectEqual(@as(?usize, 1), string.strpbrk("kernel\x00debug", "ex"));
    try std.testing.expectEqual(@as(?usize, null), string.strpbrk("kernel\x00debug", "db"));
    try std.testing.expectEqual(@as(usize, 3), string.strspn("abc123\x00tail", "abc"));
    try std.testing.expectEqual(@as(usize, 6), string.strcspn("abc123\x00tail", "xyz"));
    try std.testing.expectEqual(@as(usize, 3), string.strcspn("abc123\x00tail", "1"));
}
