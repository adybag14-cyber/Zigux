const std = @import("std");
const ctype = @import("ctype");

test "ctype ascii fold pairs preserve case and classification" {
    for ('A'..'Z' + 1) |upper| {
        const lower: u8 = @intCast(upper + ('a' - 'A'));

        try std.testing.expect(ctype.isupper(@intCast(upper)));
        try std.testing.expect(!ctype.islower(@intCast(upper)));
        try std.testing.expect(ctype.isalpha(@intCast(upper)));
        try std.testing.expect(ctype.isalnum(@intCast(upper)));
        try std.testing.expectEqual(lower, ctype.tolower(@intCast(upper)));
        try std.testing.expectEqual(lower, ctype.fastTolower(@intCast(upper)));
        try std.testing.expectEqual(@as(u8, @intCast(upper)), ctype.toupper(@intCast(upper)));

        try std.testing.expect(!ctype.isupper(lower));
        try std.testing.expect(ctype.islower(lower));
        try std.testing.expect(ctype.isalpha(lower));
        try std.testing.expect(ctype.isalnum(lower));
        try std.testing.expectEqual(lower, ctype.tolower(lower));
        try std.testing.expectEqual(lower, ctype.fastTolower(lower));
        try std.testing.expectEqual(@as(u8, @intCast(upper)), ctype.toupper(lower));
    }
}

test "ctype ascii seams keep punctuation digits and spaces out of folds" {
    const punctuation = [_]u8{ '@', '[', '`', '{', '!', '~' };
    for (punctuation) |byte| {
        try std.testing.expect(ctype.ispunct(byte));
        try std.testing.expect(ctype.isgraph(byte));
        try std.testing.expect(ctype.isprint(byte));
        try std.testing.expect(!ctype.isalpha(byte));
        try std.testing.expect(!ctype.isalnum(byte));
        try std.testing.expectEqual(byte, ctype.tolower(byte));
        try std.testing.expectEqual(byte, ctype.fastTolower(byte));
        try std.testing.expectEqual(byte, ctype.toupper(byte));
    }

    for ('0'..'9' + 1) |digit| {
        const byte: u8 = @intCast(digit);
        try std.testing.expect(ctype.isdigit(byte));
        try std.testing.expect(ctype.isxdigit(byte));
        try std.testing.expect(ctype.isalnum(byte));
        try std.testing.expect(!ctype.isalpha(byte));
        try std.testing.expectEqual(byte, ctype.tolower(byte));
        try std.testing.expectEqual(byte, ctype.fastTolower(byte));
        try std.testing.expectEqual(byte, ctype.toupper(byte));
    }

    try std.testing.expect(ctype.isspace(' '));
    try std.testing.expect(ctype.isprint(' '));
    try std.testing.expect(!ctype.isgraph(' '));
    try std.testing.expectEqual(@as(u8, ' '), ctype.fastTolower(' '));

    try std.testing.expect(ctype.isspace('\t'));
    try std.testing.expect(ctype.iscntrl('\t'));
    try std.testing.expect(!ctype.isprint('\t'));
    try std.testing.expectEqual(@as(u8, '\t'), ctype.fastTolower('\t'));

    try std.testing.expect(ctype.iscntrl(0x7f));
    try std.testing.expect(!ctype.isprint(0x7f));
    try std.testing.expectEqual(@as(u8, 0x7f), ctype.fastTolower(0x7f));
}
