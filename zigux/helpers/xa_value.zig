const std = @import("std");
const abi = @import("abi_bindings");

pub fn make(value: u32) usize {
    return (@as(usize, value) << 1) | 1;
}

pub fn isValue(raw_addr: usize) bool {
    return (raw_addr & 1) != 0;
}

pub fn toValue(raw_addr: usize) u32 {
    return @intCast(raw_addr >> 1);
}

pub fn summarize(raw_addr: usize) abi.XaValueSummary {
    if (isValue(raw_addr)) {
        return .{
            .raw_addr = raw_addr,
            .decoded_value = toValue(raw_addr),
            .flags = abi.XA_VALUE_FLAG_VALUE,
        };
    }
    return .{
        .raw_addr = raw_addr,
        .decoded_value = 0,
        .flags = abi.XA_VALUE_FLAG_PLAIN,
    };
}

test "phase3 xa value helpers stay bounded and predictable" {
    const encoded = make(37);
    const summary = summarize(encoded);
    try std.testing.expect(isValue(encoded));
    try std.testing.expectEqual(@as(u32, 37), toValue(encoded));
    try std.testing.expectEqual(@as(usize, encoded), summary.raw_addr);
    try std.testing.expectEqual(@as(u32, 37), summary.decoded_value);
    try std.testing.expectEqual(@as(u32, abi.XA_VALUE_FLAG_VALUE), summary.flags);
}

test "phase3 xa value plain sentinel stays explicit" {
    const raw: usize = 0x1000;
    const summary = summarize(raw);
    try std.testing.expect(!isValue(raw));
    try std.testing.expectEqual(@as(usize, raw), summary.raw_addr);
    try std.testing.expectEqual(@as(u32, 0), summary.decoded_value);
    try std.testing.expectEqual(@as(u32, abi.XA_VALUE_FLAG_PLAIN), summary.flags);
}