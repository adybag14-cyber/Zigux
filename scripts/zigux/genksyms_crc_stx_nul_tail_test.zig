const std = @import("std");
const crc = @import("genksyms_crc.zig");

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

test "runGenksymsCrc escapes visible STX before hiding NUL tail" {
    const visible = "stx\x02visible";
    const hidden = "hidden\x02tail";
    const next = "next";

    var input = try std.ArrayList(u8).initCapacity(std.testing.allocator, visible.len + hidden.len + next.len + 3);
    defer input.deinit(std.testing.allocator);
    try input.appendSlice(std.testing.allocator, visible);
    try input.append(std.testing.allocator, 0);
    try input.appendSlice(std.testing.allocator, hidden);
    try input.append(std.testing.allocator, '\n');
    try input.appendSlice(std.testing.allocator, next);
    try input.append(std.testing.allocator, '\n');

    var capture = try Capture(256).init(std.testing.allocator);
    defer capture.deinit();
    try crc.runGenksymsCrc(input.items, &capture);

    const visible_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{crc.crc32(visible)});
    defer std.testing.allocator.free(visible_crc);
    const hidden_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{crc.crc32(hidden)});
    defer std.testing.allocator.free(hidden_crc);
    const next_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{crc.crc32(next)});
    defer std.testing.allocator.free(next_crc);

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "{{\"cases\":[{{\"input\":\"stx\\u0002visible\",\"crc_hex\":\"{s}\"}},{{\"input\":\"next\",\"crc_hex\":\"{s}\"}}]}}\n",
        .{ visible_crc, next_crc },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, hidden) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, hidden_crc) == null);
    try std.testing.expect(std.mem.indexOfScalar(u8, capture.list.items, 0) == null);
}
