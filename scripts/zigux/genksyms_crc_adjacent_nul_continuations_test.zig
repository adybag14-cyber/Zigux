const std = @import("std");

const genksyms_crc = @import("genksyms_crc.zig");

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

test "genksyms CRC skips adjacent NUL continuations after exact-buffer split" {
    var input = try std.ArrayList(u8).initCapacity(std.testing.allocator, c_line_payload_len + 48);
    defer input.deinit(std.testing.allocator);
    try input.appendNTimes(std.testing.allocator, 'a', c_line_payload_len);
    try input.append(std.testing.allocator, 0);
    try input.appendSlice(std.testing.allocator, "hidden-tail-one\n");
    try input.append(std.testing.allocator, 0);
    try input.appendSlice(std.testing.allocator, "hidden-tail-two\r\n");
    try input.appendSlice(std.testing.allocator, "visible\n");

    var capture = try Capture(16384).init(std.testing.allocator);
    defer capture.deinit();
    try genksyms_crc.runGenksymsCrc(input.items, &capture);

    const exact_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{genksyms_crc.crc32(input.items[0..c_line_payload_len])});
    defer std.testing.allocator.free(exact_crc);
    const hidden_one_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{genksyms_crc.crc32("hidden-tail-one")});
    defer std.testing.allocator.free(hidden_one_crc);
    const hidden_two_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{genksyms_crc.crc32("hidden-tail-two")});
    defer std.testing.allocator.free(hidden_two_crc);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, exact_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"visible\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, hidden_one_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, hidden_two_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "hidden-tail-one") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "hidden-tail-two") == null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "crc_hex") == 2);
}
