const std = @import("std");
const Io = std.Io;

const crctab32 = [_]u32{
    0x00000000, 0x77073096, 0xee0e612c, 0x990951ba, 0x076dc419, 0x706af48f, 0xe963a535, 0x9e6495a3,
    0x0edb8832, 0x79dcb8a4, 0xe0d5e91e, 0x97d2d988, 0x09b64c2b, 0x7eb17cbd, 0xe7b82d07, 0x90bf1d91,
    0x1db71064, 0x6ab020f2, 0xf3b97148, 0x84be41de, 0x1adad47d, 0x6ddde4eb, 0xf4d4b551, 0x83d385c7,
    0x136c9856, 0x646ba8c0, 0xfd62f97a, 0x8a65c9ec, 0x14015c4f, 0x63066cd9, 0xfa0f3d63, 0x8d080df5,
    0x3b6e20c8, 0x4c69105e, 0xd56041e4, 0xa2677172, 0x3c03e4d1, 0x4b04d447, 0xd20d85fd, 0xa50ab56b,
    0x35b5a8fa, 0x42b2986c, 0xdbbbc9d6, 0xacbcf940, 0x32d86ce3, 0x45df5c75, 0xdcd60dcf, 0xabd13d59,
    0x26d930ac, 0x51de003a, 0xc8d75180, 0xbfd06116, 0x21b4f4b5, 0x56b3c423, 0xcfba9599, 0xb8bda50f,
    0x2802b89e, 0x5f058808, 0xc60cd9b2, 0xb10be924, 0x2f6f7c87, 0x58684c11, 0xc1611dab, 0xb6662d3d,
    0x76dc4190, 0x01db7106, 0x98d220bc, 0xefd5102a, 0x71b18589, 0x06b6b51f, 0x9fbfe4a5, 0xe8b8d433,
    0x7807c9a2, 0x0f00f934, 0x9609a88e, 0xe10e9818, 0x7f6a0dbb, 0x086d3d2d, 0x91646c97, 0xe6635c01,
    0x6b6b51f4, 0x1c6c6162, 0x856530d8, 0xf262004e, 0x6c0695ed, 0x1b01a57b, 0x8208f4c1, 0xf50fc457,
    0x65b0d9c6, 0x12b7e950, 0x8bbeb8ea, 0xfcb9887c, 0x62dd1ddf, 0x15da2d49, 0x8cd37cf3, 0xfbd44c65,
    0x4db26158, 0x3ab551ce, 0xa3bc0074, 0xd4bb30e2, 0x4adfa541, 0x3dd895d7, 0xa4d1c46d, 0xd3d6f4fb,
    0x4369e96a, 0x346ed9fc, 0xad678846, 0xda60b8d0, 0x44042d73, 0x33031de5, 0xaa0a4c5f, 0xdd0d7cc9,
    0x5005713c, 0x270241aa, 0xbe0b1010, 0xc90c2086, 0x5768b525, 0x206f85b3, 0xb966d409, 0xce61e49f,
    0x5edef90e, 0x29d9c998, 0xb0d09822, 0xc7d7a8b4, 0x59b33d17, 0x2eb40d81, 0xb7bd5c3b, 0xc0ba6cad,
    0xedb88320, 0x9abfb3b6, 0x03b6e20c, 0x74b1d29a, 0xead54739, 0x9dd277af, 0x04db2615, 0x73dc1683,
    0xe3630b12, 0x94643b84, 0x0d6d6a3e, 0x7a6a5aa8, 0xe40ecf0b, 0x9309ff9d, 0x0a00ae27, 0x7d079eb1,
    0xf00f9344, 0x8708a3d2, 0x1e01f268, 0x6906c2fe, 0xf762575d, 0x806567cb, 0x196c3671, 0x6e6b06e7,
    0xfed41b76, 0x89d32be0, 0x10da7a5a, 0x67dd4acc, 0xf9b9df6f, 0x8ebeeff9, 0x17b7be43, 0x60b08ed5,
    0xd6d6a3e8, 0xa1d1937e, 0x38d8c2c4, 0x4fdff252, 0xd1bb67f1, 0xa6bc5767, 0x3fb506dd, 0x48b2364b,
    0xd80d2bda, 0xaf0a1b4c, 0x36034af6, 0x41047a60, 0xdf60efc3, 0xa867df55, 0x316e8eef, 0x4669be79,
    0xcb61b38c, 0xbc66831a, 0x256fd2a0, 0x5268e236, 0xcc0c7795, 0xbb0b4703, 0x220216b9, 0x5505262f,
    0xc5ba3bbe, 0xb2bd0b28, 0x2bb45a92, 0x5cb36a04, 0xc2d7ffa7, 0xb5d0cf31, 0x2cd99e8b, 0x5bdeae1d,
    0x9b64c2b0, 0xec63f226, 0x756aa39c, 0x026d930a, 0x9c0906a9, 0xeb0e363f, 0x72076785, 0x05005713,
    0x95bf4a82, 0xe2b87a14, 0x7bb12bae, 0x0cb61b38, 0x92d28e9b, 0xe5d5be0d, 0x7cdcefb7, 0x0bdbdf21,
    0x86d3d2d4, 0xf1d4e242, 0x68ddb3f8, 0x1fda836e, 0x81be16cd, 0xf6b9265b, 0x6fb077e1, 0x18b74777,
    0x88085ae6, 0xff0f6a70, 0x66063bca, 0x11010b5c, 0x8f659eff, 0xf862ae69, 0x616bffd3, 0x166ccf45,
    0xa00ae278, 0xd70dd2ee, 0x4e048354, 0x3903b3c2, 0xa7672661, 0xd06016f7, 0x4969474d, 0x3e6e77db,
    0xaed16a4a, 0xd9d65adc, 0x40df0b66, 0x37d83bf0, 0xa9bcae53, 0xdebb9ec5, 0x47b2cf7f, 0x30b5ffe9,
    0xbdbdf21c, 0xcabac28a, 0x53b39330, 0x24b4a3a6, 0xbad03605, 0xcdd70693, 0x54de5729, 0x23d967bf,
    0xb3667a2e, 0xc4614ab8, 0x5d681b02, 0x2a6f2b94, 0xb40bbe37, 0xc30c8ea1, 0x5a05df1b, 0x2d02ef8d,
};

