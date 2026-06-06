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

pub fn zallocSlice(allocator: std.mem.Allocator, comptime T: type, len: usize) ![]T {
    const items = try allocator.alloc(T, len);
    for (items) |*item| {
        item.* = std.mem.zeroes(T);
    }
    return items;
}

pub fn zfreeBytes(allocator: std.mem.Allocator, bytes: *?[]u8) void {
    if (bytes.*) |slice| {
        allocator.free(slice);
        bytes.* = null;
    }
}

pub fn zfreeSlice(allocator: std.mem.Allocator, comptime T: type, items: *?[]T) void {
    if (items.*) |slice| {
        allocator.free(slice);
        items.* = null;
    }
}

pub fn zfreeValue(allocator: std.mem.Allocator, comptime T: type, value: *?*T) void {
    if (value.*) |ptr| {
        allocator.destroy(ptr);
        value.* = null;
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

test "zallocSlice zeroes aggregate elements and zfreeSlice resets owners" {
    const allocator = std.testing.allocator;
    const Entry = struct {
        count: u32,
        enabled: bool,
        link: ?*u8,
        payload: [3]u16,
    };

    var entries: ?[]Entry = try zallocSlice(allocator, Entry, 3);
    defer zfreeSlice(allocator, Entry, &entries);
    try std.testing.expect(entries != null);
    try std.testing.expectEqual(@as(usize, 3), entries.?.len);
    for (entries.?) |entry| {
        try std.testing.expectEqual(@as(u32, 0), entry.count);
        try std.testing.expectEqual(false, entry.enabled);
        try std.testing.expect(entry.link == null);
        try std.testing.expectEqualSlices(u16, &[_]u16{ 0, 0, 0 }, &entry.payload);
    }

    entries.?[1].count = 7;
    entries.?[1].enabled = true;
    entries.?[1].payload = .{ 1, 2, 3 };
    zfreeSlice(allocator, Entry, &entries);
    try std.testing.expect(entries == null);

    zfreeSlice(allocator, Entry, &entries);
    try std.testing.expect(entries == null);
}

test "zallocSlice handles zero-length typed slices" {
    const allocator = std.testing.allocator;

    var empty: ?[]u64 = try zallocSlice(allocator, u64, 0);
    try std.testing.expect(empty != null);
    try std.testing.expectEqual(@as(usize, 0), empty.?.len);

    zfreeSlice(allocator, u64, &empty);
    try std.testing.expect(empty == null);
}
