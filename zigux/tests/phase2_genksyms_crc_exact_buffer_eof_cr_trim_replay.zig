const std = @import("std");
const gen = @import("../../scripts/zigux/genksyms_crc.zig");

const c_line_payload_len = 4095;

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
            defer std.testing.allocator.free(rendered);
            try self.list.appendSlice(self.allocator, rendered);
        }

        pub fn writeByte(self: *@This(), byte: u8) !void {
            try self.list.append(self.allocator, byte);
        }
    };
}

test "lane19 exact-buffer EOF replay trims carriage returns from the final record" {
    var exact_line = try std.ArrayList(u8).initCapacity(std.testing.allocator, c_line_payload_len);
    defer exact_line.deinit(std.testing.allocator);
    try exact_line.appendNTimes(std.testing.allocator, 'a', c_line_payload_len - 2);
    try exact_line.append(std.testing.allocator, '\r');
    try exact_line.append(std.testing.allocator, '\r');

    var capture = try Capture(12288).init(std.testing.allocator);
    defer capture.deinit();
    try gen.runGenksymsCrc(exact_line.items, &capture);

    const trimmed_crc = try std.fmt.allocPrint(
        std.testing.allocator,
        "0x{x:0>8}",
        .{gen.crc32(exact_line.items[0 .. c_line_payload_len - 2])},
    );
    defer std.testing.allocator.free(trimmed_crc);
    const untrimmed_crc = try std.fmt.allocPrint(
        std.testing.allocator,
        "0x{x:0>8}",
        .{gen.crc32(exact_line.items)},
    );
    defer std.testing.allocator.free(untrimmed_crc);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, trimmed_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, untrimmed_crc) == null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "crc_hex") == 1);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"\\r\"") == null);
}
