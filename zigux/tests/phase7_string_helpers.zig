const std = @import("std");
const string_helpers = @import("string_helpers");

fn runKasprintfStrarrayWithFailingAllocator(allocator: std.mem.Allocator, prefix: []const u8, n: usize) !void {
    var result = try string_helpers.kasprintfStrarray(allocator, prefix, n);
    defer result.deinit(allocator);
}

fn runKstrdupQuotableWithFailingAllocator(allocator: std.mem.Allocator, src: ?[]const u8) !void {
    if (try string_helpers.kstrdupQuotable(allocator, src)) |quoted| {
        allocator.free(quoted);
    }
}

fn runKstrdupQuotableFileWithFailingAllocator(allocator: std.mem.Allocator, src: ?[]const u8) !void {
    const quoted = try string_helpers.kstrdupQuotableFile(allocator, src);
    allocator.free(quoted);
}

fn runKstrdupQuotableCmdlineWithFailingAllocator(allocator: std.mem.Allocator, src: ?[]const u8) !void {
    if (try string_helpers.kstrdupQuotableCmdline(allocator, src)) |quoted| {
        allocator.free(quoted);
    }
}

fn runKstrdupAndReplaceWithFailingAllocator(
    allocator: std.mem.Allocator,
    src: []const u8,
    old: u8,
    new: u8,
) !void {
    const duplicated = try string_helpers.kstrdupAndReplace(allocator, src, old, new);
    allocator.free(duplicated);
}

fn runParseIntArrayWithFailingAllocator(
    allocator: std.mem.Allocator,
    buf: []const u8,
    count: usize,
) !void {
    const parsed = try string_helpers.parseIntArray(allocator, buf, count);
    allocator.free(parsed);
}

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

    var rounded_decimal = [_]u8{0} ** 16;
    const rounded_decimal_written = string_helpers.stringGetSize(999950, 1, string_helpers.STRING_UNITS_10, &rounded_decimal, 0);
    try std.testing.expectEqual(@as(usize, 7), rounded_decimal_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '1', '0', '0', '0', ' ', 'k', 'B', 0 }, rounded_decimal[0 .. rounded_decimal_written + 1]);

    var rounded_binary = [_]u8{0} ** 16;
    const rounded_binary_written = string_helpers.string_get_size(1048064, 1, string_helpers.STRING_UNITS_2, &rounded_binary, 0);
    try std.testing.expectEqual(@as(usize, 8), rounded_binary_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '1', '0', '2', '4', ' ', 'K', 'i', 'B', 0 }, rounded_binary[0 .. rounded_binary_written + 1]);

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
    try std.testing.expectEqualSlices(u8, &[_]u8{ '\n', '\r' }, exact_fit[0..2]);
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

test "phase 7 string helpers starter keeps append-limited octal dictionary escapes reviewable" {
    var octal_dst = [_]u8{0} ** 16;
    const octal_written = string_helpers.stringEscapeMem(
        "AZ",
        &octal_dst,
        0,
        string_helpers.ESCAPE_OCTAL | string_helpers.ESCAPE_APPEND | string_helpers.ESCAPE_NAP,
        "Z",
    );
    try std.testing.expectEqual(@as(usize, 5), octal_written);
    try std.testing.expectEqualSlices(u8, "A\\132", octal_dst[0..octal_written]);

    var alias_dst = [_]u8{0} ** 16;
    const alias_written = string_helpers.string_escape_mem(
        "AZ",
        &alias_dst,
        0,
        string_helpers.ESCAPE_OCTAL | string_helpers.ESCAPE_APPEND | string_helpers.ESCAPE_NAP,
        "Z",
    );
    try std.testing.expectEqual(@as(usize, 5), alias_written);
    try std.testing.expectEqualSlices(u8, "A\\132", alias_dst[0..alias_written]);
}

test "phase 7 string helpers starter builds sequential string arrays and sentinel views" {
    var result = try string_helpers.kasprintfStrarray(std.testing.allocator, "phase7-helper", 3);
    defer result.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 3), result.names.len);
    try std.testing.expectEqualStrings("phase7-helper-0", result.names[0]);
    try std.testing.expectEqualStrings("phase7-helper-1", result.names[1]);
    try std.testing.expectEqualStrings("phase7-helper-2", result.names[2]);

    const c_array = result.cArray();
    try std.testing.expectEqualStrings("phase7-helper-0", std.mem.span(c_array[0].?));
    try std.testing.expectEqualStrings("phase7-helper-1", std.mem.span(c_array[1].?));
    try std.testing.expectEqualStrings("phase7-helper-2", std.mem.span(c_array[2].?));
    try std.testing.expectEqual(@as(?[*:0]const u8, null), c_array[result.names.len]);

    const nul_prefixed = [_]u8{ 'p', 'r', 'e', 0, 'x' };
    var nul_result = try string_helpers.kasprintf_strarray(std.testing.allocator, &nul_prefixed, 1);
    defer nul_result.deinit(std.testing.allocator);
    try std.testing.expectEqualStrings("pre-0", nul_result.names[0]);
}

