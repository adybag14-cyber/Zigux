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

test "runGenksymsCrc preserves visible tilde chunks before hidden NUL tails" {
    const hidden_tail_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("hidden~tail")});
    defer std.testing.allocator.free(hidden_tail_crc);
    const first_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("~visible")});
    defer std.testing.allocator.free(first_crc);
    const next_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("~next")});
    defer std.testing.allocator.free(next_crc);

    var capture = try Capture(256).init(std.testing.allocator);
    defer capture.deinit();
    try gen.runGenksymsCrc("~visible\x00hidden~tail\n~next\n", &capture);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"~visible\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, first_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"~next\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, next_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "hidden~tail") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, hidden_tail_crc) == null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "\"crc_hex\"") == 2);
}
