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

test "runGenksymsCrc keeps interior carriage returns but trims line endings" {
    const first = "alpha\rbravo";
    const second = "char\rdone";
    const third = "trail";
    const input = first ++ "\r\r\n" ++ second ++ "\r\n" ++ third ++ "\r\r";

    var capture = try Capture(512).init(std.testing.allocator);
    defer capture.deinit();
    try gen.runGenksymsCrc(input, &capture);

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "{{\"cases\":[{{\"input\":\"alpha\\rbravo\",\"crc_hex\":\"0x{x:0>8}\"}},{{\"input\":\"char\\rdone\",\"crc_hex\":\"0x{x:0>8}\"}},{{\"input\":\"trail\",\"crc_hex\":\"0x{x:0>8}\"}}]}}\n",
        .{ gen.crc32(first), gen.crc32(second), gen.crc32(third) },
    );
    defer std.testing.allocator.free(expected);

    const untrimmed_first_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32(first ++ "\r\r")});
    defer std.testing.allocator.free(untrimmed_first_crc);
    const untrimmed_second_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32(second ++ "\r")});
    defer std.testing.allocator.free(untrimmed_second_crc);
    const untrimmed_third_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32(third ++ "\r\r")});
    defer std.testing.allocator.free(untrimmed_third_crc);

    try std.testing.expectEqualStrings(expected, capture.list.items);
    try std.testing.expect(std.mem.indexOfScalar(u8, capture.list.items, '\r') == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, untrimmed_first_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, untrimmed_second_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, untrimmed_third_crc) == null);
}
