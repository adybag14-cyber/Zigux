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

test "phase 7 replacement and padding helpers work in place" {
    var replace_buf = [_]u8{ 'a', '-', 'b', 0, '-', 'c' };
    _ = string_helpers.strreplace(&replace_buf, '-', '_');
    try std.testing.expectEqualSlices(u8, "a_b", replace_buf[0..3]);
    try std.testing.expectEqual(@as(u8, '-'), replace_buf[4]);

    var padded = [_]u8{ 0, 0, 0, 0, 0 };
    string_helpers.memcpyAndPad(&padded, "xy", 2, '.');
    try std.testing.expectEqualSlices(u8, "xy...", &padded);
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