test "phase 7 string helpers starter reuses the blank string-array sentinel when no names are requested" {
    var zero = try string_helpers.kasprintfStrarray(std.testing.allocator, "phase7-helper", 0);
    defer zero.deinit(std.testing.allocator);
    var zero_alias = try string_helpers.kasprintf_strarray(std.testing.allocator, "phase7-helper", 0);
    defer zero_alias.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 0), zero.names.len);
    try std.testing.expectEqual(@as(usize, 1), zero.names_null_terminated.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), zero.cArray()[0]);
    try std.testing.expectEqual(zero.names_null_terminated.ptr, zero_alias.names_null_terminated.ptr);
    try std.testing.expectEqual(zero.cArray(), zero_alias.cArray());
}

test "phase 7 string helpers starter keeps sibling zero-count results on the shared sentinel after one owner deinitializes" {
    var first = try string_helpers.kasprintfStrarray(std.testing.allocator, "phase7-helper", 0);
    var second = try string_helpers.kasprintf_strarray(std.testing.allocator, "phase7-helper", 0);
    defer second.deinit(std.testing.allocator);

    const second_names_null_terminated_ptr = second.names_null_terminated.ptr;
    const second_c_array = second.cArray();

    first.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 0), first.names.len);
    try std.testing.expectEqual(@as(usize, 1), first.names_null_terminated.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), first.cArray()[0]);
    try std.testing.expectEqual(@as(usize, 0), second.names.len);
    try std.testing.expect(second.names_null_terminated.ptr == second_names_null_terminated_ptr);
    try std.testing.expect(second.cArray() == second_c_array);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), second.cArray()[0]);
}

test "phase 7 string helpers starter keeps sibling string arrays intact when one owner frees its result" {
    var first = try string_helpers.kasprintfStrarray(std.testing.allocator, "phase7-first", 2);
    var second = try string_helpers.kasprintfStrarray(std.testing.allocator, "phase7-second", 2);
    defer second.deinit(std.testing.allocator);

    const second_names_ptr = second.names.ptr;
    const second_names_nt_ptr = second.names_null_terminated.ptr;
    const second_c_array = second.cArray();

    string_helpers.kfreeStrarray(std.testing.allocator, &first);

    try std.testing.expect(second.names.ptr == second_names_ptr);
    try std.testing.expect(second.names_null_terminated.ptr == second_names_nt_ptr);
    try std.testing.expect(second.cArray() == second_c_array);
    try std.testing.expectEqualStrings("phase7-second-0", second.names[0]);
    try std.testing.expectEqualStrings("phase7-second-1", second.names[1]);
    try std.testing.expectEqualStrings("phase7-second-0", std.mem.span(second.cArray()[0].?));
    try std.testing.expectEqualStrings("phase7-second-1", std.mem.span(second.cArray()[1].?));
    try std.testing.expectEqual(@as(?[*:0]const u8, null), second.cArray()[second.names.len]);
}

test "phase 7 string helpers starter mirrors kfree_strarray teardown and stays idempotent" {
    var result = try string_helpers.kasprintfStrarray(std.testing.allocator, "phase7-helper", 2);

    string_helpers.kfreeStrarray(std.testing.allocator, &result);
    try std.testing.expectEqual(@as(usize, 0), result.names.len);
    try std.testing.expectEqual(@as(usize, 1), result.names_null_terminated.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), result.cArray()[0]);

    string_helpers.kfree_strarray(std.testing.allocator, &result);
    try std.testing.expectEqual(@as(usize, 0), result.names.len);
    try std.testing.expectEqual(@as(usize, 1), result.names_null_terminated.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), result.cArray()[0]);
}

test "phase 7 string helpers starter frees partially built arrays when allocator failure interrupts setup" {
    try std.testing.checkAllAllocationFailures(
        std.testing.allocator,
        runKasprintfStrarrayWithFailingAllocator,
        .{ "phase7-helper", 4 },
    );
}

test "phase 7 string helpers starter reports overflow before sizing the null-terminated string-array view" {
    try std.testing.expectError(
        error.Overflow,
        string_helpers.kasprintfStrarray(std.testing.allocator, "phase7-helper", std.math.maxInt(usize)),
    );
}

