const std = @import("std");
const string = @import("string");

test "phase 1 string counted-search review replay keeps sysfs and lookup order stable" {
    const sysfs_entries = [_][]const u8{
        "manual\n",
        "auto\n",
        &[_]u8{ 'a', 'u', 't', 'o', 0, 'x' },
        "safe\n",
    };
    const lookup_entries = [_][]const u8{
        "manual",
        &[_]u8{ 'a', 'u', 't', 'o', 0, 'x' },
        "auto",
        "safe",
    };
    const nul_terminated = [_]u8{ 'a', 'u', 't', 'o', 0, '!', '!' };

    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&sysfs_entries, "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(&sysfs_entries, &nul_terminated));
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(&lookup_entries, "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.match_string(&lookup_entries, &nul_terminated));
    try std.testing.expectEqual(@as(?usize, null), string.matchString(&lookup_entries, "auto\n"));
}

test "phase 1 string counted-search review replay keeps trim-after-NUL and bounded search behavior explicit" {
    const expected = [_]u8{ 'a', 'l', 'p', 'h', 'a' };
    const cstr = [_]u8{ 'a', 'b', 0, 'c', 'b' };

    var trim_buf = [_]u8{ ' ', '\t', 'a', 'l', 'p', 'h', 'a', 0, ' ', '\n', 'x' };
    const trimmed = string.trimSpaces(&trim_buf);
    try std.testing.expectEqualSlices(u8, &expected, trimmed);
    try std.testing.expectEqual(@as(u8, ' '), trim_buf[8]);
    try std.testing.expectEqual(@as(u8, '\n'), trim_buf[9]);
    try std.testing.expectEqual(@as(u8, 'x'), trim_buf[10]);

    var strim_buf = [_]u8{ ' ', '\t', 'a', 'l', 'p', 'h', 'a', 0, ' ', '\n', 'x' };
    try std.testing.expectEqualSlices(u8, &expected, string.strim(&strim_buf));

    var strstrip_buf = [_]u8{ ' ', '\t', 'a', 'l', 'p', 'h', 'a', 0, ' ', '\n', 'x' };
    try std.testing.expectEqualSlices(u8, &expected, string.strstrip(&strstrip_buf));

    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&cstr, cstr.len, 'b'));
    try std.testing.expectEqual(@as(?usize, 2), string.strnchr(&cstr, cstr.len, 0));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&cstr, cstr.len, 'c'));
}

test "phase 1 string counted-search review replay keeps memparse and earliest-dirty-byte behavior stable" {
    var moving_dirty = [_]u8{'a'} ** 160;

    moving_dirty[96] = 'b';
    try std.testing.expectEqual(@as(?usize, 96), string.memchrInv(&moving_dirty, 'a'));

    moving_dirty[96] = 'a';
    moving_dirty[48] = 'b';
    try std.testing.expectEqual(@as(?usize, 48), string.memchrInv(&moving_dirty, 'a'));

    moving_dirty[48] = 'a';
    try std.testing.expectEqual(@as(?usize, null), string.memchrInv(&moving_dirty, 'a'));

    var zero_scan = [_]u8{0} ** 96;
    zero_scan[64] = 1;
    try std.testing.expectEqual(@as(?usize, 64), string.memchrInv(&zero_scan, 0));
    try std.testing.expectEqual(@as(?usize, 64), string.memchr_inv(&zero_scan, 0));

    const parsed = string.memparse("-16 trailing");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -16))), parsed.value);
    try std.testing.expectEqualStrings(" trailing", parsed.rest);

    const saturated = string.memparse("-9223372036854775809");
    const min_signed: i64 = std.math.minInt(i64);
    try std.testing.expectEqual(@as(u64, @bitCast(min_signed)), saturated.value);
}
