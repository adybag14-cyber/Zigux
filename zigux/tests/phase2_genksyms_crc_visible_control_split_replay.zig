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

test "lane19 visible control split replay preserves leading low control bytes before the next line" {
    var split_then_visible_controls_and_next_line = try std.ArrayList(u8).initCapacity(std.testing.allocator, c_line_payload_len + 8);
    defer split_then_visible_controls_and_next_line.deinit(std.testing.allocator);
    try split_then_visible_controls_and_next_line.appendNTimes(std.testing.allocator, 'a', c_line_payload_len);
    try split_then_visible_controls_and_next_line.append(std.testing.allocator, '\x08');
    try split_then_visible_controls_and_next_line.append(std.testing.allocator, '\x0c');
    try split_then_visible_controls_and_next_line.append(std.testing.allocator, '\x01');
    try split_then_visible_controls_and_next_line.append(std.testing.allocator, 'b');
    try split_then_visible_controls_and_next_line.append(std.testing.allocator, '\n');
    try split_then_visible_controls_and_next_line.appendSlice(std.testing.allocator, "x\n");

    var capture = try Capture(16384).init(std.testing.allocator);
    defer capture.deinit();
    try gen.runGenksymsCrc(split_then_visible_controls_and_next_line.items, &capture);

    const exact_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32(split_then_visible_controls_and_next_line.items[0..c_line_payload_len])});
    defer std.testing.allocator.free(exact_crc);
    const control_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("\x08\x0c\x01b")});
    defer std.testing.allocator.free(control_crc);
    const trimmed_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("b")});
    defer std.testing.allocator.free(trimmed_crc);
    const unsplit_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32(split_then_visible_controls_and_next_line.items[0 .. c_line_payload_len + 4])});
    defer std.testing.allocator.free(unsplit_crc);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, exact_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, control_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, trimmed_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, unsplit_crc) == null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "crc_hex") == 3);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"\\b\\f\\u0001b\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"b\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"x\"") != null);
}
