const builtin = @import("builtin");
const std = @import("std");

pub const data_b = [_]u8{
    0xbe, 0x32, 0xdb, 0x7b, 0x0a, 0x18, 0x93, 0xb2,
    0x70, 0xba, 0xc4, 0x24, 0x7d, 0x83, 0x34, 0x9b,
    0xa6, 0x9c, 0x31, 0xad, 0x9c, 0x0f, 0xac, 0xe9,
    0x4c, 0xd1, 0x19, 0x99, 0x43, 0xb1, 0xaf, 0x0c,
};

pub const data_a = ".2.{....p..$}.4...1.....L...C...";
pub const fill_char: u8 = '#';
pub const test_hexdump_buf_size = 32 * 3 + 2 + 32 + 1;

pub const ExpectedText = struct {
    little: []const u8,
    big: []const u8,

    pub fn current(self: @This()) []const u8 {
        return if (builtin.target.cpu.arch.endian() == .big) self.big else self.little;
    }
};

pub const ParityCase = struct {
    name: []const u8,
    len: usize,
    rowsize: usize,
    groupsize: usize,
    ascii: bool,
    expected_length: usize,
    expected_text: ExpectedText,
};

pub const OverflowCase = struct {
    name: []const u8,
    buflen: usize,
    len: usize,
    rowsize: usize,
    groupsize: usize,
    ascii: bool,
    expected_length: usize,
    visible_text: ExpectedText,
};

pub const LengthCase = struct {
    name: []const u8,
    len: usize,
    rowsize: usize,
    groupsize: usize,
    ascii: bool,
    expected_length: usize,
};

pub const PerfCase = struct {
    label: []const u8,
    len: usize,
    rowsize: usize,
    groupsize: usize,
    ascii: bool,
    reps: usize,
    max_slowdown_pct: u64,
    expected_text: ExpectedText,
};

fn same(text: []const u8) ExpectedText {
    return .{ .little = text, .big = text };
}

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

pub fn normalizedRowsize(rowsize_input: usize) usize {
    return if (rowsize_input == 16 or rowsize_input == 32) rowsize_input else 16;
}

pub fn normalizedGroupsizeForLen(len: usize, groupsize_input: usize) usize {
    if (groupsize_input != 1 and groupsize_input != 2 and groupsize_input != 4 and groupsize_input != 8) {
        return 1;
    }
    if (groupsize_input == 0 or (len % groupsize_input) != 0) {
        return 1;
    }
    return groupsize_input;
}

fn fixtureChunks(groupsize: usize) []const []const u8 {
    return switch (groupsize) {
        8 => if (builtin.target.cpu.arch.endian() == .big) test_data_8_be[0..] else test_data_8_le[0..],
        4 => if (builtin.target.cpu.arch.endian() == .big) test_data_4_be[0..] else test_data_4_le[0..],
        2 => if (builtin.target.cpu.arch.endian() == .big) test_data_2_be[0..] else test_data_2_le[0..],
        else => test_data_1[0..],
    };
}

pub fn prepareExpectedLine(
    buffer: []u8,
    len_input: usize,
    rowsize_input: usize,
    groupsize_input: usize,
    ascii: bool,
) []const u8 {
    const rowsize = normalizedRowsize(rowsize_input);
    const len = @min(len_input, rowsize);
    if (len == 0) {
        buffer[0] = 0;
        return buffer[0..0];
    }

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
    pos -= 1;

    if (ascii) {
        const ascii_column = rowsize * 2 + rowsize / groupsize + 1;
        while (pos < ascii_column) : (pos += 1) {
            buffer[pos] = ' ';
        }
        @memcpy(buffer[pos .. pos + len], data_a[0..len]);
        pos += len;
    }

    buffer[pos] = 0;
    return buffer[0..pos];
}

pub fn expectedLength(len_input: usize, rowsize_input: usize, groupsize_input: usize, ascii: bool) usize {
    const rowsize = normalizedRowsize(rowsize_input);
    const len = @min(len_input, rowsize);
    if (len == 0) return 0;
    const groupsize = normalizedGroupsizeForLen(len, groupsize_input);
    if (ascii) return rowsize * 2 + rowsize / groupsize + 1 + len;
    return (len * 2) + (len / groupsize) - 1;
}