test "phase 7 string helpers starter duplicates and replaces only the exported c-string prefix" {
    const source = [_]u8{ 'd', 'e', 'v', '/', 'n', 'o', 'd', 'e', 0, '/', 't', 'a', 'i', 'l' };
    const duplicated = try string_helpers.kstrdupAndReplace(std.testing.allocator, &source, '/', '_');
    defer std.testing.allocator.free(duplicated);

    try std.testing.expectEqualStrings("dev_node", duplicated);
    try std.testing.expectEqual(@as(u8, 0), duplicated[duplicated.len]);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ 'd', 'e', 'v', '/', 'n', 'o', 'd', 'e', 0, '/', 't', 'a', 'i', 'l' },
        &source,
    );

    const alias = try string_helpers.kstrdup_and_replace(std.testing.allocator, "phase7-helper", '-', '_');
    defer std.testing.allocator.free(alias);
    try std.testing.expectEqualStrings("phase7_helper", alias);
}

test "phase 7 string helpers starter quotes special log-hazard bytes without widening beyond the exported c-string prefix" {
    try std.testing.expect((try string_helpers.kstrdupQuotable(std.testing.allocator, null)) == null);

    const source = [_]u8{ 'a', '\n', '"', '\\', '\x1b', 0, 'x' };
    const quoted = (try string_helpers.kstrdupQuotable(std.testing.allocator, &source)).?;
    defer std.testing.allocator.free(quoted);
    try std.testing.expectEqualStrings("a\\x0A\\x22\\x5C\\x1B", quoted);

    const alias = (try string_helpers.kstrdup_quotable(std.testing.allocator, "tab\tquote\"")).?;
    defer std.testing.allocator.free(alias);
    try std.testing.expectEqualStrings("tab\\x09quote\\x22", alias);

    const nul_prefixed = [_]u8{ 'p', 'a', 't', 'h', 0, '"', '\\' };
    const bounded = (try string_helpers.kstrdupQuotable(std.testing.allocator, &nul_prefixed)).?;
    defer std.testing.allocator.free(bounded);
    try std.testing.expectEqualStrings("path", bounded);
}

test "phase 7 string helpers starter quotes already-materialized file paths and keeps the missing-file fallback explicit" {
    const missing = try string_helpers.kstrdupQuotableFile(std.testing.allocator, null);
    defer std.testing.allocator.free(missing);
    try std.testing.expectEqualStrings("<unknown>", missing);

    const source = [_]u8{ '/', 't', 'm', 'p', '/', 'l', 'o', 'g', '\n', '"', 0, 'x' };
    const quoted = try string_helpers.kstrdupQuotableFile(std.testing.allocator, &source);
    defer std.testing.allocator.free(quoted);
    try std.testing.expectEqualStrings("/tmp/log\\x0A\\x22", quoted);

    const alias = try string_helpers.kstrdup_quotable_file(std.testing.allocator, "dev\\\"node");
    defer std.testing.allocator.free(alias);
    try std.testing.expectEqualStrings("dev\\x5C\\x22node", alias);
}

test "phase 7 string helpers starter quotes cmdlines after collapsing trailing NULs and replacing inter-argument separators" {
    const cmdline = [_]u8{ 'z', 'i', 'g', 0, 'b', 'u', 'i', 'l', 'd', '\n', '"', 0, 0 };
    const quoted = (try string_helpers.kstrdupQuotableCmdline(std.testing.allocator, &cmdline)).?;
    defer std.testing.allocator.free(quoted);
    try std.testing.expectEqualStrings("zig build\\x0A\\x22", quoted);

    const alias_input = [_]u8{ 'r', 'u', 'n', 0, 'x', 0, 0 };
    const alias_cmdline = (try string_helpers.kstrdup_quotable_cmdline(std.testing.allocator, &alias_input)).?;
    defer std.testing.allocator.free(alias_cmdline);
    try std.testing.expectEqualStrings("run x", alias_cmdline);

    const blank = [_]u8{ 0, 0 };
    const quoted_blank = (try string_helpers.kstrdupQuotableCmdline(std.testing.allocator, &blank)).?;
    defer std.testing.allocator.free(quoted_blank);
    try std.testing.expectEqualStrings("", quoted_blank);

    try std.testing.expect((try string_helpers.kstrdupQuotableCmdline(std.testing.allocator, null)) == null);
}

