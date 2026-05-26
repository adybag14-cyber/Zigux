const std = @import("std");
const ctype = @import("ctype");

test "phase1 ctype case normalization keeps ASCII non-letters stable" {
    var ch: u16 = 0;
    while (ch <= 0x7f) : (ch += 1) {
        const byte: u8 = @intCast(ch);

        try std.testing.expect(ctype.isascii(byte));
        try std.testing.expectEqual(byte, ctype.toascii(byte));

        if (ctype.isupper(byte)) {
            try std.testing.expectEqual(@as(u8, byte | 0x20), ctype.tolower(byte));
            try std.testing.expectEqual(@as(u8, byte | 0x20), ctype.fastTolower(byte));
        } else if (!ctype.islower(byte)) {
            try std.testing.expectEqual(byte, ctype.tolower(byte));
            try std.testing.expectEqual(byte, ctype.toupper(byte));
            try std.testing.expectEqual(byte, ctype.fastTolower(byte));
        }
    }
}

test "phase1 ctype case normalization is idempotent across the byte table" {
    var ch: u16 = 0;
    while (ch < 256) : (ch += 1) {
        const byte: u8 = @intCast(ch);
        const lowered = ctype.tolower(byte);
        const fast_lowered = ctype.fastTolower(byte);
        const uppered = ctype.toupper(byte);

        try std.testing.expectEqual(lowered, ctype.tolower(lowered));
        try std.testing.expectEqual(fast_lowered, ctype.fastTolower(fast_lowered));
        if (!ctype.islower(uppered)) {
            try std.testing.expectEqual(uppered, ctype.toupper(uppered));
        }

        if (ctype.isupper(byte)) {
            try std.testing.expectEqual(lowered, fast_lowered);
            try std.testing.expect(ctype.islower(lowered));
        } else {
            try std.testing.expectEqual(byte, fast_lowered);
        }

        if (ctype.isalpha(byte)) {
            try std.testing.expect(ctype.isalpha(lowered));
            if (ctype.isalpha(uppered)) {
                try std.testing.expect(ctype.isupper(uppered) or ctype.islower(uppered));
            }
        }
    }
}

test "phase1 ctype case normalization keeps latin-1 folds explicit" {
    try std.testing.expect(ctype.isupper(0xC0));
    try std.testing.expect(ctype.islower(0xE0));
    try std.testing.expectEqual(@as(u8, 0xE0), ctype.tolower(0xC0));
    try std.testing.expectEqual(@as(u8, 0xC0), ctype.toupper(0xE0));
    try std.testing.expectEqual(@as(u8, 0xF8), ctype.fastTolower(0xD8));

    try std.testing.expect(ctype.islower(0xDF));
    try std.testing.expectEqual(@as(u8, 0xBF), ctype.toupper(0xDF));
    try std.testing.expectEqual(@as(u8, 0xDF), ctype.tolower(0xDF));
    try std.testing.expectEqual(@as(u8, 0xDF), ctype.fastTolower(0xDF));

    try std.testing.expect(!ctype.isalpha(0xBF));
    try std.testing.expectEqual(@as(u8, 0xBF), ctype.tolower(0xBF));
    try std.testing.expectEqual(@as(u8, 0xBF), ctype.fastTolower(0xBF));
}
