const std = @import("std");
const string = @import("string");

test "phase1 string replay keeps sysfs newline matching first-match ordered" {
    const haystack = [_][]const u8{
        "manual\n",
        "auto\n",
        "auto",
        "off",
    };

    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 0), string.sysfsMatchString(haystack[0..], "manual"));
    try std.testing.expectEqual(@as(?usize, null), string.sysfsMatchString(haystack[0..], "missing"));
}

test "phase1 string replay keeps sysfs NUL and newline equivalence bounded" {
    const haystack = [_][]const u8{
        &[_]u8{ 'm', 'o', 'd', 'e', 0, 'x' },
        "mode\n",
        "mode-extra",
    };

    try std.testing.expect(string.sysfsStreq(&[_]u8{ 'm', 'o', 'd', 'e', 0, 'x' }, "mode\n"));
    try std.testing.expect(string.sysfs_streq("mode\n", "mode"));
    try std.testing.expectEqual(@as(?usize, 0), string.sysfsMatchString(haystack[0..], "mode"));
    try std.testing.expectEqual(@as(?usize, 0), string.sysfs_match_string(haystack[0..], "mode\n"));
    try std.testing.expectEqual(@as(?usize, 2), string.sysfsMatchString(haystack[0..], "mode-extra"));
}

test "phase1 string replay keeps memchrInv earliest dirty byte across alignment windows" {
    for (0..@sizeOf(usize)) |offset| {
        var backing: [48]u8 = @splat(0);
        backing[offset + 3] = 1;
        backing[offset + @sizeOf(usize) + 9] = 2;
        try std.testing.expectEqual(@as(?usize, 3), string.memchrInv(backing[offset .. offset + 32], 0));

        backing[offset + 3] = 0;
        try std.testing.expectEqual(@as(?usize, @sizeOf(usize) + 9), string.memchr_inv(backing[offset .. offset + 32], 0));
    }
}

test "phase1 string replay keeps memchrInv fast-path cutoff and non-zero scans stable" {
    var short: [@sizeOf(usize) * 2 - 1]u8 = @splat(0xaa);
    short[short.len - 1] = 0xab;
    try std.testing.expectEqual(@as(?usize, short.len - 1), string.memchrInv(short[0..], 0xaa));

    var long: [@sizeOf(usize) * 2]u8 = @splat(0xaa);
    long[long.len - 1] = 0xab;
    try std.testing.expectEqual(@as(?usize, long.len - 1), string.memchr_inv(long[0..], 0xaa));

    long[0] = 0xab;
    try std.testing.expectEqual(@as(?usize, 0), string.memchrInv(long[0..], 0xaa));
    long[0] = 0xaa;
    long[long.len - 1] = 0xaa;
    try std.testing.expectEqual(@as(?usize, null), string.memchrInv(long[1..], 0xaa));
}
