const std = @import("std");
const cmdline = @import("cmdline");

test "phase1 cmdline borrowed-slice replay keeps plain key value slices anchored to caller storage" {
    var backing = "  console=ttyS0,115200 root=/dev/sda1".*;
    const input = backing[0..];
    const parsed = cmdline.nextArg(input) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqualStrings("console", parsed.param);
    try std.testing.expectEqualStrings("ttyS0,115200", parsed.value.?);
    try std.testing.expectEqualStrings("root=/dev/sda1", parsed.remaining);

    const base = @intFromPtr(input.ptr);
    try std.testing.expectEqual(@as(usize, 2), @intFromPtr(parsed.param.ptr) - base);
    try std.testing.expectEqual(@as(usize, 10), @intFromPtr(parsed.value.?.ptr) - base);
    try std.testing.expectEqual(@as(usize, 23), @intFromPtr(parsed.remaining.ptr) - base);
}

test "phase1 cmdline borrowed-slice replay keeps quoted values and remaining text borrowed" {
    var backing = "root=\"/dev/sda1 quiet\" panic=-1".*;
    const input = backing[0..];
    const parsed = cmdline.nextArg(input) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqualStrings("root", parsed.param);
    try std.testing.expectEqualStrings("/dev/sda1 quiet", parsed.value.?);
    try std.testing.expectEqualStrings("panic=-1", parsed.remaining);

    try std.testing.expect(parsed.param.ptr == input.ptr);
    try std.testing.expect(parsed.value.?.ptr == input[6..].ptr);
    try std.testing.expect(parsed.remaining.ptr == input[input.len - "panic=-1".len ..].ptr);
}

test "phase1 cmdline borrowed-slice replay keeps NUL option stops and invalid suffix rest aligned" {
    try std.testing.expect(cmdline.parseOptionStr("quiet\x00debug", "quiet"));
    try std.testing.expect(!cmdline.parseOptionStr("quiet\x00debug", "debug"));

    const unsigned_invalid_suffix = cmdline.memparse("64Qtail");
    try std.testing.expectEqual(@as(u64, 64), unsigned_invalid_suffix.value);
    try std.testing.expectEqualStrings("Qtail", unsigned_invalid_suffix.rest);

    const signed_invalid_suffix = cmdline.memparse("-2Qtail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -2))), signed_invalid_suffix.value);
    try std.testing.expectEqualStrings("Qtail", signed_invalid_suffix.rest);
}
