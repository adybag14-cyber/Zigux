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

test "runGenksymsCrc escapes form feed while trimming trailing carriage returns" {
    const first_visible = "alpha\x0cform";
    const second_visible = "next\x0cvisible";
    const input = first_visible ++ "\r\n" ++ second_visible ++ "\r\r\n";

    var capture = try Capture(256).init(std.testing.allocator);
    defer capture.deinit();
    try genksyms_crc.runGenksymsCrc(input, &capture);

    const first_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{genksyms_crc.crc32(first_visible)});
    defer std.testing.allocator.free(first_crc);
    const second_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{genksyms_crc.crc32(second_visible)});
    defer std.testing.allocator.free(second_crc);
    const untrimmed_second_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{genksyms_crc.crc32(second_visible ++ "\r\r")});
    defer std.testing.allocator.free(untrimmed_second_crc);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"alpha\\fform\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"next\\fvisible\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, first_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, second_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, untrimmed_second_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\\r") == null);
    try std.testing.expectEqual(@as(usize, 2), std.mem.count(u8, capture.list.items, "crc_hex"));
}
