const std = @import("std");
const zalloc = @import("zalloc");

test "phase1 zalloc replay keeps zero-length and zeroed byte allocations aligned" {
    const allocator = std.testing.allocator;

    var empty: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    defer zalloc.zfreeBytes(allocator, &empty);
    try std.testing.expect(empty != null);
    try std.testing.expectEqual(@as(usize, 0), empty.?.len);

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 16);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes != null);
    for (bytes.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }
}

test "phase1 zalloc replay keeps value zeroing aligned across nested fields" {
    const allocator = std.testing.allocator;
    const Value = struct {
        count: u32,
        ready: bool,
        pair: struct {
            left: u8,
            right: u8,
        },
    };

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value != null);
    try std.testing.expectEqual(@as(u32, 0), value.?.count);
    try std.testing.expectEqual(false, value.?.ready);
    try std.testing.expectEqual(@as(u8, 0), value.?.pair.left);
    try std.testing.expectEqual(@as(u8, 0), value.?.pair.right);
}

test "phase1 zalloc replay keeps optional-reset frees idempotent" {
    const allocator = std.testing.allocator;
    const Value = struct {
        token: usize,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    try std.testing.expect(bytes != null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    try std.testing.expect(value != null);
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
}
