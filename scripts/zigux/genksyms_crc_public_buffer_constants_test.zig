const std = @import("std");
const gen = @import("genksyms_crc.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) !Capture {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, gen.c_line_payload_len + 256),
            .allocator = allocator,
        };
    }

    fn deinit(self: *Capture) void {
        self.list.deinit(self.allocator);
    }

    pub fn writeAll(self: *Capture, bytes: []const u8) !void {
        try self.list.appendSlice(self.allocator, bytes);
    }

    pub fn print(self: *Capture, comptime fmt: []const u8, args: anytype) !void {
        const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
        defer self.allocator.free(rendered);
        try self.list.appendSlice(self.allocator, rendered);
    }

    pub fn writeByte(self: *Capture, byte: u8) !void {
        try self.list.append(self.allocator, byte);
    }
};

test "public C buffer constants drive exact-buffer split proof" {
    try std.testing.expectEqual(@as(usize, 4096), gen.c_line_buffer_len);
    try std.testing.expectEqual(gen.c_line_buffer_len - 1, gen.c_line_payload_len);

    var input = try std.ArrayList(u8).initCapacity(std.testing.allocator, gen.c_line_payload_len + 3);
    defer input.deinit(std.testing.allocator);
    try input.appendNTimes(std.testing.allocator, 'a', gen.c_line_payload_len);
    try input.appendSlice(std.testing.allocator, "b\n");

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();
    try gen.runGenksymsCrc(input.items, &capture);

    const exact_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32(input.items[0..gen.c_line_payload_len])});
    defer std.testing.allocator.free(exact_crc);
    const continuation_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("b")});
    defer std.testing.allocator.free(continuation_crc);
    const unsplit_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32(input.items[0 .. input.items.len - 1])});
    defer std.testing.allocator.free(unsplit_crc);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, exact_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, continuation_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, unsplit_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"b\"") != null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "crc_hex") == 2);
}
