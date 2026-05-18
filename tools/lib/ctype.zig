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

test "fastTolower leaves non-uppercase punctuation unchanged" {
    try std.testing.expectEqual(@as(u8, '['), fastTolower('['));
    try std.testing.expectEqual(@as(u8, '\\'), fastTolower('\\'));
    try std.testing.expectEqual(@as(u8, '^'), fastTolower('^'));
}

test "ctype latin1 table anchors preserve case mapping" {
    const upper_a_grave: u8 = 0xC0;
    const lower_a_grave: u8 = 0xE0;

    try std.testing.expect(isupper(upper_a_grave));
    try std.testing.expect(islower(lower_a_grave));
    try std.testing.expectEqual(lower_a_grave, tolower(upper_a_grave));
    try std.testing.expectEqual(lower_a_grave, fastTolower(upper_a_grave));
    try std.testing.expectEqual(upper_a_grave, toupper(lower_a_grave));
}

test "ctype latin1 non-letter gaps stay unchanged" {
    const multiplication_sign: u8 = 0xD7;
    const division_sign: u8 = 0xF7;

    try std.testing.expect(!isalpha(multiplication_sign));
    try std.testing.expect(!isupper(multiplication_sign));
    try std.testing.expect(!islower(multiplication_sign));
    try std.testing.expectEqual(multiplication_sign, tolower(multiplication_sign));
    try std.testing.expectEqual(multiplication_sign, fastTolower(multiplication_sign));
    try std.testing.expectEqual(multiplication_sign, toupper(multiplication_sign));

    try std.testing.expect(!isalpha(division_sign));
    try std.testing.expect(!isupper(division_sign));
    try std.testing.expect(!islower(division_sign));
    try std.testing.expectEqual(division_sign, tolower(division_sign));
    try std.testing.expectEqual(division_sign, fastTolower(division_sign));
    try std.testing.expectEqual(division_sign, toupper(division_sign));
}

test "ctype latin1 non-breaking space keeps Linux whitespace flags" {
    const nbsp: u8 = 0xA0;

    try std.testing.expect(isspace(nbsp));
    try std.testing.expect(isprint(nbsp));
    try std.testing.expect(!isgraph(nbsp));
    try std.testing.expect(!ispunct(nbsp));
    try std.testing.expect(!isalpha(nbsp));
    try std.testing.expect(!isdigit(nbsp));
    try std.testing.expectEqual(nbsp, tolower(nbsp));
    try std.testing.expectEqual(nbsp, fastTolower(nbsp));
    try std.testing.expectEqual(nbsp, toupper(nbsp));
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
