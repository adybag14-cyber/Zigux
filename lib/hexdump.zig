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

fn bin2hexAppendWithPacker(dst: []u8, src: []const u8, comptime byte_packer: anytype) HexError![]u8 {
    if (dst.len < src.len * 2) {
        return HexError.DestinationTooSmall;
    }

    var rest = dst;
    for (src) |byte| {
        rest = try byte_packer(rest, byte);
    }
    return rest;
}

pub fn bin2hexAppend(dst: []u8, src: []const u8) HexError![]u8 {
    return bin2hexAppendWithPacker(dst, src, hexBytePack);
}

pub fn bin2hex(dst: []u8, src: []const u8) HexError![]u8 {
    const rest = try bin2hexAppend(dst, src);
    return dst[0 .. dst.len - rest.len];
}

pub fn bin2hexAppendUpper(dst: []u8, src: []const u8) HexError![]u8 {
    return bin2hexAppendWithPacker(dst, src, hexBytePackUpper);
}

pub fn bin2hexUpper(dst: []u8, src: []const u8) HexError![]u8 {
    const rest = try bin2hexAppendUpper(dst, src);
    return dst[0 .. dst.len - rest.len];
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
        8 => {
            var index: usize = 0;
            while (index < ngroups) : (index += 1) {
                if (index != 0) writer.appendByte(' ');
                writer.appendFixedWidthHex(readNativeInt(u64, buf[index * 8 ..][0..8]), 16);
            }
        },
        4 => {
            var index: usize = 0;
            while (index < ngroups) : (index += 1) {
                if (index != 0) writer.appendByte(' ');
                writer.appendFixedWidthHex(readNativeInt(u32, buf[index * 4 ..][0..4]), 8);
            }
        },
        2 => {
            var index: usize = 0;
            while (index < ngroups) : (index += 1) {
                if (index != 0) writer.appendByte(' ');
                writer.appendFixedWidthHex(readNativeInt(u16, buf[index * 2 ..][0..2]), 4);
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

fn readNativeInt(comptime T: type, bytes: []const u8) T {
    std.debug.assert(bytes.len == @sizeOf(T));

    const Shift = std.math.Log2Int(T);
    var value: T = 0;

    if (builtin.cpu.arch.endian() == .little) {
        for (bytes, 0..) |byte, index| {
            const shift: Shift = @intCast(index * 8);
            value |= @as(T, byte) << shift;
        }
    } else {
        for (bytes) |byte| {
            value = (value << @as(Shift, 8)) | @as(T, byte);
        }
    }

    return value;
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

    fn appendFixedWidthHex(self: *TruncatingWriter, value: anytype, digits: usize) void {
        const Int = @TypeOf(value);
        const Shift = std.math.Log2Int(Int);
        var remaining = digits;
        while (remaining > 0) {
            remaining -= 1;
            const shift: Shift = @intCast(remaining * 4);
            const nibble: u8 = @intCast((value >> shift) & 0x0f);
            self.appendByte(hex_asc[nibble]);
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

fn referenceHexToBin(ch: u8) i32 {
    return switch (ch) {
        '0'...'9' => ch - '0',
        'a'...'f' => ch - 'a' + 10,
        'A'...'F' => ch - 'A' + 10,
        else => -1,
    };
}

const test_data_b = [_]u8{
    0xbe, 0x32, 0xdb, 0x7b, 0x0a, 0x18, 0x93, 0xb2,
    0x70, 0xba, 0xc4, 0x24, 0x7d, 0x83, 0x34, 0x9b,
    0xa6, 0x9c, 0x31, 0xad, 0x9c, 0x0f, 0xac, 0xe9,
    0x4c, 0xd1, 0x19, 0x99, 0x43, 0xb1, 0xaf, 0x0c,
};

const test_ascii = ".2.{....p..$}.4...1.....L...C...";

fn assertExactCapacityFullBufferCase(
    len: usize,
    rowsize: usize,
    groupsize: usize,
    ascii: bool,
) !void {
    var exact: [160]u8 = [_]u8{'#'} ** 160;
    var roomy: [160]u8 = [_]u8{'#'} ** 160;

    const required = hexDumpLineLength(len, rowsize, groupsize, ascii);
    const exact_required = hexDumpToBuffer(
        test_data_b[0..len],
        rowsize,
        groupsize,
        exact[0 .. required + 1],
        ascii,
    );
    const roomy_required = hexDumpToBuffer(
        test_data_b[0..len],
        rowsize,
        groupsize,
        roomy[0..],
        ascii,
    );

    try std.testing.expectEqual(required, exact_required);
    try std.testing.expectEqual(required, roomy_required);
    try std.testing.expectEqualSlices(u8, std.mem.sliceTo(roomy[0..], 0), std.mem.sliceTo(exact[0..], 0));
    try std.testing.expectEqual(@as(u8, 0), exact[required]);
    try std.testing.expectEqual(@as(u8, 0), roomy[required]);

    for (exact[required + 1 ..]) |byte| {
        try std.testing.expectEqual(@as(u8, '#'), byte);
    }
    for (roomy[required + 1 ..]) |byte| {
        try std.testing.expectEqual(@as(u8, '#'), byte);
    }
}

test "hexToBin accepts digits and both alphabetic cases" {
    try std.testing.expectEqual(@as(i32, 0), hexToBin('0'));
    try std.testing.expectEqual(@as(i32, 9), hexToBin('9'));
    try std.testing.expectEqual(@as(i32, 10), hexToBin('a'));
    try std.testing.expectEqual(@as(i32, 10), hexToBin('A'));
    try std.testing.expectEqual(@as(i32, 15), hexToBin('f'));
    try std.testing.expectEqual(@as(i32, 15), hexToBin('F'));
    try std.testing.expectEqual(@as(i32, -1), hexToBin('g'));
    try std.testing.expectEqual(@as(i32, -1), hexToBin('/'));
}

test "hexToBin matches the full byte classification matrix" {
    var raw: u16 = 0;
    while (raw <= 0xff) : (raw += 1) {
        const ch: u8 = @intCast(raw);
        try std.testing.expectEqual(referenceHexToBin(ch), hexToBin(ch));
    }
}

test "hex2bin and bin2hex round-trip payloads" {
    const source = "be32db7b0a1893b2";
    var decoded: [8]u8 = undefined;
    try hex2bin(decoded[0..], source);

    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xbe, 0x32, 0xdb, 0x7b, 0x0a, 0x18, 0x93, 0xb2 }, decoded[0..]);

    var encoded: [16]u8 = undefined;
    const text = try bin2hex(encoded[0..], decoded[0..]);
    try std.testing.expectEqualSlices(u8, source, text);
}

test "bin2hexUpper emits uppercase hex text" {
    const source = [_]u8{ 0xbe, 0x32, 0xdb, 0x7b };

    var encoded: [8]u8 = undefined;
    const text = try bin2hexUpper(encoded[0..], source[0..]);
    try std.testing.expectEqualSlices(u8, "BE32DB7B", text);
}

test "bin2hexAppend helpers return the remaining destination slice" {
    const source = [_]u8{ 0xbe, 0x32, 0xdb, 0x7b };
    var encoded: [12]u8 = [_]u8{'#'} ** 12;

    var rest = try bin2hexAppend(encoded[0..], source[0..2]);
    rest = try bin2hexAppendUpper(rest, source[2..]);

    try std.testing.expectEqual(@as(usize, 4), rest.len);
    try std.testing.expectEqualSlices(u8, "be32DB7B", encoded[0..8]);
    try std.testing.expectEqualSlices(u8, "####", rest);

    var short: [7]u8 = undefined;
    try std.testing.expectError(HexError.DestinationTooSmall, bin2hexAppend(short[0..], source[0..4]));
    try std.testing.expectError(HexError.DestinationTooSmall, bin2hexAppendUpper(short[0..], source[0..4]));
}

test "hexAsc helpers expose lower and upper nibble text" {
    try std.testing.expectEqual(@as(u8, 'b'), hexAscHi(0xbe));
    try std.testing.expectEqual(@as(u8, 'e'), hexAscLo(0xbe));
    try std.testing.expectEqual(@as(u8, 'B'), hexAscUpperHi(0xbe));
    try std.testing.expectEqual(@as(u8, 'E'), hexAscUpperLo(0xbe));
    try std.testing.expectEqual(@as(u8, '0'), hexAscHi(0x0f));
    try std.testing.expectEqual(@as(u8, 'f'), hexAscLo(0x0f));
}

test "hexBytePack helpers emit expected text and reject short buffers" {
    var lower: [4]u8 = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa };
    const lower_rest = try hexBytePack(lower[0..], 0xbe);
    try std.testing.expectEqual(@as(usize, 2), lower_rest.len);
    try std.testing.expectEqualSlices(u8, "be", lower[0..2]);

    var upper: [4]u8 = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa };
    const upper_rest = try hexBytePackUpper(upper[0..], 0xbe);
    try std.testing.expectEqual(@as(usize, 2), upper_rest.len);
    try std.testing.expectEqualSlices(u8, "BE", upper[0..2]);

    var short: [1]u8 = undefined;
    try std.testing.expectError(HexError.DestinationTooSmall, hexBytePack(short[0..], 0xbe));
    try std.testing.expectError(HexError.DestinationTooSmall, hexBytePackUpper(short[0..], 0xbe));
}

test "hex2bin rejects invalid length and bad digits" {
    var decoded: [2]u8 = undefined;
    try std.testing.expectError(HexError.InvalidSourceLength, hex2bin(decoded[0..], "abc"));
    try std.testing.expectError(HexError.InvalidHexDigit, hex2bin(decoded[0..], "zz00"));
}

test "hexDumpLineLength mirrors formatter normalization" {
    const cases = [_]struct {
        len: usize,
        rowsize: usize,
        groupsize: usize,
        ascii: bool,
        want: usize,
    }{
        .{ .len = 0, .rowsize = 16, .groupsize = 1, .ascii = false, .want = 0 },
        .{ .len = 16, .rowsize = 16, .groupsize = 1, .ascii = false, .want = 47 },
        .{ .len = 16, .rowsize = 7, .groupsize = 3, .ascii = false, .want = 47 },
        .{ .len = 16, .rowsize = 7, .groupsize = 3, .ascii = true, .want = 65 },
        .{ .len = 32, .rowsize = 32, .groupsize = 1, .ascii = true, .want = 129 },
        .{ .len = 20, .rowsize = 16, .groupsize = 8, .ascii = false, .want = 33 },
        .{ .len = 15, .rowsize = 16, .groupsize = 8, .ascii = true, .want = 64 },
    };

    for (cases) |case| {
        try std.testing.expectEqual(case.want, hexDumpLineLength(case.len, case.rowsize, case.groupsize, case.ascii));
        try std.testing.expectEqual(
            case.want,
            hexDumpToBuffer(test_data_b[0..case.len], case.rowsize, case.groupsize, &[_]u8{}, case.ascii),
        );
    }
}

test "hexDumpToBuffer emits grouped and ascii text" {
    var linebuf: [160]u8 = undefined;

    try std.testing.expectEqual(@as(usize, 47), hexDumpToBuffer(test_data_b[0..16], 16, 1, linebuf[0..], false));
    try std.testing.expectEqualSlices(u8, "be 32 db 7b 0a 18 93 b2 70 ba c4 24 7d 83 34 9b", std.mem.sliceTo(linebuf[0..], 0));

    try std.testing.expectEqual(@as(usize, 65), hexDumpToBuffer(test_data_b[0..16], 16, 1, linebuf[0..], true));
    try std.testing.expectEqualSlices(u8, "be 32 db 7b 0a 18 93 b2 70 ba c4 24 7d 83 34 9b  .2.{....p..$}.4.", std.mem.sliceTo(linebuf[0..], 0));

    try std.testing.expectEqual(@as(usize, 39), hexDumpToBuffer(test_data_b[0..16], 16, 2, linebuf[0..], false));
    const grouped2 = if (builtin.cpu.arch.endian() == .big)
        "be32 db7b 0a18 93b2 70ba c424 7d83 349b"
    else
        "32be 7bdb 180a b293 ba70 24c4 837d 9b34";
    try std.testing.expectEqualSlices(u8, grouped2, std.mem.sliceTo(linebuf[0..], 0));

    try std.testing.expectEqual(@as(usize, 35), hexDumpToBuffer(test_data_b[0..16], 16, 4, linebuf[0..], false));
    const grouped4 = if (builtin.cpu.arch.endian() == .big)
        "be32db7b 0a1893b2 70bac424 7d83349b"
    else
        "7bdb32be b293180a 24c4ba70 9b34837d";
    try std.testing.expectEqualSlices(u8, grouped4, std.mem.sliceTo(linebuf[0..], 0));

    try std.testing.expectEqual(@as(usize, 33), hexDumpToBuffer(test_data_b[0..16], 16, 8, linebuf[0..], false));
    const grouped8 = if (builtin.cpu.arch.endian() == .big)
        "be32db7b0a1893b2 70bac4247d83349b"
    else
        "b293180a7bdb32be 9b34837d24c4ba70";
    try std.testing.expectEqualSlices(u8, grouped8, std.mem.sliceTo(linebuf[0..], 0));
}

test "hexDumpToBuffer proves exact 4-byte grouped ascii output" {
    var linebuf: [160]u8 = undefined;
    const required = hexDumpToBuffer(test_data_b[0..16], 16, 4, linebuf[0..], true);

    try std.testing.expectEqual(@as(usize, 53), required);
    try std.testing.expectEqualSlices(
        u8,
        if (builtin.cpu.arch.endian() == .big)
            "be32db7b 0a1893b2 70bac424 7d83349b  .2.{....p..$}.4."
        else
            "7bdb32be b293180a 24c4ba70 9b34837d  .2.{....p..$}.4.",
        std.mem.sliceTo(linebuf[0..], 0),
    );
}

test "hexDumpToBuffer proves exact 8-byte grouped output" {
    var linebuf: [160]u8 = undefined;
    const required = hexDumpToBuffer(test_data_b[0..16], 16, 8, linebuf[0..], false);

    try std.testing.expectEqual(@as(usize, 33), required);
    try std.testing.expectEqualSlices(
        u8,
        if (builtin.cpu.arch.endian() == .big)
            "be32db7b0a1893b2 70bac4247d83349b"
        else
            "b293180a7bdb32be 9b34837d24c4ba70",
        std.mem.sliceTo(linebuf[0..], 0),
    );
}

test "hexDumpToBuffer proves exact 2-byte grouped ascii output" {
    var linebuf: [160]u8 = undefined;
    const required = hexDumpToBuffer(test_data_b[0..16], 16, 2, linebuf[0..], true);

    try std.testing.expectEqual(@as(usize, 57), required);
    try std.testing.expectEqualSlices(
        u8,
        if (builtin.cpu.arch.endian() == .big)
            "be32 db7b 0a18 93b2 70ba c424 7d83 349b  .2.{....p..$}.4."
        else
            "32be 7bdb 180a b293 ba70 24c4 837d 9b34  .2.{....p..$}.4.",
        std.mem.sliceTo(linebuf[0..], 0),
    );
}

test "hexDumpToBuffer proves exact 8-byte grouped ascii output" {
    var linebuf: [160]u8 = undefined;
    const required = hexDumpToBuffer(test_data_b[0..16], 16, 8, linebuf[0..], true);

    try std.testing.expectEqual(@as(usize, 51), required);
    try std.testing.expectEqualSlices(
        u8,
        if (builtin.cpu.arch.endian() == .big)
            "be32db7b0a1893b2 70bac4247d83349b  .2.{....p..$}.4."
        else
            "b293180a7bdb32be 9b34837d24c4ba70  .2.{....p..$}.4.",
        std.mem.sliceTo(linebuf[0..], 0),
    );
}

test "hexDumpToBuffer exact-capacity full-buffer path stays aligned with fixture output" {
    try assertExactCapacityFullBufferCase(16, 16, 1, false);
    try assertExactCapacityFullBufferCase(16, 16, 2, false);
    try assertExactCapacityFullBufferCase(16, 16, 2, true);
    try assertExactCapacityFullBufferCase(16, 16, 4, false);
    try assertExactCapacityFullBufferCase(16, 16, 4, true);
    try assertExactCapacityFullBufferCase(32, 32, 2, true);
    try assertExactCapacityFullBufferCase(16, 16, 8, false);
    try assertExactCapacityFullBufferCase(16, 16, 8, true);
}
