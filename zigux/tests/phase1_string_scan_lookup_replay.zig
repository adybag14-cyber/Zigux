const std = @import("std");
const string = @import("string");

test "phase 1 string scan helpers respect count and embedded NUL boundaries" {
    const embedded = [_]u8{ 'a', 0, 'b', 'c' };
    const nul_terminated_needle = [_]u8{ 'b', 0, 'x' };

    try std.testing.expectEqual(@as(?usize, 1), string.strnstr("abc", "bc", 3));
    try std.testing.expectEqual(@as(?usize, null), string.strnstr("abc", "bc", 1));
    try std.testing.expectEqual(@as(?usize, null), string.strnstr(&embedded, "bc", 4));
    try std.testing.expectEqual(@as(?usize, 1), string.strnstr("abc", &nul_terminated_needle, 3));
    try std.testing.expectEqual(@as(?usize, 0), string.strnstr("abc", "", 0));

    try std.testing.expectEqual(@as(?usize, 1), string.strnchr("abc", 2, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr("abc", 1, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&embedded, 3, 'b'));
}

test "phase 1 string fallback index aliases keep count and terminator positions aligned" {
    const embedded = [_]u8{ 'a', 0, 'b' };

    try std.testing.expectEqual(@as(usize, 1), string.strnchrNul("abc", 3, 'b'));
    try std.testing.expectEqual(@as(usize, 2), string.strnchrNul("abc", 2, 'z'));
    try std.testing.expectEqual(@as(usize, 1), string.strnchrnul(&embedded, 3, 'z'));

    try std.testing.expectEqual(@as(usize, 3), string.strchrNul("abc", 'z'));
    try std.testing.expectEqual(@as(usize, 3), string.strchrnul("abc", 'z'));
    try std.testing.expectEqual(@as(usize, 1), string.strchrNul(&embedded, 'z'));
}

test "phase 1 string accept reject and lookup helpers preserve first match boundaries" {
    const embedded = [_]u8{ 'a', 0, 'b' };
    const accept_cstr = [_]u8{ 'a', 0, 'z' };
    const reject_cstr = [_]u8{ 'x', 0, 'y' };
    const sysfs_haystack = [_][]const u8{ "off", "auto\n", "auto", "on" };
    const plain_haystack = [_][]const u8{
        &[_]u8{ 'a', 0, 'x' },
        "beta",
        "alpha",
    };
    const colors = [_][]const u8{ "blue", "green" };
    const empty = [_][]const u8{};

    try std.testing.expectEqual(@as(?usize, 1), string.strpbrk("kernel", "xyre"));
    try std.testing.expectEqual(@as(?usize, null), string.strpbrk(&embedded, "b"));
    try std.testing.expectEqual(@as(usize, 4), string.strspn("abba!", "ab"));
    try std.testing.expectEqual(@as(usize, 1), string.strspn("abca", &accept_cstr));
    try std.testing.expectEqual(@as(usize, 4), string.strcspn("path=/tmp", "="));
    try std.testing.expectEqual(@as(usize, 2), string.strcspn("abxc", &reject_cstr));

    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs_haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.__sysfs_match_string(sysfs_haystack[0..], 3, "auto"));
    try std.testing.expectEqual(@as(?usize, null), string.__sysfs_match_string(sysfs_haystack[0..], 1, "auto"));
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(plain_haystack[0..], "a"));
    try std.testing.expectEqual(@as(?usize, 1), string.match_string(colors[0..], "green"));
    try std.testing.expectEqual(@as(?usize, null), string.sysfs_match_string(empty[0..], "auto"));
}
