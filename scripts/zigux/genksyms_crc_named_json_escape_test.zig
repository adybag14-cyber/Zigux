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

test "runGenksymsCrc emits named JSON escapes for backspace and form feed" {
    const backspace_record = "left" ++ [_]u8{0x08} ++ "right";
    const form_feed_record = "form" ++ [_]u8{0x0c} ++ "feed";
    const input = backspace_record ++ "\n" ++ form_feed_record ++ "\n";

    var capture = try Capture(256).init(std.testing.allocator);
    defer capture.deinit();
    try gen.runGenksymsCrc(input, &capture);

    const backspace_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32(backspace_record)});
    defer std.testing.allocator.free(backspace_crc);
    const form_feed_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32(form_feed_record)});
    defer std.testing.allocator.free(form_feed_crc);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"left\\bright\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"form\\ffeed\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, backspace_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, form_feed_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\\u0008") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\\u000c") == null);
    try std.testing.expect(std.mem.indexOfScalar(u8, capture.list.items, 0x08) == null);
    try std.testing.expect(std.mem.indexOfScalar(u8, capture.list.items, 0x0c) == null);
}
