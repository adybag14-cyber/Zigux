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

test "lane19 multi-megabyte exact-buffer split preserves visible CR-led control bytes, truncates at NUL, trims carriage returns, and still reaches the next tail line beyond the old CLI cap" {
    const skipped_record_count = 257;
    const skipped_record_len = gen.c_line_payload_len + 1;

    var input = try std.ArrayList(u8).initCapacity(
        std.testing.allocator,
        skipped_record_count * skipped_record_len + gen.c_line_payload_len + 15,
    );
    defer input.deinit(std.testing.allocator);

    for (0..skipped_record_count) |_| {
        try input.append(std.testing.allocator, 0);
        try input.appendNTimes(std.testing.allocator, 'a', gen.c_line_payload_len - 1);
        try input.append(std.testing.allocator, '\n');
    }

    try input.appendNTimes(std.testing.allocator, 'z', gen.c_line_payload_len);
    try input.append(std.testing.allocator, '\r');
    try input.append(std.testing.allocator, '\r');
    try input.append(std.testing.allocator, '\x08');
    try input.append(std.testing.allocator, '\x0c');
    try input.append(std.testing.allocator, '\x01');
    try input.append(std.testing.allocator, 'b');
    try input.append(std.testing.allocator, '\r');
    try input.append(std.testing.allocator, '\r');
    try input.append(std.testing.allocator, 0);
    try input.append(std.testing.allocator, 'c');
    try input.append(std.testing.allocator, '\n');
    try input.appendSlice(std.testing.allocator, "tail\n");

    try std.testing.expect(input.items.len > old_cli_cap);

    var capture = try Capture(2048).init(std.testing.allocator);
    defer capture.deinit();
    try gen.runGenksymsCrc(input.items, &capture);

    const exact_start = skipped_record_count * skipped_record_len;
    const exact_crc = try std.fmt.allocPrint(
        std.testing.allocator,
        "0x{x:0>8}",
        .{gen.crc32(input.items[exact_start .. exact_start + gen.c_line_payload_len])},
    );
    defer std.testing.allocator.free(exact_crc);
    const normalized_crc = try std.fmt.allocPrint(
        std.testing.allocator,
        "0x{x:0>8}",
        .{gen.crc32("\r\r\x08\x0c\x01b")},
    );
    defer std.testing.allocator.free(normalized_crc);
    const trailing_cr_crc = try std.fmt.allocPrint(
        std.testing.allocator,
        "0x{x:0>8}",
        .{gen.crc32("\r\r\x08\x0c\x01b\r\r")},
    );
    defer std.testing.allocator.free(trailing_cr_crc);
    const controls_without_cr_prefix_crc = try std.fmt.allocPrint(
        std.testing.allocator,
        "0x{x:0>8}",
        .{gen.crc32("\x08\x0c\x01b")},
    );
    defer std.testing.allocator.free(controls_without_cr_prefix_crc);
    const untruncated_crc = try std.fmt.allocPrint(
        std.testing.allocator,
        "0x{x:0>8}",
        .{gen.crc32("\r\r\x08\x0c\x01b\r\r\x00c")},
    );
    defer std.testing.allocator.free(untruncated_crc);
    const nul_tail_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("c")});
    defer std.testing.allocator.free(nul_tail_crc);
    const trimmed_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("b")});
    defer std.testing.allocator.free(trimmed_crc);
    const tail_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("tail")});
    defer std.testing.allocator.free(tail_crc);
    const unsplit_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32(input.items)});
    defer std.testing.allocator.free(unsplit_crc);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, exact_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, normalized_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, trailing_cr_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, controls_without_cr_prefix_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, untruncated_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, nul_tail_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, trimmed_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, tail_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, unsplit_crc) == null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "crc_hex") == 3);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"\\r\\r\\b\\f\\u0001b\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"\\b\\f\\u0001b\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"\\r\\r\\b\\f\\u0001b\\r\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"b\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"c\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"tail\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\\u0000") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"a") == null);
}
