const std = @import("std");

pub const _U: u8 = 0x01;
pub const _L: u8 = 0x02;
pub const _D: u8 = 0x04;
pub const _C: u8 = 0x08;
pub const _P: u8 = 0x10;
pub const _S: u8 = 0x20;
pub const _X: u8 = 0x40;
pub const _SP: u8 = 0x80;

pub const table = [_]u8{
    0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x28, 0x28, 0x28, 0x28, 0x28, 0x08, 0x08,
    0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08,
    0xa0, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10,
    0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10,
    0x10, 0x41, 0x41, 0x41, 0x41, 0x41, 0x41, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01,
    0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x10, 0x10, 0x10, 0x10, 0x10,
    0x10, 0x42, 0x42, 0x42, 0x42, 0x42, 0x42, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02,
    0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x10, 0x10, 0x10, 0x10, 0x08,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0xa0, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10,
    0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10,
    0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01,
    0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x10, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x02,
    0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02,
    0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x10, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02,
};

pub fn mask(ch: u8) u8 {
    return table[ch];
}

pub fn isalnum(ch: u8) bool {
    return (mask(ch) & (_U | _L | _D)) != 0;
}

pub fn isalpha(ch: u8) bool {
    return (mask(ch) & (_U | _L)) != 0;
}

pub fn iscntrl(ch: u8) bool {
    return (mask(ch) & _C) != 0;
}

pub fn isgraph(ch: u8) bool {
    return (mask(ch) & (_P | _U | _L | _D)) != 0;
}

pub fn islower(ch: u8) bool {
    return (mask(ch) & _L) != 0;
}

pub fn isprint(ch: u8) bool {
    return (mask(ch) & (_P | _U | _L | _D | _SP)) != 0;
}

pub fn ispunct(ch: u8) bool {
    return (mask(ch) & _P) != 0;
}

pub fn isspace(ch: u8) bool {
    return (mask(ch) & _S) != 0;
}

pub fn isupper(ch: u8) bool {
    return (mask(ch) & _U) != 0;
}

pub fn isxdigit(ch: u8) bool {
    return (mask(ch) & (_D | _X)) != 0;
}

pub fn isascii(ch: u8) bool {
    return ch <= 0x7f;
}

pub fn toascii(ch: u8) u8 {
    return ch & 0x7f;
}

pub fn isdigit(ch: u8) bool {
    return ch >= '0' and ch <= '9';
}

pub fn tolower(ch: u8) u8 {
    return if (isupper(ch)) ch + ('a' - 'A') else ch;
}

pub fn toupper(ch: u8) u8 {
    return if (islower(ch)) ch - ('a' - 'A') else ch;
}

pub fn fastTolower(ch: u8) u8 {
    return if (isupper(ch)) (ch | 0x20) else ch;
}

pub fn isodigit(ch: u8) bool {
    return ch >= '0' and ch <= '7';
}

test "ctype classification follows Linux table expectations" {
    try std.testing.expect(isalpha('A'));
    try std.testing.expect(isalpha('z'));
    try std.testing.expect(isdigit('7'));
    try std.testing.expect(isspace(' '));
    try std.testing.expect(isspace('\t'));
    try std.testing.expect(isxdigit('f'));
    try std.testing.expect(ispunct('!'));
    try std.testing.expect(iscntrl(0));
    try std.testing.expect(isupper('Q'));
    try std.testing.expect(islower('q'));
}

test "ctype transforms and ascii helpers behave" {
    try std.testing.expectEqual(@as(u8, 'a'), tolower('A'));
    try std.testing.expectEqual(@as(u8, 'Z'), toupper('z'));
    try std.testing.expectEqual(@as(u8, 'm'), fastTolower('M'));
    try std.testing.expectEqual(@as(u8, '!'), fastTolower('!'));
    try std.testing.expect(isascii('x'));
    try std.testing.expectEqual(@as(u8, 0x3f), toascii(0xbf));
    try std.testing.expect(isodigit('7'));
    try std.testing.expect(!isodigit('8'));
}