pub const parity_cases = [_]ParityCase{
    .{
        .name = "plain rowsize-16 group-1",
        .len = 16,
        .rowsize = 16,
        .groupsize = 1,
        .ascii = false,
        .expected_length = 47,
        .expected_text = same("be 32 db 7b 0a 18 93 b2 70 ba c4 24 7d 83 34 9b"),
    },
    .{
        .name = "ascii rowsize-16 group-1",
        .len = 16,
        .rowsize = 16,
        .groupsize = 1,
        .ascii = true,
        .expected_length = 65,
        .expected_text = same("be 32 db 7b 0a 18 93 b2 70 ba c4 24 7d 83 34 9b  .2.{....p..$}.4."),
    },
    .{
        .name = "plain rowsize-16 group-2",
        .len = 16,
        .rowsize = 16,
        .groupsize = 2,
        .ascii = false,
        .expected_length = 39,
        .expected_text = .{
            .little = "32be 7bdb 180a b293 ba70 24c4 837d 9b34",
            .big = "be32 db7b 0a18 93b2 70ba c424 7d83 349b",
        },
    },
    .{
        .name = "plain rowsize-16 group-4",
        .len = 16,
        .rowsize = 16,
        .groupsize = 4,
        .ascii = false,
        .expected_length = 35,
        .expected_text = .{
            .little = "7bdb32be b293180a 24c4ba70 9b34837d",
            .big = "be32db7b 0a1893b2 70bac424 7d83349b",
        },
    },
    .{
        .name = "ascii rowsize-16 group-4",
        .len = 16,
        .rowsize = 16,
        .groupsize = 4,
        .ascii = true,
        .expected_length = 53,
        .expected_text = .{
            .little = "7bdb32be b293180a 24c4ba70 9b34837d  .2.{....p..$}.4.",
            .big = "be32db7b 0a1893b2 70bac424 7d83349b  .2.{....p..$}.4.",
        },
    },
    .{
        .name = "ascii rowsize-32 group-2",
        .len = 32,
        .rowsize = 32,
        .groupsize = 2,
        .ascii = true,
        .expected_length = 113,
        .expected_text = .{
            .little = "32be 7bdb 180a b293 ba70 24c4 837d 9b34 9ca6 ad31 0f9c e9ac d14c 9919 b143 0caf  .2.{....p..$}.4...1.....L...C...",
            .big = "be32 db7b 0a18 93b2 70ba c424 7d83 349b a69c 31ad 9c0f ace9 4cd1 1999 43b1 af0c  .2.{....p..$}.4...1.....L...C...",
        },
    },
    .{
        .name = "normalized rowsize and groupsize fallback",
        .len = 12,
        .rowsize = 99,
        .groupsize = 3,
        .ascii = true,
        .expected_length = 61,
        .expected_text = same("be 32 db 7b 0a 18 93 b2 70 ba c4 24              .2.{....p..$"),
    },
    .{
        .name = "normalized uneven group fallback",
        .len = 9,
        .rowsize = 32,
        .groupsize = 4,
        .ascii = false,
        .expected_length = 26,
        .expected_text = same("be 32 db 7b 0a 18 93 b2 70"),
    },
    .{
        .name = "plain rowsize-16 group-8",
        .len = 16,
        .rowsize = 16,
        .groupsize = 8,
        .ascii = false,
        .expected_length = 33,
        .expected_text = .{
            .little = "b293180a7bdb32be 9b34837d24c4ba70",
            .big = "be32db7b0a1893b2 70bac4247d83349b",
        },
    },
    .{
        .name = "ascii rowsize-16 group-8",
        .len = 16,
        .rowsize = 16,
        .groupsize = 8,
        .ascii = true,
        .expected_length = 51,
        .expected_text = .{
            .little = "b293180a7bdb32be 9b34837d24c4ba70  .2.{....p..$}.4.",
            .big = "be32db7b0a1893b2 70bac4247d83349b  .2.{....p..$}.4.",
        },
    },
};

