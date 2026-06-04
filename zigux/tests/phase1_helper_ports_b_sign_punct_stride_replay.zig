const std = @import("std");
const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

fn argvItems(result: anytype) [][]u8 {
    const Result = @TypeOf(result);
    switch (@typeInfo(Result)) {
        .@"struct" => {
            if (@hasField(Result, "argv")) {
                return result.argv;
            }
        },
        else => {},
    }
    return result;
}

fn freeArgs(allocator: std.mem.Allocator, result: anytype) void {
    var owned = result;
    const Result = @TypeOf(owned);
    switch (@typeInfo(Result)) {
        .@"struct" => {
            if (@hasDecl(argv_split, "argv_free")) {
                argv_split.argv_free(&owned);
            } else {
                owned.deinit();
            }
        },
        else => argv_split.argvFree(allocator, owned),
    }
}

fn sw8(value: u32) u32 {
    if (@hasDecl(hweight, "__sw_hweight8")) {
        return hweight.__sw_hweight8(value);
    }
    return hweight.swHweight8(value);
}

fn sw16(value: u32) u32 {
    if (@hasDecl(hweight, "__sw_hweight16")) {
        return hweight.__sw_hweight16(value);
    }
    return hweight.swHweight16(value);
}

fn sw32(value: u32) u32 {
    if (@hasDecl(hweight, "__sw_hweight32")) {
        return hweight.__sw_hweight32(value);
    }
    return hweight.swHweight32(value);
}

fn sw64(value: u64) u64 {
    if (@hasDecl(hweight, "__sw_hweight64")) {
        return hweight.__sw_hweight64(value);
    }
    return hweight.swHweight64(value);
}

fn hlong(value: usize) usize {
    if (@hasDecl(hweight, "hweight_long")) {
        return hweight.hweight_long(value);
    }
    return hweight.hweightLong(value);
}

test "sign prefixed punctuation survives argv and cmdline exact boundaries" {
    const result = if (@hasDecl(argv_split, "argv_split"))
        try argv_split.argv_split(std.testing.allocator, "  -flag  +0x2K,tail  --punct=!,?  ")
    else
        try argv_split.argvSplit(std.testing.allocator, "  -flag  +0x2K,tail  --punct=!,?  ");
    defer freeArgs(std.testing.allocator, result);
    const argv = argvItems(result);

    try std.testing.expectEqual(@as(usize, 3), argv.len);
    try std.testing.expectEqualStrings("-flag", argv[0]);
    try std.testing.expectEqualStrings("+0x2K,tail", argv[1]);
    try std.testing.expectEqualStrings("--punct=!,?", argv[2]);
    try std.testing.expect(ctype.ispunct(argv[0][0]));
    try std.testing.expect(ctype.ispunct(argv[1][0]));
    try std.testing.expect(ctype.isxdigit(argv[1][3]));
    try std.testing.expect(!ctype.isalnum(argv[2][0]));

    const parsed = cmdline.memparse(argv[1]);
    try std.testing.expectEqual(@as(u64, 2 << 10), parsed.value);
    try std.testing.expectEqualStrings(",tail", parsed.rest);
    try std.testing.expect(cmdline.parseOptionStr("-flag,+0x2K\x00,--punct", "+0x2K"));
    try std.testing.expect(!cmdline.parseOptionStr("-flag,+0x2K\x00,--punct", "--punct"));

    if (@hasDecl(cmdline, "nextArg")) {
        const next = cmdline.nextArg("--punct=!,? tail") orelse return error.TestUnexpectedResult;
        try std.testing.expectEqualStrings("--punct", next.param);
        try std.testing.expectEqualStrings("!,?", next.value.?);
        try std.testing.expectEqualStrings("tail", next.remaining);
    }
}

test "ctype projection feeds hweight stride masks without widening lanes" {
    const bytes = [_]u8{ '-', '+', '0', 'x', '2', 'K', ',', '!' };
    var punct_mask: u8 = 0;
    var xdigit_mask: u8 = 0;
    var ascii_projection_sum: u32 = 0;

    for (bytes, 0..) |byte, index| {
        if (ctype.ispunct(byte)) {
            punct_mask |= @as(u8, 1) << @intCast(index);
        }
        if (ctype.isxdigit(byte)) {
            xdigit_mask |= @as(u8, 1) << @intCast(index);
        }
        ascii_projection_sum += ctype.toascii(byte);
    }

    try std.testing.expectEqual(@as(u8, 0b1100_0011), punct_mask);
    try std.testing.expectEqual(@as(u8, 0b0001_0100), xdigit_mask);
    try std.testing.expectEqual(@as(u32, 4), sw8(punct_mask));
    try std.testing.expectEqual(@as(u32, 2), sw8(xdigit_mask));
    try std.testing.expectEqual(@as(u32, 6), sw16(@as(u32, punct_mask) | (@as(u32, xdigit_mask) << 8)));
    try std.testing.expectEqual(@as(u32, 4), sw32(0x0101_0101));
    try std.testing.expectEqual(@as(u64, 11), sw64(0x0101_0101_0101_0101 | @as(u64, punct_mask)));
    try std.testing.expectEqual(@popCount(@as(usize, 0x0101_0101)), hlong(0x0101_0101));
    try std.testing.expect(ascii_projection_sum > 0);
}
