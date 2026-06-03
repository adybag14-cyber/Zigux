const std = @import("std");

const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

fn argvItems(result: anytype) [][]u8 {
    const Result = @TypeOf(result.*);
    if (@hasField(Result, "argv")) {
        return result.argv;
    }
    return result.*;
}

fn argvLen(result: anytype) usize {
    const Result = @TypeOf(result.*);
    if (@hasField(Result, "argv")) {
        return result.argc();
    }
    return result.len;
}

fn freeArgv(allocator: std.mem.Allocator, result: anytype) void {
    const Result = @TypeOf(result.*);
    if (@hasField(Result, "argv")) {
        result.deinit();
    } else {
        argv_split.argvFree(allocator, result.*);
    }
}

fn expectNameChars(name: []const u8) !void {
    try std.testing.expect(name.len != 0);
    for (name) |ch| {
        try std.testing.expect(ctype.isalnum(ch) or ch == '_' or ch == '-');
        try std.testing.expect(ctype.isprint(ch));
    }
}

test "numeric helper tokens stay aligned across argv_split cmdline ctype and hweight" {
    var args = try argv_split.argvSplit(
        std.testing.allocator,
        "size=0x10K mask=0xf0,keep flag high=255",
    );
    defer freeArgv(std.testing.allocator, &args);

    const argv = argvItems(&args);
    try std.testing.expectEqual(@as(usize, 4), argvLen(&args));

    const size_eq = std.mem.indexOfScalar(u8, argv[0], '=') orelse return error.TestUnexpectedResult;
    const size_name = argv[0][0..size_eq];
    const size_value = argv[0][size_eq + 1 ..];
    try expectNameChars(size_name);
    try std.testing.expectEqualStrings("size", size_name);
    try std.testing.expectEqualStrings("0x10K", size_value);

    const parsed_size = cmdline.memparse(size_value);
    try std.testing.expectEqual(@as(u64, 0x10 << 10), parsed_size.value);
    try std.testing.expectEqualStrings("", parsed_size.rest);
    try std.testing.expectEqual(@as(u64, 1), hweight.swHweight64(parsed_size.value));

    const mask_eq = std.mem.indexOfScalar(u8, argv[1], '=') orelse return error.TestUnexpectedResult;
    const mask_name = argv[1][0..mask_eq];
    const mask_value = argv[1][mask_eq + 1 ..];
    try expectNameChars(mask_name);
    try std.testing.expectEqualStrings("mask", mask_name);
    try std.testing.expectEqualStrings("0xf0,keep", mask_value);

    const parsed_mask = cmdline.memparse(mask_value);
    try std.testing.expectEqual(@as(u64, 0xf0), parsed_mask.value);
    try std.testing.expectEqualStrings(",keep", parsed_mask.rest);
    try std.testing.expect(ctype.ispunct(parsed_mask.rest[0]));
    try std.testing.expectEqual(@as(u32, 4), hweight.swHweight8(@intCast(parsed_mask.value)));

    try expectNameChars(argv[2]);
    try std.testing.expectEqualStrings("flag", argv[2]);

    const high_eq = std.mem.indexOfScalar(u8, argv[3], '=') orelse return error.TestUnexpectedResult;
    const high_name = argv[3][0..high_eq];
    const high_value = argv[3][high_eq + 1 ..];
    try expectNameChars(high_name);
    const parsed_high = cmdline.memparse(high_value);
    try std.testing.expectEqual(@as(u64, 255), parsed_high.value);
    try std.testing.expectEqual(@as(u32, 8), hweight.swHweight8(@intCast(parsed_high.value)));
}

test "signed suffix token keeps cmdline magnitude and byte classes stable" {
    const signed = "-2K";
    try std.testing.expect(ctype.ispunct(signed[0]));
    try std.testing.expect(ctype.isdigit(signed[1]));
    try std.testing.expect(ctype.isupper(signed[2]));
    try std.testing.expectEqual(@as(u8, 'k'), ctype.fastTolower(signed[2]));

    const amount = cmdline.memparse(signed);
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -2048))), amount.value);
    try std.testing.expectEqual(@popCount(amount.value), hweight.swHweight64(amount.value));
}
