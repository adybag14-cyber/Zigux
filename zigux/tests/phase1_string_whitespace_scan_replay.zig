const std = @import("std");
const string = @import("string");

test "string whitespace aliases preserve trimmed and compacted views" {
    try std.testing.expectEqualStrings("zigux", string.skipSpaces(" \t\nzigux"));
    try std.testing.expectEqualStrings("builder", string.skip_spaces(" \rbuilder"));

    var trim_buf = [_]u8{ ' ', '\t', 'z', 'i', 'g', ' ', 'u', 'x', ' ', '\n', 0, 'x' };
    const trimmed = string.trimSpaces(&trim_buf);
    try std.testing.expectEqualStrings("zig ux", trimmed);
    try std.testing.expectEqual(@as(u8, 0), trim_buf[8]);

    var all_space_buf = [_]u8{ ' ', '\t', '\n', 0, 'x' };
    const empty = string.strim(&all_space_buf);
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(u8, 0), all_space_buf[0]);

    var strip_buf = [_]u8{ '\r', 'a', 'l', 'p', 'h', 'a', ' ', 0, 'x' };
    try std.testing.expectEqualStrings("alpha", string.strstrip(&strip_buf));

    var compact_buf = [_]u8{ ' ', 'z', 'i', ' ', '\t', 'g', ' ', 'u', 'x', 0, 'x' };
    const compacted = string.removeSpaces(&compact_buf);
    try std.testing.expectEqualStrings("zi\tgux", compacted);
    try std.testing.expectEqual(@as(u8, 0), compact_buf[6]);

    var compact_alias_buf = [_]u8{ 'n', 'o', ' ', 's', 'p', 'a', 'c', 'e', 's', 0 };
    try std.testing.expectEqualStrings("nospaces", string.remove_spaces(&compact_alias_buf));
}

test "string dirty-byte scans and replacement aliases stop at nul" {
    const clean = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa };
    try std.testing.expectEqual(@as(?usize, null), string.memchrInv(&clean, 0xaa));
    try std.testing.expectEqual(@as(?usize, null), string.memchr_inv(&clean, 0xaa));

    const dirty = [_]u8{ 0xaa, 0xaa, 0xaa, 0xbb, 0xaa, 0xaa, 0xaa, 0xaa, 0xcc };
    try std.testing.expectEqual(@as(?usize, 3), string.memchrInv(&dirty, 0xaa));
    try std.testing.expectEqual(@as(?usize, 3), string.memchr_inv(&dirty, 0xaa));

    const tail_dirty = [_]u8{ 0xdd, 0xdd, 0xdd, 0xdd, 0xdd, 0xde };
    try std.testing.expectEqual(@as(?usize, 5), string.memchrInv(&tail_dirty, 0xdd));

    var replace_buf = [_]u8{ 'a', '-', 'b', '-', 'c', 0, '-', 'x' };
    try std.testing.expectEqual(@as(usize, 5), string.replaceChar(&replace_buf, '-', '_'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', '_', 'b', '_', 'c', 0, '-', 'x' }, &replace_buf);

    var alias_replace_buf = [_]u8{ 'x', ':', 'y', ':', 0, ':' };
    try std.testing.expectEqual(@as(usize, 4), string.strreplace(&alias_replace_buf, ':', '/'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', '/', 'y', '/', 0, ':' }, &alias_replace_buf);
}

test "string sysfs and counted lookup helpers keep newline and count rules" {
    try std.testing.expect(string.sysfsStreq("enabled\n", "enabled"));
    try std.testing.expect(string.sysfs_streq("manual", "manual\n"));
    try std.testing.expect(!string.sysfsStreq("enabled", "enable"));

    const sysfs = [_][]const u8{ "disabled", "auto\n", "manual", "auto" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&sysfs, "auto"));
    try std.testing.expectEqual(@as(?usize, null), string.sysfsMatchString(sysfs[0..1], "auto"));
    try std.testing.expectEqual(@as(?usize, 2), string.sysfs_match_string(sysfs[0..3], "manual\n"));

    const names = [_][]const u8{ "alpha", "beta", "beta", "gamma" };
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(&names, "beta"));
    try std.testing.expectEqual(@as(?usize, 3), string.match_string(&names, "gamma"));
    try std.testing.expectEqual(@as(?usize, null), string.matchString(&names, "delta"));
}
