const std = @import("std");
const string_helpers = @import("string_helpers");

test "phase 7 string helpers starter covers whitespace trimming and prefix skipping" {
    try std.testing.expectEqualStrings("hello", string_helpers.skipSpaces("   hello"));
    try std.testing.expectEqualStrings("world", string_helpers.skip_spaces("\t\nworld"));

    var trim_buf = [_]u8{ ' ', '\t', 'h', 'i', ' ', '\n' };
    try std.testing.expectEqualStrings("hi", string_helpers.trimSpaces(&trim_buf));

    var strim_buf = [_]u8{ ' ', 'h', 'i', ' ', '\n', 0, 'x', 'y' };
    try std.testing.expectEqualStrings("hi", string_helpers.strim(&strim_buf));
    try std.testing.expectEqualSlices(u8, &[_]u8{ ' ', 'h', 'i', 0, '\n', 0, 'x', 'y' }, &strim_buf);
}

test "phase 7 string helpers starter keeps sysfs matching newline aware" {
    try std.testing.expect(string_helpers.sysfsStreq("zigux\n", "zigux"));
    try std.testing.expect(string_helpers.sysfs_streq("zigux", "zigux\n"));
    try std.testing.expect(!string_helpers.sysfsStreq("zigux\nmore", "zigux"));

    const newline = [_]u8{ 'o', 'k', '\n', 0, 'x' };
    const nul = [_]u8{ 'o', 'k', 0, 'y' };
    try std.testing.expect(string_helpers.sysfsStreq(&newline, &nul));
}

test "phase 7 string helpers starter matches tables through the first null entry" {
    const values = [_]?[]const u8{
        "disabled",
        "auto\n",
        "manual",
        null,
        "ignored",
    };

    try std.testing.expectEqual(@as(?usize, 2), string_helpers.matchString(&values, "manual"));
    try std.testing.expectEqual(@as(?usize, 2), string_helpers.match_string(&values, "manual"));
    try std.testing.expectEqual(@as(?usize, 1), string_helpers.sysfsMatchString(&values, "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string_helpers.__sysfs_match_string(&values, "auto\n"));
    try std.testing.expectEqual(@as(?usize, null), string_helpers.matchString(&values, "ignored"));
}

test "phase 7 string helpers starter unescapes supported escape families and preserves unsupported escapes" {
    var escaped = [_]u8{ '\\', 'n', '\\', 'x', '4', '1', '\\', '1', '0', '1', '\\', 'e', '\\', 'q', 0 };
    var decoded = [_]u8{0} ** 16;
    const written = string_helpers.stringUnescapeAny(&escaped, &decoded, 0);
    try std.testing.expectEqual(@as(usize, 6), written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '\n', 'A', 'A', '\x1b', '\\', 'q', 0 }, decoded[0 .. written + 1]);

    var selective = [_]u8{ '\\', 'x', '4', '1', '\\', 'n', 0, '#' };
    const selective_written = string_helpers.stringUnescapeInplace(&selective, string_helpers.UNESCAPE_HEX);
    try std.testing.expectEqual(@as(usize, 3), selective_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'A', '\\', 'n', 0 }, selective[0 .. selective_written + 1]);

    var truncated_src = [_]u8{ '\\', 'q', 0, '!' };
    var truncated_dst = [_]u8{ '#', '#', '#' };
    const truncated_written = string_helpers.string_unescape(&truncated_src, &truncated_dst, 2, string_helpers.UNESCAPE_ANY);
    try std.testing.expectEqual(@as(usize, 1), truncated_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '\\', 0 }, truncated_dst[0 .. truncated_written + 1]);
}

test "phase 7 string helpers starter pads bounded copies without reading past the provided source slice" {
    var padded = [_]u8{ '#', '#', '#', '#', '#', '#' };
    string_helpers.memcpyAndPad(&padded, "zig", 3, '.');
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 'i', 'g', '.', '.', '.' }, &padded);

    var truncated = [_]u8{ '#', '#', '#', '#' };
    string_helpers.memcpy_and_pad(&truncated, "alphabet", 8, '.');
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'l', 'p', 'h' }, &truncated);

    var short_source = [_]u8{ '#', '#', '#', '#', '#' };
    string_helpers.memcpyAndPad(&short_source, "go", 4, '!');
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'g', 'o', '!', '!', '!' }, &short_source);

    var requested_beyond_source = [_]u8{ '#', '#', '#', '#', '#' };
    string_helpers.memcpyAndPad(&requested_beyond_source, "go", 8, '!');
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'g', 'o', '!', '!', '!' }, &requested_beyond_source);
}

test "phase 7 string helpers starter replaces bytes only inside the exported c-string prefix" {
    var replace_buf = [_]u8{ 'a', '-', 'b', 0, '-' };
    try std.testing.expectEqual(@as(usize, 3), string_helpers.strreplace(&replace_buf, '-', '_'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', '_', 'b', 0, '-' }, &replace_buf);
}
