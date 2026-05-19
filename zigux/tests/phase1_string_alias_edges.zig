const std = @import("std");
const string = @import("string");

test "phase1 string alias edges keep prefix suffix and basename helpers aligned" {
    const cstr = [_]u8{ 'a', 'b', 0, 'x' };
    const embedded_match = [_]u8{ 'a', 'b', 0, 'y' };
    const trailing_miss = [_]u8{ 'x', 0, 'z' };

    try std.testing.expectEqual(@as(usize, 2), string.str_has_prefix(&cstr, &embedded_match));
    try std.testing.expect(string.strstarts(&cstr, &embedded_match));
    try std.testing.expect(string.str_ends_with(&cstr, &embedded_match));
    try std.testing.expect(!string.str_ends_with(&cstr, &trailing_miss));
}

test "phase1 string alias edges keep whitespace dirty-byte and newline aliases aligned" {
    try std.testing.expectEqualStrings("zigux", string.skip_spaces(" \tzigux"));

    var trim_buf = [_]u8{ ' ', 'a', 'b', 0, ' ', '\n', 'x' };
    try std.testing.expectEqualStrings("ab", string.strstrip(&trim_buf));
    try std.testing.expectEqualSlices(u8, &[_]u8{ ' ', 'a', 'b', 0, ' ', '\n', 'x' }, &trim_buf);

    var remove_buf = [_]u8{ ' ', 'a', ' ', 'b', 0, 'x' };
    try std.testing.expectEqualStrings("ab", string.remove_spaces(&remove_buf));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 0, 'b', 0, 'x' }, &remove_buf);

    var replace_buf = [_]u8{ 'a', '-', 0, '-', 'z' };
    try std.testing.expectEqual(@as(usize, 2), string.strreplace(&replace_buf, '-', '_'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', '_', 0, '-', 'z' }, &replace_buf);

    var zero_backing = [_]u8{0} ** 48;
    zero_backing[17] = 0x7f;
    zero_backing[31] = 0x33;
    try std.testing.expectEqual(@as(?usize, 17), string.memchr_inv(&zero_backing, 0));

    const haystack = [_][]const u8{
        "disabled",
        "auto\n",
        "manual",
    };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(&haystack, "auto"));
}
