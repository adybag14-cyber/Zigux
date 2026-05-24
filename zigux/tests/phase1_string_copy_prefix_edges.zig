const std = @import("std");
const string = @import("string");

test "phase1 string copy helpers preserve C-string boundaries" {
    var copied = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa };
    try std.testing.expectEqual(@as(usize, 5), string.strlcpy(copied[0..], "alpha"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'l', 'p', 0 }, copied[0..]);

    var truncated = [_]u8{ 0xbb, 0xbb, 0xbb };
    try std.testing.expectEqual(@as(isize, -7), string.strscpy(truncated[0..], "beta"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'b', 'e', 0 }, truncated[0..]);

    var padded = [_]u8{ 1, 1, 1, 1, 1, 1 };
    try std.testing.expectEqual(@as(isize, 2), string.strscpy_pad(padded[0..], "ok"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0, 0, 0 }, padded[0..]);

    const duplicate = try string.memdup(std.testing.allocator, "zigux");
    defer std.testing.allocator.free(duplicate);
    try std.testing.expectEqualStrings("zigux", duplicate);
    try std.testing.expect(duplicate.ptr != "zigux".ptr);
}

test "phase1 string prefix and suffix helpers honor embedded NUL boundaries" {
    const nul_terminated = &[_]u8{ 'z', 'i', 'g', 0, 'x', 'x' };
    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix(nul_terminated, "zig"));
    try std.testing.expectEqual(@as(usize, 0), string.strHasPrefix(nul_terminated, "zigx"));

    try std.testing.expectEqual(@as(usize, 3), string.str_has_prefix("kernel", "ker"));
    try std.testing.expect(string.strstarts("kernel", "ker"));
    try std.testing.expect(!string.strstarts("kernel", "ern"));

    try std.testing.expect(string.strEndsWith("zigux", "gux"));
    try std.testing.expect(string.str_ends_with("zigux", "gux"));
    try std.testing.expect(!string.strEndsWith("zigux", "gix"));
    try std.testing.expect(string.strEndsWith(&[_]u8{ 'o', 'k', 0, 'x' }, "ok"));
    try std.testing.expect(!string.strEndsWith(&[_]u8{ 'o', 'k', 0, 'x' }, "kx"));
}

test "phase1 string equality and replacement helpers stop at the first NUL" {
    try std.testing.expect(string.strEq(&[_]u8{ 'a', 'b', 0, 'x' }, &[_]u8{ 'a', 'b', 0, 'y' }));
    try std.testing.expect(string.streq(&[_]u8{ 'a', 'b', 0, 'x' }, &[_]u8{ 'a', 'b', 0, 'z' }));
    try std.testing.expect(!string.strEq("abc", "abd"));

    var replaced = [_]u8{ '-', 'a', '-', 0, '-' };
    try std.testing.expectEqual(@as(usize, 3), string.replaceChar(replaced[0..], '-', '+'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ '+', 'a', '+', 0, '-' }, replaced[0..]);

    var alias_replaced = [_]u8{ 'x', '.', 'x', 0, '.' };
    try std.testing.expectEqual(@as(usize, 3), string.strreplace(alias_replaced[0..], '.', '!'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', '!', 'x', 0, '.' }, alias_replaced[0..]);
}

test "phase1 string bool aliases keep Linux-style forms in shared tests root" {
    try std.testing.expectEqual(true, try string.strtobool("y"));
    try std.testing.expectEqual(true, try string.strtobool("On"));
    try std.testing.expectEqual(false, try string.strtobool("0"));
    try std.testing.expectEqual(false, try string.strtobool("off"));
    try std.testing.expectError(error.Invalid, string.strtobool("maybe"));
    try std.testing.expectError(error.Invalid, string.strtobool(null));
}
