const std = @import("std");
const zalloc = @import("zalloc");

const Sample = struct {
    bytes: [3]u8,
    ready: bool,
    count: usize,
};

test "zalloc bytes stay live while value optionals are freed and recreated" {
    const allocator = std.testing.allocator;

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    defer zalloc.zfreeBytes(allocator, &bytes);
    var value: ?*Sample = try zalloc.zallocValue(allocator, Sample);
    defer zalloc.zfreeValue(allocator, Sample, &value);

    @memcpy(bytes.?, &[_]u8{ 9, 8, 7, 6 });
    value.?.bytes = .{ 1, 2, 3 };
    value.?.ready = true;
    value.?.count = 42;

    zalloc.zfreeValue(allocator, Sample, &value);
    try std.testing.expect(value == null);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 9, 8, 7, 6 }, bytes.?);

    value = try zalloc.zallocValue(allocator, Sample);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, &value.?.bytes);
    try std.testing.expectEqual(false, value.?.ready);
    try std.testing.expectEqual(@as(usize, 0), value.?.count);
}

test "zalloc bytes zero newly allocated storage after a prior mutated allocation is freed" {
    const allocator = std.testing.allocator;

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 3);
    @memset(bytes.?, 0xaa);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 5);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expectEqual(@as(usize, 5), bytes.?.len);
    for (bytes.?) |item| {
        try std.testing.expectEqual(@as(u8, 0), item);
    }
}

test "zalloc byte and value free helpers stay null-safe across interleaved resets" {
    const allocator = std.testing.allocator;

    var bytes: ?[]u8 = null;
    var value: ?*Sample = null;

    zalloc.zfreeBytes(allocator, &bytes);
    zalloc.zfreeValue(allocator, Sample, &value);
    try std.testing.expect(bytes == null);
    try std.testing.expect(value == null);

    bytes = try zalloc.zallocBytes(allocator, 1);
    value = try zalloc.zallocValue(allocator, Sample);
    defer zalloc.zfreeBytes(allocator, &bytes);
    defer zalloc.zfreeValue(allocator, Sample, &value);

    bytes.?[0] = 5;
    value.?.count = 99;

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    try std.testing.expectEqual(@as(usize, 99), value.?.count);

    zalloc.zfreeValue(allocator, Sample, &value);
    try std.testing.expect(value == null);
}
