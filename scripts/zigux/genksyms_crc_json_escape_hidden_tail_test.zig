const std = @import("std");
const genksyms_crc = @import("genksyms_crc.zig");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) @This() {
        return .{
            .list = std.ArrayList(u8).empty,
            .allocator = allocator,
        };
    }

    fn deinit(self: *@This()) void {
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

test "genksyms CRC JSON escapes visible bytes while excluding hidden NUL tails" {
    const visible = "quote \" and slash \\ plus tab\t";
    const hidden = "hidden \"\\\t bytes";
    const next = "next visible";

    var capture = Capture.init(std.testing.allocator);
    defer capture.deinit();

    try genksyms_crc.runGenksymsCrc(
        visible ++ "\x00" ++ hidden ++ "\n" ++ next ++ "\n",
        &capture,
    );

    const visible_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{genksyms_crc.crc32(visible)});
    defer std.testing.allocator.free(visible_crc);
    const hidden_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{genksyms_crc.crc32(hidden)});
    defer std.testing.allocator.free(hidden_crc);

    try expectContains(capture.list.items, "\"input\":\"quote \\\" and slash \\\\ plus tab\\t\"");
    try expectContains(capture.list.items, visible_crc);
    try expectContains(capture.list.items, "\"input\":\"next visible\"");
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, hidden) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, hidden_crc) == null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "crc_hex") == 2);
}
