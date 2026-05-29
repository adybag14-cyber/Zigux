const std = @import("std");
const gen = @import("./genksyms_crc.zig");

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
            defer self.allocator.free(rendered);
            try self.list.appendSlice(self.allocator, rendered);
        }

        pub fn writeByte(self: *@This(), byte: u8) !void {
            try self.list.append(self.allocator, byte);
        }
    };
}

test "lane19 exact-buffer split preserves JSON escaping before NUL truncation and CR trimming" {
    var input = try std.ArrayList(u8).initCapacity(std.testing.allocator, c_line_payload_len + 32);
    defer input.deinit(std.testing.allocator);

    try input.appendNTimes(std.testing.allocator, 'x', c_line_payload_len);
    try input.appendSlice(std.testing.allocator, "\"quoted\"\tpath\\name\r\r");
    try input.append(std.testing.allocator, 0);
    try input.appendSlice(std.testing.allocator, "ignored\nnext\n");

    var capture = try Capture(12288).init(std.testing.allocator);
    defer capture.deinit();
    try gen.runGenksymsCrc(input.items, &capture);

    const exact_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32(input.items[0..c_line_payload_len])});
    defer std.testing.allocator.free(exact_crc);
    const escaped_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("\"quoted\"\tpath\\name")});
    defer std.testing.allocator.free(escaped_crc);
    const untrimmed_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("\"quoted\"\tpath\\name\r\r")});
    defer std.testing.allocator.free(untrimmed_crc);
    const untruncated_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("\"quoted\"\tpath\\name\r\r\x00ignored")});
    defer std.testing.allocator.free(untruncated_crc);
    const next_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("next")});
    defer std.testing.allocator.free(next_crc);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, exact_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, escaped_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, untrimmed_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, untruncated_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, next_crc) != null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "crc_hex") == 3);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"\\\"quoted\\\"\\tpath\\\\name\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "ignored") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\\u0000") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"next\"") != null);
}
