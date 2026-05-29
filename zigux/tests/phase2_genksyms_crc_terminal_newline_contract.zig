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

fn expectSameRecords(left: []const Record, right: []const Record) !void {
    try std.testing.expectEqual(left.len, right.len);
    for (left, right) |left_record, right_record| {
        try std.testing.expectEqualStrings(left_record.input, right_record.input);
        try std.testing.expectEqual(left_record.crc, right_record.crc);
    }
}

test "phase2 genksyms crc treats terminal newline and unterminated EOF records alike" {
    const with_terminal_newline = try collectRecords(std.testing.allocator, "alpha\r\nbeta\r\r\n");
    defer std.testing.allocator.free(with_terminal_newline);
    const without_terminal_newline = try collectRecords(std.testing.allocator, "alpha\r\nbeta\r\r");
    defer std.testing.allocator.free(without_terminal_newline);

    try expectSameRecords(with_terminal_newline, without_terminal_newline);
    try std.testing.expectEqual(@as(usize, 2), without_terminal_newline.len);
    try std.testing.expectEqualStrings("alpha", without_terminal_newline[0].input);
    try std.testing.expectEqualStrings("beta", without_terminal_newline[1].input);
    try std.testing.expectEqual(crc32("alpha"), without_terminal_newline[0].crc);
    try std.testing.expectEqual(crc32("beta"), without_terminal_newline[1].crc);
}

test "phase2 genksyms crc skips CR-only terminal chunks with or without a newline" {
    const terminated = try collectRecords(std.testing.allocator, "visible\n\r\r\n");
    defer std.testing.allocator.free(terminated);
    const unterminated = try collectRecords(std.testing.allocator, "visible\n\r\r");
    defer std.testing.allocator.free(unterminated);
    const bare_terminal_newline = try collectRecords(std.testing.allocator, "visible\n");
    defer std.testing.allocator.free(bare_terminal_newline);

    try expectSameRecords(terminated, unterminated);
    try expectSameRecords(terminated, bare_terminal_newline);
    try std.testing.expectEqual(@as(usize, 1), terminated.len);
    try std.testing.expectEqualStrings("visible", terminated[0].input);
    try std.testing.expectEqual(crc32("visible"), terminated[0].crc);
}
