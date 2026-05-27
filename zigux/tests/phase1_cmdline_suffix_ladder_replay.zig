const std = @import("std");
const cmdline = @import("cmdline");

fn expectMemparse(text: []const u8, expected_value: u64, expected_rest: []const u8) !void {
    const parsed = cmdline.memparse(text);
    try std.testing.expectEqual(expected_value, parsed.value);
    try std.testing.expectEqualStrings(expected_rest, parsed.rest);
}

test "phase1 cmdline replay keeps unsigned suffix ladders exact and consumes only one suffix byte" {
    try expectMemparse("1Ktail", 1 << 10, "tail");
    try expectMemparse("1mrest", 1 << 20, "rest");
    try expectMemparse("1G!", 1 << 30, "!");
    try expectMemparse("1t?", 1 << 40, "?");
    try expectMemparse("1P.", 1 << 50, ".");
    try expectMemparse("1e;", 1 << 60, ";");
    try expectMemparse("1KB", 1 << 10, "B");
}

test "phase1 cmdline replay keeps signed suffix expansion ordered before clamp and rest slicing" {
    try expectMemparse("+9223372036854775807Ktail", std.math.maxInt(i64), "tail");
    try expectMemparse("-9223372036854775808Ktail", @bitCast(@as(i64, std.math.minInt(i64))), "tail");
    try expectMemparse("-0x8000000000000000Krest", @bitCast(@as(i64, std.math.minInt(i64))), "rest");
}

test "phase1 cmdline replay keeps unsigned suffix saturation exact across radix forms" {
    try expectMemparse("18446744073709551615Ktail", std.math.maxInt(u64), "tail");
    try expectMemparse("0xffffffffffffffffMrest", std.math.maxInt(u64), "rest");
    try expectMemparse("01777777777777777777777Pdone", std.math.maxInt(u64), "done");
}
