const std = @import("std");
const ctype = @import("ctype");

test "ctype ascii digit span keeps digit hex graph and print boundaries aligned" {
    try std.testing.expect(ctype.isdigit('0'));
    try std.testing.expect(ctype.isdigit('9'));
    try std.testing.expect(!ctype.isdigit('/'));
    try std.testing.expect(!ctype.isdigit(':'));

    try std.testing.expect(ctype.isxdigit('0'));
    try std.testing.expect(ctype.isxdigit('9'));
    try std.testing.expect(ctype.isxdigit('A'));
    try std.testing.expect(ctype.isxdigit('f'));
    try std.testing.expect(!ctype.isxdigit('g'));

    try std.testing.expect(ctype.isgraph('!'));
    try std.testing.expect(ctype.isgraph('0'));
    try std.testing.expect(!ctype.isgraph(' '));
    try std.testing.expect(ctype.isprint(' '));
    try std.testing.expect(!ctype.isprint('\n'));
}

test "ctype fast lowercase keeps only uppercase bytes mutable" {
    try std.testing.expectEqual(@as(u8, 'a'), ctype.fastTolower('A'));
    try std.testing.expectEqual(@as(u8, 'm'), ctype.fastTolower('m'));
    try std.testing.expectEqual(@as(u8, '!'), ctype.fastTolower('!'));
    try std.testing.expectEqual(@as(u8, 0xF8), ctype.fastTolower(0xD8));
    try std.testing.expectEqual(@as(u8, 0x80), ctype.fastTolower(0x80));
}

test "ctype ascii and octal helpers keep span edges explicit" {
    const ascii_samples = [_]u8{ 0x00, 0x7f, 0x80, 0xff };
    const expected_ascii = [_]bool{ true, true, false, false };
    const expected_toascii = [_]u8{ 0x00, 0x7f, 0x00, 0x7f };

    for (ascii_samples, expected_ascii, expected_toascii) |sample, want_ascii, want_toascii| {
        try std.testing.expectEqual(want_ascii, ctype.isascii(sample));
        try std.testing.expectEqual(want_toascii, ctype.toascii(sample));
    }

    try std.testing.expect(ctype.isodigit('0'));
    try std.testing.expect(ctype.isodigit('7'));
    try std.testing.expect(!ctype.isodigit('8'));
    try std.testing.expect(!ctype.isodigit('/'));
}
