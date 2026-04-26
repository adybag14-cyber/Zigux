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

test "phase 7 stringUnescape covers deterministic Linux escape fixtures" {
    var out = [_]u8{0} ** 32;

    const space_len = string_helpers.stringUnescape("\\f\\ \\n\\r\\t\\v", &out, out.len, string_helpers.UNESCAPE_SPACE);
    try std.testing.expectEqual(@as(usize, 7), space_len);
    try std.testing.expectEqualSlices(u8, "\x0c\\ \n\r\t\x0b", out[0..space_len]);

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
