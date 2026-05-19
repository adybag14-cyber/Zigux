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

test "zallocBytes supports zero-length slices and repeated free" {
    const allocator = std.testing.allocator;

    var bytes: ?[]u8 = try zallocBytes(allocator, 0);
    defer zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes != null);
    try std.testing.expectEqual(@as(usize, 0), bytes.?.len);

    zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
}

test "zfreeValue tolerates null optionals" {
    const allocator = std.testing.allocator;
    const Value = struct {
        count: usize,
    };

    var value: ?*Value = null;
    zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
}

test "zfreeValue supports repeated free after destroying an allocated value" {
    const allocator = std.testing.allocator;
    const Value = struct {
        count: usize,
    };

    var value: ?*Value = try zallocValue(allocator, Value);
    defer zfreeValue(allocator, Value, &value);
    try std.testing.expect(value != null);
    try std.testing.expectEqual(@as(usize, 0), value.?.count);

    zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
}

test "zallocValue zeroes aggregate storage across arrays and optionals" {
    const allocator = std.testing.allocator;
    const Value = struct {
        bytes: [4]u8,
        flags: [2]bool,
        maybe_count: ?usize,
    };

    var value: ?*Value = try zallocValue(allocator, Value);
    defer zfreeValue(allocator, Value, &value);
    try std.testing.expect(value != null);
    try std.testing.expectEqualSlices(u8, &.{ 0, 0, 0, 0 }, &value.?.bytes);
    try std.testing.expectEqualSlices(bool, &.{ false, false }, &value.?.flags);
    try std.testing.expect(value.?.maybe_count == null);
}

test "zalloc clears fresh allocations after earlier dirty frees" {
    const allocator = std.testing.allocator;
    const Value = struct {
        bytes: [4]u8,
        maybe_count: ?usize,
    };

    var bytes: ?[]u8 = try zallocBytes(allocator, 4);
    try std.testing.expect(bytes != null);
    @memset(bytes.?, 0xaa);
    zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zallocBytes(allocator, 4);
    defer zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes != null);
    try std.testing.expectEqualSlices(u8, &.{ 0, 0, 0, 0 }, bytes.?);

    var value: ?*Value = try zallocValue(allocator, Value);
    try std.testing.expect(value != null);
    value.?.bytes = .{ 0xaa, 0xbb, 0xcc, 0xdd };
    value.?.maybe_count = 7;
    zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    value = try zallocValue(allocator, Value);
    defer zfreeValue(allocator, Value, &value);
    try std.testing.expect(value != null);
    try std.testing.expectEqualSlices(u8, &.{ 0, 0, 0, 0 }, &value.?.bytes);
    try std.testing.expect(value.?.maybe_count == null);
}

test "zallocValue re-zeroes enum-backed storage after earlier dirty frees" {
    const allocator = std.testing.allocator;
    const Value = struct {
        state: enum(u8) {
            idle = 0,
            busy = 1,
            done = 2,
        },
        nested: struct {
            bytes: [2]u8,
            maybe_count: ?usize,
        },
    };

    var value: ?*Value = try zallocValue(allocator, Value);
    try std.testing.expect(value != null);
    value.?.state = .done;
    value.?.nested.bytes = .{ 0xaa, 0xbb };
    value.?.nested.maybe_count = 12;
    zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    value = try zallocValue(allocator, Value);
    defer zfreeValue(allocator, Value, &value);
    try std.testing.expect(value != null);
    try std.testing.expect(value.?.state == .idle);
    try std.testing.expectEqualSlices(u8, &.{ 0, 0 }, &value.?.nested.bytes);
    try std.testing.expect(value.?.nested.maybe_count == null);
}
