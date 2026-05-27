const std = @import("std");
const ctype = @import("ctype");

fn expectFoldPair(upper: u8, lower: u8) !void {
    try std.testing.expect(ctype.isupper(upper));
    try std.testing.expect(ctype.islower(lower));
    try std.testing.expectEqual(lower, ctype.tolower(upper));
    try std.testing.expectEqual(lower, ctype.fastTolower(upper));
    try std.testing.expectEqual(upper, ctype.toupper(lower));
    try std.testing.expectEqual(upper, ctype.toupper(upper));
    try std.testing.expectEqual(lower, ctype.tolower(lower));
}

test "phase 1 ctype replay keeps casefold symmetry across ascii and latin windows" {
    const fold_pairs = [_][2]u8{
        .{ 'A', 'a' },
        .{ 'M', 'm' },
        .{ 'Z', 'z' },
        .{ 0xC0, 0xE0 },
        .{ 0xD6, 0xF6 },
        .{ 0xD8, 0xF8 },
    };

    for (fold_pairs) |pair| {
        try expectFoldPair(pair[0], pair[1]);
    }
}

test "phase 1 ctype replay keeps whitespace and control boundaries distinct" {
    const control_space = [_]u8{ '\t', '\n', '\x0b', '\x0c', '\r' };
    for (control_space) |byte| {
        try std.testing.expect(ctype.isspace(byte));
        try std.testing.expect(ctype.iscntrl(byte));
        try std.testing.expect(!ctype.isgraph(byte));
        try std.testing.expect(!ctype.isprint(byte));
        try std.testing.expectEqual(byte, ctype.fastTolower(byte));
        try std.testing.expectEqual(byte, ctype.tolower(byte));
        try std.testing.expectEqual(byte, ctype.toupper(byte));
    }

    try std.testing.expect(ctype.isspace(' '));
    try std.testing.expect(!ctype.iscntrl(' '));
    try std.testing.expect(ctype.isprint(' '));
    try std.testing.expect(!ctype.isgraph(' '));
}

test "phase 1 ctype replay keeps digits and punctuation stable under transforms" {
    const stable_bytes = [_]u8{ '0', '7', '9', '!', '@', '[', '`', '{', '~', 0xA0, 0xB7 };

    for (stable_bytes) |byte| {
        try std.testing.expectEqual(byte, ctype.tolower(byte));
        try std.testing.expectEqual(byte, ctype.toupper(byte));
        try std.testing.expectEqual(byte, ctype.fastTolower(byte));
    }

    try std.testing.expect(ctype.isdigit('7'));
    try std.testing.expect(ctype.isodigit('7'));
    try std.testing.expect(!ctype.isodigit('8'));
    try std.testing.expect(ctype.ispunct('!'));
    try std.testing.expect(ctype.ispunct('@'));
    try std.testing.expect(!ctype.ispunct('A'));
}
