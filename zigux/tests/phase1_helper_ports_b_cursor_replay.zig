const std = @import("std");

const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

fn expectNext(
    args: []const u8,
    param: []const u8,
    value: ?[]const u8,
    remaining: []const u8,
) !cmdline.NextArgResult {
    const parsed = cmdline.nextArg(args) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings(param, parsed.param);
    if (value) |expected| {
        try std.testing.expect(parsed.value != null);
        try std.testing.expectEqualStrings(expected, parsed.value.?);
    } else {
        try std.testing.expect(parsed.value == null);
    }
    try std.testing.expectEqualStrings(remaining, parsed.remaining);
    return parsed;
}

test "argvSplit and nextArg keep cursor progress aligned across whitespace" {
    const command = "\talpha  beta=two\n gamma\r\n";
    var split = try argv_split.argvSplit(std.testing.allocator, command);
    defer split.deinit();

    try std.testing.expectEqual(@as(usize, 3), split.argc());
    try std.testing.expectEqualStrings("alpha", split.argv[0]);
    try std.testing.expectEqualStrings("beta=two", split.argv[1]);
    try std.testing.expectEqualStrings("gamma", split.argv[2]);

    const first = try expectNext(command, "alpha", null, "beta=two\n gamma\r\n");
    const second = try expectNext(first.remaining, "beta", "two", "gamma\r\n");
    const third = try expectNext(second.remaining, "gamma", null, "");
    try std.testing.expect(cmdline.nextArg(third.remaining) == null);
}

test "cmdline helpers preserve cursor boundaries around quotes suffixes and NUL" {
    const parsed = try expectNext(
        " root=\"/dev/sda1 ro\"  console=ttyS0,115200\tnohlt",
        "root",
        "/dev/sda1 ro",
        "console=ttyS0,115200\tnohlt",
    );
    const console = try expectNext(parsed.remaining, "console", "ttyS0,115200", "nohlt");
    _ = try expectNext(console.remaining, "nohlt", null, "");

    try std.testing.expect(cmdline.parseOptionStr("quiet,,debug\x00panic", "debug"));
    try std.testing.expect(cmdline.parseOptionStr("quiet,,debug\x00panic", ""));
    try std.testing.expect(!cmdline.parseOptionStr("quiet,,debug\x00panic", "panic"));
    try std.testing.expectEqual(cmdline.parseOptionStr("debug,quiet", "quiet"), cmdline.parse_option_str("debug,quiet", "quiet"));

    const sized = cmdline.memparse("0x10K,tail");
    try std.testing.expectEqual(@as(u64, 0x10 << 10), sized.value);
    try std.testing.expectEqualStrings(",tail", sized.rest);

    const negative = cmdline.memparse("-1P!");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -(@as(i64, 1) << 50)))), negative.value);
    try std.testing.expectEqualStrings("!", negative.rest);
}

test "ctype masks and hweight counts agree on command delimiter bytes" {
    const cases = [_]struct {
        ch: u8,
        expected_mask: u8,
        print: bool,
        graph: bool,
    }{
        .{ .ch = ' ', .expected_mask = ctype._S | ctype._SP, .print = true, .graph = false },
        .{ .ch = '\t', .expected_mask = ctype._C | ctype._S, .print = false, .graph = false },
        .{ .ch = ',', .expected_mask = ctype._P, .print = true, .graph = true },
        .{ .ch = 0, .expected_mask = ctype._C, .print = false, .graph = false },
        .{ .ch = 'F', .expected_mask = ctype._U | ctype._X, .print = true, .graph = true },
        .{ .ch = 'f', .expected_mask = ctype._L | ctype._X, .print = true, .graph = true },
    };

    for (cases) |case| {
        try std.testing.expectEqual(case.expected_mask, ctype.mask(case.ch));
        try std.testing.expectEqual(case.print, ctype.isprint(case.ch));
        try std.testing.expectEqual(case.graph, ctype.isgraph(case.ch));
        try std.testing.expectEqual(@as(u32, @popCount(case.expected_mask)), hweight.swHweight8(case.expected_mask));
        try std.testing.expectEqual(hweight.swHweight8(case.expected_mask), hweight.__sw_hweight8(case.expected_mask));
    }

    try std.testing.expectEqual(@as(u8, 0x00), ctype.toascii(0x80));
    try std.testing.expectEqual(@as(u32, 1), hweight.swHweight16(ctype._SP));
    try std.testing.expectEqual(@as(u32, 3), hweight.swHweight32(ctype._U | ctype._D | ctype._X));
    try std.testing.expectEqual(@as(u64, 4), hweight.swHweight64(@as(u64, ctype._P | ctype._S | ctype._X | ctype._SP)));
    try std.testing.expectEqual(hweight.hweightLong(@as(usize, ctype._U | ctype._L)), hweight.hweight_long(@as(usize, ctype._U | ctype._L)));
}
