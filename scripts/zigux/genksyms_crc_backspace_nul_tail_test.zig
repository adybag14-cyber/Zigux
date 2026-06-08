const std = @import("std");
const gen = @import("genksyms_crc.zig");

fn Capture(comptime capacity: usize) type {
    return struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, capacity),
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
}

test "genksyms CRC escapes visible backspace while hiding the NUL tail" {
    const visible_with_backspace = "sym\x08visible";
    const hidden_tail = "hidden\x08tail";
    const later_visible = "later\x08line";

    var input = try std.ArrayList(u8).initCapacity(std.testing.allocator, visible_with_backspace.len + hidden_tail.len + later_visible.len + 4);
    defer input.deinit(std.testing.allocator);
    try input.appendSlice(std.testing.allocator, visible_with_backspace);
    try input.append(std.testing.allocator, 0);
    try input.appendSlice(std.testing.allocator, hidden_tail);
    try input.append(std.testing.allocator, '\n');
    try input.appendSlice(std.testing.allocator, later_visible);
    try input.append(std.testing.allocator, '\n');

    var capture = try Capture(256).init(std.testing.allocator);
    defer capture.deinit();
    try gen.runGenksymsCrc(input.items, &capture);

    const visible_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32(visible_with_backspace)});
    defer std.testing.allocator.free(visible_crc);
    const hidden_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32(hidden_tail)});
    defer std.testing.allocator.free(hidden_crc);
    const later_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32(later_visible)});
    defer std.testing.allocator.free(later_crc);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"sym\\bvisible\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, visible_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "hidden") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, hidden_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"later\\bline\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, later_crc) != null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "crc_hex") == 2);
}
