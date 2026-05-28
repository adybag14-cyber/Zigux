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

test "lane19 exact-buffer visible-CR NUL split keeps the next line while skipping the NUL-prefixed continuation" {
    var exact_then_visible_cr_then_nul_then_next_line = try std.ArrayList(u8).initCapacity(std.testing.allocator, c_line_payload_len + 7);
    defer exact_then_visible_cr_then_nul_then_next_line.deinit(std.testing.allocator);
    try exact_then_visible_cr_then_nul_then_next_line.appendNTimes(std.testing.allocator, 'a', c_line_payload_len);
    try exact_then_visible_cr_then_nul_then_next_line.append(std.testing.allocator, '\r');
    try exact_then_visible_cr_then_nul_then_next_line.append(std.testing.allocator, 0);
    try exact_then_visible_cr_then_nul_then_next_line.append(std.testing.allocator, 'b');
    try exact_then_visible_cr_then_nul_then_next_line.append(std.testing.allocator, '\n');
    try exact_then_visible_cr_then_nul_then_next_line.appendSlice(std.testing.allocator, "x\n");

    var capture = try Capture(16384).init(std.testing.allocator);
    defer capture.deinit();
    try gen.runGenksymsCrc(exact_then_visible_cr_then_nul_then_next_line.items, &capture);

    const exact_crc = try std.fmt.allocPrint(
        std.testing.allocator,
        "0x{x:0>8}",
        .{gen.crc32(exact_then_visible_cr_then_nul_then_next_line.items[0..c_line_payload_len])},
    );
    defer std.testing.allocator.free(exact_crc);
    const blank_visible_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("\r")});
    defer std.testing.allocator.free(blank_visible_crc);
    const untruncated_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("\r\x00b")});
    defer std.testing.allocator.free(untruncated_crc);
    const trailing_only_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("b")});
    defer std.testing.allocator.free(trailing_only_crc);
    const next_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("x")});
    defer std.testing.allocator.free(next_crc);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, exact_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, blank_visible_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, untruncated_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, trailing_only_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, next_crc) != null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "crc_hex") == 2);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"\\r\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"b\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"x\"") != null);
}
