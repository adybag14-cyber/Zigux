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

test "lane19 exact-buffer EOF replay preserves visible low control bytes plus leading carriage returns in a continuation" {
    var exact_then_controls_and_leading_cr = try std.ArrayList(u8).initCapacity(std.testing.allocator, c_line_payload_len + 6);
    defer exact_then_controls_and_leading_cr.deinit(std.testing.allocator);
    try exact_then_controls_and_leading_cr.appendNTimes(std.testing.allocator, 'a', c_line_payload_len);
    try exact_then_controls_and_leading_cr.append(std.testing.allocator, '\x08');
    try exact_then_controls_and_leading_cr.append(std.testing.allocator, '\x0c');
    try exact_then_controls_and_leading_cr.append(std.testing.allocator, '\x01');
    try exact_then_controls_and_leading_cr.append(std.testing.allocator, '\r');
    try exact_then_controls_and_leading_cr.append(std.testing.allocator, '\r');
    try exact_then_controls_and_leading_cr.append(std.testing.allocator, 'b');

    var capture = try Capture(16384).init(std.testing.allocator);
    defer capture.deinit();
    try gen.runGenksymsCrc(exact_then_controls_and_leading_cr.items, &capture);

    const exact_crc = try std.fmt.allocPrint(
        std.testing.allocator,
        "0x{x:0>8}",
        .{gen.crc32(exact_then_controls_and_leading_cr.items[0..c_line_payload_len])},
    );
    defer std.testing.allocator.free(exact_crc);
    const combined_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("\x08\x0c\x01\r\rb")});
    defer std.testing.allocator.free(combined_crc);
    const control_only_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("\x08\x0c\x01b")});
    defer std.testing.allocator.free(control_only_crc);
    const leading_cr_only_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("\r\rb")});
    defer std.testing.allocator.free(leading_cr_only_crc);
    const plain_b_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("b")});
    defer std.testing.allocator.free(plain_b_crc);
    const unsplit_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32(exact_then_controls_and_leading_cr.items)});
    defer std.testing.allocator.free(unsplit_crc);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, exact_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, combined_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, control_only_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, leading_cr_only_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, plain_b_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, unsplit_crc) == null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "crc_hex") == 2);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"\\b\\f\\u0001\\r\\rb\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"\\b\\f\\u0001b\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"\\r\\rb\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"b\"") == null);
}
