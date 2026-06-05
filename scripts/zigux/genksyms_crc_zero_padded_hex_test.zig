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

test "runGenksymsCrc zero-pads crc_hex to eight digits" {
    try std.testing.expectEqual(@as(u32, 0x00e7ddce), gen.crc32("ae"));

    var capture = try Capture(96).init(std.testing.allocator);
    defer capture.deinit();

    try gen.runGenksymsCrc("int\nae\n", &capture);
    try std.testing.expectEqualStrings(
        "{\"cases\":[{\"input\":\"int\",\"crc_hex\":\"0x1451dab1\"},{\"input\":\"ae\",\"crc_hex\":\"0x00e7ddce\"}]}\n",
        capture.list.items,
    );

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"crc_hex\":\"0xe7ddce\"") == null);
}
