const std = @import("std");
const ctype = @import("ctype");

const BoundaryCase = struct {
    byte: u8,
    mask: u8,
    isalnum: bool,
    isalpha: bool,
    iscntrl: bool,
    isgraph: bool,
    islower: bool,
    isprint: bool,
    ispunct: bool,
    isspace: bool,
    isupper: bool,
    isxdigit: bool,
    isascii: bool,
    toascii: u8,
    tolower: u8,
    toupper: u8,
    fast_tolower: u8,
    isodigit: bool,
};

fn expectCase(case: BoundaryCase) !void {
    try std.testing.expectEqual(case.mask, ctype.mask(case.byte));
    try std.testing.expectEqual(case.isalnum, ctype.isalnum(case.byte));
    try std.testing.expectEqual(case.isalpha, ctype.isalpha(case.byte));
    try std.testing.expectEqual(case.iscntrl, ctype.iscntrl(case.byte));
    try std.testing.expectEqual(case.isgraph, ctype.isgraph(case.byte));
    try std.testing.expectEqual(case.islower, ctype.islower(case.byte));
    try std.testing.expectEqual(case.isprint, ctype.isprint(case.byte));
    try std.testing.expectEqual(case.ispunct, ctype.ispunct(case.byte));
    try std.testing.expectEqual(case.isspace, ctype.isspace(case.byte));
    try std.testing.expectEqual(case.isupper, ctype.isupper(case.byte));
    try std.testing.expectEqual(case.isxdigit, ctype.isxdigit(case.byte));
    try std.testing.expectEqual(case.isascii, ctype.isascii(case.byte));
    try std.testing.expectEqual(case.toascii, ctype.toascii(case.byte));
    try std.testing.expectEqual(case.tolower, ctype.tolower(case.byte));
    try std.testing.expectEqual(case.toupper, ctype.toupper(case.byte));
    try std.testing.expectEqual(case.fast_tolower, ctype.fastTolower(case.byte));
    try std.testing.expectEqual(case.isodigit, ctype.isodigit(case.byte));
}

