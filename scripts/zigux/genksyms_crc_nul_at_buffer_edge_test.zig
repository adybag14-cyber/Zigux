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

test "lane19 NUL at the C payload edge truncates before skipped newline continuation" {
    var input = try std.ArrayList(u8).initCapacity(std.testing.allocator, c_line_payload_len + 4);
    defer input.deinit(std.testing.allocator);
    try input.appendNTimes(std.testing.allocator, 'a', c_line_payload_len - 1);
    try input.append(std.testing.allocator, 0);
    try input.append(std.testing.allocator, '\n');
    try input.appendSlice(std.testing.allocator, "x\n");

    var capture = try Capture(16384).init(std.testing.allocator);
    defer capture.deinit();
    try gen.runGenksymsCrc(input.items, &capture);

    const visible_prefix = input.items[0 .. c_line_payload_len - 1];
    const visible_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32(visible_prefix)});
    defer std.testing.allocator.free(visible_crc);
    const hidden_boundary_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32(input.items[0..c_line_payload_len])});
    defer std.testing.allocator.free(hidden_boundary_crc);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, visible_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, hidden_boundary_crc) == null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "crc_hex") == 2);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"aa") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"x\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\\u0000") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"\\n\"") == null);
}
