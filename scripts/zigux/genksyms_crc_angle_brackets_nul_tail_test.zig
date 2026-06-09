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

test "runGenksymsCrc keeps angle-bracket-prefixed visible bytes before NUL" {
    var capture = try Capture(768).init(std.testing.allocator);
    defer capture.deinit();

    const input = "<<visible\x00hidden<tail\n>visible\x00hidden>tail\n<later>\n";
    try genksyms_crc.runGenksymsCrc(input, &capture);

    const less_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{genksyms_crc.crc32("<<visible")});
    defer std.testing.allocator.free(less_crc);
    const greater_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{genksyms_crc.crc32(">visible")});
    defer std.testing.allocator.free(greater_crc);
    const later_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{genksyms_crc.crc32("<later>")});
    defer std.testing.allocator.free(later_crc);
    const hidden_less_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{genksyms_crc.crc32("hidden<tail")});
    defer std.testing.allocator.free(hidden_less_crc);
    const hidden_greater_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{genksyms_crc.crc32("hidden>tail")});
    defer std.testing.allocator.free(hidden_greater_crc);

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "{{\"cases\":[{{\"input\":\"<<visible\",\"crc_hex\":\"{s}\"}},{{\"input\":\">visible\",\"crc_hex\":\"{s}\"}},{{\"input\":\"<later>\",\"crc_hex\":\"{s}\"}}]}}\n",
        .{ less_crc, greater_crc, later_crc },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "hidden<tail") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "hidden>tail") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, hidden_less_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, hidden_greater_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\\u003c") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\\u003e") == null);
}
