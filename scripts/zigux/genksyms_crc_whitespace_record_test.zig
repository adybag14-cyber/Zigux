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

test "runGenksymsCrc preserves visible whitespace records while skipping CR-only records" {
    const spaced_record = " \t ";
    const tab_record = "\t";

    var capture = try Capture(256).init(std.testing.allocator);
    defer capture.deinit();
    try crc.runGenksymsCrc(spaced_record ++ "\n\r\n" ++ tab_record ++ "\r\n", &capture);

    const spaced_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{crc.crc32(spaced_record)});
    defer std.testing.allocator.free(spaced_crc);
    const tab_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{crc.crc32(tab_record)});
    defer std.testing.allocator.free(tab_crc);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\" \\t \"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"\\t\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, spaced_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, tab_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"\"") == null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "crc_hex") == 2);
}
