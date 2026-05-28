const std = @import("std");
const cmdline = @import("cmdline");

test "cmdline memparse accepts every binary suffix case" {
    const cases = [_]struct {
        input: []const u8,
        expected: u64,
    }{
        .{ .input = "1K", .expected = 1 << 10 },
        .{ .input = "1k", .expected = 1 << 10 },
        .{ .input = "2M", .expected = 2 << 20 },
        .{ .input = "2m", .expected = 2 << 20 },
        .{ .input = "3G", .expected = 3 << 30 },
        .{ .input = "3g", .expected = 3 << 30 },
        .{ .input = "4T", .expected = 4 << 40 },
        .{ .input = "4t", .expected = 4 << 40 },
        .{ .input = "5P", .expected = 5 << 50 },
        .{ .input = "5p", .expected = 5 << 50 },
        .{ .input = "7E", .expected = 7 << 60 },
        .{ .input = "7e", .expected = 7 << 60 },
    };

    for (cases) |case| {
        const parsed = cmdline.memparse(case.input);
        try std.testing.expectEqual(case.expected, parsed.value);
        try std.testing.expectEqualStrings("", parsed.rest);
    }
}

test "cmdline memparse suffixes advance rest once" {
    const with_suffix = cmdline.memparse("12K,panic=1");
    try std.testing.expectEqual(@as(u64, 12 << 10), with_suffix.value);
    try std.testing.expectEqualStrings(",panic=1", with_suffix.rest);

    const without_suffix = cmdline.memparse("12,panic=1");
    try std.testing.expectEqual(@as(u64, 12), without_suffix.value);
    try std.testing.expectEqualStrings(",panic=1", without_suffix.rest);
}

test "cmdline memparse suffix overflow saturates" {
    const unsigned_overflow = cmdline.memparse("16E");
    try std.testing.expectEqual(std.math.maxInt(u64), unsigned_overflow.value);
    try std.testing.expectEqualStrings("", unsigned_overflow.rest);

    const signed_negative_overflow = cmdline.memparse("-16E");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, std.math.minInt(i64)))), signed_negative_overflow.value);
    try std.testing.expectEqualStrings("", signed_negative_overflow.rest);
}
