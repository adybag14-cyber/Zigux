const std = @import("std");
const gen = @import("./genksyms_crc.zig");

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

test "lane19 exact-buffer visible-CR control NUL split trims trailing carriage returns before the embedded NUL and keeps the next line" {
    var exact_then_visible_cr_controls_and_trailing_cr_then_nul_then_next_line = try std.ArrayList(u8).initCapacity(std.testing.allocator, gen.c_line_payload_len + 12);
    defer exact_then_visible_cr_controls_and_trailing_cr_then_nul_then_next_line.deinit(std.testing.allocator);
    try exact_then_visible_cr_controls_and_trailing_cr_then_nul_then_next_line.appendNTimes(std.testing.allocator, 'a', gen.c_line_payload_len);
    try exact_then_visible_cr_controls_and_trailing_cr_then_nul_then_next_line.append(std.testing.allocator, '\r');
    try exact_then_visible_cr_controls_and_trailing_cr_then_nul_then_next_line.append(std.testing.allocator, '\x08');
    try exact_then_visible_cr_controls_and_trailing_cr_then_nul_then_next_line.append(std.testing.allocator, '\x0c');
    try exact_then_visible_cr_controls_and_trailing_cr_then_nul_then_next_line.append(std.testing.allocator, '\x01');
    try exact_then_visible_cr_controls_and_trailing_cr_then_nul_then_next_line.append(std.testing.allocator, 'b');
    try exact_then_visible_cr_controls_and_trailing_cr_then_nul_then_next_line.append(std.testing.allocator, '\r');
    try exact_then_visible_cr_controls_and_trailing_cr_then_nul_then_next_line.append(std.testing.allocator, '\r');
    try exact_then_visible_cr_controls_and_trailing_cr_then_nul_then_next_line.append(std.testing.allocator, 0);
    try exact_then_visible_cr_controls_and_trailing_cr_then_nul_then_next_line.append(std.testing.allocator, 'c');
    try exact_then_visible_cr_controls_and_trailing_cr_then_nul_then_next_line.append(std.testing.allocator, '\n');
    try exact_then_visible_cr_controls_and_trailing_cr_then_nul_then_next_line.appendSlice(std.testing.allocator, "x\n");

    var capture = try Capture(16384).init(std.testing.allocator);
    defer capture.deinit();
    try gen.runGenksymsCrc(exact_then_visible_cr_controls_and_trailing_cr_then_nul_then_next_line.items, &capture);

    const exact_crc = try std.fmt.allocPrint(
        std.testing.allocator,
        "0x{x:0>8}",
        .{gen.crc32(exact_then_visible_cr_controls_and_trailing_cr_then_nul_then_next_line.items[0..gen.c_line_payload_len])},
    );
    defer std.testing.allocator.free(exact_crc);
    const normalized_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("\r\x08\x0c\x01b")});
    defer std.testing.allocator.free(normalized_crc);
    const trailing_cr_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("\r\x08\x0c\x01b\r\r")});
    defer std.testing.allocator.free(trailing_cr_crc);
    const controls_without_cr_prefix_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("\x08\x0c\x01b")});
    defer std.testing.allocator.free(controls_without_cr_prefix_crc);
    const trimmed_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("b")});
    defer std.testing.allocator.free(trimmed_crc);
    const suffix_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("c")});
    defer std.testing.allocator.free(suffix_crc);
    const untruncated_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("\r\x08\x0c\x01b\r\r\x00c")});
    defer std.testing.allocator.free(untruncated_crc);
    const next_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("x")});
    defer std.testing.allocator.free(next_crc);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, exact_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, normalized_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, trailing_cr_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, controls_without_cr_prefix_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, trimmed_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, suffix_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, untruncated_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, next_crc) != null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "crc_hex") == 3);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"\\r\\b\\f\\u0001b\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"\\b\\f\\u0001b\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"\\r\\b\\f\\u0001b\\r\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"b\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"c\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"x\"") != null);
}
