// SPDX-License-Identifier: GPL-2.0-only
const builtin = @import("builtin");
const std = @import("std");

pub const hex_asc = "0123456789abcdef";
pub const hex_asc_upper = "0123456789ABCDEF";

pub const HexError = error{
    InvalidHexDigit,
    InvalidSourceLength,
    DestinationTooSmall,
};

pub fn hexAscHi(byte: u8) u8 {
    return hex_asc[(byte >> 4) & 0x0f];
}

pub fn hexAscLo(byte: u8) u8 {
    return hex_asc[byte & 0x0f];
}

pub fn hexAscUpperHi(byte: u8) u8 {
    return hex_asc_upper[(byte >> 4) & 0x0f];
}

pub fn hexAscUpperLo(byte: u8) u8 {
    return hex_asc_upper[byte & 0x0f];
}

pub fn hexBytePack(buf: []u8, byte: u8) HexError![]u8 {
    if (buf.len < 2) {
        return HexError.DestinationTooSmall;
    }
    buf[0] = hexAscHi(byte);
    buf[1] = hexAscLo(byte);
    return buf[2..];
}

pub fn hexBytePackUpper(buf: []u8, byte: u8) HexError![]u8 {
    if (buf.len < 2) {
        return HexError.DestinationTooSmall;
    }
    buf[0] = hexAscUpperHi(byte);
    buf[1] = hexAscUpperLo(byte);
    return buf[2..];
}

pub fn hexToBin(ch: u8) i32 {
    const cu = ch & 0xdf;
    return -1 +
        decodeRange(ch, '0', '9', 1) +
        decodeRange(cu, 'A', 'F', 11);
}

pub fn hex2bin(dst: []u8, src: []const u8) HexError!void {
    if (src.len != dst.len * 2) {
        return HexError.InvalidSourceLength;
    }

    for (dst, 0..) |*byte, index| {
        const hi = hexToBin(src[index * 2]);
        if (hi < 0) {
            return HexError.InvalidHexDigit;
        }

        const lo = hexToBin(src[index * 2 + 1]);
        if (lo < 0) {
            return HexError.InvalidHexDigit;
        }

        byte.* = (@as(u8, @intCast(hi)) << 4) | @as(u8, @intCast(lo));
    }
}

pub fn bin2hex(dst: []u8, src: []const u8) HexError![]u8 {
    if (dst.len < src.len * 2) {
        return HexError.DestinationTooSmall;
    }

    var rest = dst;
    for (src) |byte| {
        rest = try hexBytePack(rest, byte);
    }
    return dst[0 .. src.len * 2];
}

pub fn hexDumpLineLength(
    len_input: usize,
    rowsize_input: usize,
    groupsize_input: usize,
    ascii: bool,
) usize {
    const rowsize = normalizedRowsize(rowsize_input);
    const len = @min(len_input, rowsize);
    const groupsize = normalizedGroupsize(len, groupsize_input);
    const ngroups = len / groupsize;

    if (ascii) {
        return rowsize * 2 + rowsize / groupsize + 1 + len;
    }
    return if (ngroups == 0) 0 else (groupsize * 2 + 1) * ngroups - 1;
}

