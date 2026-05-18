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
    if (len == 0) {
        return 0;
    }
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

    if (linebuf.len == 0) {
        return hexDumpLineLength(buf.len, rowsize_input, groupsize_input, ascii);
    }

    if (len == 0) {
        linebuf[0] = 0;
        return 0;
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

const test_data_b = [_]u8{
    0xbe, 0x32, 0xdb, 0x7b, 0x0a, 0x18, 0x93, 0xb2,
    0x70, 0xba, 0xc4, 0x24, 0x7d, 0x83, 0x34, 0x9b,
    0xa6, 0x9c, 0x31, 0xad, 0x9c, 0x0f, 0xac, 0xe9,
    0x4c, 0xd1, 0x19, 0x99, 0x43, 0xb1, 0xaf, 0x0c,
};

const test_ascii = ".2.{....p..$}.4...1.....L...C...";

const test_data_1 = [_][]const u8{
    "be", "32", "db", "7b", "0a", "18", "93", "b2",
    "70", "ba", "c4", "24", "7d", "83", "34", "9b",
    "a6", "9c", "31", "ad", "9c", "0f", "ac", "e9",
    "4c", "d1", "19", "99", "43", "b1", "af", "0c",
};

const test_data_2_le = [_][]const u8{
    "32be", "7bdb", "180a", "b293",
    "ba70", "24c4", "837d", "9b34",
    "9ca6", "ad31", "0f9c", "e9ac",
    "d14c", "9919", "b143", "0caf",
};

const test_data_2_be = [_][]const u8{
    "be32", "db7b", "0a18", "93b2",
    "70ba", "c424", "7d83", "349b",
    "a69c", "31ad", "9c0f", "ace9",
    "4cd1", "1999", "43b1", "af0c",
};

const test_data_4_le = [_][]const u8{
    "7bdb32be", "b293180a", "24c4ba70", "9b34837d",
    "ad319ca6", "e9ac0f9c", "9919d14c", "0cafb143",
};

const test_data_4_be = [_][]const u8{
    "be32db7b", "0a1893b2", "70bac424", "7d83349b",
    "a69c31ad", "9c0face9", "4cd11999", "43b1af0c",
};

const test_data_8_le = [_][]const u8{
    "b293180a7bdb32be", "9b34837d24c4ba70",
    "e9ac0f9cad319ca6", "0cafb1439919d14c",
};

const test_data_8_be = [_][]const u8{
    "be32db7b0a1893b2", "70bac4247d83349b",
    "a69c31ad9c0face9", "4cd1199943b1af0c",
};

fn fixtureChunks(groupsize: usize) []const []const u8 {
    return switch (groupsize) {
        8 => if (builtin.cpu.arch.endian() == .big) test_data_8_be[0..] else test_data_8_le[0..],
        4 => if (builtin.cpu.arch.endian() == .big) test_data_4_be[0..] else test_data_4_le[0..],
        2 => if (builtin.cpu.arch.endian() == .big) test_data_2_be[0..] else test_data_2_le[0..],
        else => test_data_1[0..],
    };
}

fn prepareExpectedLine(
    buffer: []u8,
    len_input: usize,
    rowsize_input: usize,
    groupsize_input: usize,
    ascii: bool,
) []const u8 {
    const rowsize = normalizedRowsize(rowsize_input);
    const len = @min(len_input, rowsize);
    const groupsize = normalizedGroupsize(len, groupsize_input);
    const chunks = fixtureChunks(groupsize);

    var pos: usize = 0;
    var index: usize = 0;
    while (index < len / groupsize) : (index += 1) {
        const chunk = chunks[index];
        @memcpy(buffer[pos .. pos + chunk.len], chunk);
        pos += chunk.len;
        buffer[pos] = ' ';
        pos += 1;
    }
    if (index != 0) {
        pos -= 1;
    }

    if (ascii) {
        while (pos < rowsize * 2 + rowsize / groupsize + 1) : (pos += 1) {
            buffer[pos] = ' ';
        }
        @memcpy(buffer[pos .. pos + len], test_ascii[0..len]);
        pos += len;
    }

    buffer[pos] = 0;
    return buffer[0..pos];
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

test "hex2bin and bin2hex round-trip payloads" {
    const source = "be32db7b0a1893b2";
    var decoded: [8]u8 = undefined;
    try hex2bin(decoded[0..], source);

    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xbe, 0x32, 0xdb, 0x7b, 0x0a, 0x18, 0x93, 0xb2 }, decoded[0..]);

    var encoded: [16]u8 = undefined;
    const text = try bin2hex(encoded[0..], decoded[0..]);
    try std.testing.expectEqualSlices(u8, source, text);
}

