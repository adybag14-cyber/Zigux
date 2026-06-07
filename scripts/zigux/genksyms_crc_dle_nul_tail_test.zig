const std = @import("std");
const gen = @import("./genksyms_crc.zig");

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

test "runGenksymsCrc escapes visible DLE before hiding a NUL tail" {
    const visible = "prefix" ++ [_]u8{0x10} ++ "dle";
    const input = visible ++ [_]u8{0} ++ "hidden" ++ [_]u8{0x10} ++ "tail\nnext\n";

    var capture = try Capture(512).init(std.testing.allocator);
    defer capture.deinit();
    try gen.runGenksymsCrc(input, &capture);

    const visible_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32(visible)});
    defer std.testing.allocator.free(visible_crc);
    const hidden_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("hidden" ++ [_]u8{0x10} ++ "tail")});
    defer std.testing.allocator.free(hidden_crc);
    const next_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("next")});
    defer std.testing.allocator.free(next_crc);

    try expectContains(capture.list.items, "\"input\":\"prefix\\u0010dle\"");
    try expectContains(capture.list.items, visible_crc);
    try expectContains(capture.list.items, "\"input\":\"next\"");
    try expectContains(capture.list.items, next_crc);

    try expectMissing(capture.list.items, "hidden");
    try expectMissing(capture.list.items, "tail");
    try expectMissing(capture.list.items, hidden_crc);
    try expectMissing(capture.list.items, "\\u0000");
    try std.testing.expect(std.mem.count(u8, capture.list.items, "crc_hex") == 2);
}
