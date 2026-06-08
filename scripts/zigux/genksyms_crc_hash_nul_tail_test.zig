const std = @import("std");
const gen = @import("./genksyms_crc.zig");

fn Capture(comptime capacity: usize) type {
    return struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, capacity),
                .allocator = allocator,
            };
        }

        fn deinit(self: *@This()) void {
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

fn crcHex(allocator: std.mem.Allocator, text: []const u8) ![]const u8 {
    return try std.fmt.allocPrint(allocator, "0x{x:0>8}", .{gen.crc32(text)});
}

test "hash-prefixed records remain visible around hidden NUL tails" {
    const visible_before = "#define VISIBLE_BEFORE 1";
    const hidden_tail = "#define HIDDEN_AFTER_NUL 2";
    const visible_after = "#define VISIBLE_AFTER 3";

    var input = try std.ArrayList(u8).initCapacity(std.testing.allocator, 128);
    defer input.deinit(std.testing.allocator);
    try input.appendSlice(std.testing.allocator, visible_before);
    try input.append(std.testing.allocator, 0);
    try input.appendSlice(std.testing.allocator, hidden_tail);
    try input.append(std.testing.allocator, '\n');
    try input.appendSlice(std.testing.allocator, visible_after);
    try input.append(std.testing.allocator, '\n');

    var capture = try Capture(512).init(std.testing.allocator);
    defer capture.deinit();
    try gen.runGenksymsCrc(input.items, &capture);

    const before_crc = try crcHex(std.testing.allocator, visible_before);
    defer std.testing.allocator.free(before_crc);
    const hidden_crc = try crcHex(std.testing.allocator, hidden_tail);
    defer std.testing.allocator.free(hidden_crc);
    const after_crc = try crcHex(std.testing.allocator, visible_after);
    defer std.testing.allocator.free(after_crc);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, visible_before) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, before_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, visible_after) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, after_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, hidden_tail) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, hidden_crc) == null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "\"crc_hex\"") == 2);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\\u0023") == null);
}
