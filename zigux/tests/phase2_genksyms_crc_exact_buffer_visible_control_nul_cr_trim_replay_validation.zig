const std = @import("std");
const gen = @import("genksyms_crc");

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

test "lane19 exact-buffer split replay preserves visible low control bytes while trimming trailing carriage returns before an embedded NUL" {
    var exact_then_control_then_cr_then_nul = try std.ArrayList(u8).initCapacity(std.testing.allocator, c_line_payload_len + 12);
    defer exact_then_control_then_cr_then_nul.deinit(std.testing.allocator);
    try exact_then_control_then_cr_then_nul.appendNTimes(std.testing.allocator, 'a', c_line_payload_len);
    try exact_then_control_then_cr_then_nul.append(std.testing.allocator, '\x08');
    try exact_then_control_then_cr_then_nul.append(std.testing.allocator, '\x0c');
    try exact_then_control_then_cr_then_nul.append(std.testing.allocator, '\x01');
    try exact_then_control_then_cr_then_nul.append(std.testing.allocator, 'b');
    try exact_then_control_then_cr_then_nul.append(std.testing.allocator, '\r');
    try exact_then_control_then_cr_then_nul.append(std.testing.allocator, '\r');
    try exact_then_control_then_cr_then_nul.append(std.testing.allocator, 0);
    try exact_then_control_then_cr_then_nul.append(std.testing.allocator, 'c');
    try exact_then_control_then_cr_then_nul.append(std.testing.allocator, '\n');
    try exact_then_control_then_cr_then_nul.appendSlice(std.testing.allocator, "x\n");

    var capture = try Capture(16384).init(std.testing.allocator);
    defer capture.deinit();
    try gen.runGenksymsCrc(exact_then_control_then_cr_then_nul.items, &capture);

    const exact_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32(exact_then_control_then_cr_then_nul.items[0..c_line_payload_len])});
    defer std.testing.allocator.free(exact_crc);
    const normalized_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("\x08\x0c\x01b")});
    defer std.testing.allocator.free(normalized_crc);
    const trailing_cr_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("\x08\x0c\x01b\r\r")});
    defer std.testing.allocator.free(trailing_cr_crc);
    const untruncated_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("\x08\x0c\x01b\r\r\x00c")});
    defer std.testing.allocator.free(untruncated_crc);
    const trimmed_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("b")});
    defer std.testing.allocator.free(trimmed_crc);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, exact_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, normalized_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, trailing_cr_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, untruncated_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, trimmed_crc) == null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "crc_hex") == 3);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"\\b\\f\\u0001b\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"\\b\\f\\u0001b\\r") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"x\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"b\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"c\"") == null);
}
