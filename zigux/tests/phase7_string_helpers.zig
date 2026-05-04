const std = @import("std");
const string_helpers = @import("string_helpers");
const escape_vectors = @import("fixtures/phase7_string_helpers_escape_vectors.zig");

fn cStringPrefix(text: []const u8) []const u8 {
    return text[0 .. std.mem.indexOfScalar(u8, text, 0) orelse text.len];
}

test "phase 7 string helpers module imports cleanly" {
    _ = string_helpers;
}

test "phase 7 sysfs string equality keeps newline compatibility" {
    try std.testing.expect(string_helpers.sysfsStreq("module", "module\n"));
    try std.testing.expect(!string_helpers.sysfsStreq("module", "modulex\n"));
}

test "phase 7 string matching preserves null-terminated search semantics" {
    const values = [_]?[]const u8{ "alpha", "beta", null, "gamma" };

    try std.testing.expectEqual(@as(i32, 1), string_helpers.matchString(&values, values.len, "beta"));
    try std.testing.expectEqual(@as(i32, 1), string_helpers.matchString(&values, values.len, "beta\x00ignored"));
    try std.testing.expectEqual(string_helpers.EINVAL, string_helpers.matchString(&values, values.len, "gamma"));
    try std.testing.expectEqual(@as(i32, 0), string_helpers.sysfsMatchString(&values, values.len, "alpha\n"));
}

test "phase 7 match helpers accept Linux-style all-entries search bounds" {
    const values = [_]?[]const u8{ "alpha", "beta", null, "gamma" };

    try std.testing.expectEqual(@as(i32, 1), string_helpers.matchString(&values, std.math.maxInt(usize), "beta"));
    try std.testing.expectEqual(string_helpers.EINVAL, string_helpers.matchString(&values, std.math.maxInt(usize), "gamma"));
    try std.testing.expectEqual(@as(i32, 1), string_helpers.sysfsMatchString(&values, std.math.maxInt(usize), "beta\n"));
}

test "phase 7 replacement and padding helpers work in place" {
    var replace_buf = [_]u8{ 'a', '-', 'b', 0, '-', 'c' };
    _ = string_helpers.strreplace(&replace_buf, '-', '_');
    try std.testing.expectEqualSlices(u8, "a_b", replace_buf[0..3]);
    try std.testing.expectEqual(@as(u8, '-'), replace_buf[4]);

    var padded = [_]u8{ 0, 0, 0, 0, 0 };
    string_helpers.memcpyAndPad(&padded, "xy", 2, '.');
    try std.testing.expectEqualSlices(u8, "xy...", &padded);

    var exact = [_]u8{ 0, 0 };
    string_helpers.memcpyAndPad(&exact, "xy", 2, '.');
    try std.testing.expectEqualSlices(u8, "xy", &exact);
}

test "phase 7 whitespace helpers honor C-string trimming boundaries" {
    try std.testing.expectEqualStrings("value", string_helpers.skipSpaces(" \t\nvalue\x00tail"));
    try std.testing.expectEqual(@as(usize, 0), string_helpers.skipSpaces(" \t\n\x00tail").len);

    var trimmed = [_]u8{ ' ', '\t', 'o', 'k', '\n', ' ', 0, 'x' };
    const strimmed = string_helpers.strim(&trimmed);
    try std.testing.expectEqualSlices(u8, "ok", strimmed);
    try std.testing.expectEqual(@as(u8, 0), trimmed[4]);
    try std.testing.expectEqual(@as(u8, 0), trimmed[6]);
    try std.testing.expectEqual(@as(u8, 'x'), trimmed[7]);

    var all_space = [_]u8{ ' ', '\n', '\t', 0, 'x' };
    const empty = string_helpers.strim(&all_space);
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(u8, 0), all_space[0]);
    try std.testing.expectEqual(@as(u8, 'x'), all_space[4]);
}

test "phase 7 termination helper respects bounded search windows" {
    try std.testing.expect(string_helpers.stringIsTerminated("xy\x00tail", 3));
    try std.testing.expect(!string_helpers.stringIsTerminated("xy\x00tail", 2));
    try std.testing.expect(!string_helpers.stringIsTerminated("xyz", 3));
}

test "phase 7 ASCII case helpers stop at NUL and respect destination bounds" {
    var upper = [_]u8{ '.', '.', '.', '.', '.', '.', '.' };
    string_helpers.stringUpper(&upper, "aBc1!\x00tail");
    try std.testing.expectEqualSlices(u8, "ABC1!\x00", upper[0..6]);
    try std.testing.expectEqual(@as(u8, '.'), upper[6]);

    var lower = [_]u8{ '.', '.', '.', '.' };
    string_helpers.stringLower(&lower, "Zz9!");
    try std.testing.expectEqualSlices(u8, "zz9!", &lower);
}

