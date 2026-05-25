const std = @import("std");
const string = @import("string");

test "phase1 string copy aliases preserve one-byte termination and shared truncation semantics" {
    var direct_single = [_]u8{0xaa};
    var alias_single = [_]u8{0xbb};
    const direct_single_result = string.strscpyPad(&direct_single, "hello");
    const alias_single_result = string.strscpy_pad(&alias_single, "hello");

    try std.testing.expectEqual(direct_single_result, alias_single_result);
    try std.testing.expectEqual(@as(isize, -7), direct_single_result);
    try std.testing.expectEqualSlices(u8, &[_]u8{0}, &direct_single);
    try std.testing.expectEqualSlices(u8, &[_]u8{0}, &alias_single);

    var direct = [_]u8{0xaa} ** 6;
    var alias = [_]u8{0xbb} ** 6;
    const source = [_]u8{ 'o', 'k', 0, 'x', 'y' };
    const direct_result = string.strscpyPad(&direct, &source);
    const alias_result = string.strscpy_pad(&alias, &source);

    try std.testing.expectEqual(direct_result, alias_result);
    try std.testing.expectEqual(@as(isize, 2), direct_result);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0, 0, 0 }, &direct);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0, 0, 0 }, &alias);
}

test "phase1 string spacing aliases keep shared in-place semantics" {
    try std.testing.expectEqualStrings("zigux", string.skipSpaces(" \tzigux"));
    try std.testing.expectEqualStrings("zigux", string.skip_spaces(" \tzigux"));

    var direct_trim = [_]u8{ ' ', 'z', 'i', 'g', ' ', 0, 'x' };
    var alias_trim = [_]u8{ ' ', 'z', 'i', 'g', ' ', 0, 'y' };
    try std.testing.expectEqualStrings("zig", string.trimSpaces(&direct_trim));
    try std.testing.expectEqualStrings("zig", string.strim(&alias_trim));

    var direct_remove = [_]u8{ 'z', ' ', 'i', ' ', 'g', 0 };
    var alias_remove = [_]u8{ 'z', ' ', 'i', ' ', 'g', 0 };
    try std.testing.expectEqualStrings("zig", string.removeSpaces(&direct_remove));
    try std.testing.expectEqualStrings("zig", string.remove_spaces(&alias_remove));

    var direct_replace = [_]u8{ 'a', '-', 'b', 0, '-' };
    var alias_replace = [_]u8{ 'a', '-', 'b', 0, '-' };
    try std.testing.expectEqual(string.replaceChar(&direct_replace, '-', '+'), string.strreplace(&alias_replace, '-', '+'));
    try std.testing.expectEqualSlices(u8, &direct_replace, &alias_replace);
}

test "phase1 string prefix and suffix aliases honor C-string boundaries" {
    const prefix_cstr = [_]u8{ 'k', 'e', 'r', 'n', 'e', 'l', 0, 'x' };
    const suffix_cstr = [_]u8{ 'k', 'e', 'r', 'n', 'e', 'l', 0, 'y' };

    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix(&prefix_cstr, "ker"));
    try std.testing.expectEqual(
        string.strHasPrefix(&prefix_cstr, "ker"),
        string.str_has_prefix(&prefix_cstr, "ker"),
    );
    try std.testing.expectEqual(@as(usize, 0), string.strHasPrefix(&prefix_cstr, "nel"));

    try std.testing.expect(string.strEndsWith(&suffix_cstr, "nel"));
    try std.testing.expectEqual(
        string.strEndsWith(&suffix_cstr, "nel"),
        string.str_ends_with(&suffix_cstr, "nel"),
    );
    try std.testing.expect(!string.strEndsWith(&suffix_cstr, "ely"));
}

test "phase1 string sysfs and match aliases keep first-match ordering stable" {
    const sysfs = [_][]const u8{ "disabled", "auto\n", "auto", "manual" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&sysfs, "auto"));
    try std.testing.expectEqual(
        string.sysfsMatchString(&sysfs, "auto"),
        string.sysfs_match_string(&sysfs, "auto"),
    );

    const haystack = [_][]const u8{
        "manual",
        "manual",
        "auto",
    };
    const needle_cstr = [_]u8{ 'a', 'u', 't', 'o', 0, 'x' };
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(&haystack, "manual"));
    try std.testing.expectEqual(@as(?usize, 2), string.match_string(&haystack, &needle_cstr));
}
