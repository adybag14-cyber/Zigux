const std = @import("std");
const ctype = @import("ctype");

const BoundaryCase = struct {
    byte: u8,
    cntrl: bool,
    space: bool,
    print: bool,
    graph: bool,
    punct: bool,
    alpha: bool,
};

test "ctype print and graph boundaries stay aligned on representative seam bytes" {
    for ([_]BoundaryCase{
        .{ .byte = 0x00, .cntrl = true, .space = false, .print = false, .graph = false, .punct = false, .alpha = false },
        .{ .byte = 0x09, .cntrl = true, .space = true, .print = false, .graph = false, .punct = false, .alpha = false },
        .{ .byte = 0x1f, .cntrl = true, .space = false, .print = false, .graph = false, .punct = false, .alpha = false },
        .{ .byte = 0x20, .cntrl = false, .space = true, .print = true, .graph = false, .punct = false, .alpha = false },
        .{ .byte = 0x21, .cntrl = false, .space = false, .print = true, .graph = true, .punct = true, .alpha = false },
        .{ .byte = 0x30, .cntrl = false, .space = false, .print = true, .graph = true, .punct = false, .alpha = false },
        .{ .byte = 0x41, .cntrl = false, .space = false, .print = true, .graph = true, .punct = false, .alpha = true },
        .{ .byte = 0x7e, .cntrl = false, .space = false, .print = true, .graph = true, .punct = true, .alpha = false },
        .{ .byte = 0x7f, .cntrl = true, .space = false, .print = false, .graph = false, .punct = false, .alpha = false },
        .{ .byte = 0x9f, .cntrl = false, .space = false, .print = false, .graph = false, .punct = false, .alpha = false },
        .{ .byte = 0xa0, .cntrl = false, .space = true, .print = true, .graph = false, .punct = false, .alpha = false },
        .{ .byte = 0xa1, .cntrl = false, .space = false, .print = true, .graph = true, .punct = true, .alpha = false },
        .{ .byte = 0xad, .cntrl = false, .space = false, .print = true, .graph = true, .punct = true, .alpha = false },
        .{ .byte = 0xbf, .cntrl = false, .space = false, .print = true, .graph = true, .punct = true, .alpha = false },
        .{ .byte = 0xc0, .cntrl = false, .space = false, .print = true, .graph = true, .punct = false, .alpha = true },
        .{ .byte = 0xdf, .cntrl = false, .space = false, .print = true, .graph = true, .punct = false, .alpha = true },
        .{ .byte = 0xe0, .cntrl = false, .space = false, .print = true, .graph = true, .punct = false, .alpha = true },
        .{ .byte = 0xff, .cntrl = false, .space = false, .print = true, .graph = true, .punct = false, .alpha = true },
    }) |case| {
        try std.testing.expectEqual(case.cntrl, ctype.iscntrl(case.byte));
        try std.testing.expectEqual(case.space, ctype.isspace(case.byte));
        try std.testing.expectEqual(case.print, ctype.isprint(case.byte));
        try std.testing.expectEqual(case.graph, ctype.isgraph(case.byte));
        try std.testing.expectEqual(case.punct, ctype.ispunct(case.byte));
        try std.testing.expectEqual(case.alpha, ctype.isalpha(case.byte));
    }
}

test "ctype print and graph relations stay consistent across the full byte range" {
    var byte: u16 = 0;
    while (byte < 256) : (byte += 1) {
        const ch: u8 = @intCast(byte);

        try std.testing.expectEqual(ctype.isgraph(ch), ctype.isprint(ch) and !ctype.isspace(ch));

        if (ctype.isspace(ch) and !ctype.iscntrl(ch)) {
            try std.testing.expect(ctype.isprint(ch));
            try std.testing.expect(!ctype.isgraph(ch));
        }

        if (ctype.isgraph(ch)) {
            try std.testing.expect(ctype.isprint(ch));
            try std.testing.expect(!ctype.isspace(ch));
        }

        if (ctype.iscntrl(ch)) {
            try std.testing.expect(!ctype.isprint(ch));
            try std.testing.expect(!ctype.isgraph(ch));
            try std.testing.expect(!ctype.isalpha(ch));
        }
    }
}
