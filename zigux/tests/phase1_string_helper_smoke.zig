const std = @import("std");
const string = @import("string");

test "phase1 string helper smoke keeps whitespace aliases aligned" {
    try std.testing.expectEqualStrings("zigux", string.skipSpaces(" \t\nzigux"));
    try std.testing.expectEqualStrings("zigux", string.skip_spaces(" \t\nzigux"));

    var trim_buf = [_]u8{ ' ', '\t', 'z', 'i', 'g', 'u', 'x', ' ', '\n' };
    try std.testing.expectEqualStrings("zigux", string.trimSpaces(&trim_buf));

    var strim_buf = [_]u8{ ' ', '\t', 'z', 'i', 'g', 'u', 'x', ' ', '\n' };
    try std.testing.expectEqualStrings("zigux", string.strim(&strim_buf));

    var strstrip_buf = [_]u8{ ' ', '\t', 'z', 'i', 'g', 'u', 'x', ' ', '\n' };
    try std.testing.expectEqualStrings("zigux", string.strstrip(&strstrip_buf));

    var remove_buf = [_]u8{ ' ', 'z', 'i', ' ', 'g', 'u', 'x', ' ', 0, 'x' };
    try std.testing.expectEqualStrings("zigux", string.removeSpaces(&remove_buf));

    var remove_alias_buf = [_]u8{ ' ', 'z', 'i', ' ', 'g', 'u', 'x', ' ', 0, 'x' };
    try std.testing.expectEqualStrings("zigux", string.remove_spaces(&remove_alias_buf));
}

test "phase1 string helper smoke keeps sysfs helpers newline-aware" {
    try std.testing.expect(string.sysfsStreq("auto\n", "auto"));
    try std.testing.expect(string.sysfs_streq("auto", "auto\n"));
    try std.testing.expect(!string.sysfsStreq("auto\nmore", "auto"));

    const haystack = [_][]const u8{ "disabled", "auto\n", "manual" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&haystack, "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(&haystack, "auto\n"));
    try std.testing.expectEqual(@as(?usize, null), string.sysfsMatchString(&haystack, "missing"));
}

test "phase1 string helper smoke keeps dirty-byte scans aligned" {
    var middle_dirty = [_]u8{'a'} ** 96;
    middle_dirty[37] = 'X';
    try std.testing.expectEqual(@as(?usize, 37), string.memchrInv(&middle_dirty, 'a'));
    try std.testing.expectEqual(string.memchrInv(&middle_dirty, 'a'), string.memchr_inv(&middle_dirty, 'a'));

    var zero_scan = [_]u8{0} ** 96;
    zero_scan[64] = 1;
    try std.testing.expectEqual(@as(?usize, 64), string.memchrInv(&zero_scan, 0));
    try std.testing.expectEqual(string.memchrInv(&zero_scan, 0), string.memchr_inv(&zero_scan, 0));

    const clean = [_]u8{'b'} ** 32;
    try std.testing.expectEqual(@as(?usize, null), string.memchrInv(&clean, 'b'));
}
