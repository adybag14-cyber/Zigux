const std = @import("std");
const ctype = @import("ctype");

fn expectCasePair(upper: u8, lower: u8) !void {
    try std.testing.expect(ctype.isupper(upper));
    try std.testing.expect(ctype.islower(lower));
    try std.testing.expect(ctype.isalpha(upper));
    try std.testing.expect(ctype.isalpha(lower));
    try std.testing.expect(ctype.isalnum(upper));
    try std.testing.expect(ctype.isalnum(lower));
    try std.testing.expectEqual(lower, ctype.tolower(upper));
    try std.testing.expectEqual(lower, ctype.fastTolower(upper));
    try std.testing.expectEqual(upper, ctype.toupper(lower));
    try std.testing.expectEqual(upper, ctype.toupper(upper));
    try std.testing.expectEqual(lower, ctype.tolower(lower));
    try std.testing.expectEqual(lower, ctype.fastTolower(lower));
}

test "phase 1 ctype ascii case endpoints stay bounded" {
    try expectCasePair('A', 'a');
    try expectCasePair('Z', 'z');

    for ([_]u8{ '@', '[', '`', '{' }) |ch| {
        try std.testing.expect(!ctype.isalpha(ch));
        try std.testing.expect(!ctype.isupper(ch));
        try std.testing.expect(!ctype.islower(ch));
        try std.testing.expectEqual(ch, ctype.tolower(ch));
        try std.testing.expectEqual(ch, ctype.toupper(ch));
        try std.testing.expectEqual(ch, ctype.fastTolower(ch));
    }
}

test "phase 1 ctype extended case pairs mirror table masks" {
    try expectCasePair(0xC0, 0xE0);
    try expectCasePair(0xD6, 0xF6);
    try expectCasePair(0xD8, 0xF8);
    try expectCasePair(0xDE, 0xFE);

    for ([_]u8{ 0xD7, 0xF7 }) |ch| {
        try std.testing.expect(!ctype.isalpha(ch));
        try std.testing.expect(ctype.ispunct(ch));
        try std.testing.expectEqual(ch, ctype.tolower(ch));
        try std.testing.expectEqual(ch, ctype.toupper(ch));
        try std.testing.expectEqual(ch, ctype.fastTolower(ch));
    }
}

test "phase 1 ctype case transforms leave non-case bytes unchanged" {
    for ([_]u8{ 0, ' ', '0', '9', '!', 0x7f, 0x80, 0xA0 }) |ch| {
        try std.testing.expect(!ctype.isupper(ch));
        try std.testing.expect(!ctype.islower(ch));
        try std.testing.expectEqual(ch, ctype.tolower(ch));
        try std.testing.expectEqual(ch, ctype.toupper(ch));
        try std.testing.expectEqual(ch, ctype.fastTolower(ch));
    }
}
