const std = @import("std");
const ctype = @import("ctype");

test "high-bit latin case pairs round trip through table transforms" {
    const pairs = [_]struct { upper: u8, lower: u8 }{
        .{ .upper = 0xC0, .lower = 0xE0 },
        .{ .upper = 0xC1, .lower = 0xE1 },
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
        try std.testing.expectEqual(pair.lower, ctype.tolower(pair.lower));
        try std.testing.expectEqual(pair.upper, ctype.toupper(pair.upper));
    }
}

test "fast lowercase leaves punctuation controls and already-lower bytes stable" {
    const unchanged = [_]u8{ 0x00, '\t', ' ', '!', '@', '[', '`', '{', 0x7F, 0xA0, 0xBF, 0xDF, 0xFF };

    for (unchanged) |byte| {
        try std.testing.expect(!ctype.isupper(byte));
        try std.testing.expectEqual(byte, ctype.fastTolower(byte));
        try std.testing.expectEqual(byte, ctype.tolower(byte));
    }

    try std.testing.expectEqual(@as(u8, 'z'), ctype.fastTolower('Z'));
    try std.testing.expectEqual(@as(u8, 'z'), ctype.fastTolower('z'));
}

test "ascii projection does not imply ascii classification for high bytes" {
    const samples = [_]struct { input: u8, projected: u8 }{
        .{ .input = 0x80, .projected = 0x00 },
        .{ .input = 0xA0, .projected = 0x20 },
        .{ .input = 0xBF, .projected = 0x3F },
        .{ .input = 0xC1, .projected = 0x41 },
        .{ .input = 0xE1, .projected = 0x61 },
        .{ .input = 0xFF, .projected = 0x7F },
    };

    for (samples) |sample| {
        try std.testing.expect(!ctype.isascii(sample.input));
        try std.testing.expectEqual(sample.projected, ctype.toascii(sample.input));
        try std.testing.expect(ctype.isascii(ctype.toascii(sample.input)));
    }

    try std.testing.expect(ctype.isprint(0xA0));
    try std.testing.expect(ctype.isspace(0xA0));
    try std.testing.expect(!ctype.isascii(0xA0));
}
