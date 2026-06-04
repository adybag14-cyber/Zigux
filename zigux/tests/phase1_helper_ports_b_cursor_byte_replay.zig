const std = @import("std");
const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

test "argv split preserves leading punctuation and high byte token payloads" {
    const input = "  --flag  key=value  \x80tag  path\\\\literal  ";

    if (@hasDecl(argv_split, "ArgvSplitResult")) {
        var result = try argv_split.argvSplit(std.testing.allocator, input);
        defer result.deinit();

        try std.testing.expectEqual(@as(usize, 4), result.argc());
        try std.testing.expectEqualStrings("--flag", result.argv[0]);
        try std.testing.expectEqualStrings("key=value", result.argv[1]);
        try std.testing.expectEqualSlices(u8, &[_]u8{ 0x80, 't', 'a', 'g' }, result.argv[2]);
        try std.testing.expectEqualStrings("path\\\\literal", result.argv[3]);
    } else {
        const argv = try argv_split.argvSplit(std.testing.allocator, input);
        defer argv_split.argvFree(std.testing.allocator, argv);

        try std.testing.expectEqual(@as(usize, 4), argv.len);
        try std.testing.expectEqualStrings("--flag", argv[0]);
        try std.testing.expectEqualStrings("key=value", argv[1]);
        try std.testing.expectEqualSlices(u8, &[_]u8{ 0x80, 't', 'a', 'g' }, argv[2]);
        try std.testing.expectEqualStrings("path\\\\literal", argv[3]);
    }
}

test "cmdline nextArg keeps cursor progress across quoted and empty values" {
    if (!@hasDecl(cmdline, "nextArg")) {
        return;
    }

    const first = cmdline.nextArg("root=\"/dev/nvme0n1p1 quiet\" init=\"\" panic=-1") orelse
        return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("root", first.param);
    try std.testing.expectEqualStrings("/dev/nvme0n1p1 quiet", first.value.?);
    try std.testing.expectEqualStrings("init=\"\" panic=-1", first.remaining);

    const second = cmdline.nextArg(first.remaining) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("init", second.param);
    try std.testing.expectEqualStrings("", second.value.?);
    try std.testing.expectEqualStrings("panic=-1", second.remaining);

    const third = cmdline.nextArg(second.remaining) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("panic", third.param);
    try std.testing.expectEqualStrings("-1", third.value.?);
    try std.testing.expectEqualStrings("", third.remaining);
}

test "cmdline memparse and option list stop at byte boundaries" {
    const hex_tail = cmdline.memparse("0x2z rest");
    try std.testing.expectEqual(@as(u64, 2), hex_tail.value);
    try std.testing.expectEqualStrings("z rest", hex_tail.rest);

    const signed_suffix = cmdline.memparse("-1K\x80tail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -1024))), signed_suffix.value);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x80, 't', 'a', 'i', 'l' }, signed_suffix.rest);

    try std.testing.expect(cmdline.parseOptionStr("debug,\x80opt,quiet", "\x80opt"));
    try std.testing.expect(!cmdline.parseOptionStr("debug\x00\x80opt,quiet", "\x80opt"));
}

test "ctype high-byte masks stay table-driven and ascii conversion stays lossy" {
    try std.testing.expect(!ctype.isascii(0x80));
    try std.testing.expectEqual(@as(u8, 0), ctype.toascii(0x80));
    try std.testing.expectEqual(@as(u8, ctype._U), ctype.mask(0xC0));
    try std.testing.expectEqual(@as(u8, ctype._L), ctype.mask(0xE0));
    try std.testing.expect(ctype.isalpha(0xC0));
    try std.testing.expect(ctype.isalpha(0xE0));
    try std.testing.expect(!ctype.isxdigit(0xC0));
    try std.testing.expectEqual(@as(u8, 0xE0), ctype.tolower(0xC0));
    try std.testing.expectEqual(@as(u8, 0xC0), ctype.toupper(0xE0));
    try std.testing.expectEqual(@as(u8, 0x7F), ctype.toascii(0xFF));
}

test "hweight alternating lanes match popcount through aliases when present" {
    const alternating8: u32 = 0b1010_1010;
    const alternating16: u32 = 0xaaaa;
    const alternating32: u32 = 0xaaaa_5555;
    const alternating64: u64 = 0xaaaa_5555_ffff_0000;

    try std.testing.expectEqual(@as(u32, @popCount(@as(u8, @truncate(alternating8)))), hweight.swHweight8(alternating8));
    try std.testing.expectEqual(@as(u32, @popCount(@as(u16, @truncate(alternating16)))), hweight.swHweight16(alternating16));
    try std.testing.expectEqual(@as(u32, @popCount(alternating32)), hweight.swHweight32(alternating32));
    try std.testing.expectEqual(@as(u64, @popCount(alternating64)), hweight.swHweight64(alternating64));

    if (@hasDecl(hweight, "__sw_hweight8")) {
        try std.testing.expectEqual(hweight.swHweight8(alternating8), hweight.__sw_hweight8(alternating8));
        try std.testing.expectEqual(hweight.swHweight16(alternating16), hweight.__sw_hweight16(alternating16));
        try std.testing.expectEqual(hweight.swHweight32(alternating32), hweight.__sw_hweight32(alternating32));
        try std.testing.expectEqual(hweight.swHweight64(alternating64), hweight.__sw_hweight64(alternating64));
        try std.testing.expectEqual(hweight.hweightLong(@as(usize, 0xaaaa)), hweight.hweight_long(@as(usize, 0xaaaa)));
    }
}
