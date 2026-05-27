const std = @import("std");
const zalloc = @import("zalloc");

test "zallocBytes returns an empty zeroed slice for zero length and resets idempotently" {
    const allocator = std.testing.allocator;

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    defer zalloc.zfreeBytes(allocator, &bytes);

    try std.testing.expect(bytes != null);
    try std.testing.expectEqual(@as(usize, 0), bytes.?.len);

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    // A second reset should stay a no-op for the optional holder.
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
}

test "zallocValue zeroes nested arrays, structs, and optionals" {
    const allocator = std.testing.allocator;
    const Value = struct {
        bytes: [4]u8,
        flag: bool,
        maybe: ?u16,
        pair: struct {
            left: u32,
            right: u8,
        },
    };

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);

    try std.testing.expect(value != null);
    try std.testing.expectEqualSlices(u8, &.{ 0, 0, 0, 0 }, value.?.bytes[0..]);
    try std.testing.expectEqual(false, value.?.flag);
    try std.testing.expect(value.?.maybe == null);
    try std.testing.expectEqual(@as(u32, 0), value.?.pair.left);
    try std.testing.expectEqual(@as(u8, 0), value.?.pair.right);
}

test "zallocBytes returns fresh zeroed storage after a prior caller write" {
    const allocator = std.testing.allocator;

    var first: ?[]u8 = try zalloc.zallocBytes(allocator, 6);
    defer zalloc.zfreeBytes(allocator, &first);
    try std.testing.expect(first != null);
    @memset(first.?, 0xaa);

    zalloc.zfreeBytes(allocator, &first);
    try std.testing.expect(first == null);

    var second: ?[]u8 = try zalloc.zallocBytes(allocator, 6);
    defer zalloc.zfreeBytes(allocator, &second);
    try std.testing.expect(second != null);
    for (second.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
}
