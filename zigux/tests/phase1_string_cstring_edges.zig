const std = @import("std");
const string = @import("string");

test "phase1 string cstring edges keep copy helpers aligned with C-string termination" {
    var copied = [_]u8{0xaa} ** 5;
    try std.testing.expectEqual(@as(usize, 2), string.strlcpy(&copied, "ok"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0xaa, 0xaa }, &copied);

    var trunc = [_]u8{0xaa} ** 4;
    try std.testing.expectEqual(@as(isize, -7), string.strscpy(&trunc, "hello"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'e', 'l', 0 }, &trunc);

    const src_cstr = [_]u8{ 'o', 'k', 0, 'x', 'y' };
    var padded = [_]u8{0xaa} ** 6;
    try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(&padded, &src_cstr));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0, 0, 0 }, &padded);

    var alias = [_]u8{0xaa} ** 5;
    try std.testing.expectEqual(@as(isize, 2), string.strscpy_pad(&alias, "hi"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'i', 0, 0, 0 }, &alias);
}

test "phase1 string cstring edges keep equality and prefix suffix helpers at embedded NUL boundaries" {
    const lhs = [_]u8{ 'a', 'b', 0, 'x' };
    const rhs = [_]u8{ 'a', 'b', 0, 'y' };
    const miss = [_]u8{ 'a', 'c', 0, 'y' };

    try std.testing.expect(string.streq(&lhs, &rhs));
    try std.testing.expect(!string.streq(&lhs, &miss));

    try std.testing.expectEqual(@as(usize, 2), string.strHasPrefix(&lhs, &rhs));
    try std.testing.expectEqual(@as(usize, 2), string.str_has_prefix(&lhs, &rhs));
    try std.testing.expect(string.strstarts(&lhs, &rhs));

    try std.testing.expect(string.strstarts("prefix", ""));
}

test "phase1 string cstring edges keep byte search helpers within the visible C-string" {
    const search = [_]u8{ 'a', 'b', 0, 'c', 'd' };
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&search, search.len, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&search, search.len, 'c'));
}

test "phase1 string cstring edges keep match helpers on first match and newline-aware equality" {
    const options = [_][]const u8{
        "disabled",
        "auto\n",
        "manual",
        "auto",
    };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&options, "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(&options, "auto\n"));

    const nul_needle = [_]u8{ 'm', 'a', 'n', 'u', 'a', 'l', 0, 'x' };
    try std.testing.expectEqual(@as(?usize, 2), string.matchString(&options, &nul_needle));
    try std.testing.expectEqual(@as(?usize, 2), string.match_string(&options, &nul_needle));

    try std.testing.expect(string.sysfsStreq("zigux\n", "zigux"));
    try std.testing.expect(string.sysfs_streq("zigux", "zigux\n"));
    try std.testing.expect(!string.sysfsStreq("zigux\nmore", "zigux"));
}

test "phase1 string cstring edges keep duplicated bytes and memparse results explicit" {
    const allocator = std.testing.allocator;
    const duplicated = try string.memdup(allocator, "zigux");
    defer allocator.free(duplicated);
    try std.testing.expectEqualStrings("zigux", duplicated);

    const decimal = string.memparse("64K rest");
    try std.testing.expectEqual(@as(u64, 64 << 10), decimal.value);
    try std.testing.expectEqualStrings(" rest", decimal.rest);

    const invalid = string.memparse("-xyz");
    try std.testing.expectEqual(@as(u64, 0), invalid.value);
    try std.testing.expectEqualStrings("-xyz", invalid.rest);
}
