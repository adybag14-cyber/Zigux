const std = @import("std");
const ctype = @import("ctype");

test "phase1 ctype replay keeps classification boundaries exact across control, space, print, and graph seams" {
    try std.testing.expect(ctype.iscntrl(0x1f));
    try std.testing.expect(!ctype.iscntrl(0x20));
    try std.testing.expect(ctype.isspace(0x20));
    try std.testing.expect(ctype.isprint(0x20));
    try std.testing.expect(!ctype.isgraph(0x20));

    try std.testing.expect(ctype.ispunct(0x21));
    try std.testing.expect(ctype.isgraph(0x21));
    try std.testing.expect(ctype.isprint(0x7e));
    try std.testing.expect(ctype.isgraph(0x7e));
    try std.testing.expect(ctype.iscntrl(0x7f));
    try std.testing.expect(!ctype.isprint(0x7f));
    try std.testing.expect(!ctype.isascii(0x80));
    try std.testing.expect(ctype.isspace(0xa0));
    try std.testing.expect(ctype.isprint(0xa0));
    try std.testing.expect(!ctype.isgraph(0xa0));
}

test "phase1 ctype replay keeps numeric and hexadecimal seams exact" {
    try std.testing.expect(ctype.isdigit('0'));
    try std.testing.expect(ctype.isodigit('0'));
    try std.testing.expect(ctype.isdigit('7'));
    try std.testing.expect(ctype.isodigit('7'));
    try std.testing.expect(ctype.isdigit('8'));
    try std.testing.expect(!ctype.isodigit('8'));
    try std.testing.expect(ctype.isxdigit('9'));

    try std.testing.expect(ctype.isxdigit('A'));
    try std.testing.expect(ctype.isxdigit('F'));
    try std.testing.expect(!ctype.isxdigit('G'));
    try std.testing.expect(ctype.isxdigit('a'));
    try std.testing.expect(ctype.isxdigit('f'));
    try std.testing.expect(!ctype.isxdigit('g'));
    try std.testing.expect(ctype.isalnum('f'));
    try std.testing.expect(!ctype.isalnum('-'));
}

test "phase1 ctype replay keeps ASCII trimming and extended-latin case folding aligned" {
    try std.testing.expectEqual(@as(u8, 0x7f), ctype.toascii(0xff));
    try std.testing.expectEqual(@as(u8, 0x00), ctype.toascii(0x80));
    try std.testing.expectEqual(@as(u8, 'a'), ctype.tolower('A'));
    try std.testing.expectEqual(@as(u8, 'Z'), ctype.toupper('z'));
    try std.testing.expectEqual(@as(u8, '!'), ctype.fastTolower('!'));

    try std.testing.expect(ctype.isupper(0xc0));
    try std.testing.expect(ctype.islower(0xe0));
    try std.testing.expectEqual(@as(u8, 0xe0), ctype.tolower(0xc0));
    try std.testing.expectEqual(@as(u8, 0xc0), ctype.toupper(0xe0));
    try std.testing.expectEqual(@as(u8, 0xf8), ctype.fastTolower(0xd8));
}