test "ctype extended latin pairs and table-driven invariants stay aligned" {
    try std.testing.expect(isupper(0xC0));
    try std.testing.expect(islower(0xE0));
    try std.testing.expectEqual(@as(u8, 0xE0), tolower(0xC0));
    try std.testing.expectEqual(@as(u8, 0xC0), toupper(0xE0));
    try std.testing.expectEqual(@as(u8, 0xF8), fastTolower(0xD8));

    var ch: u16 = 0;
    while (ch < 256) : (ch += 1) {
        const byte: u8 = @intCast(ch);
        const byte_mask = table[byte];

        try std.testing.expectEqual(byte_mask, mask(byte));
        try std.testing.expectEqual((byte_mask & (_U | _L | _D)) != 0, isalnum(byte));
        try std.testing.expectEqual((byte_mask & (_U | _L)) != 0, isalpha(byte));
        try std.testing.expectEqual((byte_mask & _C) != 0, iscntrl(byte));
        try std.testing.expectEqual((byte_mask & (_P | _U | _L | _D)) != 0, isgraph(byte));
        try std.testing.expectEqual((byte_mask & _L) != 0, islower(byte));
        try std.testing.expectEqual((byte_mask & (_P | _U | _L | _D | _SP)) != 0, isprint(byte));
        try std.testing.expectEqual((byte_mask & _P) != 0, ispunct(byte));
        try std.testing.expectEqual((byte_mask & _S) != 0, isspace(byte));
        try std.testing.expectEqual((byte_mask & _U) != 0, isupper(byte));
        try std.testing.expectEqual((byte_mask & (_D | _X)) != 0, isxdigit(byte));
        try std.testing.expectEqual(byte <= 0x7f, isascii(byte));
        try std.testing.expectEqual(@as(u8, byte & 0x7f), toascii(byte));

        if (isupper(byte)) {
            try std.testing.expectEqual(@as(u8, byte | 0x20), tolower(byte));
            try std.testing.expectEqual(@as(u8, byte | 0x20), fastTolower(byte));
            try std.testing.expectEqual(byte, toupper(byte));
        } else if (islower(byte)) {
            try std.testing.expectEqual(@as(u8, byte - ('a' - 'A')), toupper(byte));
            try std.testing.expectEqual(byte, tolower(byte));
            try std.testing.expectEqual(byte, fastTolower(byte));
        } else {
            try std.testing.expectEqual(byte, fastTolower(byte));
        }
    }
}

test "ctype print graph and space boundaries stay table-driven" {
    const cases = [_]struct {
        byte: u8,
        print: bool,
        graph: bool,
        space: bool,
        punct: bool,
        cntrl: bool,
    }{
        .{ .byte = 0x00, .print = false, .graph = false, .space = false, .punct = false, .cntrl = true },
        .{ .byte = ' ', .print = true, .graph = false, .space = true, .punct = false, .cntrl = false },
        .{ .byte = '!', .print = true, .graph = true, .space = false, .punct = true, .cntrl = false },
        .{ .byte = 'A', .print = true, .graph = true, .space = false, .punct = false, .cntrl = false },
        .{ .byte = 0x7f, .print = false, .graph = false, .space = false, .punct = false, .cntrl = true },
        .{ .byte = 0x80, .print = false, .graph = false, .space = false, .punct = false, .cntrl = false },
        .{ .byte = 0xa0, .print = true, .graph = false, .space = true, .punct = false, .cntrl = false },
        .{ .byte = 0xa1, .print = true, .graph = true, .space = false, .punct = true, .cntrl = false },
        .{ .byte = 0xc0, .print = true, .graph = true, .space = false, .punct = false, .cntrl = false },
    };

    for (cases) |case| {
        const byte_mask = mask(case.byte);

        try std.testing.expectEqual((byte_mask & (_P | _U | _L | _D | _SP)) != 0, isprint(case.byte));
        try std.testing.expectEqual((byte_mask & (_P | _U | _L | _D)) != 0, isgraph(case.byte));
        try std.testing.expectEqual((byte_mask & _S) != 0, isspace(case.byte));
        try std.testing.expectEqual((byte_mask & _P) != 0, ispunct(case.byte));
        try std.testing.expectEqual((byte_mask & _C) != 0, iscntrl(case.byte));

        try std.testing.expectEqual(case.print, isprint(case.byte));
        try std.testing.expectEqual(case.graph, isgraph(case.byte));
        try std.testing.expectEqual(case.space, isspace(case.byte));
        try std.testing.expectEqual(case.punct, ispunct(case.byte));
        try std.testing.expectEqual(case.cntrl, iscntrl(case.byte));
    }
}