test "phase 7 stringGetSize covers SI, binary, and formatting flag cases" {
    var out = [_]u8{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    const format_cases = [_]struct {
        flags: u32,
        expected_si: []const u8,
        expected_binary: []const u8,
    }{
        .{ .flags = 0, .expected_si = "8.39 MB", .expected_binary = "8.00 MiB" },
        .{ .flags = string_helpers.STRING_UNITS_NO_SPACE, .expected_si = "8.39MB", .expected_binary = "8.00MiB" },
        .{ .flags = string_helpers.STRING_UNITS_NO_SPACE | string_helpers.STRING_UNITS_NO_BYTES, .expected_si = "8.39M", .expected_binary = "8.00Mi" },
        .{ .flags = string_helpers.STRING_UNITS_NO_BYTES, .expected_si = "8.39 M", .expected_binary = "8.00 Mi" },
    };

    const zero_len = string_helpers.stringGetSize(0, 1, string_helpers.STRING_UNITS_10, &out);
    try std.testing.expectEqual(@as(usize, 3), zero_len);
    try std.testing.expectEqualStrings("0 B", cStringPrefix(&out));

    const si_len = string_helpers.stringGetSize(1500, 1, string_helpers.STRING_UNITS_10, &out);
    try std.testing.expectEqual(@as(usize, 7), si_len);
    try std.testing.expectEqualStrings("1.50 kB", cStringPrefix(&out));

    const binary_len = string_helpers.stringGetSize(1536, 1, string_helpers.STRING_UNITS_2, &out);
    try std.testing.expectEqual(@as(usize, 8), binary_len);
    try std.testing.expectEqualStrings("1.50 KiB", cStringPrefix(&out));

    const compact_len = string_helpers.stringGetSize(
        1536,
        1,
        string_helpers.STRING_UNITS_2 | string_helpers.STRING_UNITS_NO_SPACE | string_helpers.STRING_UNITS_NO_BYTES,
        &out,
    );
    try std.testing.expectEqual(@as(usize, 6), compact_len);
    try std.testing.expectEqualStrings("1.50Ki", cStringPrefix(&out));

    const multiplied_len = string_helpers.stringGetSize(10, 512, string_helpers.STRING_UNITS_10, &out);
    try std.testing.expectEqual(@as(usize, 7), multiplied_len);
    try std.testing.expectEqualStrings("5.12 kB", cStringPrefix(&out));

    const rounded_si_len = string_helpers.stringGetSize(1100, 1, string_helpers.STRING_UNITS_10, &out);
    try std.testing.expectEqual(@as(usize, 7), rounded_si_len);
    try std.testing.expectEqualStrings("1.10 kB", cStringPrefix(&out));

    const rounded_binary_len = string_helpers.stringGetSize(1100, 1, string_helpers.STRING_UNITS_2, &out);
    try std.testing.expectEqual(@as(usize, 8), rounded_binary_len);
    try std.testing.expectEqualStrings("1.07 KiB", cStringPrefix(&out));

    const weird_block_si_len = string_helpers.stringGetSize(3000, 1900, string_helpers.STRING_UNITS_10, &out);
    try std.testing.expectEqual(@as(usize, 7), weird_block_si_len);
    try std.testing.expectEqualStrings("5.70 MB", cStringPrefix(&out));

    const weird_block_binary_len = string_helpers.stringGetSize(3000, 1900, string_helpers.STRING_UNITS_2, &out);
    try std.testing.expectEqual(@as(usize, 8), weird_block_binary_len);
    try std.testing.expectEqualStrings("5.44 MiB", cStringPrefix(&out));

    const huge_si_len = string_helpers.stringGetSize(std.math.maxInt(u64), 4096, string_helpers.STRING_UNITS_10, &out);
    try std.testing.expectEqual(@as(usize, 7), huge_si_len);
    try std.testing.expectEqualStrings("75.6 ZB", cStringPrefix(&out));

    const huge_binary_len = string_helpers.stringGetSize(std.math.maxInt(u64), 4096, string_helpers.STRING_UNITS_2, &out);
    try std.testing.expectEqual(@as(usize, 8), huge_binary_len);
    try std.testing.expectEqualStrings("64.0 ZiB", cStringPrefix(&out));

    for (format_cases) |case| {
        @memset(&out, 0);
        const si_case_len = string_helpers.stringGetSize(16384, 512, string_helpers.STRING_UNITS_10 | case.flags, &out);
        try std.testing.expectEqual(case.expected_si.len, si_case_len);
        try std.testing.expectEqualStrings(case.expected_si, cStringPrefix(&out));

        @memset(&out, 0);
        const binary_case_len = string_helpers.stringGetSize(16384, 512, string_helpers.STRING_UNITS_2 | case.flags, &out);
        try std.testing.expectEqual(case.expected_binary.len, binary_case_len);
        try std.testing.expectEqualStrings(case.expected_binary, cStringPrefix(&out));
    }
}

test "phase 7 stringGetSize returns snprintf-style length on truncation" {
    var out = [_]u8{ '!', '!', '!', '!', '!' };
    const len = string_helpers.stringGetSize(1500, 1, string_helpers.STRING_UNITS_10, &out);

    try std.testing.expectEqual(@as(usize, 7), len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '1', '.', '5', '0', 0 }, &out);

    try std.testing.expectEqual(
        @as(usize, 7),
        string_helpers.stringGetSize(1500, 1, string_helpers.STRING_UNITS_10, &.{}),
    );
}

