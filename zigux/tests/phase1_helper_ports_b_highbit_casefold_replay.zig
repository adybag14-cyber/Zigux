const std = @import("std");
const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

fn splitArgc(split: anytype) usize {
    if (@TypeOf(split) == [][]u8) {
        return split.len;
    }
    return split.argc();
}

fn splitArg(split: anytype, index: usize) []const u8 {
    if (@TypeOf(split) == [][]u8) {
        return split[index];
    }
    return split.argv[index];
}

test "helper ports B preserve high-bit token bytes across split and cmdline surfaces" {
    var split = try argv_split.argvSplit(std.testing.allocator, "boot=\xC0 fast=\xD8 lower=\xE0 tail");
    defer {
        if (@TypeOf(split) == [][]u8) {
            argv_split.argvFree(std.testing.allocator, split);
        } else {
            split.deinit();
        }
    }

    try std.testing.expectEqual(@as(usize, 4), splitArgc(split));
    try std.testing.expectEqualStrings("boot=\xC0", splitArg(split, 0));
    try std.testing.expectEqualStrings("fast=\xD8", splitArg(split, 1));
    try std.testing.expectEqualStrings("lower=\xE0", splitArg(split, 2));

    try std.testing.expect(cmdline.parseOptionStr("plain,high\xC0,tail", "high\xC0"));
    try std.testing.expect(!cmdline.parseOptionStr("plain,high\xC0,tail", "high"));

    const parsed = cmdline.memparse("15K\xC0rest");
    try std.testing.expectEqual(@as(u64, 15 << 10), parsed.value);
    try std.testing.expectEqualStrings("\xC0rest", parsed.rest);
}

test "helper ports B keep high-bit casefold masks and hweight counts aligned" {
    const upper_a_grave: u8 = 0xC0;
    const lower_a_grave: u8 = 0xE0;
    const upper_o_slash: u8 = 0xD8;
    const lower_o_slash: u8 = 0xF8;

    try std.testing.expect(ctype.isupper(upper_a_grave));
    try std.testing.expect(ctype.islower(lower_a_grave));
    try std.testing.expectEqual(lower_a_grave, ctype.tolower(upper_a_grave));
    try std.testing.expectEqual(upper_a_grave, ctype.toupper(lower_a_grave));
    try std.testing.expectEqual(lower_o_slash, ctype.fastTolower(upper_o_slash));

    try std.testing.expect(!ctype.isascii(upper_a_grave));
    try std.testing.expectEqual(@as(u8, 0x40), ctype.toascii(upper_a_grave));
    try std.testing.expectEqual(@as(u32, 2), hweight.swHweight8(upper_a_grave));
    try std.testing.expectEqual(@as(u32, 1), hweight.swHweight8(ctype.toascii(upper_a_grave)));

    const folded_pair: u32 = (@as(u32, ctype.tolower(upper_a_grave)) << 8) | ctype.toupper(lower_a_grave);
    try std.testing.expectEqual(@as(u32, 5), hweight.swHweight16(folded_pair));
    try std.testing.expectEqual(@popCount(folded_pair & 0xffff), hweight.swHweight16(folded_pair));
}
