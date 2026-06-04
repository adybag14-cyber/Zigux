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

test "runGenksymsCrc renders high-bit bytes without control escaping" {
    const payload = [_]u8{ 's', 'y', 'm', 0x80, 0xff, 'x', '\n' };

    var capture = try Capture(128).init(std.testing.allocator);
    defer capture.deinit();
    try genksyms_crc.runGenksymsCrc(&payload, &capture);

    const rendered_input = [_]u8{ '"', 'i', 'n', 'p', 'u', 't', '"', ':', '"', 's', 'y', 'm', 0x80, 0xff, 'x', '"' };
    const escaped_high_80 = [_]u8{ '\\', 'u', '0', '0', '8', '0' };
    const escaped_high_ff = [_]u8{ '\\', 'u', '0', '0', 'f', 'f' };
    const crc_hex = try std.fmt.allocPrint(
        std.testing.allocator,
        "\"crc_hex\":\"0x{x:0>8}\"",
        .{genksyms_crc.crc32(payload[0 .. payload.len - 1])},
    );
    defer std.testing.allocator.free(crc_hex);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, &rendered_input) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, &escaped_high_80) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, &escaped_high_ff) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, crc_hex) != null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "crc_hex") == 1);
}
