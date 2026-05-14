const std = @import("std");
const string_helpers = @import("string_helpers");

test "phase 7 string helpers starter covers whitespace trimming and prefix skipping" {
    try std.testing.expectEqualStrings("hello", string_helpers.skipSpaces("   hello"));
    try std.testing.expectEqualStrings("world", string_helpers.skip_spaces("\t\nworld"));

    const nul_prefixed = [_]u8{ ' ', '\t', 0, 'x' };
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 'x' }, string_helpers.skipSpaces(&nul_prefixed));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 'x' }, string_helpers.skip_spaces(&nul_prefixed));

    var trim_buf = [_]u8{ ' ', '\t', 'h', 'i', ' ', '\n' };
    try std.testing.expectEqualStrings("hi", string_helpers.trimSpaces(&trim_buf));

    var strim_buf = [_]u8{ ' ', 'h', 'i', ' ', '\n', 0, 'x', 'y' };
    try std.testing.expectEqualStrings("hi", string_helpers.strim(&strim_buf));
    try std.testing.expectEqualSlices(u8, &[_]u8{ ' ', 'h', 'i', 0, '\n', 0, 'x', 'y' }, &strim_buf);

    var trim_whitespace_only = [_]u8{ ' ', '\t', '\n', 0, 'x' };
    try std.testing.expectEqualStrings("", string_helpers.trimSpaces(&trim_whitespace_only));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, '\t', '\n', 0, 'x' }, &trim_whitespace_only);

    var strim_whitespace_only = [_]u8{ ' ', '\t', '\n', 0, 'x' };
    try std.testing.expectEqualStrings("", string_helpers.strim(&strim_whitespace_only));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, '\t', '\n', 0, 'x' }, &strim_whitespace_only);
}

test "phase 7 string helpers starter formats bounded sizes with three significant figures" {
    var buf = [_]u8{0} ** 16;
    const written = string_helpers.stringGetSize(1536, 1, string_helpers.STRING_UNITS_2, &buf, 0);
    try std.testing.expectEqual(@as(usize, 8), written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '1', '.', '5', '0', ' ', 'K', 'i', 'B', 0 }, buf[0 .. written + 1]);

    var zero_buf = [_]u8{ '#', '#', '#', '#', '#', '#', '#', '#' };
    const zero_written = string_helpers.string_get_size(42, 0, string_helpers.STRING_UNITS_10, &zero_buf, 0);
    try std.testing.expectEqual(@as(usize, 3), zero_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '0', ' ', 'B', 0 }, zero_buf[0 .. zero_written + 1]);

    var flag_buf = [_]u8{0} ** 16;
    const flag_written = string_helpers.stringGetSize(
        1536,
        1,
        string_helpers.STRING_UNITS_2 | string_helpers.STRING_UNITS_NO_SPACE | string_helpers.STRING_UNITS_NO_BYTES,
        &flag_buf,
        0,
    );
    try std.testing.expectEqual(@as(usize, 6), flag_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '1', '.', '5', '0', 'K', 'i', 0 }, flag_buf[0 .. flag_written + 1]);

    var truncated = [_]u8{ '#', '#', '#', '#', '#' };
    const truncated_written = string_helpers.string_get_size(1536, 1, string_helpers.STRING_UNITS_2, &truncated, truncated.len);
    try std.testing.expectEqual(@as(usize, 8), truncated_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '1', '.', '5', '0', 0 }, &truncated);
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

    var alias_decoded = [_]u8{0} ** 16;
    const alias_written = string_helpers.string_unescape_any(&escaped, &alias_decoded, 0);
    try std.testing.expectEqual(@as(usize, 6), alias_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '\n', 'A', 'A', '\x1b', '\\', 'q', 0 }, alias_decoded[0 .. alias_written + 1]);

    var selective = [_]u8{ '\\', 'x', '4', '1', '\\', 'n', 0, '#' };
    const selective_written = string_helpers.stringUnescapeInplace(&selective, string_helpers.UNESCAPE_HEX);
    try std.testing.expectEqual(@as(usize, 3), selective_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'A', '\\', 'n', 0 }, selective[0 .. selective_written + 1]);

    var alias_inplace = [_]u8{ '\\', 'n', '\\', 'x', '4', '1', 0, '#' };
    const alias_inplace_written = string_helpers.string_unescape_any_inplace(&alias_inplace);
    try std.testing.expectEqual(@as(usize, 2), alias_inplace_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '\n', 'A', 0 }, alias_inplace[0 .. alias_inplace_written + 1]);

    var supported_truncated_src = [_]u8{ '\\', 'n', 0, '!' };
    var supported_truncated_dst = [_]u8{ '#', '#', '#' };
    const supported_truncated_written = string_helpers.stringUnescape(&supported_truncated_src, &supported_truncated_dst, 2, string_helpers.UNESCAPE_SPACE);
    try std.testing.expectEqual(@as(usize, 1), supported_truncated_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '\n', 0 }, supported_truncated_dst[0 .. supported_truncated_written + 1]);

    var truncated_src = [_]u8{ '\\', 'q', 0, '!' };
    var truncated_dst = [_]u8{ '#', '#', '#' };
    const truncated_written = string_helpers.string_unescape(&truncated_src, &truncated_dst, 2, string_helpers.UNESCAPE_ANY);
    try std.testing.expectEqual(@as(usize, 1), truncated_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '\\', 0 }, truncated_dst[0 .. truncated_written + 1]);
}

