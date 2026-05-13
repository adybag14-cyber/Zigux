const builtin = @import("builtin");
const std = @import("std");

pub const hex_asc = "0123456789abcdef";
pub const hex_asc_upper = "0123456789ABCDEF";

const hex_digits = hex_asc;
const native_endian = builtin.target.cpu.arch.endian();

pub const HexError = error{
    DestinationTooSmall,
};

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

pub fn hexAscHi(byte: u8) u8 {
    return hex_digits[byte >> 4];
}

pub fn hexAscLo(byte: u8) u8 {
    return hex_digits[byte & 0x0f];
}

pub fn hexAscUpperHi(byte: u8) u8 {
    return hex_asc_upper[byte >> 4];
}

pub fn hexAscUpperLo(byte: u8) u8 {
    return hex_asc_upper[byte & 0x0f];
}

pub fn hexBytePack(dst: []u8, byte: u8) HexError![]u8 {
    if (dst.len < 2) {
        return error.DestinationTooSmall;
    }
    dst[0] = hexAscHi(byte);
    dst[1] = hexAscLo(byte);
    return dst[2..];
}

pub fn hexBytePackUpper(dst: []u8, byte: u8) HexError![]u8 {
    if (dst.len < 2) {
        return error.DestinationTooSmall;
    }
    dst[0] = hexAscUpperHi(byte);
    dst[1] = hexAscUpperLo(byte);
    return dst[2..];
}

fn appendHexByte(writer: *LineWriter, byte: u8) void {
    writer.appendByte(hexAscHi(byte));
    writer.appendByte(hexAscLo(byte));
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
        dst[offset] = hexAscHi(byte);
        dst[offset + 1] = hexAscLo(byte);
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

pub fn hexDumpLineLength(len: usize, rowsize: usize, groupsize: usize, ascii: bool) usize {
    return requiredLineLength(len, rowsize, groupsize, ascii);
}

pub fn hex_dump_line_length(len: usize, rowsize: usize, groupsize: usize, ascii: bool) usize {
    return hexDumpLineLength(len, rowsize, groupsize, ascii);
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

test "hex byte helpers and packers stay aligned" {
    const byte: u8 = 0xbe;
    var lower: [2]u8 = undefined;
    var upper: [2]u8 = undefined;
    var tiny: [1]u8 = undefined;

    try std.testing.expectEqual(@as(u8, 'b'), hexAscHi(byte));
    try std.testing.expectEqual(@as(u8, 'e'), hexAscLo(byte));
    try std.testing.expectEqual(@as(u8, 'B'), hexAscUpperHi(byte));
    try std.testing.expectEqual(@as(u8, 'E'), hexAscUpperLo(byte));

    const lower_rest = try hexBytePack(lower[0..], byte);
    const upper_rest = try hexBytePackUpper(upper[0..], byte);
    try std.testing.expectEqual(@as(usize, 0), lower_rest.len);
    try std.testing.expectEqual(@as(usize, 0), upper_rest.len);
    try std.testing.expectEqualStrings("be", lower[0..]);
    try std.testing.expectEqualStrings("BE", upper[0..]);

    try std.testing.expectError(error.DestinationTooSmall, hexBytePack(tiny[0..], byte));
    try std.testing.expectError(error.DestinationTooSmall, hexBytePackUpper(tiny[0..], byte));
}

test "hex dump line length aliases the required length helper" {
    try std.testing.expectEqual(@as(usize, 0), hexDumpLineLength(0, 16, 1, false));
    try std.testing.expectEqual(requiredLineLength(16, 16, 4, true), hexDumpLineLength(16, 16, 4, true));
    try std.testing.expectEqual(requiredLineLength(9, 32, 4, false), hex_dump_line_length(9, 32, 4, false));
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

test "grouped ascii output keeps the grouped hex prefix and required length aligned" {
    var linebuf: [80]u8 = undefined;
    const input = [_]u8{ 'A', 'B', 'C', 'D' };
    const written = hexDumpToBuffer(&input, 16, 2, &linebuf, true);
    const expected_hex = if (native_endian == .little) "4241 4443" else "4142 4344";
    const expected_column = asciiColumn(16, 2);

    try std.testing.expectEqual(requiredLineLength(input.len, 16, 2, true), written);
    try std.testing.expectEqualStrings(expected_hex, linebuf[0..expected_hex.len]);
    try std.testing.expectEqualStrings("ABCD", linebuf[expected_column..written]);
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

test "invalid rowsize falls back to the 16-byte row contract" {
    var linebuf: [80]u8 = undefined;
    const input = [_]u8{
        0x00, 0x01, 0x02, 0x03,
        0x04, 0x05, 0x06, 0x07,
        0x08, 0x09, 0x0a, 0x0b,
        0x0c, 0x0d, 0x0e, 0x0f,
        0x10, 0x11, 0x12, 0x13,
    };
    const written = hexDumpToBuffer(&input, 24, 1, &linebuf, false);

    try std.testing.expectEqual(requiredLineLength(input.len, 24, 1, false), written);
    try std.testing.expectEqualStrings(
        "00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f",
        linebuf[0..written],
    );
}

test "g8 grouped ascii output follows native-endian order and the 16-byte ascii column" {
    var linebuf: [96]u8 = undefined;
    const input = [_]u8{
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
        'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
    };
    const written = hexDumpToBuffer(&input, 16, 8, &linebuf, true);
    const expected_hex = if (native_endian == .little)
        "4847464544434241 504f4e4d4c4b4a49"
    else
        "4142434445464748 494a4b4c4d4e4f50";
    const expected_column = asciiColumn(16, 8);

    try std.testing.expectEqual(requiredLineLength(input.len, 16, 8, true), written);
    try std.testing.expectEqualStrings(expected_hex, linebuf[0..expected_hex.len]);
    try std.testing.expectEqualStrings("ABCDEFGHIJKLMNOP", linebuf[expected_column..written]);
}