test "hex2bin and bin2hex snake-case aliases stay aligned" {
    var decoded_direct: [3]u8 = undefined;
    var decoded_alias: [3]u8 = undefined;
    var encoded_direct: [8]u8 = undefined;
    var encoded_alias: [8]u8 = undefined;

    try hex2Bin(&decoded_direct, "0aF15c");
    try hex2bin(&decoded_alias, "0aF15c");
    try std.testing.expectEqualSlices(u8, &decoded_direct, &decoded_alias);

    const direct_written = try bin2Hex(&encoded_direct, &decoded_direct);
    const alias_written = try bin2hex(&encoded_alias, &decoded_alias);
    try std.testing.expectEqual(@as(usize, direct_written.len), alias_written.len);
    try std.testing.expectEqualStrings(direct_written, alias_written);
    try std.testing.expectEqualStrings("0af15c", alias_written);
}

test "hexBytePack helpers chain bytes and preserve destination on bounds errors" {
    const sample = [_]u8{ 0x00, 0xbe, 0xff };
    var lower: [6]u8 = undefined;
    var upper: [6]u8 = undefined;
    var lower_rest: []u8 = lower[0..];
    var upper_rest: []u8 = upper[0..];

    for (sample) |byte| {
        lower_rest = try hexBytePack(lower_rest, byte);
        upper_rest = try hexBytePackUpper(upper_rest, byte);
    }

    try std.testing.expectEqual(@as(usize, 0), lower_rest.len);
    try std.testing.expectEqual(@as(usize, 0), upper_rest.len);
    try std.testing.expectEqualSlices(u8, "00beff", lower[0..]);
    try std.testing.expectEqualSlices(u8, "00BEFF", upper[0..]);

    var tiny_lower = [_]u8{0xaa};
    var tiny_upper = [_]u8{0xbb};
    try std.testing.expectError(HexError.DestinationTooSmall, hexBytePack(tiny_lower[0..], 0x5c));
    try std.testing.expectError(HexError.DestinationTooSmall, hexBytePackUpper(tiny_upper[0..], 0x5c));
    try std.testing.expectEqual(@as(u8, 0xaa), tiny_lower[0]);
    try std.testing.expectEqual(@as(u8, 0xbb), tiny_upper[0]);
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
        .{ .len = 0, .rowsize = 16, .groupsize = 1, .ascii = true, .want = 0 },
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

test "hexDumpToBuffer matches the kernel-style 16-byte line output" {
    var line: [16 * 3 + 2 + 16 + 1]u8 = undefined;
    var expected: [16 * 3 + 2 + 16 + 1]u8 = undefined;

    const plain_len = hexDumpToBuffer(test_data_b[0..16], 16, 1, line[0..], false);
    try std.testing.expectEqual(@as(usize, 47), plain_len);
    try std.testing.expectEqualSlices(u8, prepareExpectedLine(expected[0..], 16, 16, 1, false), std.mem.sliceTo(line[0..], 0));

    const ascii_len = hexDumpToBuffer(test_data_b[0..16], 16, 1, line[0..], true);
    try std.testing.expectEqual(@as(usize, 65), ascii_len);
    try std.testing.expectEqualSlices(
        u8,
        prepareExpectedLine(expected[0..], 16, 16, 1, true),
        std.mem.sliceTo(line[0..], 0),
    );
    try std.testing.expectEqualSlices(u8, test_ascii[0..16], std.mem.sliceTo(line[49..], 0));
}

test "hexDumpToBuffer uses native-endian grouping for 2, 4, and 8 byte groups" {
    const data = [_]u8{
        0xbe, 0x32, 0xdb, 0x7b, 0x0a, 0x18, 0x93, 0xb2,
        0x70, 0xba, 0xc4, 0x24, 0x7d, 0x83, 0x34, 0x9b,
    };

    const expected_2 = if (builtin.cpu.arch.endian() == .big)
        "be32 db7b 0a18 93b2 70ba c424 7d83 349b"
    else
        "32be 7bdb 180a b293 ba70 24c4 837d 9b34";
    const expected_4 = if (builtin.cpu.arch.endian() == .big)
        "be32db7b 0a1893b2 70bac424 7d83349b"
    else
        "7bdb32be b293180a 24c4ba70 9b34837d";
    const expected_8 = if (builtin.cpu.arch.endian() == .big)
        "be32db7b0a1893b2 70bac4247d83349b"
    else
        "b293180a7bdb32be 9b34837d24c4ba70";

    var line: [80]u8 = undefined;

    _ = hexDumpToBuffer(data[0..], 16, 2, line[0..], false);
    try std.testing.expectEqualSlices(u8, expected_2, std.mem.sliceTo(line[0..], 0));

    _ = hexDumpToBuffer(data[0..], 16, 4, line[0..], false);
    try std.testing.expectEqualSlices(u8, expected_4, std.mem.sliceTo(line[0..], 0));

    _ = hexDumpToBuffer(data[0..], 16, 8, line[0..], false);
    try std.testing.expectEqualSlices(u8, expected_8, std.mem.sliceTo(line[0..], 0));
}

test "hexDumpToBuffer reports full length when the caller buffer truncates" {
    const data = [_]u8{ 0xbe, 0x32, 0xdb, 0x7b };
    var line: [8]u8 = [_]u8{0xaa} ** 8;

    const written = hexDumpToBuffer(data[0..], 16, 1, line[0..], true);
    try std.testing.expectEqual(@as(usize, 53), written);
    try std.testing.expectEqual(@as(u8, 0), line[line.len - 1]);
    try std.testing.expectEqualSlices(u8, "be 32 d", std.mem.sliceTo(line[0..], 0));
}

test "hexDumpToBuffer keeps full grouped ASCII output when the caller buffer fits exactly" {
    const data = [_]u8{
        0xbe, 0x32, 0xdb, 0x7b, 0x0a, 0x18, 0x93, 0xb2,
        0x70, 0xba, 0xc4, 0x24, 0x7d, 0x83, 0x34, 0x9b,
    };
    const expected = if (builtin.cpu.arch.endian() == .big)
        "be32db7b 0a1893b2 70bac424 7d83349b  .2.{....p..$}.4."
    else
        "7bdb32be b293180a 24c4ba70 9b34837d  .2.{....p..$}.4.";
    var line: [54]u8 = undefined;

    const written = hexDumpToBuffer(data[0..], 16, 4, line[0..], true);
    try std.testing.expectEqual(@as(usize, 53), written);
    try std.testing.expectEqualSlices(u8, expected, std.mem.sliceTo(line[0..], 0));
    try std.testing.expectEqual(@as(u8, 0), line[written]);
}

test "hexDumpToBuffer follows kernel fixture normalization cases" {
    const Case = struct {
        len: usize,
        rowsize: usize,
        groupsize: usize,
        ascii: bool,
    };
    const cases = [_]Case{
        .{ .len = 32, .rowsize = 32, .groupsize = 1, .ascii = false },
        .{ .len = 32, .rowsize = 32, .groupsize = 2, .ascii = true },
        .{ .len = 20, .rowsize = 16, .groupsize = 8, .ascii = false },
        .{ .len = 15, .rowsize = 16, .groupsize = 8, .ascii = true },
        .{ .len = 12, .rowsize = 99, .groupsize = 3, .ascii = true },
        .{ .len = 9, .rowsize = 32, .groupsize = 4, .ascii = false },
    };

    for (cases) |case| {
        var line: [32 * 3 + 2 + 32 + 1]u8 = undefined;
        var expected: [32 * 3 + 2 + 32 + 1]u8 = undefined;

        _ = hexDumpToBuffer(test_data_b[0..case.len], case.rowsize, case.groupsize, line[0..], case.ascii);

        try std.testing.expectEqualSlices(
            u8,
            prepareExpectedLine(expected[0..], case.len, case.rowsize, case.groupsize, case.ascii),
            std.mem.sliceTo(line[0..], 0),
        );
    }
}

test "hexDumpToBuffer reports normalized required length for empty and zero-sized buffers" {
    var empty: [1]u8 = undefined;

    try std.testing.expectEqual(@as(usize, 0), hexDumpToBuffer(test_data_b[0..0], 16, 1, empty[0..], false));
    try std.testing.expectEqual(@as(usize, 0), hexDumpToBuffer(test_data_b[0..0], 16, 1, empty[0..0], false));
    try std.testing.expectEqual(@as(usize, 0), hexDumpToBuffer(test_data_b[0..0], 16, 1, empty[0..0], true));
    try std.testing.expectEqual(@as(u8, 0), empty[0]);

    try std.testing.expectEqual(@as(usize, 65), hexDumpToBuffer(test_data_b[0..16], 7, 3, empty[0..0], true));
    try std.testing.expectEqual(@as(usize, 47), hexDumpToBuffer(test_data_b[0..16], 7, 3, empty[0..0], false));
    try std.testing.expectEqual(@as(usize, 129), hexDumpToBuffer(test_data_b[0..32], 32, 1, empty[0..0], true));
}

pub const hex_to_bin = hexToBin;
pub const hex2Bin = hex2bin;
pub const bin2Hex = bin2hex;