const c_line_buffer_len = 4096;
const c_line_payload_len = c_line_buffer_len - 1;

pub fn partialCrc32One(c: u8, crc: u32) u32 {
    return crctab32[(crc ^ c) & 0xff] ^ (crc >> 8);
}

pub fn partialCrc32(s: []const u8, crc: u32) u32 {
    var result = crc;
    for (s) |c| result = partialCrc32One(c, result);
    return result;
}

pub fn crc32(s: []const u8) u32 {
    return partialCrc32(s, 0xffff_ffff) ^ 0xffff_ffff;
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

fn writeJsonEscaped(writer: anytype, text: []const u8) !void {
    for (text) |c| switch (c) {
        '\\' => try writer.writeAll("\\\\"),
        '"' => try writer.writeAll("\\\""),
        '\x08' => try writer.writeAll("\\b"),
        '\x0c' => try writer.writeAll("\\f"),
        '\n' => try writer.writeAll("\\n"),
        '\r' => try writer.writeAll("\\r"),
        '\t' => try writer.writeAll("\\t"),
        else => {
            if (c < 0x20) {
                try writer.print("\\u00{x:0>2}", .{c});
            } else {
                try writer.writeByte(c);
            }
        },
    };
}

pub fn runGenksymsCrc(input: []const u8, writer: anytype) !void {
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

pub fn main(init: std.process.Init) !void {
    const arena = init.arena.allocator();
    const io = init.io;
    const args = try init.minimal.args.toSlice(arena);

    if (args.len != 2) {
        var stderr_buffer: [128]u8 = undefined;
        var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
        try stderr_writer.interface.writeAll("Usage: genksyms_crc <input.txt>\n");
        try stderr_writer.interface.flush();
        std.process.exit(1);
    }

    const input = try Io.Dir.cwd().readFileAlloc(io, args[1], arena, .unlimited);

    var stdout_buffer: [4096]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    try runGenksymsCrc(input, &stdout_writer.interface);
    try stdout_writer.interface.flush();
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

test "crc32 matches known baseline strings" {
    try std.testing.expectEqual(@as(u32, 0x00000000), crc32(""));
    try std.testing.expectEqual(@as(u32, 0x1451dab1), crc32("int"));
}

test "partialCrc32 composes across split input" {
    const prefix = partialCrc32("VMLINUX_SYMBOL_STR(", 0xffff_ffff);
    const suffix = partialCrc32("sample_symbol)", prefix) ^ 0xffff_ffff;
    try std.testing.expectEqual(crc32("VMLINUX_SYMBOL_STR(sample_symbol)"), suffix);
}

test "normalizeCHarnessChunk truncates at the first NUL before trimming carriage returns" {
    const nul_then_final_carriage = [_]u8{ 'b', '\r', 0, 'c', '\r' };
    try std.testing.expectEqualStrings("b", normalizeCHarnessChunk(&nul_then_final_carriage));
}

test "runGenksymsCrc emits bounded json output" {
    var capture = try Capture(64).init(std.testing.allocator);
    defer capture.deinit();
    try runGenksymsCrc("int\nstruct device\n", &capture);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"int\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"crc_hex\":\"0x1451dab1\"") != null);
}

test "runGenksymsCrc preserves case order while skipping blank lines" {
    var capture = try Capture(192).init(std.testing.allocator);
    defer capture.deinit();
    try runGenksymsCrc("struct device\n\nint\r\n", &capture);
    try std.testing.expectEqualStrings(
        "{\"cases\":[{\"input\":\"struct device\",\"crc_hex\":\"0xa38c4517\"},{\"input\":\"int\",\"crc_hex\":\"0x1451dab1\"}]}\n",
        capture.list.items,
    );
}

test "runGenksymsCrc hashes a trailing unterminated line at EOF" {
    var capture = try Capture(128).init(std.testing.allocator);
    defer capture.deinit();
    try runGenksymsCrc("int\nunsigned int eof_tail", &capture);
    try std.testing.expectEqualStrings(
        "{\"cases\":[{\"input\":\"int\",\"crc_hex\":\"0x1451dab1\"},{\"input\":\"unsigned int eof_tail\",\"crc_hex\":\"0x1d2695dc\"}]}\n",
        capture.list.items,
    );
}

test "runGenksymsCrc mirrors C fgets chunking for oversized lines" {
    var long_line = try std.ArrayList(u8).initCapacity(std.testing.allocator, c_line_payload_len + 3);
    defer long_line.deinit(std.testing.allocator);
    try long_line.appendNTimes(std.testing.allocator, 'a', c_line_payload_len);
    try long_line.append(std.testing.allocator, 'b');
    try long_line.append(std.testing.allocator, '\n');

    var capture = try Capture(12288).init(std.testing.allocator);
    defer capture.deinit();
    try runGenksymsCrc(long_line.items, &capture);

    const first_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{crc32(long_line.items[0..c_line_payload_len])});
    defer std.testing.allocator.free(first_crc);
    const second_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{crc32("b")});
    defer std.testing.allocator.free(second_crc);
    const unsplit_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{crc32(long_line.items[0 .. long_line.items.len - 1])});
    defer std.testing.allocator.free(unsplit_crc);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, unsplit_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, first_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, second_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"b\"") != null);
}

