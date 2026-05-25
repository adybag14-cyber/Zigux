const std = @import("std");
const string = @import("string");

const e2big: isize = -7;

test "phase1 string copy helpers keep caller buffers reusable after truncation" {
    var buf = [_]u8{ 9, 9, 9, 9, 9, 9 };

    try std.testing.expectEqual(e2big, string.strscpy(buf[0..], "truncate"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 't', 'r', 'u', 'n', 'c', 0 }, buf[0..]);

    try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(buf[0..], &[_]u8{ 'o', 'k', 0, 'x' }));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0, 0, 0 }, buf[0..]);
}

test "phase1 string copy helpers keep zero-sized and one-byte destinations bounded" {
    var untouched = [_]u8{ 0xaa, 0xbb };
    try std.testing.expectEqual(@as(usize, 5), string.strlcpy(untouched[0..0], "hello"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xaa, 0xbb }, untouched[0..]);

    var single = [_]u8{0xff};
    try std.testing.expectEqual(e2big, string.strscpy_pad(single[0..], "x"));
    try std.testing.expectEqual(@as(u8, 0), single[0]);
}

test "phase1 string bool and equality helpers stop at the first C-string terminator" {
    try std.testing.expect(try string.strtobool(&[_]u8{ 'o', 'n', 0, 'x' }));
    try std.testing.expect(!(try string.strtobool(&[_]u8{ 'o', 'f', 0, 'x' })));
    try std.testing.expectError(error.Invalid, string.strtobool("o"));

    try std.testing.expect(string.streq(
        &[_]u8{ 'o', 'k', 0, 'x' },
        &[_]u8{ 'o', 'k', 0, 'y' },
    ));
}

test "phase1 string prefix and suffix helpers ignore bytes after embedded NUL" {
    const pathish = [_]u8{ 'p', 'r', 'e', 'f', 'i', 'x', 0, '!' };
    const prefix = [_]u8{ 'p', 'r', 'e', 'f', 'i', 'x', 0, '?' };
    const suffix = [_]u8{ 'f', 'i', 'x', 0, '?' };

    try std.testing.expectEqual(@as(usize, 6), string.strHasPrefix(pathish[0..], prefix[0..]));
    try std.testing.expect(string.strstarts(pathish[0..], "pre"));
    try std.testing.expect(string.strEndsWith(pathish[0..], suffix[0..]));
    try std.testing.expect(!string.str_ends_with(pathish[0..], "fixx"));
}
