const std = @import("std");
const cmdline = @import("cmdline");

fn expectMemparse(text: []const u8, expected_value: u64, expected_rest: []const u8) !void {
    const parsed = cmdline.memparse(text);
    try std.testing.expectEqual(expected_value, parsed.value);
    try std.testing.expectEqualStrings(expected_rest, parsed.rest);
}

test "phase1 memparse replay keeps signed radix and suffix parsing aligned" {
    try expectMemparse("-0x2Ktail", @bitCast(@as(i64, -2048)), "tail");
    try expectMemparse("+010Mmore", 8 << 20, "more");
    try expectMemparse("64K rest", 64 << 10, " rest");
}

test "phase1 memparse replay preserves no-conversion and signed-prefix boundaries" {
    try expectMemparse("xyz", 0, "xyz");
    try expectMemparse("-xyz", 0, "-xyz");
    try expectMemparse("+nope", 0, "+nope");
}

test "phase1 memparse replay keeps overflow and trailing rest boundaries exact" {
    try expectMemparse("18446744073709551616suffix", std.math.maxInt(i64), "suffix");
    try expectMemparse("18446744073709551616Ktail", std.math.maxInt(u64), "tail");
    try expectMemparse("-9223372036854775809Mmore", @bitCast(@as(i64, std.math.minInt(i64))), "more");
}
