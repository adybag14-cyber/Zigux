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

test "question marks before NUL stay visible while the hidden tail is omitted" {
    const visible = "alpha?beta?";
    const hidden = "hidden?tail";
    const next = "next?record";
    const input = visible ++ "\x00" ++ hidden ++ "\n" ++ next ++ "\n";

    var capture = try Capture(256).init(std.testing.allocator);
    defer capture.deinit();
    try gen.runGenksymsCrc(input, &capture);

    try std.testing.expectEqualStrings(
        "{\"cases\":[{\"input\":\"alpha?beta?\",\"crc_hex\":\"0x6c340253\"},{\"input\":\"next?record\",\"crc_hex\":\"0x4957d6c8\"}]}\n",
        capture.list.items,
    );
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "hidden?tail") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "0x6c3edebc") == null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "crc_hex") == 2);
}
