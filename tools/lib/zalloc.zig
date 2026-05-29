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

pub fn zallocArray(allocator: std.mem.Allocator, comptime T: type, n: usize) ![]T {
    const values = try allocator.alloc(T, n);
    @memset(values, std.mem.zeroes(T));
    return values;
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

pub fn zfreeArray(allocator: std.mem.Allocator, comptime T: type, values: *?[]T) void {
    if (values.*) |slice| {
        allocator.free(slice);
        values.* = null;
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

test "zallocArray zeroes typed slices and zfreeArray resets optionals" {
    const allocator = std.testing.allocator;
    const Entry = struct {
        id: u32,
        enabled: bool,
        tag: ?*u8,
    };

    var values: ?[]Entry = try zallocArray(allocator, Entry, 3);
    defer zfreeArray(allocator, Entry, &values);

    try std.testing.expect(values != null);
    try std.testing.expectEqual(@as(usize, 3), values.?.len);
    for (values.?) |entry| {
        try std.testing.expectEqual(@as(u32, 0), entry.id);
        try std.testing.expectEqual(false, entry.enabled);
        try std.testing.expect(entry.tag == null);
    }

    values.?[1].id = 7;
    values.?[1].enabled = true;

    zfreeArray(allocator, Entry, &values);
    try std.testing.expect(values == null);
    zfreeArray(allocator, Entry, &values);
    try std.testing.expect(values == null);
}
