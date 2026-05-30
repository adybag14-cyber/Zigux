const std = @import("std");
const testing = std.testing;

const c_line_payload_len: usize = 4095;

const Record = struct {
    text: []const u8,
    crc: u32,
};

fn crc32(bytes: []const u8) u32 {
    var crc: u32 = 0xffffffff;
    for (bytes) |byte| {
        crc ^= byte;
        var bit: u8 = 0;
        while (bit < 8) : (bit += 1) {
            const mask: u32 = 0 -% (crc & 1);
            crc = (crc >> 1) ^ (0xedb88320 & mask);
        }
    }
    return ~crc;
}

fn visiblePrefix(bytes: []const u8) []const u8 {
    const nul_index = std.mem.indexOfScalar(u8, bytes, 0) orelse bytes.len;
    var visible = bytes[0..nul_index];
    if (std.mem.endsWith(u8, visible, "\n")) {
        visible = visible[0 .. visible.len - 1];
    }
    while (std.mem.endsWith(u8, visible, "\r")) {
        visible = visible[0 .. visible.len - 1];
    }
    return visible;
}

fn collectRecords(input: []const u8, out: []Record) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (offset < input.len) {
        const remaining = input[offset..];
        const newline_rel = std.mem.indexOfScalar(u8, remaining, '\n');
        const wanted_len = if (newline_rel) |idx| idx + 1 else remaining.len;
        const chunk_len = @min(wanted_len, c_line_payload_len);
        const chunk = input[offset .. offset + chunk_len];
        offset += chunk_len;

        const visible = visiblePrefix(chunk);
        if (visible.len == 0) continue;
        out[count] = .{ .text = visible, .crc = crc32(visible) };
        count += 1;
    }
    return count;
}

fn appendExactPayload(list: *std.ArrayList(u8), byte: u8) !void {
    try list.appendNTimes(testing.allocator, byte, c_line_payload_len);
}

test "NUL-prefixed exact-buffer continuation is skipped before next visible line" {
    var input = try std.ArrayList(u8).initCapacity(testing.allocator, c_line_payload_len + 18);
    defer input.deinit(testing.allocator);
    try appendExactPayload(&input, 'a');
    try input.append(testing.allocator, 0);
    try input.appendSlice(testing.allocator, "hidden\nnext\n");

    var records: [4]Record = undefined;
    const count = collectRecords(input.items, &records);
    try testing.expectEqual(@as(usize, 2), count);
    try testing.expectEqualStrings(input.items[0..c_line_payload_len], records[0].text);
    try testing.expectEqual(crc32(input.items[0..c_line_payload_len]), records[0].crc);
    try testing.expectEqualStrings("next", records[1].text);
    try testing.expectEqual(crc32("next"), records[1].crc);
    try testing.expect(records[1].crc != crc32("hidden"));
}

test "NUL-prefixed CR continuation is skipped after exact buffer split" {
    var input = try std.ArrayList(u8).initCapacity(testing.allocator, c_line_payload_len + 20);
    defer input.deinit(testing.allocator);
    try appendExactPayload(&input, 'b');
    try input.append(testing.allocator, 0);
    try input.appendSlice(testing.allocator, "hidden\r\r\nvisible\n");

    var records: [4]Record = undefined;
    const count = collectRecords(input.items, &records);
    try testing.expectEqual(@as(usize, 2), count);
    try testing.expectEqualStrings(input.items[0..c_line_payload_len], records[0].text);
    try testing.expectEqualStrings("visible", records[1].text);
    try testing.expectEqual(crc32("visible"), records[1].crc);
    try testing.expect(records[1].crc != crc32("hidden"));
}

test "terminal NUL-prefixed continuation does not add a final CRC record" {
    var input = try std.ArrayList(u8).initCapacity(testing.allocator, c_line_payload_len + 9);
    defer input.deinit(testing.allocator);
    try appendExactPayload(&input, 'c');
    try input.append(testing.allocator, 0);
    try input.appendSlice(testing.allocator, "tail\r\r");

    var records: [4]Record = undefined;
    const count = collectRecords(input.items, &records);
    try testing.expectEqual(@as(usize, 1), count);
    try testing.expectEqualStrings(input.items[0..c_line_payload_len], records[0].text);
    try testing.expectEqual(crc32(input.items[0..c_line_payload_len]), records[0].crc);
    try testing.expect(records[0].crc != crc32("tail"));
}
