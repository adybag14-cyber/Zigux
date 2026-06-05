const std = @import("std");
const genksyms_crc = @import("./genksyms_crc.zig");

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

test "runGenksymsCrc preserves final case framing before trailing skipped chunks" {
    var capture = try Capture(256).init(std.testing.allocator);
    defer capture.deinit();

    const trailing_nul_prefixed_chunk = [_]u8{ 0, 'h', 'i', 'd', 'd', 'e', 'n', '\n' };
    try genksyms_crc.runGenksymsCrc(
        "int\nstruct device\n\n\r\n" ++ trailing_nul_prefixed_chunk ++ "\r\r",
        &capture,
    );

    const int_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{genksyms_crc.crc32("int")});
    defer std.testing.allocator.free(int_crc);
    const struct_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{genksyms_crc.crc32("struct device")});
    defer std.testing.allocator.free(struct_crc);
    const hidden_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{genksyms_crc.crc32("hidden")});
    defer std.testing.allocator.free(hidden_crc);

    try std.testing.expectEqualStrings(
        "{\"cases\":[{\"input\":\"int\",\"crc_hex\":\"",
        capture.list.items[0..36],
    );
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, int_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, struct_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, hidden_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "hidden") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"\\r\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"\\n\"") == null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "crc_hex") == 2);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "},]}") == null);
    try std.testing.expectEqualStrings("\"}]}\n", capture.list.items[capture.list.items.len - 5 ..]);
}
