const std = @import("std");
const argv_split = @import("argv_split");

fn expectSplit(input: []const u8, expected: []const []const u8) !void {
    var split = try argv_split.argvSplit(std.testing.allocator, input);
    defer split.deinit();

    try std.testing.expectEqual(expected.len, split.argc());
    try std.testing.expectEqual(expected.len, split.argv.len);
    for (expected, 0..) |want, idx| {
        try std.testing.expectEqualStrings(want, split.argv[idx]);
    }
}

test "phase 1 argvSplit treats every ASCII whitespace byte as a separator" {
    const expected = [_][]const u8{ "alpha", "beta", "gamma", "delta", "epsilon", "zeta" };
    try expectSplit("alpha\tbeta\ngamma\x0bdelta\x0cepsilon\rzeta", &expected);
}

test "phase 1 argvSplit collapses leading trailing and repeated separator runs" {
    const expected = [_][]const u8{ "root=/dev/vda", "rw", "panic=-1" };
    try expectSplit(" \t\n root=/dev/vda \r\x0b  rw \x0c panic=-1 \n\t ", &expected);
}

test "phase 1 argvSplit keeps punctuation inside non-whitespace tokens" {
    const expected = [_][]const u8{ "console=ttyS0,115200", "quiet,debug", "init=/bin/sh" };
    try expectSplit("console=ttyS0,115200\tquiet,debug\ninit=/bin/sh", &expected);
}

test "phase 1 argv split free alias resets public result state" {
    var split = try argv_split.argv_split(std.testing.allocator, "alpha beta");

    try std.testing.expectEqual(@as(usize, 2), split.argc());
    try std.testing.expectEqualStrings("alpha", split.argv[0]);
    try std.testing.expectEqualStrings("beta", split.argv[1]);

    argv_split.argv_free(&split);

    try std.testing.expectEqual(@as(usize, 0), split.argc());
    try std.testing.expectEqual(@as(usize, 0), split.argv.len);
}
