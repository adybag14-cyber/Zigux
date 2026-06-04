const std = @import("std");

const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

fn argvItems(split: anytype) []const []u8 {
    return switch (@typeInfo(@TypeOf(split))) {
        .@"struct" => split.argv,
        .pointer => split,
        else => @compileError("unsupported argvSplit result type"),
    };
}

fn cleanupArgv(allocator: std.mem.Allocator, split: anytype) void {
    return switch (@typeInfo(@TypeOf(split.*))) {
        .@"struct" => split.deinit(),
        .pointer => argv_split.argvFree(allocator, split.*),
        else => @compileError("unsupported argvSplit result type"),
    };
}

test "argv whitespace splitting preserves cmdline comma and NUL delimiter semantics" {
    var split = try argv_split.argvSplit(
        std.testing.allocator,
        " alpha,,debug\tquiet,root=16K\x00tail  final ",
    );
    defer cleanupArgv(std.testing.allocator, &split);

    const args = argvItems(split);
    try std.testing.expectEqual(@as(usize, 3), args.len);
    try std.testing.expectEqualStrings("alpha,,debug", args[0]);
    try std.testing.expectEqualStrings("quiet,root=16K\x00tail", args[1]);
    try std.testing.expectEqualStrings("final", args[2]);

    try std.testing.expect(cmdline.parseOptionStr(args[0], "debug"));
    try std.testing.expect(cmdline.parseOptionStr(args[0], ""));
    try std.testing.expect(cmdline.parseOptionStr(args[0], "alpha"));
    try std.testing.expect(!cmdline.parseOptionStr(args[0], "alpha,"));

    try std.testing.expect(cmdline.parseOptionStr(args[1], "quiet"));
    try std.testing.expect(!cmdline.parseOptionStr(args[1], "root"));
    try std.testing.expect(!cmdline.parseOptionStr(args[1], "tail"));
}

test "memparse suffix tails align ctype digit gates with hweight counts" {
    const parsed = cmdline.memparse("0777K:tail");
    try std.testing.expectEqual(@as(u64, 0o777 << 10), parsed.value);
    try std.testing.expectEqualStrings(":tail", parsed.rest);

    try std.testing.expect(ctype.isodigit('7'));
    try std.testing.expect(!ctype.isodigit('8'));
    try std.testing.expect(ctype.isdigit('8'));
    try std.testing.expect(ctype.isxdigit('F'));
    try std.testing.expect(!ctype.isxdigit('G'));

    try std.testing.expectEqual(@as(u64, @popCount(parsed.value)), hweight.swHweight64(parsed.value));
    try std.testing.expectEqual(@as(u32, @popCount(@as(u32, 0o777))), hweight.swHweight16(0o777));
    try std.testing.expectEqual(
        @as(usize, @popCount(@as(usize, 0o777 << 10))),
        hweight.hweightLong(@as(usize, 0o777 << 10)),
    );
}
