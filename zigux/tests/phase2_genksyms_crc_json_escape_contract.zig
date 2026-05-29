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

fn writeJsonEscaped(writer: anytype, text: []const u8) !void {
    for (text) |byte| switch (byte) {
        '\\' => try writer.writeAll("\\\\"),
        '"' => try writer.writeAll("\\\""),
        '\x08' => try writer.writeAll("\\b"),
        '\x0c' => try writer.writeAll("\\f"),
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

fn writeRecordJson(writer: anytype, record: Record) !void {
    try writer.writeAll("{\"input\":\"");
    try writeJsonEscaped(writer, record.input);
    try writer.print("\",\"crc_hex\":\"0x{x:0>8}\"}}", .{record.crc});
}

fn collectLineRecord(input: []const u8) ?Record {
    const line = trimTrailingCarriageReturn(input[0 .. std.mem.indexOfScalar(u8, input, '\n') orelse input.len]);
    if (line.len == 0) return null;
    return .{ .input = line, .crc = crc32(line) };
}

fn renderSingleRecordJson(allocator: std.mem.Allocator, input: []const u8) ![]u8 {
    const record = collectLineRecord(input) orelse return error.EmptyRecord;
    var output: std.Io.Writer.Allocating = .init(allocator);
    defer output.deinit();
    try writeRecordJson(&output.writer, record);
    return try allocator.dupe(u8, output.written());
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectMissing(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "phase2 genksyms crc json escapes visible control bytes after hashing raw input" {
    const raw = "sym\t\"quoted\"\\path" ++ [_]u8{0x01} ++ "\n";
    const normalized = raw[0 .. raw.len - 1];

    const json = try renderSingleRecordJson(std.testing.allocator, raw);
    defer std.testing.allocator.free(json);

    const raw_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{crc32(normalized)});
    defer std.testing.allocator.free(raw_crc);
    const escaped_text_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{crc32("sym\\t\\\"quoted\\\"\\\\path\\u0001")});
    defer std.testing.allocator.free(escaped_text_crc);

    try expectContains(json, "\"input\":\"sym\\t\\\"quoted\\\"\\\\path\\u0001\"");
    try expectContains(json, raw_crc);
    try expectMissing(json, escaped_text_crc);
    try expectMissing(json, "sym\t\"quoted\"");
}

test "phase2 genksyms crc json keeps interior C controls but trims final carriage returns" {
    const raw = "left\rright\x08\x0c\r\r\n";
    const normalized = "left\rright\x08\x0c";

    const json = try renderSingleRecordJson(std.testing.allocator, raw);
    defer std.testing.allocator.free(json);

    const normalized_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{crc32(normalized)});
    defer std.testing.allocator.free(normalized_crc);
    const untrimmed_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{crc32("left\rright\x08\x0c\r\r")});
    defer std.testing.allocator.free(untrimmed_crc);

    try expectContains(json, "\"input\":\"left\\rright\\b\\f\"");
    try expectContains(json, normalized_crc);
    try expectMissing(json, untrimmed_crc);
    try expectMissing(json, "\\r\\r\"");
}
