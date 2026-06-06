const std = @import("std");
const genksyms_crc = @import("genksyms_crc.zig");

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

test "runGenksymsCrc escapes visible ACK before hiding NUL tail" {
    const allocator = std.testing.allocator;
    const visible = "ack " ++ [_]u8{0x06} ++ " byte";
    const hidden_tail = "hidden " ++ [_]u8{0x06} ++ " tail";

    var input = try std.ArrayList(u8).initCapacity(allocator, visible.len + hidden_tail.len + 8);
    defer input.deinit(allocator);
    try input.appendSlice(allocator, visible);
    try input.append(allocator, 0);
    try input.appendSlice(allocator, hidden_tail);
    try input.appendSlice(allocator, "\nnext\n");

    var capture = try Capture(256).init(allocator);
    defer capture.deinit();
    try genksyms_crc.runGenksymsCrc(input.items, &capture);

    const visible_crc = try std.fmt.allocPrint(allocator, "0x{x:0>8}", .{genksyms_crc.crc32(visible)});
    defer allocator.free(visible_crc);
    const hidden_crc = try std.fmt.allocPrint(allocator, "0x{x:0>8}", .{genksyms_crc.crc32(hidden_tail)});
    defer allocator.free(hidden_crc);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"ack \\u0006 byte\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, visible_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "hidden") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, hidden_crc) == null);
    try std.testing.expect(std.mem.indexOfScalar(u8, capture.list.items, 0x06) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"next\"") != null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "crc_hex") == 2);
}
