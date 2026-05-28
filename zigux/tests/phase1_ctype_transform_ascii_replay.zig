const std = @import("std");
const ctype = @import("ctype");

test "ascii transforms leave non-letter sentinels unchanged" {
    const sentinels = [_]u8{ 0x00, 0x1f, ' ', '!', '/', '0', '9', ':', '@', '[', '`', '{', 0x7f };

    for (sentinels) |byte| {
        try std.testing.expectEqual(byte, ctype.tolower(byte));
        try std.testing.expectEqual(byte, ctype.toupper(byte));
        try std.testing.expectEqual(byte, ctype.fastTolower(byte));
        try std.testing.expectEqual(byte <= 0x7f, ctype.isascii(byte));
        try std.testing.expectEqual(byte, ctype.toascii(byte));
    }
}

test "letter transforms preserve case boundaries" {
    const upper_pairs = [_]struct { upper: u8, lower: u8 }{
        .{ .upper = 'A', .lower = 'a' },
        .{ .upper = 'F', .lower = 'f' },
        .{ .upper = 'Z', .lower = 'z' },
    };

    for (upper_pairs) |pair| {
        try std.testing.expect(ctype.isupper(pair.upper));
        try std.testing.expect(ctype.islower(pair.lower));
        try std.testing.expectEqual(pair.lower, ctype.tolower(pair.upper));
        try std.testing.expectEqual(pair.lower, ctype.fastTolower(pair.upper));
        try std.testing.expectEqual(pair.upper, ctype.toupper(pair.lower));
        try std.testing.expectEqual(pair.upper, ctype.toupper(pair.upper));
        try std.testing.expectEqual(pair.lower, ctype.tolower(pair.lower));
        try std.testing.expectEqual(pair.lower, ctype.fastTolower(pair.lower));
    }
}

test "latin1 ascii projection and transforms stay table driven" {
    const cases = [_]struct { byte: u8, projected: u8, lowered: u8, uppered: u8 }{
        .{ .byte = 0x80, .projected = 0x00, .lowered = 0x80, .uppered = 0x80 },
        .{ .byte = 0xA0, .projected = 0x20, .lowered = 0xA0, .uppered = 0xA0 },
        .{ .byte = 0xC0, .projected = 0x40, .lowered = 0xE0, .uppered = 0xC0 },
        .{ .byte = 0xD6, .projected = 0x56, .lowered = 0xF6, .uppered = 0xD6 },
        .{ .byte = 0xD7, .projected = 0x57, .lowered = 0xD7, .uppered = 0xD7 },
        .{ .byte = 0xD8, .projected = 0x58, .lowered = 0xF8, .uppered = 0xD8 },
        .{ .byte = 0xE0, .projected = 0x60, .lowered = 0xE0, .uppered = 0xC0 },
        .{ .byte = 0xF6, .projected = 0x76, .lowered = 0xF6, .uppered = 0xD6 },
        .{ .byte = 0xF7, .projected = 0x77, .lowered = 0xF7, .uppered = 0xF7 },
        .{ .byte = 0xF8, .projected = 0x78, .lowered = 0xF8, .uppered = 0xD8 },
        .{ .byte = 0xFF, .projected = 0x7f, .lowered = 0xFF, .uppered = 0xDF },
    };

    for (cases) |case| {
        try std.testing.expect(!ctype.isascii(case.byte));
        try std.testing.expectEqual(case.projected, ctype.toascii(case.byte));
        try std.testing.expectEqual(case.lowered, ctype.tolower(case.byte));
        try std.testing.expectEqual(case.lowered, ctype.fastTolower(case.byte));
        try std.testing.expectEqual(case.uppered, ctype.toupper(case.byte));
    }
}
