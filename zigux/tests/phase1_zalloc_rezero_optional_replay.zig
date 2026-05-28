const std = @import("std");
const zalloc = @import("zalloc");

const Nested = struct {
    bytes: [4]u8,
    flag: bool,
    count: u16,
};

test "zalloc bytes are zeroed again after mutation and free" {
    const allocator = std.testing.allocator;

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 6);
    try std.testing.expectEqual(@as(usize, 6), bytes.?.len);
    @memset(bytes.?, 0xaa);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 6);
    defer zalloc.zfreeBytes(allocator, &bytes);

    for (bytes.?) |item| {
        try std.testing.expectEqual(@as(u8, 0), item);
    }
}

test "zalloc value resets nested fields after reuse" {
    const allocator = std.testing.allocator;

    var value: ?*Nested = try zalloc.zallocValue(allocator, Nested);
    value.?.bytes = .{ 1, 2, 3, 4 };
    value.?.flag = true;
    value.?.count = 99;
    zalloc.zfreeValue(allocator, Nested, &value);
    try std.testing.expect(value == null);

    zalloc.zfreeValue(allocator, Nested, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Nested);
    defer zalloc.zfreeValue(allocator, Nested, &value);

    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, &value.?.bytes);
    try std.testing.expectEqual(false, value.?.flag);
    try std.testing.expectEqual(@as(u16, 0), value.?.count);
}

test "zero-length zalloc bytes and null optionals stay safe" {
    const allocator = std.testing.allocator;

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expectEqual(@as(usize, 0), bytes.?.len);
    zalloc.zfreeBytes(allocator, &bytes);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var value: ?*Nested = null;
    zalloc.zfreeValue(allocator, Nested, &value);
    try std.testing.expect(value == null);
}
