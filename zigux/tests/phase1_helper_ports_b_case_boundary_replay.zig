const std = @import("std");

const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

fn argvSlice(result: anytype) [][]u8 {
    const Result = @TypeOf(result);
    return switch (@typeInfo(Result)) {
        .@"struct" => result.argv,
        else => result,
    };
}

fn argvLen(result: anytype) usize {
    const Result = @TypeOf(result);
    return switch (@typeInfo(Result)) {
        .@"struct" => result.argc(),
        else => result.len,
    };
}

fn freeArgv(allocator: std.mem.Allocator, result: anytype) void {
    const Ptr = @TypeOf(result);
    const Result = @typeInfo(Ptr).pointer.child;
    switch (@typeInfo(Result)) {
        .@"struct" => result.deinit(),
        else => argv_split.argvFree(allocator, result.*),
    }
}

fn hasNextArg() bool {
    return @hasDecl(cmdline, "nextArg");
}

fn hasHweightAliases() bool {
    return @hasDecl(hweight, "__sw_hweight8") and
        @hasDecl(hweight, "__sw_hweight16") and
        @hasDecl(hweight, "__sw_hweight32") and
        @hasDecl(hweight, "__sw_hweight64") and
        @hasDecl(hweight, "hweight_long");
}

fn expectCaseMask(ch: u8, expected_mask: u8) !void {
    try std.testing.expectEqual(expected_mask, ctype.mask(ch));
    try std.testing.expectEqual((expected_mask & (ctype._U | ctype._L | ctype._D)) != 0, ctype.isalnum(ch));
    try std.testing.expectEqual((expected_mask & (ctype._U | ctype._L)) != 0, ctype.isalpha(ch));
    try std.testing.expectEqual((expected_mask & ctype._U) != 0, ctype.isupper(ch));
    try std.testing.expectEqual((expected_mask & ctype._L) != 0, ctype.islower(ch));
    try std.testing.expectEqual((expected_mask & (ctype._D | ctype._X)) != 0, ctype.isxdigit(ch));
}

test "case boundary replay keeps helper ports aligned" {
    var split = try argv_split.argvSplit(std.testing.allocator, "  CPU=0xAaK  flag=MixedCase  tail=\\xC0\\xE0  ");
    defer freeArgv(std.testing.allocator, &split);
    const argv = argvSlice(split);

    try std.testing.expectEqual(@as(usize, 3), argvLen(split));
    try std.testing.expectEqualStrings("CPU=0xAaK", argv[0]);
    try std.testing.expectEqualStrings("flag=MixedCase", argv[1]);
    try std.testing.expectEqualStrings("tail=\\xC0\\xE0", argv[2]);

    try std.testing.expect(cmdline.parseOptionStr("CPU=0xAaK,flag,MixedCase", "flag"));
    try std.testing.expect(cmdline.parse_option_str("CPU=0xAaK,flag,MixedCase", "MixedCase"));
    try std.testing.expect(!cmdline.parseOptionStr("CPU=0xAaK,flag,MixedCase", "mixedcase"));

    if (comptime hasNextArg()) {
        const first = cmdline.nextArg("CPU=0xAaK flag=MixedCase") orelse return error.TestUnexpectedResult;
        try std.testing.expectEqualStrings("CPU", first.param);
        try std.testing.expectEqualStrings("0xAaK", first.value.?);
        try std.testing.expectEqualStrings("flag=MixedCase", first.remaining);
    }

    const parsed = cmdline.memparse(argv[0][4..]);
    try std.testing.expectEqual(@as(u64, 0xaa << 10), parsed.value);
    try std.testing.expectEqualStrings("", parsed.rest);

    try expectCaseMask('A', ctype._U | ctype._X);
    try expectCaseMask('a', ctype._L | ctype._X);
    try expectCaseMask('F', ctype._U | ctype._X);
    try expectCaseMask('f', ctype._L | ctype._X);
    try expectCaseMask('G', ctype._U);
    try expectCaseMask('g', ctype._L);
    try std.testing.expectEqual(@as(u8, 'a'), ctype.tolower('A'));
    try std.testing.expectEqual(@as(u8, 'A'), ctype.toupper('a'));
    try std.testing.expectEqual(@as(u8, 'z'), ctype.fastTolower('Z'));

    const ascii_case_mask: u32 = (@as(u32, 1) << ('A' - 'A')) |
        (@as(u32, 1) << ('F' - 'A')) |
        (@as(u32, 1) << ('G' - 'A')) |
        (@as(u32, 1) << ('Z' - 'A'));
    try std.testing.expectEqual(@as(u32, 4), hweight.swHweight32(ascii_case_mask));
    try std.testing.expectEqual(@as(u32, 3), hweight.swHweight8(ascii_case_mask));
    try std.testing.expectEqual(@as(u32, 3), hweight.swHweight16(ascii_case_mask));
    try std.testing.expectEqual(@as(usize, 4), hweight.hweightLong(ascii_case_mask));

    if (comptime hasHweightAliases()) {
        try std.testing.expectEqual(hweight.swHweight8(ascii_case_mask), hweight.__sw_hweight8(ascii_case_mask));
        try std.testing.expectEqual(hweight.swHweight16(ascii_case_mask), hweight.__sw_hweight16(ascii_case_mask));
        try std.testing.expectEqual(hweight.swHweight32(ascii_case_mask), hweight.__sw_hweight32(ascii_case_mask));
        try std.testing.expectEqual(hweight.hweightLong(ascii_case_mask), hweight.hweight_long(ascii_case_mask));
    }
}

test "latin case boundary and option fences stay exact" {
    try std.testing.expect(cmdline.parseOptionStr("LatinUpper,LatinLower\x00ignored", "LatinLower"));
    try std.testing.expect(!cmdline.parseOptionStr("LatinUpper,LatinLower\x00ignored", "ignored"));
    try std.testing.expect(!cmdline.parseOptionStr("LatinUpper,LatinLower", "latinlower"));

    try expectCaseMask(0xC0, ctype._U);
    try expectCaseMask(0xE0, ctype._L);
    try std.testing.expectEqual(@as(u8, 0xE0), ctype.tolower(0xC0));
    try std.testing.expectEqual(@as(u8, 0xC0), ctype.toupper(0xE0));
    try std.testing.expectEqual(@as(u8, 0xF8), ctype.fastTolower(0xD8));
    try std.testing.expect(!ctype.isascii(0xC0));
    try std.testing.expectEqual(@as(u8, 0x40), ctype.toascii(0xC0));

    const latin_mask: u64 = (@as(u64, 1) << 0) |
        (@as(u64, 1) << 1) |
        (@as(u64, 1) << 56) |
        (@as(u64, 1) << 63);
    try std.testing.expectEqual(@as(u64, 4), hweight.swHweight64(latin_mask));
    if (comptime hasHweightAliases()) {
        try std.testing.expectEqual(hweight.swHweight64(latin_mask), hweight.__sw_hweight64(latin_mask));
    }
}
