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

test "runGenksymsCrc preserves valid UTF-8 records as JSON data" {
    const record = "struct zigux_\xcf\x80_device_\xe2\x98\x83";

    var capture = try Capture(256).init(std.testing.allocator);
    defer capture.deinit();
    try genksyms_crc.runGenksymsCrc(record ++ "\n", &capture);

    const expected_crc = try std.fmt.allocPrint(
        std.testing.allocator,
        "0x{x:0>8}",
        .{genksyms_crc.crc32(record)},
    );
    defer std.testing.allocator.free(expected_crc);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"" ++ record ++ "\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, expected_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\\u00cf") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\\u0098") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\\u0083") == null);
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, capture.list.items, "crc_hex"));
}
