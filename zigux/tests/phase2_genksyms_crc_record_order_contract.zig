const std = @import("std");

const Record = struct {
    input: []const u8,
    crc: u32,
};

fn crc32(bytes: []const u8) u32 {
    var crc: u32 = 0xffff_ffff;
    for (bytes) |byte| {
        crc ^= byte;
        var bit: u8 = 0;
        while (bit < 8) : (bit += 1) {
            const mask: u32 = 0 -% (crc & 1);
            crc = (crc >> 1) ^ (0xedb8_8320 & mask);
        }
    }
    return crc ^ 0xffff_ffff;
}

fn trimTrailingCarriageReturn(text: []const u8) []const u8 {
    var end = text.len;
    while (end > 0 and text[end - 1] == '\r') end -= 1;
    return text[0..end];
}

fn collectRecords(allocator: std.mem.Allocator, input: []const u8) ![]Record {
    var records: std.ArrayList(Record) = .empty;
    errdefer records.deinit(allocator);

    var start: usize = 0;
    while (start < input.len) {
        const newline_offset = std.mem.indexOfScalar(u8, input[start..], '\n');
        const line_end = if (newline_offset) |offset| start + offset else input.len;
        const line = trimTrailingCarriageReturn(input[start..line_end]);
        if (line.len > 0) {
            try records.append(allocator, .{ .input = line, .crc = crc32(line) });
        }
        if (newline_offset == null) break;
        start = line_end + 1;
    }

    return try records.toOwnedSlice(allocator);
}

fn writeJsonEscaped(writer: anytype, text: []const u8) !void {
    for (text) |byte| switch (byte) {
        '\\' => try writer.writeAll("\\\\"),
        '"' => try writer.writeAll("\\\""),
        '\n' => try writer.writeAll("\\n"),
        '\r' => try writer.writeAll("\\r"),
        '\t' => try writer.writeAll("\\t"),
        else => {
            if (byte < 0x20) {
                try writer.print("\\u00{x:0>2}", .{byte});
            } else {
                try writer.writeByte(byte);
            }
        },
    };
}

fn writeRecordsJson(writer: anytype, records: []const Record) !void {
    try writer.writeByte('[');
    for (records, 0..) |record, index| {
        if (index != 0) try writer.writeByte(',');
        try writer.writeAll("{\"input\":\"");
        try writeJsonEscaped(writer, record.input);
        try writer.print("\",\"crc_hex\":\"0x{x:0>8}\"}}", .{record.crc});
    }
    try writer.writeByte(']');
}

fn renderRecordsJson(allocator: std.mem.Allocator, input: []const u8) ![]u8 {
    const records = try collectRecords(allocator, input);
    defer allocator.free(records);

    var output: std.Io.Writer.Allocating = .init(allocator);
    defer output.deinit();
    try writeRecordsJson(&output.writer, records);
    return try allocator.dupe(u8, output.written());
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase2 genksyms crc preserves normalized record order and duplicates" {
    const input = "beta\r\r\nalpha\nbeta\r\n\n\r\r\nomega\n";

    const records = try collectRecords(std.testing.allocator, input);
    defer std.testing.allocator.free(records);

    try std.testing.expectEqual(@as(usize, 4), records.len);
    try std.testing.expectEqualStrings("beta", records[0].input);
    try std.testing.expectEqualStrings("alpha", records[1].input);
    try std.testing.expectEqualStrings("beta", records[2].input);
    try std.testing.expectEqualStrings("omega", records[3].input);
    try std.testing.expectEqual(crc32("beta"), records[0].crc);
    try std.testing.expectEqual(crc32("alpha"), records[1].crc);
    try std.testing.expectEqual(records[0].crc, records[2].crc);
    try std.testing.expectEqual(crc32("omega"), records[3].crc);
}

test "phase2 genksyms crc rendered records stay order-sensitive" {
    const ordered = try renderRecordsJson(std.testing.allocator, "alpha\nbeta\nalpha\n");
    defer std.testing.allocator.free(ordered);
    const reversed = try renderRecordsJson(std.testing.allocator, "alpha\nalpha\nbeta\n");
    defer std.testing.allocator.free(reversed);

    try std.testing.expect(!std.mem.eql(u8, ordered, reversed));
    try expectContains(ordered, "\"input\":\"alpha\",\"crc_hex\":");
    try expectContains(ordered, "\"input\":\"beta\",\"crc_hex\":");
    try expectContains(ordered, "0x");
}
