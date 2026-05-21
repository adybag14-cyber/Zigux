const std = @import("std");
const ctype = @import("ctype");

const Case = struct {
    ch: u8,
    mask: u8,
    is_alnum: bool,
    is_alpha: bool,
    is_cntrl: bool,
    is_graph: bool,
    is_lower: bool,
    is_print: bool,
    is_punct: bool,
    is_space: bool,
    is_upper: bool,
    is_xdigit: bool,
    is_ascii: bool,
    to_ascii: u8,
    to_lower: u8,
    fast_to_lower: u8,
    to_upper: u8,
    is_odigit: bool,
};

fn expectCase(case: Case) !void {
    try std.testing.expectEqual(case.mask, ctype.mask(case.ch));
    try std.testing.expectEqual(case.is_alnum, ctype.isalnum(case.ch));
    try std.testing.expectEqual(case.is_alpha, ctype.isalpha(case.ch));
    try std.testing.expectEqual(case.is_cntrl, ctype.iscntrl(case.ch));
    try std.testing.expectEqual(case.is_graph, ctype.isgraph(case.ch));
    try std.testing.expectEqual(case.is_lower, ctype.islower(case.ch));
    try std.testing.expectEqual(case.is_print, ctype.isprint(case.ch));
    try std.testing.expectEqual(case.is_punct, ctype.ispunct(case.ch));
    try std.testing.expectEqual(case.is_space, ctype.isspace(case.ch));
    try std.testing.expectEqual(case.is_upper, ctype.isupper(case.ch));
    try std.testing.expectEqual(case.is_xdigit, ctype.isxdigit(case.ch));
    try std.testing.expectEqual(case.is_ascii, ctype.isascii(case.ch));
    try std.testing.expectEqual(case.to_ascii, ctype.toascii(case.ch));
    try std.testing.expectEqual(case.to_lower, ctype.tolower(case.ch));
    try std.testing.expectEqual(case.fast_to_lower, ctype.fastTolower(case.ch));
    try std.testing.expectEqual(case.to_upper, ctype.toupper(case.ch));
    try std.testing.expectEqual(case.is_odigit, ctype.isodigit(case.ch));
}

test "phase1 ctype replay imports the current helper surface" {
    try std.testing.expect(@hasDecl(ctype, "mask"));
    try std.testing.expect(@hasDecl(ctype, "fastTolower"));
    try std.testing.expect(@hasDecl(ctype, "isodigit"));
}

test "phase1 ctype replay keeps mixed ascii and latin cases aligned" {
    const cases = [_]Case{
        .{
            .ch = 'A',
            .mask = ctype._U | ctype._X,
            .is_alnum = true,
            .is_alpha = true,
            .is_cntrl = false,
            .is_graph = true,
            .is_lower = false,
            .is_print = true,
            .is_punct = false,
            .is_space = false,
            .is_upper = true,
            .is_xdigit = true,
            .is_ascii = true,
            .to_ascii = 'A',
            .to_lower = 'a',
            .fast_to_lower = 'a',
            .to_upper = 'A',
            .is_odigit = false,
        },
        .{
            .ch = 'g',
            .mask = ctype._L,
            .is_alnum = true,
            .is_alpha = true,
            .is_cntrl = false,
            .is_graph = true,
            .is_lower = true,
            .is_print = true,
            .is_punct = false,
            .is_space = false,
            .is_upper = false,
            .is_xdigit = false,
            .is_ascii = true,
            .to_ascii = 'g',
            .to_lower = 'g',
            .fast_to_lower = 'g',
            .to_upper = 'G',
            .is_odigit = false,
        },
        .{
            .ch = '7',
            .mask = ctype._D,
            .is_alnum = true,
            .is_alpha = false,
            .is_cntrl = false,
            .is_graph = true,
            .is_lower = false,
            .is_print = true,
            .is_punct = false,
            .is_space = false,
            .is_upper = false,
            .is_xdigit = true,
            .is_ascii = true,
            .to_ascii = '7',
            .to_lower = '7',
            .fast_to_lower = '7',
            .to_upper = '7',
            .is_odigit = true,
        },
        .{
            .ch = '!',
            .mask = ctype._P,
            .is_alnum = false,
            .is_alpha = false,
            .is_cntrl = false,
            .is_graph = true,
            .is_lower = false,
            .is_print = true,
            .is_punct = true,
            .is_space = false,
            .is_upper = false,
            .is_xdigit = false,
            .is_ascii = true,
            .to_ascii = '!',
            .to_lower = '!',
            .fast_to_lower = '!',
            .to_upper = '!',
            .is_odigit = false,
        },
        .{
            .ch = 0xD8,
            .mask = ctype._U,
            .is_alnum = true,
            .is_alpha = true,
            .is_cntrl = false,
            .is_graph = true,
            .is_lower = false,
            .is_print = true,
            .is_punct = false,
            .is_space = false,
            .is_upper = true,
            .is_xdigit = false,
            .is_ascii = false,
            .to_ascii = 0x58,
            .to_lower = 0xF8,
            .fast_to_lower = 0xF8,
            .to_upper = 0xD8,
            .is_odigit = false,
        },
        .{
            .ch = 0xF8,
            .mask = ctype._L,
            .is_alnum = true,
            .is_alpha = true,
            .is_cntrl = false,
            .is_graph = true,
            .is_lower = true,
            .is_print = true,
            .is_punct = false,
            .is_space = false,
            .is_upper = false,
            .is_xdigit = false,
            .is_ascii = false,
            .to_ascii = 0x78,
            .to_lower = 0xF8,
            .fast_to_lower = 0xF8,
            .to_upper = 0xD8,
            .is_odigit = false,
        },
    };

    for (cases) |case| {
        try expectCase(case);
    }
}

test "phase1 ctype replay keeps whitespace and control boundaries distinct" {
    const whitespace = [_]u8{ ' ', '\t', '\n', '\r', 0x0b, 0x0c };
    for (whitespace) |ch| {
        try std.testing.expect(ctype.isspace(ch));
        try std.testing.expect(ctype.isprint(ch) == (ch == ' '));
        try std.testing.expect(ctype.isgraph(ch) == false);
    }

    const controls = [_]u8{ 0x00, 0x1f, 0x7f };
    for (controls) |ch| {
        try std.testing.expect(ctype.iscntrl(ch));
        try std.testing.expect(!ctype.isprint(ch));
        try std.testing.expectEqual(ch, ctype.fastTolower(ch));
    }
}
