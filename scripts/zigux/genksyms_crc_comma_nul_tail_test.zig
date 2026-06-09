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

test "runGenksymsCrc keeps comma records visible while hiding post-nul comma tails" {
    var capture = try Capture(256).init(std.testing.allocator);
    defer capture.deinit();

    const visible_before_nul = ",visible,type,";
    const later_visible = ",after,record";
    const hidden_tail = "hidden,tail";
    try gen.runGenksymsCrc(visible_before_nul ++ "\x00" ++ hidden_tail ++ "\n" ++ later_visible ++ "\n", &capture);

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "{{\"cases\":[{{\"input\":\"{s}\",\"crc_hex\":\"0x{x:0>8}\"}},{{\"input\":\"{s}\",\"crc_hex\":\"0x{x:0>8}\"}}]}}\n",
        .{
            visible_before_nul,
            gen.crc32(visible_before_nul),
            later_visible,
            gen.crc32(later_visible),
        },
    );
    defer std.testing.allocator.free(expected);

    const hidden_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32(hidden_tail)});
    defer std.testing.allocator.free(hidden_crc);

    try std.testing.expectEqualStrings(expected, capture.list.items);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, hidden_tail) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, hidden_crc) == null);
}