test "runGenksymsCrc keeps an exact-buffer EOF record unsplit" {
    var exact_line = try std.ArrayList(u8).initCapacity(std.testing.allocator, c_line_payload_len);
    defer exact_line.deinit(std.testing.allocator);
    try exact_line.appendNTimes(std.testing.allocator, 'a', c_line_payload_len);

    var capture = try Capture(12288).init(std.testing.allocator);
    defer capture.deinit();
    try runGenksymsCrc(exact_line.items, &capture);
    const exact_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{crc32(exact_line.items)});
    defer std.testing.allocator.free(exact_crc);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, exact_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"aa") != null);
    try std.testing.expectEqualStrings("{\"cases\":[{\"input\":\"", capture.list.items[0..20]);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "crc_hex") == 1);
}

test "runGenksymsCrc trims carriage returns from an exact-buffer EOF record" {
    var exact_line = try std.ArrayList(u8).initCapacity(std.testing.allocator, c_line_payload_len);
    defer exact_line.deinit(std.testing.allocator);
    try exact_line.appendNTimes(std.testing.allocator, 'a', c_line_payload_len - 2);
    try exact_line.append(std.testing.allocator, '\r');
    try exact_line.append(std.testing.allocator, '\r');

    var capture = try Capture(12288).init(std.testing.allocator);
    defer capture.deinit();
    try runGenksymsCrc(exact_line.items, &capture);

    const trimmed_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{crc32(exact_line.items[0 .. c_line_payload_len - 2])});
    defer std.testing.allocator.free(trimmed_crc);
    const untrimmed_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{crc32(exact_line.items)});
    defer std.testing.allocator.free(untrimmed_crc);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, trimmed_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, untrimmed_crc) == null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "crc_hex") == 1);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"\\r\"") == null);
}

