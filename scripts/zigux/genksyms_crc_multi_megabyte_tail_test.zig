const std = @import("std");
const gen = @import("./genksyms_crc.zig");

const old_cli_cap = 1024 * 1024;

fn Capture(comptime capacity: usize) type {
    return struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        pub fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, capacity),
                .allocator = allocator,
            };
        }

        pub fn deinit(self: *@This()) void {
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

test "lane19 multi-megabyte NUL-prefixed corpus still reaches the visible tail beyond the old CLI cap" {
    const skipped_record_count = 257;
    const skipped_record_len = gen.c_line_payload_len + 1;

    var input = try std.ArrayList(u8).initCapacity(
        std.testing.allocator,
        skipped_record_count * skipped_record_len + "tail\n".len,
    );
    defer input.deinit(std.testing.allocator);

    for (0..skipped_record_count) |_| {
        try input.append(std.testing.allocator, 0);
        try input.appendNTimes(std.testing.allocator, 'a', gen.c_line_payload_len - 1);
        try input.append(std.testing.allocator, '\n');
    }
    try input.appendSlice(std.testing.allocator, "tail\n");

    try std.testing.expect(input.items.len > old_cli_cap);

    var capture = try Capture(256).init(std.testing.allocator);
    defer capture.deinit();
    try gen.runGenksymsCrc(input.items, &capture);

    const tail_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("tail")});
    defer std.testing.allocator.free(tail_crc);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"tail\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, tail_crc) != null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "crc_hex") == 1);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\\u0000") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"a") == null);
}
