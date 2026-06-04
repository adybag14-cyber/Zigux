const std = @import("std");
const ctype = @import("ctype");

test "ctype high-bit Latin case transforms stay table driven" {
    const pairs = [_]struct {
        upper: u8,
        lower: u8,
    }{
        .{ .upper = 0xC0, .lower = 0xE0 },
        .{ .upper = 0xD6, .lower = 0xF6 },
        .{ .upper = 0xD8, .lower = 0xF8 },
        .{ .upper = 0xDE, .lower = 0xFE },
    };

    for (pairs) |pair| {
        try std.testing.expect(ctype.isupper(pair.upper));
        try std.testing.expect(!ctype.islower(pair.upper));
        try std.testing.expect(ctype.islower(pair.lower));
        try std.testing.expect(!ctype.isupper(pair.lower));
        try std.testing.expectEqual(pair.lower, ctype.tolower(pair.upper));
        try std.testing.expectEqual(pair.lower, ctype.fastTolower(pair.upper));
        try std.testing.expectEqual(pair.upper, ctype.toupper(pair.lower));
        try std.testing.expect(!ctype.isascii(pair.upper));
        try std.testing.expect(!ctype.isascii(pair.lower));
    }
}

test "ctype high-bit punctuation and spacing masks stay distinct" {
    try std.testing.expect(ctype.isspace(0xA0));
    try std.testing.expect(ctype.isprint(0xA0));
    try std.testing.expect(!ctype.isgraph(0xA0));
    try std.testing.expect(!ctype.isascii(0xA0));
    try std.testing.expectEqual(@as(u8, 0x20), ctype.toascii(0xA0));

    const punctuation = [_]u8{ 0xA1, 0xB7, 0xBF, 0xD7, 0xF7 };
    for (punctuation) |ch| {
        try std.testing.expect(ctype.ispunct(ch));
        try std.testing.expect(ctype.isgraph(ch));
        try std.testing.expect(ctype.isprint(ch));
        try std.testing.expect(!ctype.isalpha(ch));
        try std.testing.expectEqual(ch, ctype.tolower(ch));
        try std.testing.expectEqual(ch, ctype.toupper(ch));
        try std.testing.expectEqual(ch, ctype.fastTolower(ch));
    }
}

test "ctype digit and xdigit boundaries do not leak into high-bit bytes" {
    const ascii_hex = [_]u8{ '0', '9', 'A', 'F', 'a', 'f' };
    for (ascii_hex) |ch| {
        try std.testing.expect(ctype.isxdigit(ch));
    }

    const non_hex = [_]u8{ 'G', 'g', '/', ':', 0xB2, 0xC0, 0xE0, 0xFF };
    for (non_hex) |ch| {
        try std.testing.expect(!ctype.isxdigit(ch));
        try std.testing.expect(!ctype.isdigit(ch));
        try std.testing.expect(!ctype.isodigit(ch));
    }

    try std.testing.expect(ctype.isodigit('7'));
    try std.testing.expect(!ctype.isodigit('8'));
}
