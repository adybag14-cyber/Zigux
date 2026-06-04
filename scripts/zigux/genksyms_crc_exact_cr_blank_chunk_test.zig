const std = @import("std");
const genksyms_crc = @import("./genksyms_crc.zig");

const c_line_payload_len = 4095;

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

test "runGenksymsCrc skips an exact-buffer carriage-return-only chunk before visible tail" {
    var input = try std.ArrayList(u8).initCapacity(std.testing.allocator, c_line_payload_len + 6);
    defer input.deinit(std.testing.allocator);
    try input.appendNTimes(std.testing.allocator, '\r', c_line_payload_len);
    try input.appendSlice(std.testing.allocator, "tail\n");

    var capture = try Capture(128).init(std.testing.allocator);
    defer capture.deinit();
    try genksyms_crc.runGenksymsCrc(input.items, &capture);

    const tail_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{genksyms_crc.crc32("tail")});
    defer std.testing.allocator.free(tail_crc);

    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, capture.list.items, "crc_hex"));
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"tail\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, tail_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"\\r") == null);
}