test "phase 7 escape flag masks stay aligned with the Linux helper contract" {
    try std.testing.expectEqual(
        string_helpers.UNESCAPE_SPACE |
            string_helpers.UNESCAPE_OCTAL |
            string_helpers.UNESCAPE_HEX |
            string_helpers.UNESCAPE_SPECIAL,
        string_helpers.UNESCAPE_ALL_MASK,
    );
    try std.testing.expectEqual(
        string_helpers.ESCAPE_SPACE |
            string_helpers.ESCAPE_SPECIAL |
            string_helpers.ESCAPE_NULL |
            string_helpers.ESCAPE_OCTAL |
            string_helpers.ESCAPE_NP |
            string_helpers.ESCAPE_HEX |
            string_helpers.ESCAPE_NA |
            string_helpers.ESCAPE_NAP |
            string_helpers.ESCAPE_APPEND,
        string_helpers.ESCAPE_ALL_MASK,
    );
}

test "phase 7 parseIntArray keeps the counted get_options contract explicit" {
    const ints = try string_helpers.parseIntArray(std.testing.allocator, "1-3,5");
    defer std.testing.allocator.free(ints);

    try std.testing.expectEqualSlices(i32, &[_]i32{ 4, 1, 2, 3, 5 }, ints);
}

test "phase 7 parseIntArray keeps base and sign parsing explicit" {
    const ints = try string_helpers.parseIntArray(std.testing.allocator, "0x10,07,-2");
    defer std.testing.allocator.free(ints);

    try std.testing.expectEqualSlices(i32, &[_]i32{ 3, 16, 7, -2 }, ints);
}

test "phase 7 parseIntArray stops at the first NUL and truncates wide values" {
    const ints = try string_helpers.parseIntArray(std.testing.allocator, "4294967297\x00,3");
    defer std.testing.allocator.free(ints);

    try std.testing.expectEqualSlices(i32, &[_]i32{ 1, 1 }, ints);
}

test "phase 7 parseIntArray reports missing integer input" {
    try std.testing.expectError(error.NoEntry, string_helpers.parseIntArray(std.testing.allocator, ""));
    try std.testing.expectError(error.NoEntry, string_helpers.parseIntArray(std.testing.allocator, "+,7"));
    try std.testing.expectError(error.NoEntry, string_helpers.parseIntArray(std.testing.allocator, "words only"));
}

test "phase 7 parseIntArrayUser keeps count-bounded copy semantics explicit" {
    const ints = try string_helpers.parseIntArrayUser(std.testing.allocator, "1-3,5", 3);
    defer std.testing.allocator.free(ints);

    try std.testing.expectEqualSlices(i32, &[_]i32{ 3, 1, 2, 3 }, ints);

    const counted = try string_helpers.parseIntArrayUser(std.testing.allocator, "7,9tail", 3);
    defer std.testing.allocator.free(counted);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 2, 7, 9 }, counted);

    try std.testing.expectError(error.NoEntry, string_helpers.parseIntArrayUser(std.testing.allocator, "1,2", 0));
}

