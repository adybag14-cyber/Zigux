const std = @import("std");
const genksyms_crc = @import("genksyms_crc.zig");

const c_line_payload_len = 4095;

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

test "runGenksymsCrc mirrors consecutive full C fgets chunks before newline" {
    var input = try std.ArrayList(u8).initCapacity(std.testing.allocator, c_line_payload_len * 2 + 5);
    defer input.deinit(std.testing.allocator);
    try input.appendNTimes(std.testing.allocator, 'a', c_line_payload_len);
    try input.appendNTimes(std.testing.allocator, 'b', c_line_payload_len);
    try input.appendSlice(std.testing.allocator, "tail\n");

    var capture = try Capture(c_line_payload_len * 2 + 512).init(std.testing.allocator);
    defer capture.deinit();
    try genksyms_crc.runGenksymsCrc(input.items, &capture);

    const first_chunk_crc = try std.fmt.allocPrint(
        std.testing.allocator,
        "0x{x:0>8}",
        .{genksyms_crc.crc32(input.items[0..c_line_payload_len])},
    );
    defer std.testing.allocator.free(first_chunk_crc);
    const second_chunk_crc = try std.fmt.allocPrint(
        std.testing.allocator,
        "0x{x:0>8}",
        .{genksyms_crc.crc32(input.items[c_line_payload_len .. c_line_payload_len * 2])},
    );
    defer std.testing.allocator.free(second_chunk_crc);
    const tail_crc = try std.fmt.allocPrint(
        std.testing.allocator,
        "0x{x:0>8}",
        .{genksyms_crc.crc32("tail")},
    );
    defer std.testing.allocator.free(tail_crc);
    const merged_line_crc = try std.fmt.allocPrint(
        std.testing.allocator,
        "0x{x:0>8}",
        .{genksyms_crc.crc32(input.items[0 .. input.items.len - 1])},
    );
    defer std.testing.allocator.free(merged_line_crc);
    const second_plus_tail_crc = try std.fmt.allocPrint(
        std.testing.allocator,
        "0x{x:0>8}",
        .{genksyms_crc.crc32(input.items[c_line_payload_len .. input.items.len - 1])},
    );
    defer std.testing.allocator.free(second_plus_tail_crc);

    try std.testing.expect(std.mem.startsWith(u8, capture.list.items, "{\"cases\":[{\"input\":\"aa"));
    try std.testing.expect(std.mem.endsWith(u8, capture.list.items, "\"}]}\n"));
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, first_chunk_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, second_chunk_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, tail_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"tail\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, merged_line_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, second_plus_tail_crc) == null);
    try std.testing.expectEqual(@as(usize, 3), std.mem.count(u8, capture.list.items, "\"crc_hex\""));
    try std.testing.expectEqual(@as(usize, 2), std.mem.count(u8, capture.list.items, "},{\"input\""));
}
