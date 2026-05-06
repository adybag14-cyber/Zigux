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