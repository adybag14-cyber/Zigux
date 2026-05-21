const std = @import("std");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const string = @import("string");

const ascii_whitespace = [_]u8{ ' ', '\t', '\n', '\r', 0x0b, 0x0c };

test "phase1 whitespace surface replay keeps ASCII whitespace aligned across ctype string and cmdline" {
    for (ascii_whitespace) |ch| {
        try std.testing.expect(ctype.isspace(ch));
    }

    var trim_buf = [_]u8{ ' ', '\t', '\n', '\r', 0x0b, 0x0c, 'z', 'i', 'g', 'u', 'x', 0x0c, '\r', '\n', '\t', ' ', 0 };
    try std.testing.expectEqualStrings("zigux", string.strim(trim_buf[0..]));

    const parsed = cmdline.nextArg(" \t\n\r\x0b\x0cdebug=1 tail") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("debug", parsed.param);
    try std.testing.expectEqualStrings("1", parsed.value.?);
    try std.testing.expectEqualStrings("tail", parsed.remaining);
}

test "phase1 whitespace surface replay keeps non-breaking space as a ctype-only boundary" {
    const nbsp: u8 = 0xa0;
    try std.testing.expect(ctype.isspace(nbsp));

    var trim_buf = [_]u8{ nbsp, 'm', 'o', 'd', 'e', nbsp, 0 };
    const trimmed = string.strim(trim_buf[0..]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ nbsp, 'm', 'o', 'd', 'e', nbsp }, trimmed);

    const args = [_]u8{ nbsp, 'q', 'u', 'i', 'e', 't', ' ', 't', 'a', 'i', 'l' };
    const parsed = cmdline.nextArg(args[0..]) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualSlices(u8, &[_]u8{ nbsp, 'q', 'u', 'i', 'e', 't' }, parsed.param);
    try std.testing.expect(parsed.value == null);
    try std.testing.expectEqualStrings("tail", parsed.remaining);
}

test "phase1 whitespace surface replay keeps removeSpaces narrower than ctype and cmdline splitting" {
    try std.testing.expect(ctype.isspace(' '));
    try std.testing.expect(ctype.isspace('\t'));

    var remove_buf = [_]u8{ 'a', ' ', '\t', 'b', ' ', 0 };
    const removed = string.removeSpaces(remove_buf[0..]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', '\t', 'b' }, removed);

    const first = cmdline.nextArg(" \ta\tb") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("a", first.param);
    try std.testing.expect(first.value == null);
    try std.testing.expectEqualStrings("b", first.remaining);

    var trim_buf = [_]u8{ ' ', '\t', 'a', '\t', 'b', ' ', 0 };
    try std.testing.expectEqualStrings("a\tb", string.strim(trim_buf[0..]));
}
