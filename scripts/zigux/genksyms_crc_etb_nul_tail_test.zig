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

test "runGenksymsCrc escapes visible ETB before truncating NUL tail" {
    const etb_record = [_]u8{ 'a', 'l', 'p', 'h', 'a', 0x17, 'e', 't', 'b', 0, 'h', 'i', 'd', 'd', 'e', 'n', '\n', 'o', 'm', 'e', 'g', 'a', '\n' };
    const visible = etb_record[0..9];

    var capture = try Capture(256).init(std.testing.allocator);
    defer capture.deinit();
    try genksyms_crc.runGenksymsCrc(&etb_record, &capture);

    const visible_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{genksyms_crc.crc32(visible)});
    defer std.testing.allocator.free(visible_crc);
    const hidden_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{genksyms_crc.crc32("hidden")});
    defer std.testing.allocator.free(hidden_crc);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"alpha\\u0017etb\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, visible_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "hidden") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, hidden_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"omega\"") != null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "crc_hex") == 2);
}
