const std = @import("std");
const string_helpers = @import("string_helpers");

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

test "phase 7 parseIntArray keeps base and sign parsing explicit" {
    const ints = try string_helpers.parseIntArray(std.testing.allocator, "0x10,07,-2");
    defer string_helpers.freeIntArray(std.testing.allocator, ints);

    try std.testing.expectEqualSlices(i32, &[_]i32{ 3, 16, 7, -2 }, ints);
}

test "phase 7 parseIntArray respects first-NUL and no-entry behavior" {
    const ints = try string_helpers.parseIntArray(std.testing.allocator, "1-3,9\x00ignored");
    defer string_helpers.freeIntArray(std.testing.allocator, ints);

    try std.testing.expectEqualSlices(i32, &[_]i32{ 4, 1, 2, 3, 9 }, ints);
    try std.testing.expectError(error.NoEntry, string_helpers.parseIntArray(std.testing.allocator, "none"));
}

test "phase 7 parseIntArrayUser copies a bounded user buffer before parsing" {
    const ints = try string_helpers.parseIntArrayUser(std.testing.allocator, "1-3,9 trailing", 5);
    defer string_helpers.freeIntArray(std.testing.allocator, ints);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 4, 1, 2, 3, 9 }, ints);

    const nul_bounded = try string_helpers.parseIntArrayUser(std.testing.allocator, "7,8\x00ignored,9", 11);
    defer string_helpers.freeIntArray(std.testing.allocator, nul_bounded);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 2, 7, 8 }, nul_bounded);
}

test "phase 7 parseIntArrayUser fails closed on short buffers and empty copied input" {
    try std.testing.expectError(error.Fault, string_helpers.parseIntArrayUser(std.testing.allocator, "12", 3));
    try std.testing.expectError(error.NoEntry, string_helpers.parseIntArrayUser(std.testing.allocator, "none", 4));
}

test "phase 7 stringUnescape covers deterministic Linux escape fixtures" {
    var out = [_]u8{0} ** 32;

    const space_len = string_helpers.stringUnescape("\\f\\ \\n\\r\\t\\v", &out, out.len, string_helpers.UNESCAPE_SPACE);
    try std.testing.expectEqual(@as(usize, 7), space_len);
    try std.testing.expectEqualSlices(u8, "\x0c\\ \n\r\t\x0b", out[0..space_len]);

    const octal_len = string_helpers.stringUnescape("\\40\\1\\387\\0064\\05\\040\\8a\\110\\777", &out, out.len, string_helpers.UNESCAPE_OCTAL);
    try std.testing.expectEqual(@as(usize, 15), octal_len);
    try std.testing.expectEqualSlices(u8, " \x01\x0387\x064\x05 \\8aH?7", out[0..octal_len]);

    const hex_len = string_helpers.stringUnescape("\\xv\\xa\\x2c\\xD\\x6f2", &out, out.len, string_helpers.UNESCAPE_HEX);
    try std.testing.expectEqual(@as(usize, 8), hex_len);
    try std.testing.expectEqualSlices(u8, "\\xv\n,\ro2", out[0..hex_len]);

    const special_len = string_helpers.stringUnescape("\\h\\\\\\\"\\a\\e\\", &out, out.len, string_helpers.UNESCAPE_SPECIAL);
    try std.testing.expectEqual(@as(usize, 7), special_len);
    try std.testing.expectEqualSlices(u8, "\\h\\\"\x07\x1b\\", out[0..special_len]);

    const any_len = string_helpers.stringUnescape("\\n\\x41\\040\\e", &out, out.len, string_helpers.UNESCAPE_ANY);
    try std.testing.expectEqual(@as(usize, 4), any_len);
    try std.testing.expectEqualSlices(u8, "\nA \x1b", out[0..any_len]);
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

test "phase 7 stringEscapeMem covers the bounded escape subset" {
    var out = [_]u8{0} ** 64;

    const any_len = string_helpers.stringEscapeMem("\n\\\x00", &out, string_helpers.ESCAPE_ANY, null);
    try std.testing.expectEqual(@as(usize, 6), any_len);
    try std.testing.expectEqualSlices(u8, "\\n\\\\\\0", out[0..any_len]);

    const hex_len = string_helpers.stringEscapeMem("A\x01z", &out, string_helpers.ESCAPE_NP | string_helpers.ESCAPE_HEX, null);
    try std.testing.expectEqual(@as(usize, 6), hex_len);
    try std.testing.expectEqualSlices(u8, "A\\x01z", out[0..hex_len]);
}

test "phase 7 stringEscapeMem keeps only and append behavior deterministic" {
    var out = [_]u8{0} ** 64;

    const dict_len = string_helpers.stringEscapeMem("A\n\tZ", &out, string_helpers.ESCAPE_SPACE, "\n");
    try std.testing.expectEqual(@as(usize, 5), dict_len);
    try std.testing.expectEqualSlices(u8, "A\\n\tZ", out[0..dict_len]);

    const append_len = string_helpers.stringEscapeMem("A\nZ", &out, string_helpers.ESCAPE_NAP | string_helpers.ESCAPE_HEX | string_helpers.ESCAPE_APPEND, "\n");
    try std.testing.expectEqual(@as(usize, 6), append_len);
    try std.testing.expectEqualSlices(u8, "A\\x0aZ", out[0..append_len]);
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

test "phase 7 kasprintfStrarray deinit resets exported views to the zero-count sentinel state" {
    var names = try string_helpers.kasprintfStrarray(std.testing.allocator, "cpu", 2);
    var empty = try string_helpers.kasprintfStrarray(std.testing.allocator, "cpu", 0);
    defer empty.deinit(std.testing.allocator);

    names.deinit(std.testing.allocator);
    try std.testing.expectEqual(@as(usize, 0), names.names.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), names.cArray()[0]);
    try std.testing.expectEqual(@as(usize, 0), empty.names.len);
    try std.testing.expect(names.cArray() == empty.cArray());
    try std.testing.expect(names.names_null_terminated.ptr == empty.names_null_terminated.ptr);

    names.deinit(std.testing.allocator);
    try std.testing.expect(names.cArray() == empty.cArray());
    try std.testing.expect(names.names_null_terminated.ptr == empty.names_null_terminated.ptr);
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

test "phase 7 skipSpaces and strim honor C-string whitespace bounds" {
    try std.testing.expectEqualStrings("ready", string_helpers.skipSpaces(" \t\nready\x00tail"));

    var padded = [_]u8{ ' ', '\t', 'o', 'k', ' ', '\n', 0, 'x', ' ' };
    const trimmed = string_helpers.strim(&padded);
    try std.testing.expectEqualStrings("ok", trimmed);
    try std.testing.expectEqual(@as(u8, 0), padded[4]);
    try std.testing.expectEqual(@as(u8, 'x'), padded[7]);
}
