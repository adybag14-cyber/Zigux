const std = @import("std");
const cmdline = @import("cmdline");

test "phase1 cmdline replay keeps incomplete signed radix prefixes unconsumed" {
    const negative_hex = cmdline.memparse("-0xK tail");
    try std.testing.expectEqual(@as(u64, 0), negative_hex.value);
    try std.testing.expectEqualStrings("-0xK tail", negative_hex.rest);

    const positive_hex = cmdline.memparse("+0Xmore");
    try std.testing.expectEqual(@as(u64, 0), positive_hex.value);
    try std.testing.expectEqualStrings("+0Xmore", positive_hex.rest);

    const signed_prefix_only = cmdline.memparse("-0x");
    try std.testing.expectEqual(@as(u64, 0), signed_prefix_only.value);
    try std.testing.expectEqualStrings("-0x", signed_prefix_only.rest);
}

test "phase1 cmdline replay keeps option scans bounded by the first embedded NUL" {
    try std.testing.expect(cmdline.parseOptionStr(",debug\x00,trace", "debug"));
    try std.testing.expect(cmdline.parseOptionStr("debug,,trace", ""));
    try std.testing.expect(!cmdline.parseOptionStr(",debug\x00,trace", "trace"));
    try std.testing.expect(!cmdline.parseOptionStr("debug\x00,trace", ""));
}
