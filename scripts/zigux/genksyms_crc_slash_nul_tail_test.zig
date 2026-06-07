const std = @import("std");
const crc = @import("genksyms_crc.zig");

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

test "runGenksymsCrc keeps visible slash bytes unescaped before hiding the NUL tail" {
    var capture = try Capture(256).init(std.testing.allocator);
    defer capture.deinit();

    try crc.runGenksymsCrc("dir/name/member\x00hidden/slash/tail\nnext/record\n", &capture);

    const visible_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{crc.crc32("dir/name/member")});
    defer std.testing.allocator.free(visible_crc);
    const hidden_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{crc.crc32("hidden/slash/tail")});
    defer std.testing.allocator.free(hidden_crc);
    const next_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{crc.crc32("next/record")});
    defer std.testing.allocator.free(next_crc);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"dir/name/member\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"dir\\/name\\/member\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, visible_crc) != null);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "hidden/slash/tail") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, hidden_crc) == null);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"next/record\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, next_crc) != null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "\"crc_hex\"") == 2);
}
