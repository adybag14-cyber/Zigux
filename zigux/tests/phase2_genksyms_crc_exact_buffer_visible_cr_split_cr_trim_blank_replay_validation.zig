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

test "lane19 exact-buffer split replay trims trailing carriage returns, keeps visible leading carriage returns, and skips a following blank continuation" {
    var exact_then_visible_cr_then_trimmed_blank_then_line = try std.ArrayList(u8).initCapacity(std.testing.allocator, c_line_payload_len + 10);
    defer exact_then_visible_cr_then_trimmed_blank_then_line.deinit(std.testing.allocator);
    try exact_then_visible_cr_then_trimmed_blank_then_line.appendNTimes(std.testing.allocator, 'a', c_line_payload_len);
    try exact_then_visible_cr_then_trimmed_blank_then_line.append(std.testing.allocator, '\r');
    try exact_then_visible_cr_then_trimmed_blank_then_line.append(std.testing.allocator, '\r');
    try exact_then_visible_cr_then_trimmed_blank_then_line.append(std.testing.allocator, 'b');
    try exact_then_visible_cr_then_trimmed_blank_then_line.append(std.testing.allocator, '\r');
    try exact_then_visible_cr_then_trimmed_blank_then_line.append(std.testing.allocator, '\r');
    try exact_then_visible_cr_then_trimmed_blank_then_line.append(std.testing.allocator, '\n');
    try exact_then_visible_cr_then_trimmed_blank_then_line.append(std.testing.allocator, '\r');
    try exact_then_visible_cr_then_trimmed_blank_then_line.append(std.testing.allocator, '\n');
    try exact_then_visible_cr_then_trimmed_blank_then_line.appendSlice(std.testing.allocator, "x\n");

    var capture = try Capture(16384).init(std.testing.allocator);
    defer capture.deinit();
    try gen.runGenksymsCrc(exact_then_visible_cr_then_trimmed_blank_then_line.items, &capture);

    const exact_crc = try std.fmt.allocPrint(
        std.testing.allocator,
        "0x{x:0>8}",
        .{gen.crc32(exact_then_visible_cr_then_trimmed_blank_then_line.items[0..c_line_payload_len])},
    );
    defer std.testing.allocator.free(exact_crc);
    const normalized_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("\r\rb")});
    defer std.testing.allocator.free(normalized_crc);
    const trailing_cr_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("\r\rb\r\r")});
    defer std.testing.allocator.free(trailing_cr_crc);
    const trimmed_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("b")});
    defer std.testing.allocator.free(trimmed_crc);
    const blank_visible_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("\r")});
    defer std.testing.allocator.free(blank_visible_crc);
    const next_line_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("x")});
    defer std.testing.allocator.free(next_line_crc);
    const unsplit_crc = try std.fmt.allocPrint(
        std.testing.allocator,
        "0x{x:0>8}",
        .{gen.crc32(exact_then_visible_cr_then_trimmed_blank_then_line.items[0 .. c_line_payload_len + 5])},
    );
    defer std.testing.allocator.free(unsplit_crc);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, exact_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, normalized_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, trailing_cr_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, trimmed_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, blank_visible_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, next_line_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, unsplit_crc) == null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "crc_hex") == 3);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"\\r\\rb\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"\\r\\rb\\r\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"b\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"\\r\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"\\n\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"x\"") != null);
}
