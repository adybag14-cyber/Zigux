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

test "runGenksymsCrc preserves ampersand-prefixed visible chunks before NUL" {
    const visible_line = "&visible&type";
    const hidden_tail = "&hidden&tail";
    const next_line = "&next&record";
    const input = visible_line ++ "\x00" ++ hidden_tail ++ "\n" ++ next_line ++ "\n";

    var capture = try Capture(512).init(std.testing.allocator);
    defer capture.deinit();
    try genksyms_crc.runGenksymsCrc(input, &capture);

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "{{\"cases\":[{{\"input\":\"{s}\",\"crc_hex\":\"0x{x:0>8}\"}},{{\"input\":\"{s}\",\"crc_hex\":\"0x{x:0>8}\"}}]}}\n",
        .{
            visible_line,
            genksyms_crc.crc32(visible_line),
            next_line,
            genksyms_crc.crc32(next_line),
        },
    );
    defer std.testing.allocator.free(expected);

    const hidden_crc = try std.fmt.allocPrint(
        std.testing.allocator,
        "0x{x:0>8}",
        .{genksyms_crc.crc32(hidden_tail)},
    );
    defer std.testing.allocator.free(hidden_crc);

    try std.testing.expectEqualStrings(expected, capture.list.items);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, hidden_tail) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, hidden_crc) == null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "crc_hex") == 2);
}