test "phase 7 kstrdupQuotable reuses the bounded escape subset for log-safe duplication" {
    const quoted = (try string_helpers.kstrdupQuotable(std.testing.allocator, "A\n\t\\\"\x00tail")).?;
    defer std.testing.allocator.free(quoted);

    try std.testing.expectEqualStrings("A\\x0a\\x09\\x5c\\x22", quoted);
    try std.testing.expectEqual(@as(u8, 0), quoted[quoted.len]);

    try std.testing.expectEqual(@as(?[:0]u8, null), try string_helpers.kstrdupQuotable(std.testing.allocator, null));
}

test "phase 7 kstrdupAndReplace keeps ownership and first-NUL replacement boundaries explicit" {
    const replaced = (try string_helpers.kstrdupAndReplace(std.testing.allocator, "a-b-a\x00tail", '-', '_')).?;
    defer std.testing.allocator.free(replaced);

    try std.testing.expectEqualStrings("a_b_a", replaced);
    try std.testing.expectEqual(@as(u8, 0), replaced[replaced.len]);

    var source = [_]u8{ 'x', '-', 'y', 0, '-', 'z' };
    const duplicated = (try string_helpers.kstrdupAndReplace(std.testing.allocator, &source, '-', '.')).?;
    defer std.testing.allocator.free(duplicated);

    try std.testing.expectEqualStrings("x.y", duplicated);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', '-', 'y', 0, '-', 'z' }, &source);
    try std.testing.expectEqual(@as(?[:0]u8, null), try string_helpers.kstrdupAndReplace(std.testing.allocator, null, '-', '.'));
}

test "phase 7 kasprintfStrarray returns sequential owned strings with a null-pointer terminator" {
    var names = try string_helpers.kasprintfStrarray(std.testing.allocator, "cpu", 3);
    defer names.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 3), names.names.len);
    try std.testing.expectEqualStrings("cpu-0", names.names[0]);
    try std.testing.expectEqualStrings("cpu-1", names.names[1]);
    try std.testing.expectEqualStrings("cpu-2", names.names[2]);
    try std.testing.expectEqualStrings("cpu-1", std.mem.span(names.cArray()[1].?));
    try std.testing.expectEqual(@as(?[*:0]const u8, null), names.cArray()[3]);
}

test "phase 7 kasprintfStrarrayRaw keeps direct C-style pointer ownership explicit" {
    const raw = try string_helpers.kasprintfStrarrayRaw(std.testing.allocator, "cpu", 3);
    defer string_helpers.kfreeStrarrayRaw(std.testing.allocator, raw, 3);

    try std.testing.expectEqual(@as(usize, 4), raw.len);
    try std.testing.expectEqualStrings("cpu-0", std.mem.span(raw[0].?));
    try std.testing.expectEqualStrings("cpu-1", std.mem.span(raw[1].?));
    try std.testing.expectEqualStrings("cpu-2", std.mem.span(raw[2].?));
    try std.testing.expectEqual(@as(?[*:0]u8, null), raw[3]);
}

test "phase 7 kasprintfStrarrayRaw keeps zero-count and first-NUL prefixes explicit" {
    const prefixed = try string_helpers.kasprintfStrarrayRaw(std.testing.allocator, "tty\x00ignored", 2);
    defer string_helpers.kfreeStrarrayRaw(std.testing.allocator, prefixed, 2);

    try std.testing.expectEqualStrings("tty-0", std.mem.span(prefixed[0].?));
    try std.testing.expectEqualStrings("tty-1", std.mem.span(prefixed[1].?));
    try std.testing.expectEqual(@as(?[*:0]u8, null), prefixed[2]);

    const empty = try string_helpers.kasprintfStrarrayRaw(std.testing.allocator, "cpu", 0);
    defer string_helpers.kfreeStrarrayRaw(std.testing.allocator, empty, 0);

    try std.testing.expectEqual(@as(usize, 1), empty.len);
    try std.testing.expectEqual(@as(?[*:0]u8, null), empty[0]);

    string_helpers.kfreeStrarrayRaw(std.testing.allocator, null, 0);
}

test "phase 7 kasprintfStrarrayRaw keeps zero-count ownership distinct across callers" {
    const empty_a = try string_helpers.kasprintfStrarrayRaw(std.testing.allocator, "cpu", 0);
    const empty_b = try string_helpers.kasprintfStrarrayRaw(std.testing.allocator, "cpu", 0);
    defer string_helpers.kfreeStrarrayRaw(std.testing.allocator, empty_a, 0);
    defer string_helpers.kfreeStrarrayRaw(std.testing.allocator, empty_b, 99);

    try std.testing.expectEqual(@as(usize, 1), empty_a.len);
    try std.testing.expectEqual(@as(?[*:0]u8, null), empty_a[0]);
    try std.testing.expectEqual(@as(usize, 1), empty_b.len);
    try std.testing.expectEqual(@as(?[*:0]u8, null), empty_b[0]);
    try std.testing.expect(empty_a.ptr != empty_b.ptr);
}

