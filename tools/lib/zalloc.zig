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

test "zallocValue zeroes nested aggregates before optional owner release" {
    const allocator = std.testing.allocator;
    const Inner = struct {
        flags: [3]bool,
        counter: u32,
        maybe_byte: ?*u8,
    };
    const Value = struct {
        inner: Inner,
        slots: [4]usize,
        maybe_slice: ?[]u8,
        enabled: bool,
    };

    var value: ?*Value = try zallocValue(allocator, Value);
    defer zfreeValue(allocator, Value, &value);

    try std.testing.expect(value != null);
    for (value.?.inner.flags) |flag| {
        try std.testing.expectEqual(false, flag);
    }
    try std.testing.expectEqual(@as(u32, 0), value.?.inner.counter);
    try std.testing.expect(value.?.inner.maybe_byte == null);
    for (value.?.slots) |slot| {
        try std.testing.expectEqual(@as(usize, 0), slot);
    }
    try std.testing.expect(value.?.maybe_slice == null);
    try std.testing.expectEqual(false, value.?.enabled);

    value.?.inner.counter = 99;
    value.?.slots[2] = 7;
    value.?.enabled = true;

    zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
    zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
}