test "phase 7 string helpers starter keeps exact-fit, terminator-only, and zero-capacity unescape destinations reviewable" {
    var exact_fit = [_]u8{ '!', '!', '!' };
    const exact_fit_len = string_helpers.stringUnescape("\n\r", &exact_fit, exact_fit.len, string_helpers.UNESCAPE_SPACE);
    try std.testing.expectEqual(@as(usize, 2), exact_fit_len);
    try std.testing.expectEqualSlices(u8, "
", exact_fit[0..2]);
    try std.testing.expectEqual(@as(u8, 0), exact_fit[2]);

    var terminator_only = [_]u8{ '!', '!' };
    const terminator_only_len = string_helpers.stringUnescape("\n\r", &terminator_only, 1, string_helpers.UNESCAPE_SPACE);
    try std.testing.expectEqual(@as(usize, 0), terminator_only_len);
    try std.testing.expectEqual(@as(u8, 0), terminator_only[0]);
    try std.testing.expectEqual(@as(u8, '!'), terminator_only[1]);

    var zero_capacity = [_]u8{};
    const zero_capacity_len = string_helpers.stringUnescape("\n", &zero_capacity, 0, string_helpers.UNESCAPE_SPACE);
    try std.testing.expectEqual(@as(usize, 0), zero_capacity_len);
}

test "phase 7 string helpers starter escapes bounded memory across flag families and dictionary modes" {
    var escaped = [_]u8{ 0, '\n', '\\', '"', 0x7f };
    var dst = [_]u8{0} ** 24;
    const written = string_helpers.stringEscapeMem(
        &escaped,
        &dst,
        0,
        string_helpers.ESCAPE_SPACE | string_helpers.ESCAPE_SPECIAL | string_helpers.ESCAPE_NULL | string_helpers.ESCAPE_HEX,
        null,
    );
    try std.testing.expectEqual(@as(usize, 12), written);
    try std.testing.expectEqualSlices(u8, "\\0\\n\\\\\\\"\\x7F", dst[0..written]);

    var alias_dst = [_]u8{0} ** 16;
    const alias_written = string_helpers.string_escape_mem_any_np(&[_]u8{ '\n', 0x7f }, &alias_dst, 0, null);
    try std.testing.expectEqual(@as(usize, 6), alias_written);
    try std.testing.expectEqualSlices(u8, "\\n\\177", alias_dst[0..alias_written]);

    var limited_dst = [_]u8{0} ** 8;
    const limited_written = string_helpers.stringEscapeMem("AZ", &limited_dst, 0, string_helpers.ESCAPE_HEX, "Z");
    try std.testing.expectEqual(@as(usize, 5), limited_written);
    try std.testing.expectEqualSlices(u8, "A\\x5A", limited_dst[0..limited_written]);

    var appended_dst = [_]u8{0} ** 8;
    const appended_written = string_helpers.stringEscapeMem(
        "AZ",
        &appended_dst,
        0,
        string_helpers.ESCAPE_HEX | string_helpers.ESCAPE_NA | string_helpers.ESCAPE_APPEND,
        "Z",
    );
    try std.testing.expectEqual(@as(usize, 5), appended_written);
    try std.testing.expectEqualSlices(u8, "A\\x5A", appended_dst[0..appended_written]);

    const terminated = [_]u8{ 'A', 0, '\n' };
    var string_dst = [_]u8{0} ** 8;
    const string_written = string_helpers.stringEscapeStr(
        &terminated,
        &string_dst,
        0,
        string_helpers.ESCAPE_HEX | string_helpers.ESCAPE_NA,
        null,
    );
    try std.testing.expectEqual(@as(usize, 1), string_written);
    try std.testing.expectEqualSlices(u8, "A", string_dst[0..string_written]);

    var any_np_dst = [_]u8{0} ** 8;
    const any_np_written = string_helpers.string_escape_str_any_np(&[_]u8{ '\n', 0 }, &any_np_dst, 0, null);
    try std.testing.expectEqual(@as(usize, 2), any_np_written);
    try std.testing.expectEqualSlices(u8, "\\n", any_np_dst[0..any_np_written]);

    var truncated = [_]u8{ '#', '#', '#' };
    const truncated_written = string_helpers.stringEscapeMem(&[_]u8{0}, &truncated, truncated.len, string_helpers.ESCAPE_HEX, null);
    try std.testing.expectEqual(@as(usize, 4), truncated_written);
    try std.testing.expectEqualSlices(u8, "\\x0", &truncated);
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