test "phase1 ctype boundary replay keeps representative table edges aligned" {
    const cases = [_]BoundaryCase{
        .{
            .byte = 0x00,
            .mask = ctype._C,
            .isalnum = false,
            .isalpha = false,
            .iscntrl = true,
            .isgraph = false,
            .islower = false,
            .isprint = false,
            .ispunct = false,
            .isspace = false,
            .isupper = false,
            .isxdigit = false,
            .isascii = true,
            .toascii = 0x00,
            .tolower = 0x00,
            .toupper = 0x00,
            .fast_tolower = 0x00,
            .isodigit = false,
        },
        .{
            .byte = '\t',
            .mask = ctype._C | ctype._S,
            .isalnum = false,
            .isalpha = false,
            .iscntrl = true,
            .isgraph = false,
            .islower = false,
            .isprint = false,
            .ispunct = false,
            .isspace = true,
            .isupper = false,
            .isxdigit = false,
            .isascii = true,
            .toascii = '\t',
            .tolower = '\t',
            .toupper = '\t',
            .fast_tolower = '\t',
            .isodigit = false,
        },
        .{
            .byte = ' ',
            .mask = ctype._S | ctype._SP,
            .isalnum = false,
            .isalpha = false,
            .iscntrl = false,
            .isgraph = false,
            .islower = false,
            .isprint = true,
            .ispunct = false,
            .isspace = true,
            .isupper = false,
            .isxdigit = false,
            .isascii = true,
            .toascii = ' ',
            .tolower = ' ',
            .toupper = ' ',
            .fast_tolower = ' ',
            .isodigit = false,
        },
        .{
            .byte = '0',
            .mask = ctype._D,
            .isalnum = true,
            .isalpha = false,
            .iscntrl = false,
            .isgraph = true,
            .islower = false,
            .isprint = true,
            .ispunct = false,
            .isspace = false,
            .isupper = false,
            .isxdigit = true,
            .isascii = true,
            .toascii = '0',
            .tolower = '0',
            .toupper = '0',
            .fast_tolower = '0',
            .isodigit = true,
        },
        .{
            .byte = '9',
            .mask = ctype._D,
            .isalnum = true,
            .isalpha = false,
            .iscntrl = false,
            .isgraph = true,
            .islower = false,
            .isprint = true,
            .ispunct = false,
            .isspace = false,
            .isupper = false,
            .isxdigit = true,
            .isascii = true,
            .toascii = '9',
            .tolower = '9',
            .toupper = '9',
            .fast_tolower = '9',
            .isodigit = false,
        },
        .{
            .byte = 'A',
            .mask = ctype._U | ctype._X,
            .isalnum = true,
            .isalpha = true,
            .iscntrl = false,
            .isgraph = true,
            .islower = false,
            .isprint = true,
            .ispunct = false,
            .isspace = false,
            .isupper = true,
            .isxdigit = true,
            .isascii = true,
            .toascii = 'A',
            .tolower = 'a',
            .toupper = 'A',
            .fast_tolower = 'a',
            .isodigit = false,
        },
        .{
            .byte = 'F',
            .mask = ctype._U | ctype._X,
            .isalnum = true,
            .isalpha = true,
            .iscntrl = false,
            .isgraph = true,
            .islower = false,
            .isprint = true,
            .ispunct = false,
            .isspace = false,
            .isupper = true,
            .isxdigit = true,
            .isascii = true,
            .toascii = 'F',
            .tolower = 'f',
            .toupper = 'F',
            .fast_tolower = 'f',
            .isodigit = false,
        },
        .{
            .byte = 'G',
            .mask = ctype._U,
            .isalnum = true,
            .isalpha = true,
            .iscntrl = false,
            .isgraph = true,
            .islower = false,
            .isprint = true,
            .ispunct = false,
            .isspace = false,
            .isupper = true,
            .isxdigit = false,
            .isascii = true,
            .toascii = 'G',
            .tolower = 'g',
            .toupper = 'G',
            .fast_tolower = 'g',
            .isodigit = false,
        },
        .{
            .byte = 'a',
            .mask = ctype._L | ctype._X,
            .isalnum = true,
            .isalpha = true,
            .iscntrl = false,
            .isgraph = true,
            .islower = true,
            .isprint = true,
            .ispunct = false,
            .isspace = false,
            .isupper = false,
            .isxdigit = true,
            .isascii = true,
            .toascii = 'a',
            .tolower = 'a',
            .toupper = 'A',
            .fast_tolower = 'a',
            .isodigit = false,
        },
        .{
            .byte = 'g',
            .mask = ctype._L,
            .isalnum = true,
            .isalpha = true,
            .iscntrl = false,
            .isgraph = true,
            .islower = true,
            .isprint = true,
            .ispunct = false,
            .isspace = false,
            .isupper = false,
            .isxdigit = false,
            .isascii = true,
            .toascii = 'g',
            .tolower = 'g',
            .toupper = 'G',
            .fast_tolower = 'g',
            .isodigit = false,
        },
        .{
            .byte = '~',
            .mask = ctype._P,
            .isalnum = false,
            .isalpha = false,
            .iscntrl = false,
            .isgraph = true,
            .islower = false,
            .isprint = true,
            .ispunct = true,
            .isspace = false,
            .isupper = false,
            .isxdigit = false,
            .isascii = true,
            .toascii = '~',
            .tolower = '~',
            .toupper = '~',
            .fast_tolower = '~',
            .isodigit = false,
        },
        .{
            .byte = 0x7f,
            .mask = ctype._C,
            .isalnum = false,
            .isalpha = false,
            .iscntrl = true,
            .isgraph = false,
            .islower = false,
            .isprint = false,
            .ispunct = false,
            .isspace = false,
            .isupper = false,
            .isxdigit = false,
            .isascii = true,
            .toascii = 0x7f,
            .tolower = 0x7f,
            .toupper = 0x7f,
            .fast_tolower = 0x7f,
            .isodigit = false,
        },
        .{
            .byte = 0x80,
            .mask = 0x00,
            .isalnum = false,
            .isalpha = false,
            .iscntrl = false,
            .isgraph = false,
            .islower = false,
            .isprint = false,
            .ispunct = false,
            .isspace = false,
            .isupper = false,
            .isxdigit = false,
            .isascii = false,
            .toascii = 0x00,
            .tolower = 0x80,
            .toupper = 0x80,
            .fast_tolower = 0x80,
            .isodigit = false,
        },
        .{
            .byte = 0xA0,
            .mask = ctype._S | ctype._SP,
            .isalnum = false,
            .isalpha = false,
            .iscntrl = false,
            .isgraph = false,
            .islower = false,
            .isprint = true,
            .ispunct = false,
            .isspace = true,
            .isupper = false,
            .isxdigit = false,
            .isascii = false,
            .toascii = 0x20,
            .tolower = 0xA0,
            .toupper = 0xA0,
            .fast_tolower = 0xA0,
            .isodigit = false,
        },
        .{
            .byte = 0xC0,
            .mask = ctype._U,
            .isalnum = true,
            .isalpha = true,
            .iscntrl = false,
            .isgraph = true,
            .islower = false,
            .isprint = true,
            .ispunct = false,
            .isspace = false,
            .isupper = true,
            .isxdigit = false,
            .isascii = false,
            .toascii = 0x40,
            .tolower = 0xE0,
            .toupper = 0xC0,
            .fast_tolower = 0xE0,
            .isodigit = false,
        },
        .{
            .byte = 0xD8,
            .mask = ctype._U,
            .isalnum = true,
            .isalpha = true,
            .iscntrl = false,
            .isgraph = true,
            .islower = false,
            .isprint = true,
            .ispunct = false,
            .isspace = false,
            .isupper = true,
            .isxdigit = false,
            .isascii = false,
            .toascii = 0x58,
            .tolower = 0xF8,
            .toupper = 0xD8,
            .fast_tolower = 0xF8,
            .isodigit = false,
        },
        .{
            .byte = 0xE0,
            .mask = ctype._L,
            .isalnum = true,
            .isalpha = true,
            .iscntrl = false,
            .isgraph = true,
            .islower = true,
            .isprint = true,
            .ispunct = false,
            .isspace = false,
            .isupper = false,
            .isxdigit = false,
            .isascii = false,
            .toascii = 0x60,
            .tolower = 0xE0,
            .toupper = 0xC0,
            .fast_tolower = 0xE0,
            .isodigit = false,
        },
        .{
            .byte = 0xFF,
            .mask = ctype._L,
            .isalnum = true,
            .isalpha = true,
            .iscntrl = false,
            .isgraph = true,
            .islower = true,
            .isprint = true,
            .ispunct = false,
            .isspace = false,
            .isupper = false,
            .isxdigit = false,
            .isascii = false,
            .toascii = 0x7f,
            .tolower = 0xFF,
            .toupper = 0xDF,
            .fast_tolower = 0xFF,
            .isodigit = false,
        },
    };

    for (cases) |case| {
        try expectCase(case);
    }
}