pub fn hexDumpToBuffer(
    buf: []const u8,
    rowsize_input: usize,
    groupsize_input: usize,
    linebuf: []u8,
    ascii: bool,
) usize {
    const rowsize = normalizedRowsize(rowsize_input);
    const len = @min(buf.len, rowsize);
    const groupsize = normalizedGroupsize(len, groupsize_input);
    const required = hexDumpLineLength(buf.len, rowsize_input, groupsize_input, ascii);

    if (linebuf.len == 0) {
        return required;
    }

    if (len == 0) {
        linebuf[0] = 0;
        return 0;
    }

    if (linebuf.len > required) {
        return hexDumpToFullBuffer(buf[0..len], rowsize, groupsize, linebuf, ascii);
    }

    var writer = TruncatingWriter.init(linebuf);
    const ngroups = len / groupsize;
    const ascii_column = rowsize * 2 + rowsize / groupsize + 1;

    switch (groupsize) {
        8, 4, 2 => {
            var index: usize = 0;
            while (index < ngroups) : (index += 1) {
                if (index != 0) writer.appendByte(' ');
                writer.appendGroupHex(buf[index * groupsize ..][0..groupsize]);
            }
        },
        else => {
            for (buf[0..len]) |byte| {
                writer.appendByte(hexAscHi(byte));
                writer.appendByte(hexAscLo(byte));
                writer.appendByte(' ');
            }
            if (len != 0) {
                writer.removeLastByte();
            }
        },
    }

    if (ascii) {
        while (writer.required < ascii_column) {
            writer.appendByte(' ');
        }
        for (buf[0..len]) |byte| {
            writer.appendByte(if (byte < 0x80 and std.ascii.isPrint(byte)) byte else '.');
        }
    }

    writer.finish();
    return writer.required;
}

fn hexDumpToFullBuffer(
    buf: []const u8,
    rowsize: usize,
    groupsize: usize,
    linebuf: []u8,
    ascii: bool,
) usize {
    var pos: usize = 0;

    var group_start: usize = 0;
    while (group_start < buf.len) : (group_start += groupsize) {
        if (group_start != 0) {
            linebuf[pos] = ' ';
            pos += 1;
        }
        writeGroupHex(linebuf, &pos, buf[group_start .. group_start + groupsize]);
    }

    if (ascii) {
        const ascii_column = rowsize * 2 + rowsize / groupsize + 1;
        while (pos < ascii_column) : (pos += 1) {
            linebuf[pos] = ' ';
        }
        for (buf) |byte| {
            linebuf[pos] = if (byte < 0x80 and std.ascii.isPrint(byte)) byte else '.';
            pos += 1;
        }
    }

    linebuf[pos] = 0;
    return pos;
}

fn writeGroupHex(linebuf: []u8, pos: *usize, bytes: []const u8) void {
    if (builtin.cpu.arch.endian() == .little and bytes.len > 1) {
        var index = bytes.len;
        while (index > 0) {
            index -= 1;
            writeHexByte(linebuf, pos, bytes[index]);
        }
        return;
    }

    for (bytes) |byte| {
        writeHexByte(linebuf, pos, byte);
    }
}

fn writeHexByte(linebuf: []u8, pos: *usize, byte: u8) void {
    linebuf[pos.*] = hexAscHi(byte);
    linebuf[pos.* + 1] = hexAscLo(byte);
    pos.* += 2;
}

fn normalizedRowsize(rowsize_input: usize) usize {
    return if (rowsize_input == 16 or rowsize_input == 32) rowsize_input else 16;
}

fn normalizedGroupsize(len: usize, groupsize_input: usize) usize {
    var groupsize = groupsize_input;
    if (!std.math.isPowerOfTwo(groupsize) or groupsize > 8 or groupsize == 0) {
        groupsize = 1;
    }
    if (len % groupsize != 0) {
        groupsize = 1;
    }
    return groupsize;
}

fn decodeRange(ch: u8, first: u8, last: u8, bias: i8) i8 {
    const ch_i: i32 = ch;
    const first_i: i32 = first;
    const last_i: i32 = last;
    const bias_i: i32 = bias;

    const mask = @as(u32, @bitCast((ch_i - last_i - 1) & (first_i - 1 - ch_i))) >> 8;
    return @intCast((ch_i - first_i + bias_i) & @as(i32, @bitCast(mask)));
}

