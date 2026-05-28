const std = @import("std");
const ctype = @import("ctype");

fn expectSpaceControlPartition(byte: u8, expected: struct {
    isspace: bool,
    iscntrl: bool,
    isprint: bool,
    isgraph: bool,
}) !void {
    try std.testing.expectEqual(expected.isspace, ctype.isspace(byte));
    try std.testing.expectEqual(expected.iscntrl, ctype.iscntrl(byte));
    try std.testing.expectEqual(expected.isprint, ctype.isprint(byte));
    try std.testing.expectEqual(expected.isgraph, ctype.isgraph(byte));
}

test "ctype keeps representative space control partition anchors aligned" {
    try expectSpaceControlPartition(0x00, .{ .isspace = false, .iscntrl = true, .isprint = false, .isgraph = false });
    try expectSpaceControlPartition('\t', .{ .isspace = true, .iscntrl = true, .isprint = false, .isgraph = false });
    try expectSpaceControlPartition('\n', .{ .isspace = true, .iscntrl = true, .isprint = false, .isgraph = false });
    try expectSpaceControlPartition('\r', .{ .isspace = true, .iscntrl = true, .isprint = false, .isgraph = false });
    try expectSpaceControlPartition(' ', .{ .isspace = true, .iscntrl = false, .isprint = true, .isgraph = false });
    try expectSpaceControlPartition('!', .{ .isspace = false, .iscntrl = false, .isprint = true, .isgraph = true });
    try expectSpaceControlPartition(0x7f, .{ .isspace = false, .iscntrl = true, .isprint = false, .isgraph = false });
    try expectSpaceControlPartition(0xa0, .{ .isspace = true, .iscntrl = false, .isprint = true, .isgraph = false });
}

test "ctype ascii space control partition follows stable set relations" {
    var byte: u16 = 0;
    while (byte < 0x80) : (byte += 1) {
        const ch: u8 = @intCast(byte);
        const is_space = ctype.isspace(ch);
        const is_cntrl = ctype.iscntrl(ch);
        const is_print = ctype.isprint(ch);
        const is_graph = ctype.isgraph(ch);

        try std.testing.expectEqual(is_graph, is_print and !is_space);

        if (is_space) {
            if (ch == ' ') {
                try std.testing.expect(!is_cntrl);
                try std.testing.expect(is_print);
                try std.testing.expect(!is_graph);
            } else {
                try std.testing.expect(is_cntrl);
                try std.testing.expect(!is_print);
                try std.testing.expect(!is_graph);
            }
        }

        if (is_cntrl) {
            try std.testing.expect(!is_graph);
            try std.testing.expect(!ctype.ispunct(ch));
            try std.testing.expect(!ctype.isalpha(ch));
            try std.testing.expect(!ctype.isdigit(ch));
        }

        if (is_graph) {
            try std.testing.expect(!is_cntrl);
            try std.testing.expect(!is_space);
        }
    }
}
