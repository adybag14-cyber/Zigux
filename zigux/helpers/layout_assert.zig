const std = @import("std");

pub fn size(comptime T: type, expected: usize) !void {
    try std.testing.expectEqual(expected, @sizeOf(T));
}

pub fn align(comptime T: type, expected: usize) !void {
    try std.testing.expectEqual(expected, @alignOf(T));
}

pub fn offset(comptime T: type, comptime field_name: []const u8, expected: usize) !void {
    try std.testing.expectEqual(expected, @offsetOf(T, field_name));
}
