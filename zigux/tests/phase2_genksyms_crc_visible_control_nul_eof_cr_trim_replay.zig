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

test "lane19 visible control EOF replay preserves leading low control bytes before a NUL while trimming trailing carriage returns" {
    var split_then_control_nul_eof_cr = try std.ArrayList(u8).initCapacity(std.testing.allocator, c_line_payload_len + 9);
    defer split_then_control_nul_eof_cr.deinit(std.testing.allocator);
    try split_then_control_nul_eof_cr.appendNTimes(std.testing.allocator, 'a', c_line_payload_len);
    try split_then_control_nul_eof_cr.append(std.testing.allocator, '\x08');
    try split_then_control_nul_eof_cr.append(std.testing.allocator, '\x0c');
    try split_then_control_nul_eof_cr.append(std.testing.allocator, '\x01');
    try split_then_control_nul_eof_cr.append(std.testing.allocator, 'b');
    try split_then_control_nul_eof_cr.append(std.testing.allocator, '\r');
    try split_then_control_nul_eof_cr.append(std.testing.allocator, '\r');
    try split_then_control_nul_eof_cr.append(std.testing.allocator, 0);
    try split_then_control_nul_eof_cr.append(std.testing.allocator, 'c');

    var capture = try Capture(16384).init(std.testing.allocator);
    defer capture.deinit();
    try gen.runGenksymsCrc(split_then_control_nul_eof_cr.items, &capture);

    const exact_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32(split_then_control_nul_eof_cr.items[0..c_line_payload_len])});
    defer std.testing.allocator.free(exact_crc);
    const normalized_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("\x08\x0c\x01b")});
    defer std.testing.allocator.free(normalized_crc);
    const trailing_cr_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("\x08\x0c\x01b\r\r")});
    defer std.testing.allocator.free(trailing_cr_crc);
    const untruncated_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("\x08\x0c\x01b\r\r\x00c")});
    defer std.testing.allocator.free(untruncated_crc);
    const trimmed_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("b")});
    defer std.testing.allocator.free(trimmed_crc);
    const unsplit_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32(split_then_control_nul_eof_cr.items)});
    defer std.testing.allocator.free(unsplit_crc);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, exact_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, normalized_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, trailing_cr_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, untruncated_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, trimmed_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, unsplit_crc) == null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "crc_hex") == 2);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"\\b\\f\\u0001b\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"\\b\\f\\u0001b\\r\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"b\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"c\"") == null);
}