test "phase1 ctype extended latin pair replay stays symmetric" {
    const pairs = [_]struct { upper: u8, lower: u8 }{
        .{ .upper = 0xC0, .lower = 0xE0 },
        .{ .upper = 0xC5, .lower = 0xE5 },
        .{ .upper = 0xD6, .lower = 0xF6 },
        .{ .upper = 0xD8, .lower = 0xF8 },
        .{ .upper = 0xDE, .lower = 0xFE },
    };

    for (pairs) |pair| {
        try std.testing.expect(ctype.isupper(pair.upper));
        try std.testing.expect(ctype.islower(pair.lower));
        try std.testing.expectEqual(pair.lower, ctype.tolower(pair.upper));
        try std.testing.expectEqual(pair.lower, ctype.fastTolower(pair.upper));
        try std.testing.expectEqual(pair.upper, ctype.toupper(pair.lower));
        try std.testing.expectEqual(ctype.mask(pair.upper), ctype._U);
        try std.testing.expectEqual(ctype.mask(pair.lower), ctype._L);
    }
}

test "phase1 ctype replay keeps printable and graph boundaries distinct" {
    const graphic_ascii = [_]u8{ '!', '0', 'A', 'a', '~' };
    for (graphic_ascii) |byte| {
        try std.testing.expect(ctype.isgraph(byte));
        try std.testing.expect(ctype.isprint(byte));
        try std.testing.expect(!ctype.isspace(byte));
        try std.testing.expect(!ctype.iscntrl(byte));
    }

    const printable_only = [_]u8{ ' ', 0xA0 };
    for (printable_only) |byte| {
        try std.testing.expect(!ctype.isgraph(byte));
        try std.testing.expect(ctype.isprint(byte));
        try std.testing.expect(ctype.isspace(byte));
    }

    const control_only = [_]u8{ 0x00, '\n', 0x7F };
    for (control_only) |byte| {
        try std.testing.expect(ctype.iscntrl(byte));
        try std.testing.expect(!ctype.isprint(byte));
        try std.testing.expect(!ctype.isgraph(byte));
    }
}
