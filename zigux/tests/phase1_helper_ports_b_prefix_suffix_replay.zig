const std = @import("std");

const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

fn freeLegacyArgv(allocator: std.mem.Allocator, argv: [][]u8) void {
    for (argv) |arg| {
        allocator.free(arg);
    }
    allocator.free(argv);
}

test "helper ports B preserve prefix and suffix boundaries" {
    if (comptime @hasDecl(argv_split, "ArgvSplitResult")) {
        var split = try argv_split.argvSplit(std.testing.allocator, "\n\talpha  beta\tgamma  ");
        defer split.deinit();

        try std.testing.expectEqual(@as(usize, 3), split.argc());
        try std.testing.expectEqualStrings("alpha", split.argv[0]);
        try std.testing.expectEqualStrings("beta", split.argv[1]);
        try std.testing.expectEqualStrings("gamma", split.argv[2]);
    } else {
        const split = try argv_split.argvSplit(std.testing.allocator, "\n\talpha  beta\tgamma  ");
        defer freeLegacyArgv(std.testing.allocator, split);

        try std.testing.expectEqual(@as(usize, 3), split.len);
        try std.testing.expectEqualStrings("alpha", split[0]);
        try std.testing.expectEqualStrings("beta", split[1]);
        try std.testing.expectEqualStrings("gamma", split[2]);
    }

    try std.testing.expect(cmdline.parseOptionStr("early,debug\x00late,quiet", "debug"));
    try std.testing.expect(!cmdline.parseOptionStr("early,debug\x00late,quiet", "quiet"));
    try std.testing.expect(!cmdline.parseOptionStr("early,debuggable,late", "debug"));

    const decimal = cmdline.memparse("15Ksuffix");
    try std.testing.expectEqual(@as(u64, 15 << 10), decimal.value);
    try std.testing.expectEqualStrings("suffix", decimal.rest);

    const hex = cmdline.memparse("0x10G-tail");
    try std.testing.expectEqual(@as(u64, 0x10 << 30), hex.value);
    try std.testing.expectEqualStrings("-tail", hex.rest);

    const negative = cmdline.memparse("-1Kdone");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -1024))), negative.value);
    try std.testing.expectEqualStrings("done", negative.rest);

    if (comptime @hasDecl(cmdline, "nextArg")) {
        const parsed = cmdline.nextArg("  boot=fast  tail=safe   ") orelse return error.TestUnexpectedResult;
        try std.testing.expectEqualStrings("boot", parsed.param);
        try std.testing.expectEqualStrings("fast", parsed.value.?);
        try std.testing.expectEqualStrings("tail=safe   ", parsed.remaining);
    }
}

test "helper ports B keep byte lane and ascii projection boundaries aligned" {
    try std.testing.expect(ctype.iscntrl(0));
    try std.testing.expect(ctype.iscntrl(0x1f));
    try std.testing.expect(!ctype.isprint(0x7f));
    try std.testing.expect(!ctype.isascii(0x80));
    try std.testing.expectEqual(@as(u8, 0), ctype.toascii(0x80));
    try std.testing.expectEqual(@as(u8, ' '), ctype.toascii(0xa0));
    try std.testing.expect(ctype.isspace(0xa0));
    try std.testing.expect(ctype.isprint(0xa0));
    try std.testing.expect(!ctype.isascii(0xff));
    try std.testing.expectEqual(@as(u8, 0x7f), ctype.toascii(0xff));

    const byte_window: u32 = 0xffff_ff7e;
    try std.testing.expectEqual(@as(u32, @popCount(@as(u8, 0x7e))), hweight.swHweight8(byte_window));
    if (comptime @hasDecl(hweight, "__sw_hweight8")) {
        try std.testing.expectEqual(hweight.swHweight8(byte_window), hweight.__sw_hweight8(byte_window));
    }

    const half_window: u32 = 0xffff_7e81;
    try std.testing.expectEqual(@as(u32, @popCount(@as(u16, 0x7e81))), hweight.swHweight16(half_window));
    if (comptime @hasDecl(hweight, "__sw_hweight16")) {
        try std.testing.expectEqual(hweight.swHweight16(half_window), hweight.__sw_hweight16(half_window));
    }

    const word_window: u32 = 0x8000_0001;
    try std.testing.expectEqual(@as(u32, 2), hweight.swHweight32(word_window));
    if (comptime @hasDecl(hweight, "__sw_hweight32")) {
        try std.testing.expectEqual(hweight.swHweight32(word_window), hweight.__sw_hweight32(word_window));
    }

    const wide_window: u64 = 0x8000_0000_0000_0001;
    try std.testing.expectEqual(@as(u64, 2), hweight.swHweight64(wide_window));
    if (comptime @hasDecl(hweight, "__sw_hweight64")) {
        try std.testing.expectEqual(hweight.swHweight64(wide_window), hweight.__sw_hweight64(wide_window));
    }

    const long_value: usize = if (@sizeOf(usize) == 4) 0x8000_0001 else 0x8000_0000_0000_0001;
    try std.testing.expectEqual(@as(usize, 2), hweight.hweightLong(long_value));
    if (comptime @hasDecl(hweight, "hweight_long")) {
        try std.testing.expectEqual(hweight.hweightLong(long_value), hweight.hweight_long(long_value));
    }
}