const TruncatingWriter = struct {
    buffer: []u8,
    required: usize = 0,

    fn init(buffer: []u8) TruncatingWriter {
        return .{ .buffer = buffer };
    }

    fn appendByte(self: *TruncatingWriter, byte: u8) void {
        if (self.required + 1 < self.buffer.len) {
            self.buffer[self.required] = byte;
        }
        self.required += 1;
    }

    fn appendGroupHex(self: *TruncatingWriter, bytes: []const u8) void {
        if (builtin.cpu.arch.endian() == .little and bytes.len > 1) {
            var index = bytes.len;
            while (index > 0) {
                index -= 1;
                self.appendByte(hexAscHi(bytes[index]));
                self.appendByte(hexAscLo(bytes[index]));
            }
            return;
        }

        for (bytes) |byte| {
            self.appendByte(hexAscHi(byte));
            self.appendByte(hexAscLo(byte));
        }
    }

    fn removeLastByte(self: *TruncatingWriter) void {
        if (self.required == 0) {
            return;
        }
        self.required -= 1;
    }

    fn finish(self: *TruncatingWriter) void {
        const terminator_index = @min(self.required, self.buffer.len - 1);
        self.buffer[terminator_index] = 0;
    }
};

test "hex conversion helpers cover mixed-case decoding and upper or lower encoding" {
    const sample = [_]u8{ 0x00, 0xab, 0x7f, 0xf0 };
    var decoded: [sample.len]u8 = undefined;
    var lower: [sample.len * 2]u8 = undefined;
    var upper: [sample.len * 2]u8 = undefined;
    var upper_rest: []u8 = upper[0..];

    try std.testing.expectEqual(@as(i32, 0), hexToBin('0'));
    try std.testing.expectEqual(@as(i32, 9), hexToBin('9'));
    try std.testing.expectEqual(@as(i32, 10), hexToBin('a'));
    try std.testing.expectEqual(@as(i32, 10), hexToBin('A'));
    try std.testing.expectEqual(@as(i32, 15), hexToBin('f'));
    try std.testing.expectEqual(@as(i32, 15), hexToBin('F'));
    try std.testing.expectEqual(@as(i32, -1), hexToBin('/'));
    try std.testing.expectEqual(@as(i32, -1), hexToBin('g'));

    try hex2bin(decoded[0..], "00Ab7fF0");
    try std.testing.expectEqualSlices(u8, &sample, decoded[0..]);

    try std.testing.expectEqualStrings("00ab7ff0", try bin2hex(lower[0..], &sample));

    for (sample) |byte| {
        upper_rest = try hexBytePackUpper(upper_rest, byte);
    }
    try std.testing.expectEqual(@as(usize, 0), upper_rest.len);
    try std.testing.expectEqualStrings("00AB7FF0", upper[0..]);
}

test "hex nibble helpers stay aligned with byte-pack helpers across the full byte range" {
    var lower: [2]u8 = undefined;
    var upper: [2]u8 = undefined;
    var decoded: [1]u8 = undefined;

    for (0..256) |value| {
        const byte: u8 = @intCast(value);

        _ = try hexBytePack(lower[0..], byte);
        _ = try hexBytePackUpper(upper[0..], byte);

        try std.testing.expectEqual(hexAscHi(byte), lower[0]);
        try std.testing.expectEqual(hexAscLo(byte), lower[1]);
        try std.testing.expectEqual(hexAscUpperHi(byte), upper[0]);
        try std.testing.expectEqual(hexAscUpperLo(byte), upper[1]);

        try hex2bin(decoded[0..], lower[0..]);
        try std.testing.expectEqual(byte, decoded[0]);
        try hex2bin(decoded[0..], upper[0..]);
        try std.testing.expectEqual(byte, decoded[0]);
    }
}

test "hex conversion helpers reject malformed sources and undersized destinations" {
    var decoded: [4]u8 = undefined;
    var short_encoded: [7]u8 = undefined;
    var tiny: [1]u8 = undefined;

    try std.testing.expectError(HexError.InvalidSourceLength, hex2bin(decoded[0..], "00ab7ff"));
    try std.testing.expectError(HexError.InvalidHexDigit, hex2bin(decoded[0..], "00ag7ff0"));
    try std.testing.expectError(HexError.DestinationTooSmall, bin2hex(short_encoded[0..], &[_]u8{ 0x00, 0xab, 0x7f, 0xf0 }));
    try std.testing.expectError(HexError.DestinationTooSmall, hexBytePack(tiny[0..], 0xbe));
    try std.testing.expectError(HexError.DestinationTooSmall, hexBytePackUpper(tiny[0..], 0xbe));
}

