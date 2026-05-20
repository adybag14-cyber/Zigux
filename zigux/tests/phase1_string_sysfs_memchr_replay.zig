const std = @import("std");
const string = @import("string");

test "phase 1 string replay keeps sysfs newline folding on the earliest matching entry" {
    const haystack = [_][]const u8{
        "disabled\n",
        "auto\n",
        "auto",
        "manual",
    };

    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&haystack, "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&haystack, "auto\n"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(&haystack, "auto"));
    try std.testing.expectEqual(@as(?usize, null), string.sysfsMatchString(&haystack, "missing"));
}

test "phase 1 string replay keeps sysfs folding distinct from exact matchString semantics" {
    const newline_first = [_][]const u8{
        "mode\n",
        "mode",
    };

    try std.testing.expect(string.sysfsStreq("mode\n", "mode"));
    try std.testing.expect(string.sysfs_streq("mode", "mode\n"));
    try std.testing.expectEqual(@as(?usize, 0), string.sysfsMatchString(&newline_first, "mode"));
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(&newline_first, "mode"));
    try std.testing.expectEqual(@as(?usize, 0), string.match_string(&newline_first, "mode\n"));
}

test "phase 1 string replay keeps memchrInv on the earliest dirty byte across cutoff boundaries" {
    const cutoff = @sizeOf(usize) * 2;

    var short_scan = [_]u8{0} ** (cutoff - 1);
    short_scan[short_scan.len - 1] = 7;
    try std.testing.expectEqual(@as(?usize, short_scan.len - 1), string.memchrInv(short_scan[0..], 0));
    try std.testing.expectEqual(string.memchrInv(short_scan[0..], 0), string.memchr_inv(short_scan[0..], 0));

    var long_scan = [_]u8{0} ** cutoff;
    long_scan[long_scan.len - 1] = 9;
    try std.testing.expectEqual(@as(?usize, long_scan.len - 1), string.memchrInv(long_scan[0..], 0));

    var shifted_backing = [_]u8{0xaa} ** (cutoff + @sizeOf(usize));
    for (0..@sizeOf(usize)) |prefix| {
        const slice = shifted_backing[prefix .. prefix + cutoff];
        @memset(shifted_backing[0..], 0xaa);
        slice[3] = 0x11;
        slice[cutoff - 1] = 0x22;
        try std.testing.expectEqual(@as(?usize, 3), string.memchrInv(slice, 0xaa));
    }
}
