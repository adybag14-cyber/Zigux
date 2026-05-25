const std = @import("std");
const ctype = @import("ctype");

test "phase1 ctype replay keeps direct ASCII and digit fences exact" {
    var ch: u16 = 0;
    while (ch < 256) : (ch += 1) {
        const byte: u8 = @intCast(ch);

        try std.testing.expectEqual(byte <= 0x7f, ctype.isascii(byte));
        try std.testing.expectEqual(@as(u8, byte & 0x7f), ctype.toascii(byte));
        try std.testing.expectEqual(byte >= '0' and byte <= '9', ctype.isdigit(byte));
        try std.testing.expectEqual(byte >= '0' and byte <= '7', ctype.isodigit(byte));
    }
}

test "phase1 ctype replay keeps case helpers closed over Linux table pairs" {
    try std.testing.expectEqual(@as(u8, 0xE0), ctype.tolower(0xC0));
    try std.testing.expectEqual(@as(u8, 0xC0), ctype.toupper(0xE0));
    try std.testing.expectEqual(@as(u8, 0xF8), ctype.fastTolower(0xD8));

    var ch: u16 = 0;
    while (ch < 256) : (ch += 1) {
        const byte: u8 = @intCast(ch);
        if (ctype.isupper(byte)) {
            try std.testing.expectEqual(byte, ctype.toupper(byte));
            try std.testing.expectEqual(ctype.tolower(ctype.toupper(byte)), ctype.tolower(byte));
            try std.testing.expectEqual(ctype.tolower(byte), ctype.fastTolower(byte));
        } else if (ctype.islower(byte)) {
            try std.testing.expectEqual(byte, ctype.tolower(byte));
            try std.testing.expectEqual(ctype.toupper(ctype.tolower(byte)), ctype.toupper(byte));
        } else {
            try std.testing.expectEqual(byte, ctype.fastTolower(byte));
        }
    }
}