test "hexdump grouped plain output stays exact at full and truncated buffer capacity" {
    const input = [_]u8{
        0xbe, 0x32, 0xdb, 0x7b,
        0x0a, 0x18, 0x93, 0xb2,
        0x70, 0xba, 0xc4, 0x24,
        0x7d, 0x83, 0x34, 0x9b,
    };
    const cases = [_]struct {
        groupsize: usize,
        expected: []const u8,
    }{
        .{
            .groupsize = 2,
            .expected = if (builtin.cpu.arch.endian() == .big)
                "be32 db7b 0a18 93b2 70ba c424 7d83 349b"
            else
                "32be 7bdb 180a b293 ba70 24c4 837d 9b34",
        },
        .{
            .groupsize = 4,
            .expected = if (builtin.cpu.arch.endian() == .big)
                "be32db7b 0a1893b2 70bac424 7d83349b"
            else
                "7bdb32be b293180a 24c4ba70 9b34837d",
        },
        .{
            .groupsize = 8,
            .expected = if (builtin.cpu.arch.endian() == .big)
                "be32db7b0a1893b2 70bac4247d83349b"
            else
                "b293180a7bdb32be 9b34837d24c4ba70",
        },
    };

    for (cases) |case| {
        const required = hexDumpLineLength(input.len, 16, case.groupsize, false);
        try std.testing.expectEqual(@as(usize, case.expected.len), required);

        var exact: [48]u8 = undefined;
        const exact_written = hexDumpToBuffer(&input, 16, case.groupsize, exact[0 .. required + 1], false);
        try std.testing.expectEqual(required, exact_written);
        try std.testing.expectEqualSlices(u8, case.expected, std.mem.sliceTo(exact[0 .. required + 1], 0));
        try std.testing.expectEqual(@as(u8, 0), exact[required]);

        var truncated: [48]u8 = [_]u8{0xaa} ** 48;
        const truncated_written = hexDumpToBuffer(&input, 16, case.groupsize, truncated[0..required], false);
        try std.testing.expectEqual(required, truncated_written);
        try std.testing.expectEqualSlices(u8, case.expected[0 .. required - 1], std.mem.sliceTo(truncated[0..required], 0));
        try std.testing.expectEqual(@as(u8, 0), truncated[required - 1]);
    }
}

test "hexdump grouped-2 ascii output stays exact at full buffer capacity" {
    const input = [_]u8{
        0xbe, 0x32, 0xdb, 0x7b,
        0x0a, 0x18, 0x93, 0xb2,
        0x70, 0xba, 0xc4, 0x24,
        0x7d, 0x83, 0x34, 0x9b,
    };
    const expected = if (builtin.cpu.arch.endian() == .big)
        "be32 db7b 0a18 93b2 70ba c424 7d83 349b  .2.{....p..$}.4."
    else
        "32be 7bdb 180a b293 ba70 24c4 837d 9b34  .2.{....p..$}.4.";
    var exact: [58]u8 = undefined;

    const required = hexDumpLineLength(input.len, 16, 2, true);
    try std.testing.expectEqual(@as(usize, expected.len), required);
    try std.testing.expectEqual(@as(usize, 57), required);

    const written = hexDumpToBuffer(&input, 16, 2, exact[0..], true);
    try std.testing.expectEqual(required, written);
    try std.testing.expectEqualSlices(u8, expected, std.mem.sliceTo(exact[0..], 0));
    try std.testing.expectEqual(@as(u8, 0), exact[required]);
}

