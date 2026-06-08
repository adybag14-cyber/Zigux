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

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectMissing(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn crcHex(allocator: std.mem.Allocator, text: []const u8) ![]u8 {
    return std.fmt.allocPrint(allocator, "0x{x:0>8}", .{gen.crc32(text)});
}

test "runGenksymsCrc preserves visible asterisks before embedded NUL" {
    var input = try std.ArrayList(u8).initCapacity(std.testing.allocator, 64);
    defer input.deinit(std.testing.allocator);
    try input.appendSlice(std.testing.allocator, "*visible*type");
    try input.append(std.testing.allocator, 0);
    try input.appendSlice(std.testing.allocator, "hidden*tail\n*next*record\n");

    var capture = try Capture(256).init(std.testing.allocator);
    defer capture.deinit();
    try gen.runGenksymsCrc(input.items, &capture);

    const visible_crc = try crcHex(std.testing.allocator, "*visible*type");
    defer std.testing.allocator.free(visible_crc);
    const next_crc = try crcHex(std.testing.allocator, "*next*record");
    defer std.testing.allocator.free(next_crc);
    const hidden_crc = try crcHex(std.testing.allocator, "hidden*tail");
    defer std.testing.allocator.free(hidden_crc);

    try expectContains(capture.list.items, "\"input\":\"*visible*type\"");
    try expectContains(capture.list.items, visible_crc);
    try expectContains(capture.list.items, "\"input\":\"*next*record\"");
    try expectContains(capture.list.items, next_crc);

    try expectMissing(capture.list.items, "hidden*tail");
    try expectMissing(capture.list.items, hidden_crc);
    try std.testing.expect(std.mem.indexOfScalar(u8, capture.list.items, 0) == null);
    try std.testing.expectEqual(@as(usize, 2), std.mem.count(u8, capture.list.items, "crc_hex"));
}
