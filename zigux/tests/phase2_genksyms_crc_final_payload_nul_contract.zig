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

test "final payload slot NUL trims the visible prefix before skipping newline continuation" {
    var input = try std.ArrayList(u8).initCapacity(std.testing.allocator, c_line_payload_len + 3);
    defer input.deinit(std.testing.allocator);
    try input.appendNTimes(std.testing.allocator, 'a', c_line_payload_len - 2);
    try input.append(std.testing.allocator, '\r');
    try input.append(std.testing.allocator, 0);
    try input.append(std.testing.allocator, '\n');
    try input.appendSlice(std.testing.allocator, "x\n");

    var cursor: usize = 0;
    const first = nextCHarnessLineChunk(input.items, &cursor) orelse return error.MissingFirstChunk;
    const blank = nextCHarnessLineChunk(input.items, &cursor) orelse return error.MissingBlankContinuation;
    const tail = nextCHarnessLineChunk(input.items, &cursor) orelse return error.MissingTailChunk;

    try std.testing.expectEqual(@as(usize, c_line_payload_len - 2), first.len);
    try std.testing.expect(std.mem.allEqual(u8, first, 'a'));
    try std.testing.expectEqualStrings("", blank);
    try std.testing.expectEqualStrings("x", tail);
    try std.testing.expect(nextCHarnessLineChunk(input.items, &cursor) == null);

    const trimmed_crc = crc32(first);
    const untrimmed_visible_crc = crc32(input.items[0 .. c_line_payload_len - 1]);
    const tail_crc = crc32(tail);

    try std.testing.expect(trimmed_crc != untrimmed_visible_crc);
    try std.testing.expectEqual(@as(u32, 0x8cdc_1683), tail_crc);
}
