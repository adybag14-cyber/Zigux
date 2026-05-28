const std = @import("std");
const ctype = @import("ctype");

const ProjectionCase = struct {
    source: u8,
    projected: u8,
    is_space: bool,
    is_digit: bool,
    is_upper: bool,
    is_lower: bool,
    is_punct: bool,
    is_cntrl: bool,
};

fn expectProjection(case: ProjectionCase) !void {
    const projected = ctype.toascii(case.source);
    try std.testing.expectEqual(case.projected, projected);
    try std.testing.expect(ctype.isascii(projected));
    try std.testing.expectEqual(projected, case.source & 0x7f);
    try std.testing.expectEqual(case.is_space, ctype.isspace(projected));
    try std.testing.expectEqual(case.is_digit, ctype.isdigit(projected));
    try std.testing.expectEqual(case.is_upper, ctype.isupper(projected));
    try std.testing.expectEqual(case.is_lower, ctype.islower(projected));
    try std.testing.expectEqual(case.is_punct, ctype.ispunct(projected));
    try std.testing.expectEqual(case.is_cntrl, ctype.iscntrl(projected));
}

test "toascii projects representative high bytes onto the expected ASCII surface" {
    const cases = [_]ProjectionCase{
        .{ .source = 0x80, .projected = 0x00, .is_space = false, .is_digit = false, .is_upper = false, .is_lower = false, .is_punct = false, .is_cntrl = true },
        .{ .source = 0x89, .projected = '\t', .is_space = true, .is_digit = false, .is_upper = false, .is_lower = false, .is_punct = false, .is_cntrl = true },
        .{ .source = 0xA0, .projected = ' ', .is_space = true, .is_digit = false, .is_upper = false, .is_lower = false, .is_punct = false, .is_cntrl = false },
        .{ .source = 0xA1, .projected = '!', .is_space = false, .is_digit = false, .is_upper = false, .is_lower = false, .is_punct = true, .is_cntrl = false },
        .{ .source = 0xB1, .projected = '1', .is_space = false, .is_digit = true, .is_upper = false, .is_lower = false, .is_punct = false, .is_cntrl = false },
        .{ .source = 0xC1, .projected = 'A', .is_space = false, .is_digit = false, .is_upper = true, .is_lower = false, .is_punct = false, .is_cntrl = false },
        .{ .source = 0xDA, .projected = 'Z', .is_space = false, .is_digit = false, .is_upper = true, .is_lower = false, .is_punct = false, .is_cntrl = false },
        .{ .source = 0xE1, .projected = 'a', .is_space = false, .is_digit = false, .is_upper = false, .is_lower = true, .is_punct = false, .is_cntrl = false },
        .{ .source = 0xFA, .projected = 'z', .is_space = false, .is_digit = false, .is_upper = false, .is_lower = true, .is_punct = false, .is_cntrl = false },
        .{ .source = 0xFF, .projected = 0x7f, .is_space = false, .is_digit = false, .is_upper = false, .is_lower = false, .is_punct = false, .is_cntrl = true },
    };

    for (cases) |case| {
        try expectProjection(case);
    }
}

test "toascii projection stays idempotent and classification-stable across the full byte range" {
    var value: u16 = 0;
    while (value < 256) : (value += 1) {
        const byte: u8 = @intCast(value);
        const projected = ctype.toascii(byte);
        const ascii_twin: u8 = byte & 0x7f;

        try std.testing.expectEqual(ascii_twin, projected);
        try std.testing.expectEqual(projected, ctype.toascii(projected));
        try std.testing.expect(ctype.isascii(projected));

        try std.testing.expectEqual(ctype.mask(ascii_twin), ctype.mask(projected));
        try std.testing.expectEqual(ctype.isalnum(ascii_twin), ctype.isalnum(projected));
        try std.testing.expectEqual(ctype.isalpha(ascii_twin), ctype.isalpha(projected));
        try std.testing.expectEqual(ctype.iscntrl(ascii_twin), ctype.iscntrl(projected));
        try std.testing.expectEqual(ctype.isdigit(ascii_twin), ctype.isdigit(projected));
        try std.testing.expectEqual(ctype.isgraph(ascii_twin), ctype.isgraph(projected));
        try std.testing.expectEqual(ctype.islower(ascii_twin), ctype.islower(projected));
        try std.testing.expectEqual(ctype.isodigit(ascii_twin), ctype.isodigit(projected));
        try std.testing.expectEqual(ctype.isprint(ascii_twin), ctype.isprint(projected));
        try std.testing.expectEqual(ctype.ispunct(ascii_twin), ctype.ispunct(projected));
        try std.testing.expectEqual(ctype.isspace(ascii_twin), ctype.isspace(projected));
        try std.testing.expectEqual(ctype.isupper(ascii_twin), ctype.isupper(projected));
        try std.testing.expectEqual(ctype.isxdigit(ascii_twin), ctype.isxdigit(projected));
        try std.testing.expectEqual(ctype.tolower(ascii_twin), ctype.tolower(projected));
        try std.testing.expectEqual(ctype.toupper(ascii_twin), ctype.toupper(projected));
        try std.testing.expectEqual(ctype.fastTolower(ascii_twin), ctype.fastTolower(projected));
    }
}