test "phase 7 string helpers starter parses bounded comma lists and positive ranges" {
    const source = [_]u8{ '1', ',', '3', '-', '5', ',', '0', 'x', '7', ',', '0', '1', 0, '9' };
    const parsed = try string_helpers.parseIntArray(std.testing.allocator, &source, source.len);
    defer std.testing.allocator.free(parsed);

    try std.testing.expectEqual(@as(i32, 6), parsed[0]);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 1, 3, 4, 5, 7, 1 }, parsed[1..]);

    const alias = try string_helpers.parse_int_array(std.testing.allocator, "2-4", 3);
    defer std.testing.allocator.free(alias);
    try std.testing.expectEqual(@as(i32, 3), alias[0]);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 2, 3, 4 }, alias[1..]);
}

test "phase 7 string helpers starter stops parse-int-array at invalid tokens, first NUL, and explicit count bounds" {
    const partial = try string_helpers.parseIntArray(std.testing.allocator, "9,11,broken,15", "9,11,broken,15".len);
    defer std.testing.allocator.free(partial);
    try std.testing.expectEqual(@as(i32, 2), partial[0]);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 9, 11 }, partial[1..]);

    const nul_bounded = [_]u8{ '7', ',', '8', 0, ',', '9' };
    const bounded = try string_helpers.parse_int_array(std.testing.allocator, &nul_bounded, nul_bounded.len);
    defer std.testing.allocator.free(bounded);
    try std.testing.expectEqual(@as(i32, 2), bounded[0]);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 7, 8 }, bounded[1..]);

    const count_limited = try string_helpers.parseIntArray(std.testing.allocator, "4,6,8", 3);
    defer std.testing.allocator.free(count_limited);
    try std.testing.expectEqual(@as(i32, 2), count_limited[0]);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 4, 6 }, count_limited[1..]);
}

test "phase 7 string helpers starter reports empty parse-int-array input as no entry" {
    try std.testing.expectError(error.NoEntry, string_helpers.parseIntArray(std.testing.allocator, "broken", "broken".len));
    try std.testing.expectError(error.NoEntry, string_helpers.parse_int_array(std.testing.allocator, "", 0));
}

test "phase 7 string helpers starter reports parse-int-array allocation failure cleanly" {
    try std.testing.checkAllAllocationFailures(
        std.testing.allocator,
        runParseIntArrayWithFailingAllocator,
        .{ "1-4,0x8", 7 },
    );
}

test "phase 7 string helpers starter uppercases and lowercases only through the exported c-string boundary" {
    const upper_src = [_]u8{ 'm', 'i', 'x', 'e', 'd', 0, 'z' };
    var upper_dst = [_]u8{ '#', '#', '#', '#', '#', '#', '#' };
    string_helpers.stringUpper(&upper_dst, &upper_src);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'M', 'I', 'X', 'E', 'D', 0, '#' }, &upper_dst);

    const lower_src = [_]u8{ 'Z', 'I', 'G', 'u', 'X', 0, 'Q' };
    var lower_dst = [_]u8{ '#', '#', '#', '#', '#', '#', '#' };
    string_helpers.string_lower(&lower_dst, &lower_src);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 'i', 'g', 'u', 'x', 0, '#' }, &lower_dst);

    var bounded_upper = [_]u8{ '#', '#', '#' };
    string_helpers.string_upper(&bounded_upper, "phase7");
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'P', 'H', 'A' }, &bounded_upper);

    var bounded_lower = [_]u8{ '#', '#', '#', '#' };
    string_helpers.stringLower(&bounded_lower, "ZIGUX");
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 'i', 'g', 'u' }, &bounded_lower);
}

test "phase 7 string helpers starter reports kstrdupQuotable allocation failure cleanly" {
    try std.testing.checkAllAllocationFailures(
        std.testing.allocator,
        runKstrdupQuotableWithFailingAllocator,
        .{
            "phase7\nquote\"",
        },
    );
}

test "phase 7 string helpers starter reports kstrdupQuotableFile allocation failure cleanly" {
    try std.testing.checkAllAllocationFailures(
        std.testing.allocator,
        runKstrdupQuotableFileWithFailingAllocator,
        .{
            "/tmp/phase7\nquote\"",
        },
    );
}

test "phase 7 string helpers starter reports kstrdupQuotableCmdline allocation failure cleanly" {
    try std.testing.checkAllAllocationFailures(
        std.testing.allocator,
        runKstrdupQuotableCmdlineWithFailingAllocator,
        .{
            "zig\x00test\x00\x00",
        },
    );
}

test "phase 7 string helpers starter reports duplicate-and-replace allocation failure cleanly" {
    try std.testing.checkAllAllocationFailures(
        std.testing.allocator,
        runKstrdupAndReplaceWithFailingAllocator,
        .{ "phase7/helper", '/', '_' },
    );
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
