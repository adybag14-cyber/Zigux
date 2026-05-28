const std = @import("std");
const cmdline = @import("cmdline");

fn signedBits(value: i64) u64 {
    return @bitCast(value);
}

fn expectMemparse(text: []const u8, expected_value: u64, expected_rest: []const u8) !void {
    const parsed = cmdline.memparse(text);
    try std.testing.expectEqual(expected_value, parsed.value);
    try std.testing.expectEqualStrings(expected_rest, parsed.rest);
}

test "memparse keeps signed radix suffix ladders aligned" {
    try expectMemparse("-0x2Ktail", signedBits(-2048), "tail");
    try expectMemparse("+010Mmore", @as(u64, 8) << 20, "more");
    try expectMemparse("-077Gdone", signedBits(-(@as(i64, 63) << 30)), "done");
    try expectMemparse("+0X7Pstop", (@as(u64, 7) << 50), "stop");
}

test "memparse consumes only one suffix byte after signed radix values" {
    try expectMemparse("-0x2KB", signedBits(-2048), "B");
    try expectMemparse("+010MiB", @as(u64, 8) << 20, "iB");
    try expectMemparse("-0X4kib", signedBits(-4096), "ib");
    try expectMemparse("+077GHz", (@as(u64, 63) << 30), "Hz");
}

test "memparse clamps signed radix suffix overflow before rest alignment" {
    try expectMemparse(
        "+0x20000000000000Krest",
        @as(u64, @intCast(std.math.maxInt(i64))),
        "rest",
    );
    try expectMemparse(
        "-0x20000000000000Krest",
        signedBits(std.math.minInt(i64)),
        "rest",
    );
}

test "memparse leaves incomplete signed radix prefixes untouched" {
    try expectMemparse("-0x", 0, "-0x");
    try expectMemparse("+0Xtail", 0, "+0Xtail");
    try expectMemparse("-0xG", 0, "-0xG");
    try expectMemparse("+0XKrest", 0, "+0XKrest");
}
