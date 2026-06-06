const std = @import("std");
const genksyms_crc = @import("genksyms_crc.zig");

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

test "runGenksymsCrc escapes visible file separator while hiding NUL tail" {
    const visible = "alpha \x1c beta";
    const hidden = "hidden_file_separator_tail";

    var input = try std.ArrayList(u8).initCapacity(
        std.testing.allocator,
        visible.len + hidden.len + "after\n".len + 2,
    );
    defer input.deinit(std.testing.allocator);
    try input.appendSlice(std.testing.allocator, visible);
    try input.append(std.testing.allocator, 0);
    try input.appendSlice(std.testing.allocator, hidden);
    try input.append(std.testing.allocator, '\n');
    try input.appendSlice(std.testing.allocator, "after\n");

    var capture = try Capture(256).init(std.testing.allocator);
    defer capture.deinit();
    try genksyms_crc.runGenksymsCrc(input.items, &capture);

    const visible_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{genksyms_crc.crc32(visible)});
    defer std.testing.allocator.free(visible_crc);
    const hidden_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{genksyms_crc.crc32(hidden)});
    defer std.testing.allocator.free(hidden_crc);
    const after_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{genksyms_crc.crc32("after")});
    defer std.testing.allocator.free(after_crc);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"alpha \\u001c beta\"") != null);
    try std.testing.expect(std.mem.indexOfScalar(u8, capture.list.items, 0x1c) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, visible_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, hidden) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, hidden_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\\u0000") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"after\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, after_crc) != null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "crc_hex") == 2);
}
