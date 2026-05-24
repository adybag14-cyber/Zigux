const std = @import("std");
const ctype = @import("ctype");

fn isAsciiWhitespace(byte: u8) bool {
    return switch (byte) {
        ' ', '\t', '\n', '\r', 0x0b, 0x0c => true,
        else => false,
    };
}

fn isAsciiHexDigit(byte: u8) bool {
    return (byte >= '0' and byte <= '9') or
        (byte >= 'A' and byte <= 'F') or
        (byte >= 'a' and byte <= 'f');
}

test "phase1 ctype replay keeps ascii class boundaries aligned" {
    var ch: u16 = 0;
    while (ch < 128) : (ch += 1) {
        const byte: u8 = @intCast(ch);

        try std.testing.expectEqual(isAsciiWhitespace(byte), ctype.isspace(byte));
        try std.testing.expectEqual(byte >= '0' and byte <= '9', ctype.isdigit(byte));
        try std.testing.expectEqual(byte >= '0' and byte <= '7', ctype.isodigit(byte));
        try std.testing.expectEqual(isAsciiHexDigit(byte), ctype.isxdigit(byte));
        try std.testing.expectEqual(byte >= 'A' and byte <= 'Z', ctype.isupper(byte));
        try std.testing.expectEqual(byte >= 'a' and byte <= 'z', ctype.islower(byte));
        try std.testing.expectEqual(
            (byte >= 'A' and byte <= 'Z') or (byte >= 'a' and byte <= 'z'),
            ctype.isalpha(byte),
        );
        try std.testing.expectEqual(
            (byte >= 'A' and byte <= 'Z') or
                (byte >= 'a' and byte <= 'z') or
                (byte >= '0' and byte <= '9'),
            ctype.isalnum(byte),
        );
        try std.testing.expectEqual(byte <= 0x7f, ctype.isascii(byte));
        try std.testing.expectEqual(@as(u8, byte & 0x7f), ctype.toascii(byte));
    }
}

test "phase1 ctype replay preserves printable and graph partitions" {
    try std.testing.expect(ctype.isspace(' '));
    try std.testing.expect(ctype.isprint(' '));
    try std.testing.expect(!ctype.isgraph(' '));
    try std.testing.expect(!ctype.ispunct(' '));

    for ([_]u8{ '\t', '\n', '\r', 0x0b, 0x0c }) |byte| {
        try std.testing.expect(ctype.isspace(byte));
        try std.testing.expect(ctype.iscntrl(byte));
        try std.testing.expect(!ctype.isprint(byte));
        try std.testing.expect(!ctype.isgraph(byte));
    }

    for ([_]u8{ '!', '#', '@', '[', '`', '{', '~' }) |byte| {
        try std.testing.expect(ctype.ispunct(byte));
        try std.testing.expect(ctype.isgraph(byte));
        try std.testing.expect(ctype.isprint(byte));
        try std.testing.expect(!ctype.isalnum(byte));
    }
}

test "phase1 ctype replay keeps case folding and latin table pairs aligned" {
    var upper: u8 = 'A';
    while (upper <= 'Z') : (upper += 1) {
        const lower = upper + ('a' - 'A');
        try std.testing.expectEqual(lower, ctype.tolower(upper));
        try std.testing.expectEqual(lower, ctype.fastTolower(upper));
        try std.testing.expectEqual(upper, ctype.toupper(lower));
    }

    var ch: u16 = 0;
    while (ch < 256) : (ch += 1) {
        const byte: u8 = @intCast(ch);
        if (!ctype.isupper(byte)) {
            try std.testing.expectEqual(byte, ctype.tolower(byte));
            try std.testing.expectEqual(byte, ctype.fastTolower(byte));
        }
        if (!ctype.islower(byte)) {
            try std.testing.expectEqual(byte, ctype.toupper(byte));
        }
    }

    try std.testing.expectEqual(@as(u8, 0xE0), ctype.tolower(0xC0));
    try std.testing.expectEqual(@as(u8, 0xC0), ctype.toupper(0xE0));
    try std.testing.expectEqual(@as(u8, 0xF8), ctype.fastTolower(0xD8));
    try std.testing.expect(ctype.isupper(0xC0));
    try std.testing.expect(ctype.islower(0xE0));
}
