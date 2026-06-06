const std = @import("std");
const crc = @import("genksyms_crc.zig");

fn Capture(comptime capacity: usize) type {
    return struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        pub fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, capacity),
                .allocator = allocator,
            };
        }

        pub fn deinit(self: *@This()) void {
            self.list.deinit(self.allocator);
        }

        pub fn writeAll(self: *@This(), bytes: []const u8) !void {
            try self.list.appendSlice(self.allocator, bytes);
        }

        pub fn print(self: *@This(), comptime fmt: []const u8, args: anytype) !void {
            const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
            defer self.allocator.free(rendered);
            try self.list.appendSlice(self.allocator, rendered);
        }

        pub fn writeByte(self: *@This(), byte: u8) !void {
            try self.list.append(self.allocator, byte);
        }
    };
}

test "DEL remains visible before NUL truncates hidden tail" {
    const visible = [_]u8{ 'd', 'e', 'l', '-', 0x7f, '-', 'v', 'i', 's', 'i', 'b', 'l', 'e' };
    const hidden = "hidden-del-tail";

    var input = try std.ArrayList(u8).initCapacity(std.testing.allocator, visible.len + hidden.len + 8);
    defer input.deinit(std.testing.allocator);
    try input.appendSlice(std.testing.allocator, &visible);
    try input.append(std.testing.allocator, 0);
    try input.appendSlice(std.testing.allocator, hidden);
    try input.append(std.testing.allocator, '\n');
    try input.appendSlice(std.testing.allocator, "after\n");

    var capture = try Capture(256).init(std.testing.allocator);
    defer capture.deinit();
    try crc.runGenksymsCrc(input.items, &capture);

    const visible_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{crc.crc32(&visible)});
    defer std.testing.allocator.free(visible_crc);
    const hidden_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{crc.crc32(hidden)});
    defer std.testing.allocator.free(hidden_crc);

    try std.testing.expect(std.mem.indexOfScalar(u8, capture.list.items, 0x7f) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\\u007f") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, hidden) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, hidden_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, visible_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"after\"") != null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "crc_hex") == 2);
}
