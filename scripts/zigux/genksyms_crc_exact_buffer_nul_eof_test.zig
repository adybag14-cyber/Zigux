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

test "lane19 exact-buffer EOF skips a NUL-prefixed continuation" {
    var exact_then_nul_tail = try std.ArrayList(u8).initCapacity(std.testing.allocator, c_line_payload_len + 3);
    defer exact_then_nul_tail.deinit(std.testing.allocator);
    try exact_then_nul_tail.appendNTimes(std.testing.allocator, 'a', c_line_payload_len);
    try exact_then_nul_tail.append(std.testing.allocator, 0);
    try exact_then_nul_tail.append(std.testing.allocator, 'b');
    try exact_then_nul_tail.append(std.testing.allocator, 'c');

    var capture = try Capture(12288).init(std.testing.allocator);
    defer capture.deinit();
    try gen.runGenksymsCrc(exact_then_nul_tail.items, &capture);

    const exact_crc = try std.fmt.allocPrint(
        std.testing.allocator,
        "0x{x:0>8}",
        .{gen.crc32(exact_then_nul_tail.items[0..c_line_payload_len])},
    );
    defer std.testing.allocator.free(exact_crc);
    const skipped_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("bc")});
    defer std.testing.allocator.free(skipped_crc);
    const unsplit_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32(exact_then_nul_tail.items)});
    defer std.testing.allocator.free(unsplit_crc);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, exact_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, skipped_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, unsplit_crc) == null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "crc_hex") == 1);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"bc\"") == null);
}