test "phase 7 string-array helpers reject usize overflow before allocation" {
    try std.testing.expectError(
        error.Overflow,
        string_helpers.kasprintfStrarrayRaw(std.testing.allocator, "cpu", std.math.maxInt(usize)),
    );
    try std.testing.expectError(
        error.Overflow,
        string_helpers.kasprintfStrarray(std.testing.allocator, "cpu", std.math.maxInt(usize)),
    );
}

test "phase 7 kfreeStrarrayRaw keeps counted partial teardown safe" {
    const raw = try std.testing.allocator.alloc(?[*:0]u8, 4);
    @memset(raw, null);
    raw[0] = (try std.testing.allocator.dupeZ(u8, "tty-0")).ptr;
    raw[1] = (try std.testing.allocator.dupeZ(u8, "tty-1")).ptr;
    string_helpers.kfreeStrarrayRaw(std.testing.allocator, raw, 2);
}

test "phase 7 kfreeStrarray keeps first-NUL prefixes, zero-count reuse, and repeated teardown safe" {
    var prefixed = try string_helpers.kasprintfStrarray(std.testing.allocator, "tty\x00ignored", 2);
    try std.testing.expectEqualStrings("tty-0", prefixed.names[0]);
    try std.testing.expectEqualStrings("tty-1", prefixed.names[1]);
    string_helpers.kfreeStrarray(std.testing.allocator, &prefixed);
    try std.testing.expectEqual(@as(usize, 0), prefixed.names.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), prefixed.cArray()[0]);
    string_helpers.kfreeStrarray(std.testing.allocator, &prefixed);

    var empty = try string_helpers.kasprintfStrarray(std.testing.allocator, "cpu", 0);
    try std.testing.expectEqual(@as(usize, 0), empty.names.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), empty.cArray()[0]);
    string_helpers.kfreeStrarray(std.testing.allocator, &empty);
    string_helpers.kfreeStrarray(std.testing.allocator, &empty);
}

test "phase 7 stringUnescape covers deterministic Linux escape fixtures" {
    var out = [_]u8{0} ** 32;

    for (escape_vectors.unescape_cases) |case| {
        @memset(&out, 0);
        const actual_len = string_helpers.stringUnescape(case.input, &out, out.len, case.flags);
        try std.testing.expectEqual(case.expected_len, actual_len);
        try std.testing.expectEqualSlices(u8, case.expected, out[0..actual_len]);
    }
}

test "phase 7 stringUnescape supports in-place and bounded destination behavior" {
    var inplace = [_]u8{ '\\', 'n', '\\', 'x', '4', '1', 0, '?', '?' };
    const inplace_len = string_helpers.stringUnescape(inplace[0..], inplace[0..], 0, string_helpers.UNESCAPE_ANY);
    try std.testing.expectEqual(@as(usize, 2), inplace_len);
    try std.testing.expectEqualSlices(u8, "\nA", inplace[0..2]);
    try std.testing.expectEqual(@as(u8, 0), inplace[2]);

    var bounded = [_]u8{ '!', '!', '!', '!' };
    const bounded_len = string_helpers.stringUnescape("\\n\\r", &bounded, bounded.len, string_helpers.UNESCAPE_SPACE);
    try std.testing.expectEqual(@as(usize, 2), bounded_len);
    try std.testing.expectEqualSlices(u8, "\n\r", bounded[0..2]);
    try std.testing.expectEqual(@as(u8, 0), bounded[2]);
    try std.testing.expectEqual(@as(u8, '!'), bounded[3]);

    var exact = [_]u8{ '!', '!', '!' };
    const exact_len = string_helpers.stringUnescape("\\n\\r", &exact, exact.len, string_helpers.UNESCAPE_SPACE);
    try std.testing.expectEqual(@as(usize, 2), exact_len);
    try std.testing.expectEqualSlices(u8, "\n\r", exact[0..2]);
    try std.testing.expectEqual(@as(u8, 0), exact[2]);
}

