const std = @import("std");
const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

fn argvItems(result: anytype) [][]u8 {
    const Result = @typeInfo(@TypeOf(result)).pointer.child;
    return switch (@typeInfo(Result)) {
        .@"struct" => result.argv,
        else => result.*,
    };
}

fn argvCount(result: anytype) usize {
    const Result = @typeInfo(@TypeOf(result)).pointer.child;
    return switch (@typeInfo(Result)) {
        .@"struct" => result.argc(),
        else => result.*.len,
    };
}

fn argvDeinit(allocator: std.mem.Allocator, result: anytype) void {
    const Result = @typeInfo(@TypeOf(result)).pointer.child;
    switch (@typeInfo(Result)) {
        .@"struct" => result.deinit(),
        else => argv_split.argvFree(allocator, result.*),
    }
}

fn hweight8(value: u32) u32 {
    if (@hasDecl(hweight, "__sw_hweight8")) {
        return hweight.__sw_hweight8(value);
    }
    return hweight.swHweight8(value);
}

fn hweight16(value: u32) u32 {
    if (@hasDecl(hweight, "__sw_hweight16")) {
        return hweight.__sw_hweight16(value);
    }
    return hweight.swHweight16(value);
}

test "empty assignment tokens keep zero-length values visible across helper ports B" {
    var split = try argv_split.argvSplit(
        std.testing.allocator,
        "root= console=ttyS0 quiet=0 debug= 0",
    );
    defer argvDeinit(std.testing.allocator, &split);

    const argv = argvItems(&split);
    try std.testing.expectEqual(@as(usize, 5), argvCount(&split));
    try std.testing.expectEqualStrings("root=", argv[0]);
    try std.testing.expectEqualStrings("console=ttyS0", argv[1]);
    try std.testing.expectEqualStrings("quiet=0", argv[2]);
    try std.testing.expectEqualStrings("debug=", argv[3]);
    try std.testing.expectEqualStrings("0", argv[4]);

    try std.testing.expect(!cmdline.parseOptionStr("root=,debug=,quiet=0", "root"));
    try std.testing.expect(!cmdline.parse_option_str("root=,debug=,quiet=0", "debug"));
    try std.testing.expect(cmdline.parseOptionStr("root,debug,quiet=0", "root"));

    const zero = cmdline.memparse(argv[4]);
    try std.testing.expectEqual(@as(u64, 0), zero.value);
    try std.testing.expectEqualStrings("", zero.rest);

    var equals_mask: u16 = 0;
    var digit_mask: u16 = 0;
    for (argv, 0..) |arg, token_index| {
        for (arg) |ch| {
            if (ch == '=') {
                equals_mask |= @as(u16, 1) << @intCast(token_index);
                try std.testing.expect(ctype.ispunct(ch));
                try std.testing.expect(ctype.isgraph(ch));
            }
            if (ctype.isdigit(ch)) {
                digit_mask |= @as(u16, 1) << @intCast(token_index);
            }
        }
    }

    try std.testing.expectEqual(@as(u16, 0b0_1111), equals_mask);
    try std.testing.expectEqual(@as(u16, 0b1_0110), digit_mask);
    try std.testing.expectEqual(@as(u32, 4), hweight8(equals_mask));
    try std.testing.expectEqual(@as(u32, 3), hweight16(digit_mask));
}

test "current cmdline nextArg exposes empty values without hiding following tokens" {
    if (!@hasDecl(cmdline, "nextArg")) {
        return;
    }

    const first = cmdline.nextArg("root= debug= quiet") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("root", first.param);
    try std.testing.expectEqualStrings("", first.value.?);
    try std.testing.expectEqualStrings("debug= quiet", first.remaining);

    const second = cmdline.next_arg(first.remaining) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("debug", second.param);
    try std.testing.expectEqualStrings("", second.value.?);
    try std.testing.expectEqualStrings("quiet", second.remaining);

    const bare = cmdline.nextArg(second.remaining) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("quiet", bare.param);
    try std.testing.expect(bare.value == null);
    try std.testing.expectEqualStrings("", bare.remaining);
}
