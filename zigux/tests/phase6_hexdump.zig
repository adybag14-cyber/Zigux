const std = @import("std");
const builtin = @import("builtin");
const hexdump = @import("hexdump");

const test_data_b = [_]u8{
    0xbe, 0x32, 0xdb, 0x7b, 0x0a, 0x18, 0x93, 0xb2,
    0x70, 0xba, 0xc4, 0x24, 0x7d, 0x83, 0x34, 0x9b,
    0xa6, 0x9c, 0x31, 0xad, 0x9c, 0x0f, 0xac, 0xe9,
    0x4c, 0xd1, 0x19, 0x99, 0x43, 0xb1, 0xaf, 0x0c,
};

const test_ascii = ".2.{....p..$}.4...1.....L...C...";
const fill_char: u8 = '#';
const test_hexdump_buf_size = 32 * 3 + 2 + 32 + 1;

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

fn normalizedRowsize(rowsize_input: usize) usize {
    return if (rowsize_input == 16 or rowsize_input == 32) rowsize_input else 16;
}

fn normalizedGroupsizeForLen(len: usize, groupsize_input: usize) usize {
    var groupsize = groupsize_input;
    if (!std.math.isPowerOfTwo(groupsize) or groupsize > 8 or groupsize == 0) {
        groupsize = 1;
    }
    if (len % groupsize != 0) {
        groupsize = 1;
    }
    return groupsize;
}

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
    const groupsize = normalizedGroupsizeForLen(len, groupsize_input);
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

fn expectedLength(len_input: usize, rowsize_input: usize, groupsize_input: usize, ascii: bool) usize {
    const rowsize = normalizedRowsize(rowsize_input);
    const len = @min(len_input, rowsize);
    const groupsize = normalizedGroupsizeForLen(len, groupsize_input);
    if (ascii) {
        return rowsize * 2 + rowsize / groupsize + 1 + len;
    }
    return if (len == 0) 0 else (groupsize * 2 + 1) * (len / groupsize) - 1;
}

fn assertParityCase(len: usize, rowsize: usize, groupsize: usize, ascii: bool) !void {
    var actual: [test_hexdump_buf_size]u8 = undefined;
    var expected: [test_hexdump_buf_size]u8 = undefined;

    const required = hexdump.hexDumpToBuffer(test_data_b[0..len], rowsize, groupsize, actual[0..], ascii);
    const want = prepareExpectedLine(expected[0..], len, rowsize, groupsize, ascii);

    try std.testing.expectEqual(expectedLength(len, rowsize, groupsize, ascii), required);
    try std.testing.expectEqualSlices(u8, want, std.mem.sliceTo(actual[0..], 0));
}

fn assertOverflowCase(buflen: usize, len: usize, rowsize: usize, groupsize: usize, ascii: bool) !void {
    var actual: [test_hexdump_buf_size]u8 = [_]u8{fill_char} ** test_hexdump_buf_size;
    var expected: [test_hexdump_buf_size]u8 = [_]u8{fill_char} ** test_hexdump_buf_size;

    const required = hexdump.hexDumpToBuffer(test_data_b[0..len], rowsize, groupsize, actual[0..buflen], ascii);
    const wanted_length = expectedLength(len, rowsize, groupsize, ascii);

    if (buflen > 0) {
        _ = prepareExpectedLine(expected[0..], len, rowsize, groupsize, ascii);
        const visible = @min(wanted_length + 1, buflen);
        expected[visible - 1] = 0;
        @memset(expected[visible..], fill_char);
    }

    try std.testing.expectEqual(wanted_length, required);
    try std.testing.expectEqualSlices(u8, expected[0..], actual[0..]);
}

test "phase 6 hexdump module imports cleanly" {
    _ = hexdump;
}

test "phase 6 hexdump parity matrix matches kernel fixture preparation" {
    const rowsizes = [_]usize{ 16, 32 };
    const groupsizes = [_]usize{ 1, 2, 4, 8 };

    for (rowsizes) |rowsize| {
        var len: usize = 1;
        while (len <= rowsize) : (len += 1) {
            for (groupsizes) |groupsize| {
                try assertParityCase(len, rowsize, groupsize, false);
                try assertParityCase(len, rowsize, groupsize, true);
            }
        }
    }
}

test "phase 6 hexdump overflow contract matches truncation expectations" {
    const rowsizes = [_]usize{ 16, 32 };
    const groupsizes = [_]usize{ 1, 2, 4, 8 };

    var buflen: usize = 0;
    while (buflen <= test_hexdump_buf_size) : (buflen += 1) {
        for (rowsizes) |rowsize| {
            for (groupsizes) |groupsize| {
                const full_len = rowsize;
                try assertOverflowCase(buflen, full_len, rowsize, groupsize, false);
                try assertOverflowCase(buflen, full_len, rowsize, groupsize, true);
            }
        }
    }
}

test "phase 6 hexdump covers normalization and empty-buffer edge cases" {
    try assertParityCase(0, 16, 1, false);
    try assertParityCase(12, 99, 3, true);
    try assertParityCase(9, 32, 4, false);

    var empty: [1]u8 = undefined;
    try std.testing.expectEqual(@as(usize, 65), hexdump.hexDumpToBuffer(test_data_b[0..16], 7, 3, empty[0..0], true));
    try std.testing.expectEqual(@as(usize, 47), hexdump.hexDumpToBuffer(test_data_b[0..16], 7, 3, empty[0..0], false));
    try std.testing.expectEqual(@as(usize, 129), hexdump.hexDumpToBuffer(test_data_b[0..32], 32, 1, empty[0..0], true));
}
