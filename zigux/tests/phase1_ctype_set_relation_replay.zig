const std = @import("std");
const ctype = @import("ctype");

test "phase1 ctype replay keeps alnum and alpha partitions aligned" {
    var ch: u16 = 0;
    while (ch < 256) : (ch += 1) {
        const byte: u8 = @intCast(ch);

        try std.testing.expectEqual(
            ctype.isalpha(byte) or ctype.isdigit(byte),
            ctype.isalnum(byte),
        );
        try std.testing.expectEqual(
            ctype.isupper(byte) or ctype.islower(byte),
            ctype.isalpha(byte),
        );
    }
}

test "phase1 ctype replay keeps printable graph and punctuation relations aligned" {
    var ch: u16 = 0;
    while (ch < 256) : (ch += 1) {
        const byte: u8 = @intCast(ch);

        try std.testing.expectEqual(
            ctype.isgraph(byte) and !ctype.isalnum(byte),
            ctype.ispunct(byte),
        );
        if (ctype.isgraph(byte)) {
            try std.testing.expect(ctype.isprint(byte));
        }
    }

    try std.testing.expect(ctype.isprint(' '));
    try std.testing.expect(!ctype.isgraph(' '));
    try std.testing.expect(ctype.isprint(0xa0));
    try std.testing.expect(!ctype.isgraph(0xa0));
    try std.testing.expect(!ctype.isprint('\t'));
    try std.testing.expect(!ctype.isgraph('\t'));
}
