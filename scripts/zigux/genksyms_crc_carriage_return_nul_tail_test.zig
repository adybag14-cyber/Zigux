const std = @import("std");
const gen = @import("genksyms_crc.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) !Capture {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 512),
            .allocator = allocator,
        };
    }

    fn deinit(self: *Capture) void {
        self.list.deinit(self.allocator);
    }

    pub fn writeAll(self: *Capture, bytes: []const u8) !void {
        try self.list.appendSlice(self.allocator, bytes);
    }

    pub fn writeByte(self: *Capture, byte: u8) !void {
        try self.list.append(self.allocator, byte);
    }

    pub fn print(self: *Capture, comptime fmt: []const u8, args: anytype) !void {
        const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
        defer self.allocator.free(rendered);
        try self.writeAll(rendered);
    }
};

test "runGenksymsCrc escapes visible carriage returns before NUL tails" {
    const hidden_tail = "hidden\rcrc";
    const first_visible = "left\rright";
    const second_visible = "next\rvisible";
    const input = first_visible ++ "\x00" ++ hidden_tail ++ "\n" ++ second_visible ++ "\x00ignored\r\n";

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();
    try gen.runGenksymsCrc(input, &capture);

    const first_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32(first_visible)});
    defer std.testing.allocator.free(first_crc);
    const second_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32(second_visible)});
    defer std.testing.allocator.free(second_crc);
    const hidden_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32(hidden_tail)});
    defer std.testing.allocator.free(hidden_crc);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"left\\rright\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"next\\rvisible\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, first_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, second_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, hidden_tail) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, hidden_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "ignored") == null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "crc_hex") == 2);
}
