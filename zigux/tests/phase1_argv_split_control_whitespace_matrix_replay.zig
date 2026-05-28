const std = @import("std");
const argv_split = @import("argv_split");

fn expectTokens(text: []const u8, expected: []const []const u8) !void {
    var result = try argv_split.argvSplit(std.testing.allocator, text);
    defer result.deinit();

    try std.testing.expectEqual(expected.len, result.argc());
    for (expected, 0..) |token, idx| {
        try std.testing.expectEqualSlices(u8, token, result.argv[idx]);
    }
}

test "argvSplit collapses the full ASCII control-whitespace set between tokens" {
    try expectTokens(
        "alpha beta\tgamma\ndelta\r" ++ [_]u8{0x0b} ++ "epsilon" ++ [_]u8{0x0c} ++ "zeta",
        &.{
            "alpha",
            "beta",
            "gamma",
            "delta",
            "epsilon",
            "zeta",
        },
    );
}

test "argvSplit only splits on ASCII whitespace across the C0 and DEL range" {
    var byte: u8 = 1;
    while (true) : (byte +%= 1) {
        const sample = [_]u8{ 'x', byte, 'y' };
        var result = try argv_split.argvSplit(std.testing.allocator, &sample);
        defer result.deinit();

        if (std.ascii.isWhitespace(byte)) {
            try std.testing.expectEqual(@as(usize, 2), result.argc());
            try std.testing.expectEqualSlices(u8, "x", result.argv[0]);
            try std.testing.expectEqualSlices(u8, "y", result.argv[1]);
        } else {
            const expected = [_]u8{ 'x', byte, 'y' };
            try std.testing.expectEqual(@as(usize, 1), result.argc());
            try std.testing.expectEqualSlices(u8, &expected, result.argv[0]);
        }

        if (byte == 0x7f) {
            break;
        }
    }
}

test "argvSplit preserves non-whitespace control bytes inside surrounding tokens" {
    const text = [_]u8{
        'l',  'e',  'f',  't',
        0x01, 0x07, 0x1b, 0x1f,
        0x7f, 'r',  'i',  'g',
        'h',  't',  ' ',  't',
        'a',  'i',  'l',
    };
    const expected = [_]u8{
        'l',  'e',  'f',  't',
        0x01, 0x07, 0x1b, 0x1f,
        0x7f, 'r',  'i',  'g',
        'h',  't',
    };

    var result = try argv_split.argvSplit(std.testing.allocator, &text);
    defer result.deinit();

    try std.testing.expectEqual(@as(usize, 2), result.argc());
    try std.testing.expectEqualSlices(u8, &expected, result.argv[0]);
    try std.testing.expectEqualSlices(u8, "tail", result.argv[1]);
}
