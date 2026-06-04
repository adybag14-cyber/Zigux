const std = @import("std");

const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

fn splitLen(result: anytype) usize {
    const info = @typeInfo(@TypeOf(result));
    if (info == .pointer) {
        return result.len;
    }
    return result.argc();
}

fn splitAt(result: anytype, index: usize) []const u8 {
    const info = @typeInfo(@TypeOf(result));
    if (info == .pointer) {
        return result[index];
    }
    return result.argv[index];
}

fn freeSplit(allocator: std.mem.Allocator, result: anytype) void {
    const info = @typeInfo(@TypeOf(result.*));
    if (info == .pointer) {
        argv_split.argvFree(allocator, result.*);
        return;
    }
    result.deinit();
}

test "signed suffix tokens stay aligned across helper ports B" {
    const text = "root=-2K limit=+0x10K mask=0xf0f0";
    var split = try argv_split.argvSplit(std.testing.allocator, text);
    defer freeSplit(std.testing.allocator, &split);

    try std.testing.expectEqual(@as(usize, 3), splitLen(split));
    try std.testing.expectEqualStrings("root=-2K", splitAt(split, 0));
    try std.testing.expectEqualStrings("limit=+0x10K", splitAt(split, 1));
    try std.testing.expectEqualStrings("mask=0xf0f0", splitAt(split, 2));

    const negative = cmdline.memparse("-2Ktail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -2048))), negative.value);
    try std.testing.expectEqualStrings("tail", negative.rest);

    const positive_hex = cmdline.memparse("+0x10K,rest");
    try std.testing.expectEqual(@as(u64, 0x10 << 10), positive_hex.value);
    try std.testing.expectEqualStrings(",rest", positive_hex.rest);

    try std.testing.expect(ctype.ispunct('-'));
    try std.testing.expect(ctype.isdigit('2'));
    try std.testing.expect(ctype.isupper('K'));
    try std.testing.expect(ctype.isxdigit('f'));
    try std.testing.expectEqual(@as(u8, 'k'), ctype.tolower('K'));

    try std.testing.expectEqual(
        @as(u64, @intCast(@popCount(negative.value))),
        hweight.swHweight64(negative.value),
    );
    try std.testing.expectEqual(@as(u32, 8), hweight.swHweight16(0xf0f0));
}

test "nul-fenced option tokens and high bytes preserve helper boundaries" {
    const options = "quiet,root=-2K,debug=\"quoted\",mask=0xf0f0\x00ignored";

    try std.testing.expect(cmdline.parseOptionStr(options, "root=-2K"));
    try std.testing.expect(cmdline.parseOptionStr(options, "debug=\"quoted\""));
    try std.testing.expect(!cmdline.parseOptionStr(options, "debug"));
    try std.testing.expect(!cmdline.parseOptionStr(options, "ignored"));

    const parsed = cmdline.memparse("0xf0f0!");
    try std.testing.expectEqual(@as(u64, 0xf0f0), parsed.value);
    try std.testing.expectEqualStrings("!", parsed.rest);

    try std.testing.expect(ctype.isascii('!'));
    try std.testing.expect(!ctype.isascii(0x80));
    try std.testing.expectEqual(@as(u8, 0x2b), ctype.toascii(0xab));
    try std.testing.expect(!ctype.isodigit('8'));

    try std.testing.expectEqual(@as(u32, @intCast(@popCount(@as(u32, 0xf0f0)))), hweight.swHweight32(0xf0f0));
    try std.testing.expectEqual(@as(usize, @intCast(@popCount(@as(usize, 0xf0f0)))), hweight.hweightLong(0xf0f0));
}
