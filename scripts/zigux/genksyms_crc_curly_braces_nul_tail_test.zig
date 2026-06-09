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

test "runGenksymsCrc keeps curly-brace-prefixed visible bytes before NUL" {
    const left_visible = "{visible{type";
    const right_visible = "}visible}type";
    const next_visible = "{next}record";
    const left_hidden = "{hidden{tail";
    const right_hidden = "}hidden}tail";
    const input = left_visible ++ "\x00" ++ left_hidden ++ "\n" ++
        right_visible ++ "\x00" ++ right_hidden ++ "\n" ++
        next_visible ++ "\n";

    var capture = try Capture(768).init(std.testing.allocator);
    defer capture.deinit();
    try genksyms_crc.runGenksymsCrc(input, &capture);

    const left_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{genksyms_crc.crc32(left_visible)});
    defer std.testing.allocator.free(left_crc);
    const right_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{genksyms_crc.crc32(right_visible)});
    defer std.testing.allocator.free(right_crc);
    const next_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{genksyms_crc.crc32(next_visible)});
    defer std.testing.allocator.free(next_crc);
    const left_hidden_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{genksyms_crc.crc32(left_hidden)});
    defer std.testing.allocator.free(left_hidden_crc);
    const right_hidden_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{genksyms_crc.crc32(right_hidden)});
    defer std.testing.allocator.free(right_hidden_crc);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"{visible{type\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"}visible}type\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"{next}record\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, left_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, right_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, next_crc) != null);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, left_hidden) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, right_hidden) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, left_hidden_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, right_hidden_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\\u007b") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\\u007d") == null);
    try std.testing.expectEqual(@as(usize, 3), std.mem.count(u8, capture.list.items, "crc_hex"));
}
