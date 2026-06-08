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

test "genksyms crc keeps visible caret chunks before nul tail" {
    const visible_first = "^visible";
    const hidden_tail = "^hidden-caret-tail";
    const visible_next = "^next";

    var capture = try Capture(256).init(std.testing.allocator);
    defer capture.deinit();

    try genksyms_crc.runGenksymsCrc(visible_first ++ "\x00" ++ hidden_tail ++ "\n" ++ visible_next ++ "\n", &capture);

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "{{\"cases\":[{{\"input\":\"{s}\",\"crc_hex\":\"0x{x:0>8}\"}},{{\"input\":\"{s}\",\"crc_hex\":\"0x{x:0>8}\"}}]}}\n",
        .{
            visible_first,
            genksyms_crc.crc32(visible_first),
            visible_next,
            genksyms_crc.crc32(visible_next),
        },
    );
    defer std.testing.allocator.free(expected);

    const hidden_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{genksyms_crc.crc32(hidden_tail)});
    defer std.testing.allocator.free(hidden_crc);

    try std.testing.expectEqualStrings(expected, capture.list.items);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, hidden_tail) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, hidden_crc) == null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "\"crc_hex\"") == 2);
}
