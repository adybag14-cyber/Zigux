const std = @import("std");
const gen = @import("genksyms_crc.zig");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOmits(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

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

test "runGenksymsCrc keeps visible high-bit bytes before NUL only" {
    const input = "hi\x80\xffZ\x00hidden\x80\xff\nnext\xff\n";

    var capture = try Capture(256).init(std.testing.allocator);
    defer capture.deinit();
    try gen.runGenksymsCrc(input, &capture);

    const first_marker = [_]u8{ '"', 'i', 'n', 'p', 'u', 't', '"', ':', '"', 'h', 'i', 0x80, 0xff, 'Z', '"' };
    const second_marker = [_]u8{ '"', 'i', 'n', 'p', 'u', 't', '"', ':', '"', 'n', 'e', 'x', 't', 0xff, '"' };
    try expectContains(capture.list.items, &first_marker);
    try expectContains(capture.list.items, &second_marker);

    const hidden_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("hidden\x80\xff")});
    defer std.testing.allocator.free(hidden_crc);
    try expectOmits(capture.list.items, "hidden");
    try expectOmits(capture.list.items, hidden_crc);

    try expectOmits(capture.list.items, "\\u0080");
    try expectOmits(capture.list.items, "\\u00ff");
    try std.testing.expectEqual(@as(usize, 2), std.mem.count(u8, capture.list.items, "crc_hex"));
}
