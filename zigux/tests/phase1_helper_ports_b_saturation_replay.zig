const std = @import("std");

const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

const SplitReturn = @typeInfo(@TypeOf(argv_split.argvSplit)).@"fn".return_type.?;
const SplitPayload = @typeInfo(SplitReturn).error_union.payload;
const split_has_result_struct = @hasField(SplitPayload, "argv");

fn splitArgv(allocator: std.mem.Allocator, text: []const u8) !SplitPayload {
    return try argv_split.argvSplit(allocator, text);
}

fn argvItems(result: *SplitPayload) [][]u8 {
    return if (split_has_result_struct) result.argv else result.*;
}

fn freeArgv(allocator: std.mem.Allocator, result: *SplitPayload) void {
    if (split_has_result_struct) {
        argv_split.argvFree(result);
    } else {
        argv_split.argvFree(allocator, result.*);
    }
}

fn expectSaturatingValue(token: []const u8, expected: u64, expected_rest: []const u8) !void {
    const parsed = cmdline.memparse(token);
    try std.testing.expectEqual(expected, parsed.value);
    try std.testing.expectEqualStrings(expected_rest, parsed.rest);
}

fn expectAllDigits(token: []const u8) !void {
    for (token) |byte| {
        try std.testing.expect(ctype.isdigit(byte));
        try std.testing.expect(ctype.isxdigit(byte));
        try std.testing.expect(ctype.isalnum(byte));
    }
}

test "oversized argv numeric tokens saturate through cmdline and hweight" {
    var result = try splitArgv(
        std.testing.allocator,
        "9223372036854775808 -9223372036854775809 18446744073709551616K",
    );
    defer freeArgv(std.testing.allocator, &result);
    const argv = argvItems(&result);

    try std.testing.expectEqual(@as(usize, 3), argv.len);
    try expectAllDigits(argv[0]);
    try std.testing.expect(ctype.ispunct(argv[1][0]));
    try expectAllDigits(argv[1][1..]);
    try expectAllDigits(argv[2][0 .. argv[2].len - 1]);
    try std.testing.expect(ctype.isupper(argv[2][argv[2].len - 1]));
    try std.testing.expect(!ctype.isxdigit(argv[2][argv[2].len - 1]));

    try expectSaturatingValue(argv[0], @as(u64, std.math.maxInt(i64)), "");
    try expectSaturatingValue(argv[1], @as(u64, 0x8000_0000_0000_0000), "");
    try expectSaturatingValue(argv[2], std.math.maxInt(u64), "");

    try std.testing.expectEqual(@as(u64, 63), hweight.swHweight64(cmdline.memparse(argv[0]).value));
    try std.testing.expectEqual(@as(u64, 1), hweight.swHweight64(cmdline.memparse(argv[1]).value));
    try std.testing.expectEqual(@as(u64, 64), hweight.swHweight64(cmdline.memparse(argv[2]).value));
}

test "suffix overflow consumes only the suffix and leaves the tail intact" {
    var result = try splitArgv(
        std.testing.allocator,
        "16777216Ttail 0xffffffffffffffffP,after",
    );
    defer freeArgv(std.testing.allocator, &result);
    const argv = argvItems(&result);

    try std.testing.expectEqual(@as(usize, 2), argv.len);
    try std.testing.expect(ctype.isupper(argv[0][8]));
    try std.testing.expect(ctype.islower(argv[0][9]));
    try std.testing.expect(ctype.isupper(argv[1][18]));
    try std.testing.expect(ctype.ispunct(argv[1][19]));

    try expectSaturatingValue(argv[0], std.math.maxInt(u64), "tail");
    try expectSaturatingValue(argv[1], std.math.maxInt(u64), ",after");
    try std.testing.expectEqual(@as(u64, 64), hweight.swHweight64(cmdline.memparse(argv[0]).value));
    try std.testing.expectEqual(@as(u64, 64), hweight.swHweight64(cmdline.memparse(argv[1]).value));
}

test "saturated masks keep Linux style aliases aligned when present" {
    const all_bits = cmdline.memparse("9223372036854775808K").value;
    try std.testing.expectEqual(std.math.maxInt(u64), all_bits);
    try std.testing.expectEqual(@as(u64, 64), hweight.swHweight64(all_bits));

    const low32: u32 = @truncate(all_bits);
    try std.testing.expectEqual(@as(u32, 32), hweight.swHweight32(low32));
    try std.testing.expectEqual(@as(u32, 16), hweight.swHweight16(low32));
    try std.testing.expectEqual(@as(u32, 8), hweight.swHweight8(low32));

    if (@hasDecl(hweight, "__sw_hweight64")) {
        try std.testing.expectEqual(hweight.swHweight64(all_bits), hweight.__sw_hweight64(all_bits));
        try std.testing.expectEqual(hweight.swHweight32(low32), hweight.__sw_hweight32(low32));
        try std.testing.expectEqual(hweight.swHweight16(low32), hweight.__sw_hweight16(low32));
        try std.testing.expectEqual(hweight.swHweight8(low32), hweight.__sw_hweight8(low32));
    }
}
