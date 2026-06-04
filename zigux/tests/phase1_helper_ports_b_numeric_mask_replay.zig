const std = @import("std");

const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

fn argvLen(result: anytype) usize {
    return if (@TypeOf(result) == [][]u8) result.len else result.argc();
}

fn argvAt(result: anytype, index: usize) []const u8 {
    return if (@TypeOf(result) == [][]u8) result[index] else result.argv[index];
}

fn argvDeinit(result: anytype) void {
    if (@TypeOf(result.*) == [][]u8) {
        argv_split.argvFree(std.testing.allocator, result.*);
    } else {
        result.deinit();
    }
}

fn expectHweightAliases(value: u32) !void {
    try std.testing.expectEqual(@as(u32, @popCount(value)), hweight.swHweight32(value));
    if (@hasDecl(hweight, "__sw_hweight32")) {
        try std.testing.expectEqual(hweight.swHweight32(value), hweight.__sw_hweight32(value));
    }
}

test "numeric prefixes stay literal in argv while cmdline parses their values" {
    var split = try argv_split.argvSplit(std.testing.allocator, "size=0x10K mask=0xf0f0 mode=0755");
    defer argvDeinit(&split);

    try std.testing.expectEqual(@as(usize, 3), argvLen(split));
    try std.testing.expectEqualStrings("size=0x10K", argvAt(split, 0));
    try std.testing.expectEqualStrings("mask=0xf0f0", argvAt(split, 1));
    try std.testing.expectEqualStrings("mode=0755", argvAt(split, 2));

    if (@hasDecl(cmdline, "nextArg")) {
        const first = cmdline.next_arg("size=0x10K mask=0xf0f0 mode=0755") orelse return error.TestUnexpectedResult;
        try std.testing.expectEqualStrings("size", first.param);
        try std.testing.expectEqualStrings("0x10K", first.value.?);
        try std.testing.expectEqualStrings("mask=0xf0f0 mode=0755", first.remaining);
    }

    const size = cmdline.memparse("0x10K,tail");
    try std.testing.expectEqual(@as(u64, 0x10 << 10), size.value);
    try std.testing.expectEqualStrings(",tail", size.rest);

    const mask = cmdline.memparse("0xf0f0 mode");
    try std.testing.expectEqual(@as(u64, 0xf0f0), mask.value);
    try std.testing.expectEqualStrings(" mode", mask.rest);

    const mode = cmdline.memparse("0755;");
    try std.testing.expectEqual(@as(u64, 0o755), mode.value);
    try std.testing.expectEqualStrings(";", mode.rest);

    try std.testing.expect(!cmdline.parseOptionStr("size=0x10K,mask=0xf0f0,debug", "mask"));
    try std.testing.expect(cmdline.parse_option_str("size=0x10K,mask=0xf0f0,debug", "debug"));
}

test "ctype and hweight pin the same numeric mask bytes" {
    const hex_token = "0xFf";
    for (hex_token) |byte| {
        try std.testing.expect(ctype.isgraph(byte));
        try std.testing.expect(!ctype.isspace(byte));
    }

    try std.testing.expect(ctype.isdigit('0'));
    try std.testing.expect(ctype.isodigit('7'));
    try std.testing.expect(!ctype.isodigit('8'));
    try std.testing.expect(ctype.isxdigit('F'));
    try std.testing.expect(ctype.isxdigit('f'));
    try std.testing.expect(!ctype.isxdigit('x'));
    try std.testing.expect(ctype.isalpha('K'));
    try std.testing.expect(!ctype.isxdigit('K'));

    const parsed_mask: u32 = @intCast(cmdline.memparse("0xf0f0").value);
    try std.testing.expectEqual(@as(u32, 8), hweight.swHweight16(parsed_mask));
    if (@hasDecl(hweight, "__sw_hweight16")) {
        try std.testing.expectEqual(hweight.swHweight16(parsed_mask), hweight.__sw_hweight16(parsed_mask));
    }

    const parsed_size: u32 = @intCast(cmdline.memparse("0x10K").value);
    try expectHweightAliases(parsed_size);
    try std.testing.expectEqual(@as(u32, 1), hweight.swHweight32(parsed_size));

    const packed_digits = (@as(u32, '0') << 24) | (@as(u32, 'x') << 16) | (@as(u32, 'F') << 8) | @as(u32, 'f');
    try expectHweightAliases(packed_digits);
}
