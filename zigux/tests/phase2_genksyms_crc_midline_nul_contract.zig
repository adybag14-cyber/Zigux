const std = @import("std");

const c_line_buffer_len = 4096;
const c_line_payload_len = c_line_buffer_len - 1;

fn truncateAtFirstNul(text: []const u8) []const u8 {
    return text[0 .. std.mem.indexOfScalar(u8, text, 0) orelse text.len];
}

fn trimTrailingCarriageReturn(text: []const u8) []const u8 {
    var end = text.len;
    while (end > 0 and text[end - 1] == '\r') end -= 1;
    return text[0..end];
}

fn normalizeCHarnessChunk(text: []const u8) []const u8 {
    return trimTrailingCarriageReturn(truncateAtFirstNul(text));
}

fn nextCHarnessLineChunk(input: []const u8, cursor: *usize) ?[]const u8 {
    if (cursor.* >= input.len) return null;

    const remaining = input[cursor.*..];
    const scan_len = @min(remaining.len, c_line_payload_len);
    const scan = remaining[0..scan_len];

    if (std.mem.indexOfScalar(u8, scan, '\n')) |newline_index| {
        cursor.* += newline_index + 1;
        return normalizeCHarnessChunk(scan[0..newline_index]);
    }

    cursor.* += scan_len;
    return normalizeCHarnessChunk(scan);
}

fn crc32(text: []const u8) u32 {
    var crc: u32 = 0xffff_ffff;
    for (text) |byte| {
        crc ^= byte;
        for (0..8) |_| {
            const mask = @as(u32, 0) -% (crc & 1);
            crc = (crc >> 1) ^ (0xedb8_8320 & mask);
        }
    }
    return crc ^ 0xffff_ffff;
}

fn writeJsonEscaped(writer: anytype, text: []const u8) !void {
    for (text) |c| switch (c) {
        '\\' => try writer.writeAll("\\\\"),
        '"' => try writer.writeAll("\\\""),
        '\n' => try writer.writeAll("\\n"),
        '\r' => try writer.writeAll("\\r"),
        '\t' => try writer.writeAll("\\t"),
        else => try writer.writeByte(c),
    };
}

fn runGenksymsCrc(input: []const u8, writer: anytype) !void {
    try writer.writeAll("{\"cases\":[");
    var cursor: usize = 0;
    var first = true;
    while (nextCHarnessLineChunk(input, &cursor)) |line| {
        if (line.len == 0) continue;
        if (!first) try writer.writeByte(',');
        first = false;
        try writer.writeAll("{\"input\":\"");
        try writeJsonEscaped(writer, line);
        try writer.writeAll("\",\"crc_hex\":\"");
        try writer.print("0x{x:0>8}", .{crc32(line)});
        try writer.writeAll("\"}");
    }
    try writer.writeAll("]}\n");
}

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

        fn writeAll(self: *@This(), bytes: []const u8) !void {
            try self.list.appendSlice(self.allocator, bytes);
        }

        fn print(self: *@This(), comptime fmt: []const u8, args: anytype) !void {
            const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
            defer self.allocator.free(rendered);
            try self.list.appendSlice(self.allocator, rendered);
        }

        fn writeByte(self: *@This(), byte: u8) !void {
            try self.list.append(self.allocator, byte);
        }
    };
}

test "midline NUL truncates an ordinary chunk while the next line still hashes" {
    var input = try std.ArrayList(u8).initCapacity(std.testing.allocator, 96);
    defer input.deinit(std.testing.allocator);
    try input.appendSlice(std.testing.allocator, "unsigned long visible");
    try input.append(std.testing.allocator, 0);
    try input.appendSlice(std.testing.allocator, "hidden_suffix_should_not_hash\r\n");
    try input.appendSlice(std.testing.allocator, "struct tail\n");

    var cursor: usize = 0;
    const visible = nextCHarnessLineChunk(input.items, &cursor) orelse return error.MissingVisibleChunk;
    const tail = nextCHarnessLineChunk(input.items, &cursor) orelse return error.MissingTailChunk;

    try std.testing.expectEqualStrings("unsigned long visible", visible);
    try std.testing.expectEqualStrings("struct tail", tail);
    try std.testing.expect(nextCHarnessLineChunk(input.items, &cursor) == null);

    const hidden_suffix = "unsigned long visiblehidden_suffix_should_not_hash";
    try std.testing.expect(crc32(visible) != crc32(hidden_suffix));
    try std.testing.expectEqual(@as(u32, 0x7f5f_89b1), crc32(tail));
}

test "midline NUL output omits hidden bytes from the JSON and CRC packet" {
    var input = try std.ArrayList(u8).initCapacity(std.testing.allocator, 96);
    defer input.deinit(std.testing.allocator);
    try input.appendSlice(std.testing.allocator, "int alpha");
    try input.append(std.testing.allocator, 0);
    try input.appendSlice(std.testing.allocator, "int poisoned\r\n");
    try input.appendSlice(std.testing.allocator, "int beta\n");

    var output = try Capture(256).init(std.testing.allocator);
    defer output.deinit();
    try runGenksymsCrc(input.items, &output);

    const alpha_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{crc32("int alpha")});
    defer std.testing.allocator.free(alpha_crc);
    const poisoned_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{crc32("int alphaint poisoned")});
    defer std.testing.allocator.free(poisoned_crc);
    const beta_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{crc32("int beta")});
    defer std.testing.allocator.free(beta_crc);

    try std.testing.expect(std.mem.indexOf(u8, output.list.items, "\"input\":\"int alpha\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, output.list.items, "\"input\":\"int beta\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, output.list.items, "poisoned") == null);
    try std.testing.expect(std.mem.indexOf(u8, output.list.items, alpha_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, output.list.items, beta_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, output.list.items, poisoned_crc) == null);
    try std.testing.expectEqual(@as(usize, 2), std.mem.count(u8, output.list.items, "crc_hex"));
}
