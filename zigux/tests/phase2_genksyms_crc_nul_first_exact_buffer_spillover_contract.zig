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

test "phase2 genksyms crc NUL-first exact-buffer chunk skips before spillover" {
    var input = try std.ArrayList(u8).initCapacity(std.testing.allocator, c_line_payload_len + 2);
    defer input.deinit(std.testing.allocator);
    try input.append(std.testing.allocator, 0);
    try input.appendNTimes(std.testing.allocator, 'a', c_line_payload_len - 1);
    try input.appendSlice(std.testing.allocator, "b\n");

    var cursor: usize = 0;
    const invisible = nextCHarnessLineChunk(input.items, &cursor) orelse return error.MissingInvisibleRecord;
    const visible = nextCHarnessLineChunk(input.items, &cursor) orelse return error.MissingVisibleRecord;

    try std.testing.expectEqualStrings("", invisible);
    try std.testing.expectEqualStrings("b", visible);
    try std.testing.expectEqual(@as(?[]const u8, null), nextCHarnessLineChunk(input.items, &cursor));
    try std.testing.expectEqual(@as(u32, 0x71be_eff9), crc32(visible));
    try std.testing.expect(crc32(input.items[0..c_line_payload_len]) != crc32(visible));
}

test "phase2 genksyms crc NUL-first exact-buffer skips CR-only spillover" {
    var input = try std.ArrayList(u8).initCapacity(std.testing.allocator, c_line_payload_len + 5);
    defer input.deinit(std.testing.allocator);
    try input.append(std.testing.allocator, 0);
    try input.appendNTimes(std.testing.allocator, 'a', c_line_payload_len - 1);
    try input.appendSlice(std.testing.allocator, "\r\r\nx\n");

    var cursor: usize = 0;
    const hidden_exact = nextCHarnessLineChunk(input.items, &cursor) orelse return error.MissingHiddenExactChunk;
    const hidden_spillover = nextCHarnessLineChunk(input.items, &cursor) orelse return error.MissingHiddenSpillover;
    const visible = nextCHarnessLineChunk(input.items, &cursor) orelse return error.MissingVisibleTail;

    try std.testing.expectEqualStrings("", hidden_exact);
    try std.testing.expectEqualStrings("", hidden_spillover);
    try std.testing.expectEqualStrings("x", visible);
    try std.testing.expectEqual(@as(?[]const u8, null), nextCHarnessLineChunk(input.items, &cursor));
    try std.testing.expectEqual(@as(u32, 0x8cdc_1683), crc32(visible));
}