test "hexdump grouped ascii path reports the same required length for exact and truncated buffers" {
    const input = [_]u8{
        0xbe, 0x32, 0xdb, 0x7b,
        0x0a, 0x18, 0x93, 0xb2,
        0x70, 0xba, 0xc4, 0x24,
        0x7d, 0x83, 0x34, 0x9b,
    };
    const expected = if (builtin.cpu.arch.endian() == .big)
        "be32db7b 0a1893b2 70bac424 7d83349b  .2.{....p..$}.4."
    else
        "7bdb32be b293180a 24c4ba70 9b34837d  .2.{....p..$}.4.";

    const required = hexDumpLineLength(input.len, 16, 4, true);
    try std.testing.expectEqual(@as(usize, expected.len), required);
    try std.testing.expectEqual(@as(usize, 53), required);

    var exact: [54]u8 = undefined;
    const exact_written = hexDumpToBuffer(&input, 16, 4, exact[0..], true);
    try std.testing.expectEqual(required, exact_written);
    try std.testing.expectEqualSlices(u8, expected, std.mem.sliceTo(exact[0..], 0));
    try std.testing.expectEqual(@as(u8, 0), exact[required]);

    var truncated: [53]u8 = [_]u8{0xaa} ** 53;
    const truncated_written = hexDumpToBuffer(&input, 16, 4, truncated[0..], true);
    try std.testing.expectEqual(required, truncated_written);
    try std.testing.expectEqualSlices(u8, expected[0 .. expected.len - 1], std.mem.sliceTo(truncated[0..], 0));
    try std.testing.expectEqual(@as(u8, 0), truncated[truncated.len - 1]);
}

test "hexdump one-byte caller buffers still report full length and stay NUL terminated" {
    const input = [_]u8{ 0xbe, 0x32, 0xdb, 0x7b };
    const cases = [_]struct {
        rowsize: usize,
        groupsize: usize,
        ascii: bool,
    }{
        .{ .rowsize = 16, .groupsize = 1, .ascii = false },
        .{ .rowsize = 16, .groupsize = 2, .ascii = true },
        .{ .rowsize = 7, .groupsize = 3, .ascii = true },
    };

    for (cases) |case| {
        var single = [_]u8{0xaa};
        const required = hexDumpLineLength(input.len, case.rowsize, case.groupsize, case.ascii);
        const written = hexDumpToBuffer(&input, case.rowsize, case.groupsize, single[0..], case.ascii);
        try std.testing.expectEqual(required, written);
        try std.testing.expectEqual(@as(u8, 0), single[0]);
    }

    var empty = [_]u8{0xaa};
    try std.testing.expectEqual(@as(usize, 0), hexDumpToBuffer(input[0..0], 16, 1, empty[0..], false));
    try std.testing.expectEqual(@as(u8, 0), empty[0]);
}

test "hexdump grouped-8 ascii output stays exact at full buffer capacity" {
    const input = [_]u8{
        0xbe, 0x32, 0xdb, 0x7b,
        0x0a, 0x18, 0x93, 0xb2,
        0x70, 0xba, 0xc4, 0x24,
        0x7d, 0x83, 0x34, 0x9b,
    };
    const expected = if (builtin.cpu.arch.endian() == .big)
        "be32db7b0a1893b2 70bac4247d83349b  .2.{....p..$}.4."
    else
        "b293180a7bdb32be 9b34837d24c4ba70  .2.{....p..$}.4.";
    var exact: [52]u8 = undefined;

    const required = hexDumpLineLength(input.len, 16, 8, true);
    try std.testing.expectEqual(@as(usize, expected.len), required);
    try std.testing.expectEqual(@as(usize, 51), required);

    const written = hexDumpToBuffer(&input, 16, 8, exact[0..], true);
    try std.testing.expectEqual(required, written);
    try std.testing.expectEqualSlices(u8, expected, std.mem.sliceTo(exact[0..], 0));
    try std.testing.expectEqual(@as(u8, 0), exact[required]);
}
