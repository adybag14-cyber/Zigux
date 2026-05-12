const builtin = @import("builtin");
const std = @import("std");

pub const hex_asc = "0123456789abcdef";
pub const hex_asc_upper = "0123456789ABCDEF";

const hex_digits = hex_asc;
const native_endian = builtin.target.cpu.arch.endian();

const LineWriter = struct {
    buffer: []u8,
    total: usize = 0,

    fn appendByte(self: *LineWriter, byte: u8) void {
        if (self.buffer.len != 0 and self.total < self.buffer.len - 1) {
            self.buffer[self.total] = byte;
        }
        self.total += 1;
    }

    fn finish(self: *LineWriter) void {
        if (self.buffer.len == 0) {
            return;
        }

        const nul_index = @min(self.total, self.buffer.len - 1);
        self.buffer[nul_index] = 0;
    }
};

fn normalizedRowSize(rowsize: usize) usize {
    return if (rowsize == 16 or rowsize == 32) rowsize else 16;
}

fn normalizedGroupSize(len: usize, groupsize: usize) usize {
    if (groupsize != 1 and groupsize != 2 and groupsize != 4 and groupsize != 8) {
        return 1;
    }
    if ((len % groupsize) != 0) {
        return 1;
    }
    return groupsize;
}

fn asciiColumn(rowsize: usize, groupsize: usize) usize {
    return rowsize * 2 + (rowsize / groupsize) + 1;
}

fn appendHexByte(writer: *LineWriter, byte: u8) void {
    writer.appendByte(hex_digits[byte >> 4]);
    writer.appendByte(hex_digits[byte & 0x0f]);
}

fn appendGroupedHex(writer: *LineWriter, chunk: []const u8) void {
    if (native_endian == .little) {
        var idx = chunk.len;
        while (idx != 0) {
            idx -= 1;
            appendHexByte(writer, chunk[idx]);
        }
        return;
    }

    for (chunk) |byte| {
        appendHexByte(writer, byte);
    }
}

fn printableAscii(byte: u8) u8 {
    return if (byte < 0x80 and std.ascii.isPrint(byte)) byte else '.';
}

pub fn hexToBin(ch: u8) ?u8 {
    if (ch >= '0' and ch <= '9') {
        return ch - '0';
    }

    const folded = ch | 0x20;
    if (folded >= 'a' and folded <= 'f') {
        return folded - 'a' + 10;
    }

    return null;
}

pub fn hex_to_bin(ch: u8) isize {
    return if (hexToBin(ch)) |value| value else -1;
}

pub const Hex2BinError = error{
    InvalidHex,
    InvalidLength,
};

pub fn hex2Bin(dst: []u8, src: []const u8) Hex2BinError!void {
    if (src.len != dst.len * 2) {
        return error.InvalidLength;
    }

    for (dst, 0..) |*byte, idx| {
        const hi = hexToBin(src[idx * 2]) orelse return error.InvalidHex;
        const lo = hexToBin(src[idx * 2 + 1]) orelse return error.InvalidHex;
        byte.* = (hi << 4) | lo;
    }
}

pub fn hex2bin(dst: []u8, src: []const u8) Hex2BinError!void {
    return hex2Bin(dst, src);
}

pub fn bin2Hex(dst: []u8, src: []const u8) []u8 {
    std.debug.assert(dst.len >= src.len * 2);

    var offset: usize = 0;
    for (src) |byte| {
        dst[offset] = hex_digits[byte >> 4];
        dst[offset + 1] = hex_digits[byte & 0x0f];
        offset += 2;
    }

    return dst[0..offset];
}

pub fn bin2hex(dst: []u8, src: []const u8) []u8 {
    return bin2Hex(dst, src);
}

pub fn requiredLineLength(len: usize, rowsize: usize, groupsize: usize, ascii: bool) usize {
    const actual_rowsize = normalizedRowSize(rowsize);
    const actual_len = @min(len, actual_rowsize);
    if (actual_len == 0) {
        return 0;
    }

    const actual_groupsize = normalizedGroupSize(actual_len, groupsize);
    const ngroups = actual_len / actual_groupsize;
    if (ascii) {
        return asciiColumn(actual_rowsize, actual_groupsize) + actual_len;
    }
    return (actual_len * 2) + ngroups - 1;
}

