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
}

test "phase 7 stringGetSize returns snprintf-style length on truncation" {
    var out = [_]u8{ '!', '!', '!', '!', '!' };
    const len = string_helpers.stringGetSize(1500, 1, string_helpers.STRING_UNITS_10, &out);

    try std.testing.expectEqual(@as(usize, 7), len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '1', '.', '5', '0', 0 }, &out);
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
}
