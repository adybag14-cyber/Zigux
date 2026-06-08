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

test "zallocValue zeroes aggregate fields and resets the owner" {
    const allocator = std.testing.allocator;
    const Tag = enum { cold, warm };
    const Value = struct {
        bytes: [4]u8,
        maybe_len: ?usize,
        next: ?*u8,
        state: Tag,
        mask: u16,
    };

    var value: ?*Value = try zallocValue(allocator, Value);
    defer zfreeValue(allocator, Value, &value);

    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, &value.?.bytes);
    try std.testing.expect(value.?.maybe_len == null);
    try std.testing.expect(value.?.next == null);
    try std.testing.expectEqual(Tag.cold, value.?.state);
    try std.testing.expectEqual(@as(u16, 0), value.?.mask);

    value.?.bytes = .{ 1, 2, 3, 4 };
    value.?.maybe_len = 4;
    value.?.mask = 0xffff;
    zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
}
