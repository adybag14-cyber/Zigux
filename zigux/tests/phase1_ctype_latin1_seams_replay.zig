const std = @import("std");
const ctype = @import("ctype");

fn expectLatinPair(upper: u8) !void {
    const lower: u8 = upper + 0x20;

    try std.testing.expect(ctype.isupper(upper));
    try std.testing.expect(!ctype.islower(upper));
    try std.testing.expect(ctype.isalpha(upper));
    try std.testing.expect(ctype.isalnum(upper));
    try std.testing.expectEqual(lower, ctype.tolower(upper));
    try std.testing.expectEqual(lower, ctype.fastTolower(upper));
    try std.testing.expectEqual(upper, ctype.toupper(upper));

    try std.testing.expect(!ctype.isupper(lower));
    try std.testing.expect(ctype.islower(lower));
    try std.testing.expect(ctype.isalpha(lower));
    try std.testing.expect(ctype.isalnum(lower));
    try std.testing.expectEqual(lower, ctype.tolower(lower));
    try std.testing.expectEqual(lower, ctype.fastTolower(lower));
    try std.testing.expectEqual(upper, ctype.toupper(lower));
}

test "phase1 ctype replay keeps latin1 case pairs aligned across the split ranges" {
    for (0xC0..0xD7) |upper| {
        try expectLatinPair(@intCast(upper));
    }

    for (0xD8..0xDF) |upper| {
        try expectLatinPair(@intCast(upper));
    }
}

test "phase1 ctype replay keeps latin1 seam bytes truthful" {
    for ([_]u8{ 0xD7, 0xF7, 0xBF }) |byte| {
        try std.testing.expect(ctype.ispunct(byte));
        try std.testing.expect(ctype.isgraph(byte));
        try std.testing.expect(ctype.isprint(byte));
        try std.testing.expect(!ctype.isalpha(byte));
        try std.testing.expect(!ctype.isalnum(byte));
        try std.testing.expectEqual(byte, ctype.tolower(byte));
        try std.testing.expectEqual(byte, ctype.fastTolower(byte));
        try std.testing.expectEqual(byte, ctype.toupper(byte));
    }

    try std.testing.expect(ctype.isspace(0xA0));
    try std.testing.expect(ctype.isprint(0xA0));
    try std.testing.expect(!ctype.isgraph(0xA0));
    try std.testing.expectEqual(@as(u8, 0xA0), ctype.fastTolower(0xA0));

    try std.testing.expect(ctype.islower(0xFF));
    try std.testing.expectEqual(@as(u8, 0xDF), ctype.toupper(0xFF));
    try std.testing.expectEqual(@as(u8, 0x7F), ctype.toascii(0xFF));
    try std.testing.expect(!ctype.isascii(0xFF));
}