test "phase 7 string helper wrappers keep shared any-flag and C-string ownership rules" {
    var any = [_]u8{0} ** 8;
    const any_len = string_helpers.stringUnescapeAny("\\n\\x41", &any, any.len);
    try std.testing.expectEqual(@as(usize, 2), any_len);
    try std.testing.expectEqualSlices(u8, "\nA", any[0..any_len]);

    var any_inplace = [_]u8{ '\\', '0', '4', '0', 0, '?', '?' };
    const any_inplace_len = string_helpers.stringUnescapeAnyInplace(&any_inplace);
    try std.testing.expectEqual(@as(usize, 1), any_inplace_len);
    try std.testing.expectEqualSlices(u8, " ", any_inplace[0..any_inplace_len]);
    try std.testing.expectEqual(@as(u8, 0), any_inplace[any_inplace_len]);
    try std.testing.expectEqual(@as(u8, '?'), any_inplace[5]);

    var flagged_inplace = [_]u8{ '\\', 'n', 0, '?', '?' };
    const flagged_inplace_len = string_helpers.stringUnescapeInplace(&flagged_inplace, string_helpers.UNESCAPE_SPACE);
    try std.testing.expectEqual(@as(usize, 1), flagged_inplace_len);
    try std.testing.expectEqualSlices(u8, "\n", flagged_inplace[0..flagged_inplace_len]);
    try std.testing.expectEqual(@as(u8, 0), flagged_inplace[flagged_inplace_len]);

    var str_out = [_]u8{ '?', '?', '?', '?', '?', '?', '?', '?', '?' };
    const str_len = string_helpers.stringEscapeStr("A\n\x00tail", &str_out, str_out.len, string_helpers.ESCAPE_HEX, null);
    try std.testing.expectEqual(@as(usize, 8), str_len);
    try std.testing.expectEqualSlices(u8, "\\x41\\x0a", str_out[0..str_len]);
    try std.testing.expectEqual(@as(u8, '?'), str_out[str_len]);

    var str_any_np = [_]u8{ '?', '?', '?', '?', '?' };
    const str_any_np_len = string_helpers.stringEscapeStrAnyNp("A\n\x00tail", &str_any_np, str_any_np.len, null);
    try std.testing.expectEqual(@as(usize, 3), str_any_np_len);
    try std.testing.expectEqualSlices(u8, "A\\n", str_any_np[0..str_any_np_len]);
    try std.testing.expectEqual(@as(u8, '?'), str_any_np[str_any_np_len]);

    var zero_sized = [_]u8{ '!', '!', '!', '!' };
    const zero_sized_len = string_helpers.stringEscapeStr("A\n\x00tail", &zero_sized, 0, string_helpers.ESCAPE_HEX, null);
    try std.testing.expectEqual(@as(usize, 8), zero_sized_len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '!', '!', '!', '!' }, &zero_sized);

    const zero_sized_any_np_len = string_helpers.stringEscapeStrAnyNp("A\n\x00tail", &zero_sized, 0, null);
    try std.testing.expectEqual(@as(usize, 3), zero_sized_any_np_len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '!', '!', '!', '!' }, &zero_sized);

    var mem_any_np = [_]u8{ '?', '?', '?', '?', '?' };
    const mem_any_np_len = string_helpers.stringEscapeMemAnyNp("\n", &mem_any_np, null);
    try std.testing.expectEqual(@as(usize, 2), mem_any_np_len);
    try std.testing.expectEqualSlices(u8, "\\n", mem_any_np[0..mem_any_np_len]);
    try std.testing.expectEqual(@as(u8, '?'), mem_any_np[mem_any_np_len]);
}

test "phase 7 stringEscapeMem covers the bounded escape subset" {
    var out = [_]u8{0} ** 64;

    for (escape_vectors.escape_cases) |case| {
        @memset(&out, 0);
        const actual_len = string_helpers.stringEscapeMem(case.input, &out, case.flags, case.only);
        try std.testing.expectEqual(case.expected_len, actual_len);
        try std.testing.expectEqualSlices(u8, case.expected, out[0..actual_len]);
    }
}

test "phase 7 stringEscapeMem reports truncated output length without forcing a terminator" {
    var out = [_]u8{ '?', '?', '?', '?', '?' };
    const len = string_helpers.stringEscapeMem("\n", &out, string_helpers.ESCAPE_HEX, null);

    try std.testing.expectEqual(@as(usize, 4), len);
    try std.testing.expectEqualSlices(u8, "\\x0a?", &out);

    try std.testing.expectEqual(
        @as(usize, 2),
        string_helpers.stringEscapeMem("\n", &.{}, string_helpers.ESCAPE_SPACE, null),
    );
}
