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

fn expectRecordTexts(input: []const u8, expected: []const []const u8) !void {
    var records: [8]Record = undefined;
    const count = collectRecords(input, &records);
    try testing.expectEqual(expected.len, count);
    for (expected, 0..) |text, index| {
        try testing.expectEqualStrings(text, records[index].text);
        try testing.expectEqual(crc32(text), records[index].crc);
    }
}

test "terminal empty newline records do not add CRC entries" {
    const alpha_crc = crc32("alpha");
    var one: [4]Record = undefined;
    const one_count = collectRecords("alpha\n", &one);
    try testing.expectEqual(@as(usize, 1), one_count);
    try testing.expectEqual(alpha_crc, one[0].crc);

    var with_final_empty: [4]Record = undefined;
    const with_final_empty_count = collectRecords("alpha\n\n", &with_final_empty);
    try testing.expectEqual(@as(usize, 1), with_final_empty_count);
    try testing.expectEqualStrings("alpha", with_final_empty[0].text);
    try testing.expectEqual(alpha_crc, with_final_empty[0].crc);

    var with_multiple_final_empty: [4]Record = undefined;
    const multiple_count = collectRecords("alpha\n\n\n", &with_multiple_final_empty);
    try testing.expectEqual(@as(usize, 1), multiple_count);
    try testing.expectEqualStrings("alpha", with_multiple_final_empty[0].text);
    try testing.expectEqual(alpha_crc, with_multiple_final_empty[0].crc);
}

test "empty final records are skipped at exact fgets payload boundary" {
    var exact_payload = [_]u8{'a'} ** c_line_payload_len;
    var input: [c_line_payload_len + 2]u8 = undefined;
    @memcpy(input[0..c_line_payload_len], &exact_payload);
    input[c_line_payload_len] = '\n';
    input[c_line_payload_len + 1] = '\n';

    var records: [4]Record = undefined;
    const count = collectRecords(&input, &records);
    try testing.expectEqual(@as(usize, 1), count);
    try testing.expectEqualStrings(&exact_payload, records[0].text);
    try testing.expectEqual(crc32(&exact_payload), records[0].crc);
}

test "blank-only inputs stay recordless" {
    try expectRecordTexts("", &.{});
    try expectRecordTexts("\n", &.{});
    try expectRecordTexts("\n\n", &.{});
}
