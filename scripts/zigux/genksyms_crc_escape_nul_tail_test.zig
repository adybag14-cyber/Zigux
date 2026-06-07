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

fn crcHex(allocator: std.mem.Allocator, bytes: []const u8) ![]const u8 {
    return try std.fmt.allocPrint(allocator, "0x{x:0>8}", .{gen.crc32(bytes)});
}

test "runGenksymsCrc escapes visible ESC before NUL while hiding the tail" {
    const visible = "prefix" ++ [_]u8{0x1b} ++ "escape";
    const hidden = "hidden" ++ [_]u8{0x1b} ++ "tail";
    const next = "next" ++ [_]u8{0x1b} ++ "visible";

    const input = visible ++ [_]u8{0} ++ hidden ++ "\n" ++ next ++ "\n";

    var capture = try Capture(512).init(std.testing.allocator);
    defer capture.deinit();
    try gen.runGenksymsCrc(input, &capture);

    const visible_crc = try crcHex(std.testing.allocator, visible);
    defer std.testing.allocator.free(visible_crc);
    const hidden_crc = try crcHex(std.testing.allocator, hidden);
    defer std.testing.allocator.free(hidden_crc);
    const next_crc = try crcHex(std.testing.allocator, next);
    defer std.testing.allocator.free(next_crc);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"prefix\\u001bescape\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, visible_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "hidden") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\\u001btail") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, hidden_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"next\\u001bvisible\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, next_crc) != null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "crc_hex") == 2);
}
