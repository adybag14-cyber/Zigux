const std = @import("std");

pub fn zallocBytes(allocator: std.mem.Allocator, size: usize) ![]u8 {
    const bytes = try allocator.alloc(u8, size);
    @memset(bytes, 0);
    return bytes;
}

pub fn zallocValue(allocator: std.mem.Allocator, comptime T: type) !*T {
    const value = try allocator.create(T);
    value.* = std.mem.zeroes(T);
    return value;
}

pub fn zallocArray(allocator: std.mem.Allocator, comptime T: type, len: usize) ![]T {
    const items = try allocator.alloc(T, len);
    @memset(items, std.mem.zeroes(T));
    return items;
}

pub fn zfreeBytes(allocator: std.mem.Allocator, bytes: *?[]u8) void {
    if (bytes.*) |slice| {
        allocator.free(slice);
        bytes.* = null;
    }
}

pub fn zfreeValue(allocator: std.mem.Allocator, comptime T: type, value: *?*T) void {
    if (value.*) |ptr| {
        allocator.destroy(ptr);
        value.* = null;
    }
}

pub fn zfreeArray(allocator: std.mem.Allocator, comptime T: type, items: *?[]T) void {
    if (items.*) |slice| {
        allocator.free(slice);
        items.* = null;
    }
}

test "zalloc zeroes memory and zfree resets optionals" {
    const allocator = std.testing.allocator;
    const Value = struct {
        a: u32,
        b: bool,
    };

    var bytes: ?[]u8 = try zallocBytes(allocator, 8);
    defer zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes != null);
    for (bytes.?) |item| {
        try std.testing.expectEqual(@as(u8, 0), item);
    }

    var value: ?*Value = try zallocValue(allocator, Value);
    defer zfreeValue(allocator, Value, &value);
    try std.testing.expectEqual(@as(u32, 0), value.?.a);
    try std.testing.expectEqual(false, value.?.b);

    zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
}

test "zallocBytes handles zero-sized slices and resets their owner" {
    const allocator = std.testing.allocator;

    var bytes: ?[]u8 = try zallocBytes(allocator, 0);
    try std.testing.expect(bytes != null);
    try std.testing.expectEqual(@as(usize, 0), bytes.?.len);

    zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
}

test "zfree helpers are no-ops for empty owners" {
    const allocator = std.testing.allocator;
    const Value = struct {
        seen: bool,
    };

    var bytes: ?[]u8 = null;
    zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var value: ?*Value = null;
    zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
}

test "zallocArray zeroes typed arrays and zfreeArray resets owners" {
    const allocator = std.testing.allocator;
    const Tag = enum(u8) {
        zero = 0,
        hot = 1,
    };
    const Value = struct {
        count: usize,
        flags: [3]u8,
        maybe: ?*usize,
        enabled: bool,
        tag: Tag,
    };

    var items: ?[]Value = try zallocArray(allocator, Value, 3);
    defer zfreeArray(allocator, Value, &items);

    try std.testing.expect(items != null);
    try std.testing.expectEqual(@as(usize, 3), items.?.len);
    for (items.?) |item| {
        try std.testing.expectEqual(@as(usize, 0), item.count);
        try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, &item.flags);
        try std.testing.expect(item.maybe == null);
        try std.testing.expectEqual(false, item.enabled);
        try std.testing.expectEqual(Tag.zero, item.tag);
    }

    items.?[1].count = 17;
    items.?[1].flags = .{ 1, 2, 3 };
    items.?[1].enabled = true;
    items.?[1].tag = .hot;
    try std.testing.expectEqual(@as(usize, 17), items.?[1].count);

    zfreeArray(allocator, Value, &items);
    try std.testing.expect(items == null);

    zfreeArray(allocator, Value, &items);
    try std.testing.expect(items == null);
}

test "zallocArray handles zero lengths and allocation failures" {
    const allocator = std.testing.allocator;

    var empty: ?[]u16 = try zallocArray(allocator, u16, 0);
    try std.testing.expect(empty != null);
    try std.testing.expectEqual(@as(usize, 0), empty.?.len);
    zfreeArray(allocator, u16, &empty);
    try std.testing.expect(empty == null);

    var failing = std.testing.FailingAllocator.init(allocator, .{ .fail_index = 0 });
    const failed = zallocArray(failing.allocator(), u32, 4);
    try std.testing.expectError(error.OutOfMemory, failed);
}
