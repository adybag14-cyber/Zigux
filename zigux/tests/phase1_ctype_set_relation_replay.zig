const std = @import("std");
const ctype = @import("ctype");

test "phase1 ctype replay keeps helper set relations aligned across the full byte table" {
    var ch: u16 = 0;
    while (ch < 256) : (ch += 1) {
        const byte: u8 = @intCast(ch);

        try std.testing.expectEqual(
            ctype.isalpha(byte) or ctype.isdigit(byte),
            ctype.isalnum(byte),
        );
        try std.testing.expectEqual(
            ctype.isgraph(byte) and !ctype.isalnum(byte),
            ctype.ispunct(byte),
        );
        try std.testing.expectEqual(ctype.isgraph(byte) or byte == 0x20 or byte == 0xA0, ctype.isprint(byte));
        try std.testing.expect(!ctype.isgraph(byte) or ctype.isprint(byte));

        if (ctype.isspace(byte) and byte != 0x20 and byte != 0xA0) {
            try std.testing.expect(!ctype.isprint(byte));
            try std.testing.expect(!ctype.isgraph(byte));
        }
    }
}

test "phase1 ctype replay keeps printable-space and latin punctuation seams truthful" {
    try std.testing.expect(ctype.isspace(0x20));
    try std.testing.expect(ctype.isprint(0x20));
    try std.testing.expect(!ctype.isgraph(0x20));
    try std.testing.expect(!ctype.ispunct(0x20));

    try std.testing.expect(ctype.isspace(0xA0));
    try std.testing.expect(ctype.isprint(0xA0));
    try std.testing.expect(!ctype.isgraph(0xA0));
    try std.testing.expect(!ctype.ispunct(0xA0));

    try std.testing.expect(ctype.isspace('\t'));
    try std.testing.expect(!ctype.isprint('\t'));
    try std.testing.expect(!ctype.isgraph('\t'));
    try std.testing.expect(!ctype.ispunct('\t'));

    try std.testing.expect(ctype.isspace('\n'));
    try std.testing.expect(!ctype.isprint('\n'));
    try std.testing.expect(!ctype.isgraph('\n'));
    try std.testing.expect(!ctype.ispunct('\n'));

    try std.testing.expect(ctype.ispunct(0xD7));
    try std.testing.expect(ctype.isgraph(0xD7));
    try std.testing.expect(ctype.isprint(0xD7));
    try std.testing.expect(!ctype.isalpha(0xD7));

    try std.testing.expect(ctype.ispunct(0xF7));
    try std.testing.expect(ctype.isgraph(0xF7));
    try std.testing.expect(ctype.isprint(0xF7));
    try std.testing.expect(!ctype.isalpha(0xF7));

    try std.testing.expect(ctype.isalpha(0xDF));
    try std.testing.expect(ctype.islower(0xDF));
    try std.testing.expect(!ctype.ispunct(0xDF));
}
