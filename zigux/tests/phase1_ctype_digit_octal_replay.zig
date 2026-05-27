const std = @import("std");
const ctype = @import("ctype");

test "ctype decimal and octal digits keep their direct contracts" {
    for ('0'..'9' + 1) |raw| {
        const byte: u8 = @intCast(raw);

        try std.testing.expect(ctype.isdigit(byte));
        try std.testing.expect(ctype.isalnum(byte));
        try std.testing.expect(ctype.isgraph(byte));
        try std.testing.expect(ctype.isprint(byte));
        try std.testing.expect(ctype.isxdigit(byte));
        try std.testing.expect(!ctype.isalpha(byte));
        try std.testing.expect(!ctype.isspace(byte));
        try std.testing.expect(!ctype.iscntrl(byte));
        try std.testing.expect(!ctype.ispunct(byte));
        try std.testing.expectEqual(byte <= '7', ctype.isodigit(byte));
        try std.testing.expectEqual(byte, ctype.tolower(byte));
        try std.testing.expectEqual(byte, ctype.fastTolower(byte));
        try std.testing.expectEqual(byte, ctype.toupper(byte));
    }
}

test "ctype hex seams keep neighbors out of digit and xdigit buckets" {
    const lower_hex = "abcdef";
    const upper_hex = "ABCDEF";
    for (lower_hex, upper_hex) |lower, upper| {
        try std.testing.expect(ctype.isxdigit(lower));
        try std.testing.expect(ctype.isxdigit(upper));
        try std.testing.expect(ctype.isalpha(lower));
        try std.testing.expect(ctype.isalpha(upper));
        try std.testing.expect(ctype.isalnum(lower));
        try std.testing.expect(ctype.isalnum(upper));
        try std.testing.expect(!ctype.isdigit(lower));
        try std.testing.expect(!ctype.isdigit(upper));
        try std.testing.expect(!ctype.isodigit(lower));
        try std.testing.expect(!ctype.isodigit(upper));
    }

    const before_zero: u8 = '/';
    const after_nine: u8 = ':';
    const before_upper_a: u8 = '@';
    const after_upper_f: u8 = 'G';
    const before_lower_a: u8 = '`';
    const after_lower_f: u8 = 'g';

    const non_digits = [_]u8{
        before_zero,
        after_nine,
        before_upper_a,
        after_upper_f,
        before_lower_a,
        after_lower_f,
    };

    for (non_digits) |byte| {
        try std.testing.expect(!ctype.isdigit(byte));
        try std.testing.expect(!ctype.isodigit(byte));
    }

    try std.testing.expect(ctype.ispunct(before_zero));
    try std.testing.expect(ctype.ispunct(after_nine));
    try std.testing.expect(ctype.ispunct(before_upper_a));
    try std.testing.expect(ctype.ispunct(before_lower_a));

    try std.testing.expect(!ctype.isxdigit(before_zero));
    try std.testing.expect(!ctype.isxdigit(after_nine));
    try std.testing.expect(!ctype.isxdigit(before_upper_a));
    try std.testing.expect(!ctype.isxdigit(after_upper_f));
    try std.testing.expect(!ctype.isxdigit(before_lower_a));
    try std.testing.expect(!ctype.isxdigit(after_lower_f));

    try std.testing.expect(ctype.isupper(after_upper_f));
    try std.testing.expect(!ctype.isupper(before_upper_a));
    try std.testing.expect(ctype.islower(after_lower_f));
    try std.testing.expect(!ctype.islower(before_lower_a));
}
