const std = @import("std");
const string = @import("string");

test "phase1 string helper shared replay keeps whitespace aliases aligned" {
    try std.testing.expectEqualStrings("zigux  lane", string.skipSpaces(" \t\nzigux  lane"));
    try std.testing.expectEqualStrings("zigux  lane", string.skip_spaces(" \t\nzigux  lane"));

    var trimmed_buf = [_]u8{ ' ', '\t', 'z', 'i', 'g', 'u', 'x', ' ', '\n', 0, 'x' };
    try std.testing.expectEqualStrings("zigux", string.trimSpaces(&trimmed_buf));

    var strim_buf = [_]u8{ '\n', ' ', 'h', 'e', 'l', 'p', 'e', 'r', '\t', 0, 'x' };
    try std.testing.expectEqualStrings("helper", string.strim(&strim_buf));

    var strstrip_buf = [_]u8{ ' ', 'p', 'a', 'c', 'k', 'e', 't', ' ', '\r', 0, 'x' };
    try std.testing.expectEqualStrings("packet", string.strstrip(&strstrip_buf));
}

test "phase1 string helper shared replay keeps removal and dirty-byte scans aligned" {
    var direct_remove = [_]u8{ ' ', 'z', 'i', ' ', 'g', '\t', 'u', ' ', 'x', ' ', 0, 'x' };
    var alias_remove = direct_remove;
    try std.testing.expectEqualStrings("zig\tux", string.removeSpaces(&direct_remove));
    try std.testing.expectEqualStrings("zig\tux", string.remove_spaces(&alias_remove));
    try std.testing.expectEqualSlices(u8, &direct_remove, &alias_remove);

    var zero_scan = [_]u8{0} ** (@sizeOf(usize) * 2 + 5);
    zero_scan[@sizeOf(usize) + 3] = 9;
    try std.testing.expectEqual(@as(?usize, @sizeOf(usize) + 3), string.memchrInv(&zero_scan, 0));
    try std.testing.expectEqual(string.memchrInv(&zero_scan, 0), string.memchr_inv(&zero_scan, 0));

    var byte_scan = [_]u8{'a'} ** (@sizeOf(usize) * 2 + 7);
    byte_scan[@sizeOf(usize) * 2 + 1] = 'b';
    try std.testing.expectEqual(@as(?usize, @sizeOf(usize) * 2 + 1), string.memchrInv(&byte_scan, 'a'));
    try std.testing.expectEqual(string.memchrInv(&byte_scan, 'a'), string.memchr_inv(&byte_scan, 'a'));
}

test "phase1 string helper shared replay keeps sysfs and match routes aligned" {
    try std.testing.expect(string.sysfsStreq("auto\n", "auto"));
    try std.testing.expect(string.sysfs_streq("auto", "auto\n"));
    try std.testing.expect(!string.sysfsStreq("auto\nmore", "auto"));

    const sysfs_modes = [_][]const u8{ "off", "auto\n", "manual", "auto" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&sysfs_modes, "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(&sysfs_modes, "auto"));
    const limited_sysfs_modes = sysfs_modes[0..1];
    try std.testing.expectEqual(@as(?usize, null), string.sysfsMatchString(limited_sysfs_modes, "auto"));

    const match_modes = [_][]const u8{
        &[_]u8{ 'm', 'a', 'n', 0, 'x' },
        "auto",
        "manual",
    };
    const auto_cstr = [_]u8{ 'a', 'u', 't', 'o', 0, 'x' };
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(&match_modes, "man"));
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(&match_modes, &auto_cstr));
    try std.testing.expectEqual(@as(?usize, 2), string.match_string(&match_modes, "manual"));
    try std.testing.expectEqual(@as(?usize, null), string.match_string(&match_modes, "missing"));
}
