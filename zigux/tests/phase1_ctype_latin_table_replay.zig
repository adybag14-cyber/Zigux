const std = @import("std");
const ctype = @import("ctype");

fn expectMask(byte: u8, expected: u8) !void {
    try std.testing.expectEqual(expected, ctype.mask(byte));
    try std.testing.expectEqual(expected, ctype.table[byte]);
}

test "phase1 ctype replay keeps key ASCII mask windows aligned" {
    try expectMask(0, ctype._C);
    try expectMask('\t', ctype._S | ctype._C);
    try expectMask('\n', ctype._S | ctype._C);
    try expectMask(' ', ctype._S | ctype._SP);
    try expectMask('0', ctype._D);
    try expectMask('9', ctype._D);
    try expectMask('A', ctype._U | ctype._X);
    try expectMask('F', ctype._U | ctype._X);
    try expectMask('G', ctype._U);
    try expectMask('a', ctype._L | ctype._X);
    try expectMask('f', ctype._L | ctype._X);
    try expectMask('g', ctype._L);
    try expectMask('!', ctype._P);
    try expectMask(0x7f, ctype._C);
}

test "phase1 ctype replay keeps latin pairs and transforms aligned" {
    try std.testing.expect(ctype.isupper(0xC0));
    try std.testing.expect(ctype.islower(0xE0));
    try std.testing.expect(ctype.isupper(0xD8));
    try std.testing.expect(ctype.islower(0xF8));

    try std.testing.expectEqual(@as(u8, 0xE0), ctype.tolower(0xC0));
    try std.testing.expectEqual(@as(u8, 0xC0), ctype.toupper(0xE0));
    try std.testing.expectEqual(@as(u8, 0xF8), ctype.fastTolower(0xD8));

    try std.testing.expect(!ctype.isascii(0xC0));
    try std.testing.expectEqual(@as(u8, 0x40), ctype.toascii(0xC0));
    try std.testing.expectEqual(@as(u8, 0x78), ctype.toascii(0xF8));
}

test "phase1 ctype replay keeps representative predicate windows tied to the table" {
    const bytes = [_]u8{
        0,   '\t', '\n', ' ', '!', '/', '0', '7', '8',  '9',  ':',  '@',  'A',  'F',  'G',
        'Z', '[',  '`',  'a', 'f', 'g', 'z', '{', 0x7f, 0xA0, 0xC0, 0xD8, 0xE0, 0xF8, 0xFF,
    };

    for (bytes) |byte| {
        const byte_mask = ctype.table[byte];
        try std.testing.expectEqual((byte_mask & (ctype._U | ctype._L | ctype._D)) != 0, ctype.isalnum(byte));
        try std.testing.expectEqual((byte_mask & (ctype._U | ctype._L)) != 0, ctype.isalpha(byte));
        try std.testing.expectEqual((byte_mask & ctype._C) != 0, ctype.iscntrl(byte));
        try std.testing.expectEqual((byte_mask & (ctype._P | ctype._U | ctype._L | ctype._D)) != 0, ctype.isgraph(byte));
        try std.testing.expectEqual((byte_mask & ctype._L) != 0, ctype.islower(byte));
        try std.testing.expectEqual((byte_mask & (ctype._P | ctype._U | ctype._L | ctype._D | ctype._SP)) != 0, ctype.isprint(byte));
        try std.testing.expectEqual((byte_mask & ctype._P) != 0, ctype.ispunct(byte));
        try std.testing.expectEqual((byte_mask & ctype._S) != 0, ctype.isspace(byte));
        try std.testing.expectEqual((byte_mask & ctype._U) != 0, ctype.isupper(byte));
        try std.testing.expectEqual((byte_mask & (ctype._D | ctype._X)) != 0, ctype.isxdigit(byte));
        try std.testing.expectEqual(byte >= '0' and byte <= '9', ctype.isdigit(byte));
        try std.testing.expectEqual(byte >= '0' and byte <= '7', ctype.isodigit(byte));

        if (ctype.isupper(byte)) {
            try std.testing.expectEqual(@as(u8, byte | 0x20), ctype.tolower(byte));
            try std.testing.expectEqual(@as(u8, byte | 0x20), ctype.fastTolower(byte));
            try std.testing.expectEqual(byte, ctype.toupper(byte));
        } else if (ctype.islower(byte)) {
            try std.testing.expectEqual(@as(u8, byte - ('a' - 'A')), ctype.toupper(byte));
            try std.testing.expectEqual(byte, ctype.tolower(byte));
            try std.testing.expectEqual(byte, ctype.fastTolower(byte));
        } else {
            try std.testing.expectEqual(byte, ctype.fastTolower(byte));
        }
    }
}
