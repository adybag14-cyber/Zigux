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

test "runGenksymsCrc preserves visible DEL bytes while hiding NUL tails" {
    var capture = try Capture(256).init(std.testing.allocator);
    defer capture.deinit();

    const visible_del = "visible\x7fdel";
    const later_del = "later\x7fvisible";
    const hidden_tail = "hidden\x7fcrc";
    try genksyms_crc.runGenksymsCrc(visible_del ++ "\x00" ++ hidden_tail ++ "\n" ++ later_del ++ "\n", &capture);

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "{{\"cases\":[{{\"input\":\"" ++ visible_del ++ "\",\"crc_hex\":\"0x{x:0>8}\"}},{{\"input\":\"" ++ later_del ++ "\",\"crc_hex\":\"0x{x:0>8}\"}}]}}\n",
        .{
            genksyms_crc.crc32(visible_del),
            genksyms_crc.crc32(later_del),
        },
    );
    defer std.testing.allocator.free(expected);

    const hidden_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{genksyms_crc.crc32(hidden_tail)});
    defer std.testing.allocator.free(hidden_crc);

    try std.testing.expectEqualStrings(expected, capture.list.items);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, hidden_tail) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, hidden_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\\u007f") == null);
    try std.testing.expect(std.mem.indexOfScalar(u8, capture.list.items, 0x7f) != null);
}
