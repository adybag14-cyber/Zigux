const std = @import("std");

const c_line_buffer_len = 4096;
const c_line_payload_len = c_line_buffer_len - 1;

const Record = struct {
    len: usize,
    crc: u32,
    first: u8,
    last: u8,
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

fn truncateAtFirstNul(text: []const u8) []const u8 {
    return text[0 .. std.mem.indexOfScalar(u8, text, 0) orelse text.len];
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

fn collectNonEmptyRecords(allocator: std.mem.Allocator, input: []const u8) !std.ArrayList(Record) {
    var records = try std.ArrayList(Record).initCapacity(allocator, 4);
    var cursor: usize = 0;
    while (nextCHarnessLineChunk(input, &cursor)) |line| {
        if (line.len == 0) continue;
        try records.append(allocator, .{
            .len = line.len,
            .crc = crc32(line),
            .first = line[0],
            .last = line[line.len - 1],
        });
    }
    return records;
}

fn containsCrc(records: []const Record, crc: u32) bool {
    for (records) |record| {
        if (record.crc == crc) return true;
    }
    return false;
}

test "phase2 genksyms crc truncates an exact-buffer record at an interior NUL" {
    var input = try std.ArrayList(u8).initCapacity(std.testing.allocator, c_line_payload_len + "tail\n".len);
    defer input.deinit(std.testing.allocator);
    try input.appendNTimes(std.testing.allocator, 'a', 2048);
    try input.append(std.testing.allocator, 0);
    try input.appendNTimes(std.testing.allocator, 'z', c_line_payload_len - input.items.len);
    try input.appendSlice(std.testing.allocator, "tail\n");

    var records = try collectNonEmptyRecords(std.testing.allocator, input.items);
    defer records.deinit(std.testing.allocator);

    const visible = input.items[0..2048];
    try std.testing.expectEqual(@as(usize, 2), records.items.len);
    try std.testing.expectEqual(@as(usize, visible.len), records.items[0].len);
    try std.testing.expectEqual(@as(u8, 'a'), records.items[0].first);
    try std.testing.expectEqual(@as(u8, 'a'), records.items[0].last);
    try std.testing.expectEqual(crc32(visible), records.items[0].crc);
    try std.testing.expectEqual(crc32("tail"), records.items[1].crc);
    try std.testing.expect(!containsCrc(records.items, crc32(input.items[0..c_line_payload_len])));
    try std.testing.expect(!containsCrc(records.items, crc32(input.items[2049..c_line_payload_len])));
}

test "phase2 genksyms crc keeps leading CR bytes before an exact-buffer interior NUL" {
    var input = try std.ArrayList(u8).initCapacity(std.testing.allocator, c_line_payload_len + "next\n".len);
    defer input.deinit(std.testing.allocator);
    try input.appendSlice(std.testing.allocator, "\r\rvisible");
    const visible_len = input.items.len;
    try input.append(std.testing.allocator, 0);
    try input.appendSlice(std.testing.allocator, "hidden\r\r");
    try input.appendNTimes(std.testing.allocator, 'q', c_line_payload_len - input.items.len);
    try input.appendSlice(std.testing.allocator, "next\n");

    var records = try collectNonEmptyRecords(std.testing.allocator, input.items);
    defer records.deinit(std.testing.allocator);

    const visible = input.items[0..visible_len];
    try std.testing.expectEqual(@as(usize, 2), records.items.len);
    try std.testing.expectEqual(@as(usize, visible_len), records.items[0].len);
    try std.testing.expectEqual(@as(u8, '\r'), records.items[0].first);
    try std.testing.expectEqual(@as(u8, 'e'), records.items[0].last);
    try std.testing.expectEqual(crc32(visible), records.items[0].crc);
    try std.testing.expectEqual(crc32("next"), records.items[1].crc);
    try std.testing.expect(!containsCrc(records.items, crc32("visible")));
    try std.testing.expect(!containsCrc(records.items, crc32("hidden")));
    try std.testing.expect(!containsCrc(records.items, crc32(input.items[0..c_line_payload_len])));
}