pub fn hexDumpToBuffer(buf: []const u8, rowsize: usize, groupsize: usize, linebuf: []u8, ascii: bool) usize {
    const actual_rowsize = normalizedRowSize(rowsize);
    const actual_len = @min(buf.len, actual_rowsize);
    if (linebuf.len == 0) {
        return requiredLineLength(actual_len, actual_rowsize, groupsize, ascii);
    }

    const actual_groupsize = normalizedGroupSize(actual_len, groupsize);
    var writer = LineWriter{ .buffer = linebuf };

    if (actual_len == 0) {
        writer.finish();
        return 0;
    }

    if (actual_groupsize == 1) {
        for (buf[0..actual_len], 0..) |byte, idx| {
            if (idx != 0) {
                writer.appendByte(' ');
            }
            appendHexByte(&writer, byte);
        }
    } else {
        var offset: usize = 0;
        while (offset < actual_len) : (offset += actual_groupsize) {
            if (offset != 0) {
                writer.appendByte(' ');
            }
            appendGroupedHex(&writer, buf[offset .. offset + actual_groupsize]);
        }
    }

    if (ascii) {
        const ascii_column = asciiColumn(actual_rowsize, actual_groupsize);
        while (writer.total < ascii_column) {
            writer.appendByte(' ');
        }
        for (buf[0..actual_len]) |byte| {
            writer.appendByte(printableAscii(byte));
        }
    }

    writer.finish();
    return writer.total;
}

pub fn hex_dump_to_buffer(buf: []const u8, rowsize: usize, groupsize: usize, linebuf: []u8, ascii: bool) usize {
    return hexDumpToBuffer(buf, rowsize, groupsize, linebuf, ascii);
}

test "hex_to_bin accepts numeric, lower, and upper digits" {
    try std.testing.expectEqual(@as(?u8, 0), hexToBin('0'));
    try std.testing.expectEqual(@as(?u8, 9), hexToBin('9'));
    try std.testing.expectEqual(@as(?u8, 10), hexToBin('a'));
    try std.testing.expectEqual(@as(?u8, 15), hexToBin('F'));
    try std.testing.expectEqual(@as(isize, -1), hex_to_bin('g'));
}

test "hex2bin decodes mixed-case input" {
    var decoded: [3]u8 = undefined;
    try hex2Bin(&decoded, "0aF15c");
    try std.testing.expectEqualSlices(u8, &.{ 0x0a, 0xf1, 0x5c }, &decoded);
}

test "hex2bin rejects malformed input" {
    var decoded: [2]u8 = undefined;

    try std.testing.expectError(error.InvalidLength, hex2Bin(&decoded, "0f0"));
    try std.testing.expectError(error.InvalidHex, hex2bin(&decoded, "0x0f"));
}

test "bin2hex emits lowercase output and returns the written slice" {
    var encoded: [8]u8 = undefined;
    const written = bin2Hex(&encoded, &.{ 0x0a, 0xf1, 0x5c });

    try std.testing.expectEqual(@as(usize, 6), written.len);
    try std.testing.expectEqualStrings("0af15c", written);
}

test "hex dump formats one-byte groups without ascii" {
    var linebuf: [32]u8 = undefined;
    const input = [_]u8{ 0x00, 0x01, 0x02, 0x03 };
    const written = hexDumpToBuffer(&input, 16, 1, &linebuf, false);

    try std.testing.expectEqual(@as(usize, 11), written);
    try std.testing.expectEqualStrings("00 01 02 03", linebuf[0..written]);
}

test "hex dump pads to the ascii column" {
    var linebuf: [80]u8 = undefined;
    const input = [_]u8{ 'A', 'B', 0x00, 0x7f };
    const written = hexDumpToBuffer(&input, 16, 1, &linebuf, true);
    const expected_column = asciiColumn(16, 1);

    try std.testing.expectEqual(@as(usize, expected_column + input.len), written);
    try std.testing.expectEqualStrings("41 42 00 7f", linebuf[0..11]);
    try std.testing.expectEqualStrings("AB..", linebuf[expected_column..written]);
}

test "hex dump truncation still reports the full logical length" {
    var linebuf: [8]u8 = undefined;
    const input = [_]u8{ 0x00, 0x01, 0x02, 0x03 };
    const written = hexDumpToBuffer(&input, 16, 1, &linebuf, false);

    try std.testing.expectEqual(@as(usize, 11), written);
    try std.testing.expectEqualStrings("00 01 0", linebuf[0 .. linebuf.len - 1]);
    try std.testing.expectEqual(@as(u8, 0), linebuf[linebuf.len - 1]);
}

test "hex dump grouped output follows native-endian group order" {
    var linebuf: [32]u8 = undefined;
    const input = [_]u8{ 0x10, 0x11, 0x12, 0x13 };
    const written = hexDumpToBuffer(&input, 16, 2, &linebuf, false);
    const expected = if (native_endian == .little) "1110 1312" else "1011 1213";

    try std.testing.expectEqual(@as(usize, expected.len), written);
    try std.testing.expectEqualStrings(expected, linebuf[0..written]);
}

test "invalid group sizes fall back to single-byte formatting" {
    var linebuf: [32]u8 = undefined;
    const input = [_]u8{ 0xaa, 0xbb, 0xcc };
    const written = hexDumpToBuffer(&input, 16, 3, &linebuf, false);

    try std.testing.expectEqual(@as(usize, 8), written);
    try std.testing.expectEqualStrings("aa bb cc", linebuf[0..written]);
}