test "runGenksymsCrc skips the blank newline-only continuation after an exact-buffer line" {
    var exact_line = try std.ArrayList(u8).initCapacity(std.testing.allocator, c_line_payload_len + 1);
    defer exact_line.deinit(std.testing.allocator);
    try exact_line.appendNTimes(std.testing.allocator, 'a', c_line_payload_len);
    try exact_line.append(std.testing.allocator, '\n');

    var capture = try Capture(12288).init(std.testing.allocator);
    defer capture.deinit();
    try runGenksymsCrc(exact_line.items, &capture);

    const exact_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{crc32(exact_line.items[0..c_line_payload_len])});
    defer std.testing.allocator.free(exact_crc);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, exact_crc) != null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "crc_hex") == 1);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"\\n\"") == null);
}

test "runGenksymsCrc skips repeated blank continuations after an exact-buffer split" {
    var exact_then_blank_chunks = try std.ArrayList(u8).initCapacity(std.testing.allocator, c_line_payload_len + 5);
    defer exact_then_blank_chunks.deinit(std.testing.allocator);
    try exact_then_blank_chunks.appendNTimes(std.testing.allocator, 'a', c_line_payload_len);
    try exact_then_blank_chunks.append(std.testing.allocator, '\n');
    try exact_then_blank_chunks.append(std.testing.allocator, '\r');
    try exact_then_blank_chunks.append(std.testing.allocator, '\n');
    try exact_then_blank_chunks.appendSlice(std.testing.allocator, "x\n");

    var capture = try Capture(16384).init(std.testing.allocator);
    defer capture.deinit();
    try runGenksymsCrc(exact_then_blank_chunks.items, &capture);

    const exact_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{crc32(exact_then_blank_chunks.items[0..c_line_payload_len])});
    defer std.testing.allocator.free(exact_crc);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, exact_crc) != null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "crc_hex") == 2);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"x\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"\\n\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"\\r\"") == null);
}

test "runGenksymsCrc skips a NUL-prefixed visible continuation after an exact-buffer split" {
    var exact_then_nul_chunk = try std.ArrayList(u8).initCapacity(std.testing.allocator, c_line_payload_len + 6);
    defer exact_then_nul_chunk.deinit(std.testing.allocator);
    try exact_then_nul_chunk.appendNTimes(std.testing.allocator, 'a', c_line_payload_len);
    try exact_then_nul_chunk.append(std.testing.allocator, 0);
    try exact_then_nul_chunk.appendSlice(std.testing.allocator, "bc\nx\n");

    var capture = try Capture(16384).init(std.testing.allocator);
    defer capture.deinit();
    try runGenksymsCrc(exact_then_nul_chunk.items, &capture);

    const exact_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{crc32(exact_then_nul_chunk.items[0..c_line_payload_len])});
    defer std.testing.allocator.free(exact_crc);
    const skipped_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{crc32("bc")});
    defer std.testing.allocator.free(skipped_crc);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, exact_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, skipped_crc) == null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "crc_hex") == 2);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"x\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"bc\"") == null);
}
