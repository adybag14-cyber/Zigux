const std = @import("std");

const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

fn argvSlice(result: anytype) []const []const u8 {
    return switch (@typeInfo(@TypeOf(result))) {
        .@"struct" => result.argv,
        .pointer => result,
        else => @compileError("unsupported argvSplit result shape"),
    };
}

fn freeArgv(allocator: std.mem.Allocator, result: anytype) void {
    switch (@typeInfo(@TypeOf(result.*))) {
        .@"struct" => result.deinit(),
        .pointer => argv_split.argvFree(allocator, result.*),
        else => @compileError("unsupported argvSplit result shape"),
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

fn bitFor(ch: u8) u32 {
    return @as(u32, 1) << @as(u5, @truncate(ch));
}

test "helper ports B keep signed suffix tokens and case windows aligned" {
    var result = try argv_split.argvSplit(
        std.testing.allocator,
        "  -0x2Ktail +010Mmore  MIXED=AbCdEf  ",
    );
    defer freeArgv(std.testing.allocator, &result);
    const argv = argvSlice(result);

    try std.testing.expectEqual(@as(usize, 3), argv.len);
    try std.testing.expectEqualStrings("-0x2Ktail", argv[0]);
    try std.testing.expectEqualStrings("+010Mmore", argv[1]);
    try std.testing.expectEqualStrings("MIXED=AbCdEf", argv[2]);

    const negative = cmdline.memparse(argv[0]);
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -2048))), negative.value);
    try std.testing.expectEqualStrings("tail", negative.rest);

    const positive = cmdline.memparse(argv[1]);
    try std.testing.expectEqual(@as(u64, 8 << 20), positive.value);
    try std.testing.expectEqualStrings("more", positive.rest);

    const mixed = argv[2];
    try std.testing.expect(ctype.isupper(mixed[0]));
    try std.testing.expect(ctype.islower(mixed[7]));
    try std.testing.expectEqual(@as(u8, 'm'), ctype.tolower(mixed[0]));
    try std.testing.expectEqual(@as(u8, 'B'), ctype.toupper(mixed[7]));
    try std.testing.expectEqual(@as(u8, '='), ctype.fastTolower('='));

    const sign_suffix_window: u32 =
        bitFor('-') |
        bitFor('+') |
        bitFor('K') |
        bitFor('M');
    try std.testing.expectEqual(@as(u32, 2), hweight.swHweight32(sign_suffix_window));
    try std.testing.expectEqual(
        hweight8(sign_suffix_window & 0xff) + hweight16((sign_suffix_window >> 8) & 0xffff),
        hweight.swHweight32(sign_suffix_window),
    );
}

test "helper ports B preserve option fences around case-sensitive tokens" {
    var result = try argv_split.argvSplit(
        std.testing.allocator,
        "quiet,debug\x00NOHLT debug=1 debug",
    );
    defer freeArgv(std.testing.allocator, &result);
    const argv = argvSlice(result);

    try std.testing.expectEqual(@as(usize, 3), argv.len);
    try std.testing.expect(cmdline.parseOptionStr(argv[0], "debug"));
    try std.testing.expect(!cmdline.parseOptionStr(argv[0], "NOHLT"));
    try std.testing.expect(!cmdline.parseOptionStr(argv[1], "debug"));
    try std.testing.expectEqualStrings("debug", argv[2]);

    for (argv[2]) |ch| {
        try std.testing.expect(ctype.islower(ch));
        try std.testing.expect(ctype.isalpha(ch));
    }

    const debug_mask: u32 =
        bitFor('d') |
        bitFor('e') |
        bitFor('b') |
        bitFor('u') |
        bitFor('g');
    try std.testing.expectEqual(@as(u32, 5), hweight.swHweight32(debug_mask));
    try std.testing.expectEqual(@as(u32, 4), hweight8(debug_mask));
    try std.testing.expectEqual(@as(u32, 1), hweight16(debug_mask >> 8));
}
