const std = @import("std");
const string = @import("string");

test "phase1 string match replay keeps sysfs and plain string match ordering explicit" {
    const sysfs_haystack = [_][]const u8{ "off", "auto\n", "auto", "on" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs_haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(sysfs_haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, null), string.__sysfs_match_string(sysfs_haystack[0..], 1, "auto"));

    const c_string_haystack = [_][]const u8{
        &[_]u8{ 'm', 'a', 'n', 0, 'x' },
        "auto",
        "manual",
        "manual",
    };
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(c_string_haystack[0..], "man"));
    try std.testing.expectEqual(@as(?usize, 2), string.match_string(c_string_haystack[0..], "manual"));
    try std.testing.expectEqual(@as(?usize, null), string.matchString(c_string_haystack[0..], "missing"));
}

test "phase1 string match replay keeps memchrInv earliest-dirty-byte behavior stable" {
    var zero_scan = [_]u8{0} ** 40;
    zero_scan[17] = 3;
    try std.testing.expectEqual(@as(?usize, 17), string.memchrInv(zero_scan[0..], 0));
    try std.testing.expectEqual(@as(?usize, 17), string.memchr_inv(zero_scan[0..], 0));

    for (0..@sizeOf(usize)) |offset| {
        var aligned = [_]u8{7} ** 48;
        aligned[offset + 13] = 4;
        try std.testing.expectEqual(@as(?usize, 13), string.memchrInv(aligned[offset .. offset + 32], 7));
    }

    const short = [_]u8{ 9, 9, 5, 9, 9 };
    try std.testing.expectEqual(@as(?usize, 2), string.memchrInv(short[0..], 9));
}

test "phase1 string match replay keeps signed memparse saturation and rest handling explicit" {
    const invalid = string.memparse("-abc");
    try std.testing.expectEqual(@as(u64, 0), invalid.value);
    try std.testing.expectEqualStrings("-abc", invalid.rest);

    const signed_suffix = string.memparse("-9000000000000K");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -9216000000000000))), signed_suffix.value);
    try std.testing.expectEqualStrings("", signed_suffix.rest);

    const clamped_positive = string.memparse("+9223372036854775808 tail");
    try std.testing.expectEqual(@as(u64, @intCast(std.math.maxInt(i64))), clamped_positive.value);
    try std.testing.expectEqualStrings(" tail", clamped_positive.rest);

    const saturated_suffix = string.memparse("18446744073709551615Ktail");
    try std.testing.expectEqual(std.math.maxInt(u64), saturated_suffix.value);
    try std.testing.expectEqualStrings("tail", saturated_suffix.rest);

    const signed_rest = string.memparse("-16 trailing");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -16))), signed_rest.value);
    try std.testing.expectEqualStrings(" trailing", signed_rest.rest);
}

test "phase1 string match replay keeps memdup byte-for-byte and allocator-safe" {
    const duplicated = try string.memdup(std.testing.allocator, &[_]u8{ 'z', 'i', 'g', 0, 'x' });
    defer std.testing.allocator.free(duplicated);

    try std.testing.expectEqual(@as(usize, 5), duplicated.len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 'i', 'g', 0, 'x' }, duplicated);
}