pub const overflow_cases = [_]OverflowCase{
    .{
        .name = "zero-sized caller buffer reports required ascii length",
        .buflen = 0,
        .len = 16,
        .rowsize = 7,
        .groupsize = 3,
        .ascii = true,
        .expected_length = 65,
        .visible_text = same(""),
    },
    .{
        .name = "short ascii buffer truncates but stays NUL terminated",
        .buflen = 8,
        .len = 4,
        .rowsize = 16,
        .groupsize = 1,
        .ascii = true,
        .expected_length = 53,
        .visible_text = same("be 32 d"),
    },
    .{
        .name = "grouped plain buffer truncates deterministically",
        .buflen = 20,
        .len = 16,
        .rowsize = 16,
        .groupsize = 2,
        .ascii = false,
        .expected_length = 39,
        .visible_text = .{
            .little = "32be 7bdb 180a b293",
            .big = "be32 db7b 0a18 93b2",
        },
    },
    .{
        .name = "normalized ascii buffer truncates after fallback formatting",
        .buflen = 12,
        .len = 15,
        .rowsize = 16,
        .groupsize = 8,
        .ascii = true,
        .expected_length = 64,
        .visible_text = same("be 32 db 7b"),
    },
};

pub const length_cases = [_]LengthCase{
    .{ .name = "empty plain line reports zero length", .len = 0, .rowsize = 16, .groupsize = 1, .ascii = false, .expected_length = 0 },
    .{ .name = "empty ascii line reports zero length", .len = 0, .rowsize = 16, .groupsize = 1, .ascii = true, .expected_length = 0 },
    .{ .name = "plain rowsize-16 group-1 line length", .len = 16, .rowsize = 16, .groupsize = 1, .ascii = false, .expected_length = 47 },
    .{ .name = "ascii rowsize-16 group-1 line length", .len = 16, .rowsize = 16, .groupsize = 1, .ascii = true, .expected_length = 65 },
    .{ .name = "plain rowsize-16 group-4 line length", .len = 16, .rowsize = 16, .groupsize = 4, .ascii = false, .expected_length = 35 },
    .{ .name = "ascii rowsize-16 group-4 line length", .len = 16, .rowsize = 16, .groupsize = 4, .ascii = true, .expected_length = 53 },
    .{ .name = "ascii rowsize-32 group-1 line length", .len = 32, .rowsize = 32, .groupsize = 1, .ascii = true, .expected_length = 129 },
    .{ .name = "plain rowsize-16 group-8 line length", .len = 16, .rowsize = 16, .groupsize = 8, .ascii = false, .expected_length = 33 },
    .{ .name = "ascii rowsize-16 group-8 line length", .len = 16, .rowsize = 16, .groupsize = 8, .ascii = true, .expected_length = 51 },
    .{ .name = "normalized rowsize and groupsize fallback line length", .len = 16, .rowsize = 7, .groupsize = 3, .ascii = true, .expected_length = 65 },
    .{ .name = "uneven group fallback line length", .len = 9, .rowsize = 32, .groupsize = 4, .ascii = false, .expected_length = 26 },
};

