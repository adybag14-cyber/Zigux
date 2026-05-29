const std = @import("std");

const c_line_buffer_len = 4096;
const c_line_payload_len = c_line_buffer_len - 1;

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

test "phase2 genksyms crc CR-newline inside C buffer trims without an empty continuation" {
    var input = try std.ArrayList(u8).initCapacity(std.testing.allocator, c_line_payload_len + 2);
    defer input.deinit(std.testing.allocator);
    try input.appendNTimes(std.testing.allocator, 'a', c_line_payload_len - 2);
    try input.appendSlice(std.testing.allocator, "\r\nz\n");

    var cursor: usize = 0;
    const first = nextCHarnessLineChunk(input.items, &cursor) orelse return error.MissingFirstRecord;
    const second = nextCHarnessLineChunk(input.items, &cursor) orelse return error.MissingSecondRecord;

    try std.testing.expectEqual(@as(usize, c_line_payload_len - 2), first.len);
    try std.testing.expectEqualStrings("z", second);
    try std.testing.expectEqual(@as(?[]const u8, null), nextCHarnessLineChunk(input.items, &cursor));
    try std.testing.expectEqual(crc32(input.items[0 .. c_line_payload_len - 2]), crc32(first));
    try std.testing.expectEqual(@as(u32, 0x62d2_77af), crc32(second));
}

test "phase2 genksyms crc CR at final payload slot defers newline as an empty record" {
    var input = try std.ArrayList(u8).initCapacity(std.testing.allocator, c_line_payload_len + 3);
    defer input.deinit(std.testing.allocator);
    try input.appendNTimes(std.testing.allocator, 'a', c_line_payload_len - 1);
    try input.appendSlice(std.testing.allocator, "\r\nz\n");

    var cursor: usize = 0;
    const first = nextCHarnessLineChunk(input.items, &cursor) orelse return error.MissingFirstRecord;
    const empty = nextCHarnessLineChunk(input.items, &cursor) orelse return error.MissingEmptyBoundaryRecord;
    const visible = nextCHarnessLineChunk(input.items, &cursor) orelse return error.MissingVisibleTail;

    try std.testing.expectEqual(@as(usize, c_line_payload_len - 1), first.len);
    try std.testing.expectEqualStrings("", empty);
    try std.testing.expectEqualStrings("z", visible);
    try std.testing.expectEqual(@as(?[]const u8, null), nextCHarnessLineChunk(input.items, &cursor));
    try std.testing.expectEqual(crc32(input.items[0 .. c_line_payload_len - 1]), crc32(first));
    try std.testing.expectEqual(@as(u32, 0x0000_0000), crc32(empty));
    try std.testing.expectEqual(@as(u32, 0x62d2_77af), crc32(visible));
}
