const std = @import("std");
const gen = @import("genksyms_crc.zig");

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

test "genksyms crc escapes visible CAN before NUL and drops hidden tail" {
    var input = try std.ArrayList(u8).initCapacity(std.testing.allocator, 96);
    defer input.deinit(std.testing.allocator);
    try input.appendSlice(std.testing.allocator, "can");
    try input.append(std.testing.allocator, 0x18);
    try input.appendSlice(std.testing.allocator, "visible");
    try input.append(std.testing.allocator, 0);
    try input.appendSlice(std.testing.allocator, "hidden");
    try input.append(std.testing.allocator, 0x18);
    try input.appendSlice(std.testing.allocator, "tail\nnext");
    try input.append(std.testing.allocator, 0x18);
    try input.appendSlice(std.testing.allocator, "visible\n");

    var capture = try Capture(512).init(std.testing.allocator);
    defer capture.deinit();
    try gen.runGenksymsCrc(input.items, &capture);

    const visible = "can\x18visible";
    const later = "next\x18visible";
    const hidden = "hiddentail";
    const visible_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32(visible)});
    defer std.testing.allocator.free(visible_crc);
    const later_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32(later)});
    defer std.testing.allocator.free(later_crc);
    const hidden_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32(hidden)});
    defer std.testing.allocator.free(hidden_crc);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"can\\u0018visible\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"next\\u0018visible\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, visible_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, later_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "hidden") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, hidden_crc) == null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "crc_hex") == 2);
}