pub const perf_cases = [_]PerfCase{
    .{
        .label = "16B-plain-g1",
        .len = 16,
        .rowsize = 16,
        .groupsize = 1,
        .ascii = false,
        .reps = 40_000,
        .max_slowdown_pct = 175,
        .expected_text = .{
            .little = "be 32 db 7b 0a 18 93 b2 70 ba c4 24 7d 83 34 9b",
            .big = "be 32 db 7b 0a 18 93 b2 70 ba c4 24 7d 83 34 9b",
        },
    },
    .{
        .label = "32B-ascii-g2",
        .len = 32,
        .rowsize = 32,
        .groupsize = 2,
        .ascii = true,
        .reps = 10_000,
        .max_slowdown_pct = 550,
        .expected_text = .{
            .little = "32be 7bdb 180a b293 ba70 24c4 837d 9b34 9ca6 ad31 0f9c e9ac d14c 9919 b143 0caf  .2.{....p..$}.4...1.....L...C...",
            .big = "be32 db7b 0a18 93b2 70ba c424 7d83 349b a69c 31ad 9c0f ace9 4cd1 1999 43b1 af0c  .2.{....p..$}.4...1.....L...C...",
        },
    },
    .{
        .label = "16B-ascii-g4",
        .len = 16,
        .rowsize = 16,
        .groupsize = 4,
        .ascii = true,
        .reps = 20_000,
        .max_slowdown_pct = 550,
        .expected_text = .{
            .little = "7bdb32be b293180a 24c4ba70 9b34837d  .2.{....p..$}.4.",
            .big = "be32db7b 0a1893b2 70bac424 7d83349b  .2.{....p..$}.4.",
        },
    },
    .{
        .label = "16B-ascii-g8",
        .len = 16,
        .rowsize = 16,
        .groupsize = 8,
        .ascii = true,
        .reps = 20_000,
        .max_slowdown_pct = 600,
        .expected_text = .{
            .little = "b293180a7bdb32be 9b34837d24c4ba70  .2.{....p..$}.4.",
            .big = "be32db7b0a1893b2 70bac4247d83349b  .2.{....p..$}.4.",
        },
    },
    .{
        .label = "12B-ascii-fallback",
        .len = 12,
        .rowsize = 99,
        .groupsize = 3,
        .ascii = true,
        .reps = 20_000,
        .max_slowdown_pct = 550,
        .expected_text = same("be 32 db 7b 0a 18 93 b2 70 ba c4 24              .2.{....p..$"),
    },
};

test "phase 6 hexdump curated length packet stays bounded to the documented matrix" {
    const expected = [_][]const u8{
        "empty plain line reports zero length",
        "empty ascii line reports zero length",
        "plain rowsize-16 group-1 line length",
        "ascii rowsize-16 group-1 line length",
        "plain rowsize-16 group-4 line length",
        "ascii rowsize-16 group-4 line length",
        "ascii rowsize-32 group-1 line length",
        "plain rowsize-16 group-8 line length",
        "ascii rowsize-16 group-8 line length",
        "normalized rowsize and groupsize fallback line length",
        "uneven group fallback line length",
    };
    try std.testing.expectEqual(expected.len, length_cases.len);
    for (expected, length_cases) |name, case| {
        try std.testing.expectEqualStrings(name, case.name);
    }
}

test "phase 6 hexdump empty-length fixtures keep plain and ascii rows silent" {
    var buffer = [_]u8{0xaa};

    try std.testing.expectEqualStrings("", prepareExpectedLine(buffer[0..], 0, 16, 1, false));
    try std.testing.expectEqual(@as(u8, 0), buffer[0]);

    buffer[0] = 0xaa;
    try std.testing.expectEqualStrings("", prepareExpectedLine(buffer[0..], 0, 16, 1, true));
    try std.testing.expectEqual(@as(u8, 0), buffer[0]);

    try std.testing.expectEqual(@as(usize, 0), expectedLength(0, 16, 1, false));
    try std.testing.expectEqual(@as(usize, 0), expectedLength(0, 16, 1, true));
}

test "phase 6 hexdump perf packet stays aligned with the documented matrix" {
    try std.testing.expectEqual(@as(usize, 5), perf_cases.len);
    try std.testing.expectEqual(@as(u64, 600), perf_cases[3].max_slowdown_pct);
    try std.testing.expectEqualStrings("be 32 db 7b 0a 18 93 b2 70 ba c4 24 7d 83 34 9b", perf_cases[0].expected_text.current());
    try std.testing.expectEqualStrings("16B-ascii-g8", perf_cases[3].label);
    try std.testing.expectEqualStrings("b293180a7bdb32be 9b34837d24c4ba70  .2.{....p..$}.4.", perf_cases[3].expected_text.little);
    try std.testing.expectEqualStrings("be32db7b0a1893b2 70bac4247d83349b  .2.{....p..$}.4.", perf_cases[3].expected_text.big);
    try std.testing.expectEqualStrings("12B-ascii-fallback", perf_cases[4].label);
    try std.testing.expectEqual(@as(u64, 550), perf_cases[4].max_slowdown_pct);
    try std.testing.expectEqualStrings("be 32 db 7b 0a 18 93 b2 70 ba c4 24              .2.{....p..$", perf_cases[4].expected_text.current());
}