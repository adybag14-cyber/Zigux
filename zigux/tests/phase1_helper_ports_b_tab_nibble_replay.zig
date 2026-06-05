const std = @import("std");
const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

fn bitFor(index: usize) u64 {
    return @as(u64, 1) << @intCast(index);
}

fn xdigitMask(text: []const u8) u64 {
    var mask: u64 = 0;
    for (text, 0..) |ch, index| {
        if (ctype.isxdigit(ch)) {
            mask |= bitFor(index);
        }
    }
    return mask;
}

fn expectHweight64(value: u64, expected: u64) !void {
    try std.testing.expectEqual(expected, hweight.swHweight64(value));
    if (@hasDecl(hweight, "__sw_hweight64")) {
        try std.testing.expectEqual(expected, hweight.__sw_hweight64(value));
    }
}

fn expectHweight32(value: u32, expected: u32) !void {
    try std.testing.expectEqual(expected, hweight.swHweight32(value));
    if (@hasDecl(hweight, "__sw_hweight32")) {
        try std.testing.expectEqual(expected, hweight.__sw_hweight32(value));
    }
}

test "tab-delimited argv hex tokens drive ctype nibble masks and hweight counts" {
    const text = "\t0x0f\t0xF0\tA5-f\tplain";

    if (@hasDecl(argv_split, "ArgvSplitResult")) {
        var result = try argv_split.argvSplit(std.testing.allocator, text);
        defer result.deinit();

        try std.testing.expectEqual(@as(usize, 4), result.argc());
        try std.testing.expectEqualStrings("0x0f", result.argv[0]);
        try std.testing.expectEqualStrings("0xF0", result.argv[1]);
        try std.testing.expectEqualStrings("A5-f", result.argv[2]);
        try std.testing.expectEqualStrings("plain", result.argv[3]);

        try expectHweight64(xdigitMask(result.argv[0]), 3);
        try expectHweight64(xdigitMask(result.argv[1]), 3);
        try expectHweight64(xdigitMask(result.argv[2]), 3);
        try expectHweight64(xdigitMask(result.argv[3]), 1);
    } else {
        const argv = try argv_split.argvSplit(std.testing.allocator, text);
        defer argv_split.argvFree(std.testing.allocator, argv);

        try std.testing.expectEqual(@as(usize, 4), argv.len);
        try std.testing.expectEqualStrings("0x0f", argv[0]);
        try std.testing.expectEqualStrings("0xF0", argv[1]);
        try std.testing.expectEqualStrings("A5-f", argv[2]);
        try std.testing.expectEqualStrings("plain", argv[3]);

        try expectHweight64(xdigitMask(argv[0]), 3);
        try expectHweight64(xdigitMask(argv[1]), 3);
        try expectHweight64(xdigitMask(argv[2]), 3);
        try expectHweight64(xdigitMask(argv[3]), 1);
    }
}

test "cmdline tab rests and quoted nibble values stay aligned with ctype" {
    const lower = cmdline.memparse("0x0fK\ttrail");
    try std.testing.expectEqual(@as(u64, 15 << 10), lower.value);
    try std.testing.expectEqualStrings("\ttrail", lower.rest);

    const upper = cmdline.memparse("+0xF0M\ttrail");
    try std.testing.expectEqual(@as(u64, 0xF0 << 20), upper.value);
    try std.testing.expectEqualStrings("\ttrail", upper.rest);

    try std.testing.expect(ctype.isxdigit('f'));
    try std.testing.expect(ctype.isxdigit('F'));
    try std.testing.expect(!ctype.isxdigit('g'));
    try std.testing.expectEqual(@as(u8, 'f'), ctype.fastTolower('F'));

    if (@hasDecl(cmdline, "nextArg")) {
        const parsed = cmdline.nextArg("mask=\"0x0f AF\" next=done") orelse return error.TestUnexpectedResult;
        try std.testing.expectEqualStrings("mask", parsed.param);
        try std.testing.expectEqualStrings("0x0f AF", parsed.value.?);
        try std.testing.expectEqualStrings("next=done", parsed.remaining);
        try expectHweight64(xdigitMask(parsed.value.?), 6);
    }
}

test "nibble lane masks keep low-width hweight helpers honest" {
    const low_nibbles: u32 = 0x0000_00ff;
    const alternating_nibbles: u32 = 0x0000_aaaa;
    const high_noise_low_lane: u32 = 0xffff_000f;

    try expectHweight32(low_nibbles, 8);
    try expectHweight32(alternating_nibbles, 8);
    try std.testing.expectEqual(@as(u32, 4), hweight.swHweight8(high_noise_low_lane));
    try std.testing.expectEqual(@as(u32, 4), hweight.swHweight16(high_noise_low_lane));

    if (@hasDecl(hweight, "__sw_hweight8")) {
        try std.testing.expectEqual(@as(u32, 4), hweight.__sw_hweight8(high_noise_low_lane));
    }
    if (@hasDecl(hweight, "__sw_hweight16")) {
        try std.testing.expectEqual(@as(u32, 4), hweight.__sw_hweight16(high_noise_low_lane));
    }
    if (@hasDecl(hweight, "hweight_long")) {
        try std.testing.expectEqual(hweight.hweightLong(@as(usize, 0x0f0f)), hweight.hweight_long(@as(usize, 0x0f0f)));
    }
}
