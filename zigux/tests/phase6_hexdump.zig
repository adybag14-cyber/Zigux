const std = @import("std");
const hexdump = @import("hexdump");
const fixtures = @import("phase6_hexdump_vectors");

const test_data_b = fixtures.data_b;
const fill_char = fixtures.fill_char;
const test_hexdump_buf_size = fixtures.test_hexdump_buf_size;

fn assertParityCase(len: usize, rowsize: usize, groupsize: usize, ascii: bool) !void {
    var actual: [test_hexdump_buf_size]u8 = undefined;
    var expected: [test_hexdump_buf_size]u8 = undefined;

    const required = hexdump.hexDumpToBuffer(test_data_b[0..len], rowsize, groupsize, actual[0..], ascii);
    const want = fixtures.prepareExpectedLine(expected[0..], len, rowsize, groupsize, ascii);

    try std.testing.expectEqual(fixtures.expectedLength(len, rowsize, groupsize, ascii), required);
    try std.testing.expectEqualSlices(u8, want, std.mem.sliceTo(actual[0..], 0));
}

fn assertOverflowCase(buflen: usize, len: usize, rowsize: usize, groupsize: usize, ascii: bool) !void {
    var actual: [test_hexdump_buf_size]u8 = [_]u8{fill_char} ** test_hexdump_buf_size;
    var expected: [test_hexdump_buf_size]u8 = [_]u8{fill_char} ** test_hexdump_buf_size;

    const required = hexdump.hexDumpToBuffer(test_data_b[0..len], rowsize, groupsize, actual[0..buflen], ascii);
    const wanted_length = fixtures.expectedLength(len, rowsize, groupsize, ascii);

    if (buflen > 0) {
        _ = fixtures.prepareExpectedLine(expected[0..], len, rowsize, groupsize, ascii);
        const visible = @min(wanted_length + 1, buflen);
        expected[visible - 1] = 0;
        @memset(expected[visible..], fill_char);
    }

    try std.testing.expectEqual(wanted_length, required);
    try std.testing.expectEqualSlices(u8, expected[0..], actual[0..]);
}

fn assertFixtureParityCase(case: fixtures.ParityCase) !void {
    var actual: [test_hexdump_buf_size]u8 = undefined;
    const required = hexdump.hexDumpToBuffer(test_data_b[0..case.len], case.rowsize, case.groupsize, actual[0..], case.ascii);

    try std.testing.expectEqual(case.expected_length, required);
    try std.testing.expectEqualSlices(u8, case.expected_text.current(), std.mem.sliceTo(actual[0..], 0));
}

fn assertFixtureOverflowCase(case: fixtures.OverflowCase) !void {
    var actual: [test_hexdump_buf_size]u8 = [_]u8{fill_char} ** test_hexdump_buf_size;
    const required = hexdump.hexDumpToBuffer(test_data_b[0..case.len], case.rowsize, case.groupsize, actual[0..case.buflen], case.ascii);

    try std.testing.expectEqual(case.expected_length, required);
    if (case.buflen == 0) {
        try std.testing.expectEqualSlices(u8, &[_]u8{fill_char} ** test_hexdump_buf_size, actual[0..]);
        return;
    }

    const visible = case.visible_text.current();
    try std.testing.expectEqualSlices(u8, visible, std.mem.sliceTo(actual[0..], 0));

    const terminator_index = @min(case.expected_length, case.buflen - 1);
    try std.testing.expectEqual(@as(u8, 0), actual[terminator_index]);
    for (actual[terminator_index + 1 ..]) |byte| {
        try std.testing.expectEqual(fill_char, byte);
    }
}

fn assertFixtureLengthCase(case: fixtures.LengthCase) !void {
    try std.testing.expectEqual(
        case.expected_length,
        hexdump.hexDumpLineLength(case.len, case.rowsize, case.groupsize, case.ascii),
    );
    try std.testing.expectEqual(
        case.expected_length,
        hexdump.hexDumpToBuffer(test_data_b[0..case.len], case.rowsize, case.groupsize, &[_]u8{}, case.ascii),
    );
}

fn assertFixturePerfCase(case: fixtures.PerfCase) !void {
    var actual: [test_hexdump_buf_size]u8 = undefined;
    var expected: [test_hexdump_buf_size]u8 = undefined;
    const required = hexdump.hexDumpToBuffer(test_data_b[0..case.len], case.rowsize, case.groupsize, actual[0..], case.ascii);
    const want = fixtures.prepareExpectedLine(expected[0..], case.len, case.rowsize, case.groupsize, case.ascii);

    try std.testing.expect(case.reps > 0);
    try std.testing.expect(case.max_slowdown_pct > 0);
    try std.testing.expectEqual(fixtures.expectedLength(case.len, case.rowsize, case.groupsize, case.ascii), required);
    try std.testing.expectEqualSlices(u8, want, std.mem.sliceTo(actual[0..], 0));
}

test "phase 6 hexdump module imports cleanly" {
    _ = hexdump;
}

test "phase 6 hexdump serialized linux-derived vectors stay in sync" {
    try std.testing.expectEqual(@as(usize, 10), fixtures.parity_cases.len);
    for (fixtures.parity_cases) |case| {
        try assertFixtureParityCase(case);
    }
}

test "phase 6 hexdump serialized overflow vectors stay in sync" {
    for (fixtures.overflow_cases) |case| {
        try assertFixtureOverflowCase(case);
    }
}

test "phase 6 hexdump serialized required-length vectors stay in sync" {
    try std.testing.expectEqual(@as(usize, 9), fixtures.length_cases.len);
    for (fixtures.length_cases) |case| {
        try assertFixtureLengthCase(case);
    }
}

test "phase 6 hexdump perf fixture packet stays in sync" {
    try std.testing.expectEqual(@as(usize, 4), fixtures.perf_cases.len);
    for (fixtures.perf_cases) |case| {
        try assertFixturePerfCase(case);
    }
}

test "phase 6 hexdump uppercase nibble helpers stay aligned with byte packing" {
    const sample = [_]u8{ 0x00, 0x09, 0x3c, 0xbe, 0xff };
    var lower: [2]u8 = undefined;
    var upper: [2]u8 = undefined;
    var tiny: [1]u8 = undefined;

    for (sample) |byte| {
        const lower_rest = try hexdump.hexBytePack(lower[0..], byte);
        const upper_rest = try hexdump.hexBytePackUpper(upper[0..], byte);

        try std.testing.expectEqual(@as(usize, 0), lower_rest.len);
        try std.testing.expectEqual(@as(usize, 0), upper_rest.len);
        try std.testing.expectEqual(hexdump.hexAscHi(byte), lower[0]);
        try std.testing.expectEqual(hexdump.hexAscLo(byte), lower[1]);
        try std.testing.expectEqual(hexdump.hexAscUpperHi(byte), upper[0]);
        try std.testing.expectEqual(hexdump.hexAscUpperLo(byte), upper[1]);
        try std.testing.expectEqual(std.ascii.toUpper(lower[0]), upper[0]);
        try std.testing.expectEqual(std.ascii.toUpper(lower[1]), upper[1]);
    }

    try std.testing.expectError(hexdump.HexError.DestinationTooSmall, hexdump.hexBytePackUpper(tiny[0..], 0xbe));
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

test "phase 6 hexdump grouped ASCII output stays intact when buffer capacity is exact" {
    const expected = if (@import("builtin").cpu.arch.endian() == .big)
        "be32db7b 0a1893b2 70bac424 7d83349b  .2.{....p..$}.4."
    else
        "7bdb32be b293180a 24c4ba70 9b34837d  .2.{....p..$}.4.";
    var actual: [54]u8 = undefined;

    const required = hexdump.hexDumpToBuffer(test_data_b[0..16], 16, 4, actual[0..], true);
    try std.testing.expectEqual(@as(usize, 53), required);
    try std.testing.expectEqualSlices(u8, expected, std.mem.sliceTo(actual[0..], 0));
    try std.testing.expectEqual(@as(u8, 0), actual[required]);
}

test "phase 6 hexdump covers normalization and empty-buffer edge cases" {
    const normalized_parity_case = fixtures.parity_cases[7];
    const uneven_group_parity_case = fixtures.parity_cases[8];
    const normalized_overflow_case = fixtures.overflow_cases[3];
    const normalized_length_case = fixtures.length_cases[7];
    const uneven_group_length_case = fixtures.length_cases[8];

    try std.testing.expectEqualStrings("normalized rowsize and groupsize fallback", normalized_parity_case.name);
    try std.testing.expectEqualStrings("normalized uneven group fallback", uneven_group_parity_case.name);
    try std.testing.expectEqualStrings("normalized ascii buffer truncates after fallback formatting", normalized_overflow_case.name);
    try std.testing.expectEqualStrings("normalized rowsize and groupsize fallback line length", normalized_length_case.name);
    try std.testing.expectEqualStrings("uneven group fallback line length", uneven_group_length_case.name);

    try assertFixtureParityCase(normalized_parity_case);
    try assertFixtureParityCase(uneven_group_parity_case);
    try assertFixtureOverflowCase(normalized_overflow_case);
    try assertFixtureLengthCase(normalized_length_case);
    try assertFixtureLengthCase(uneven_group_length_case);

    try assertParityCase(0, 16, 1, false);
    try assertParityCase(12, 99, 3, true);
    try assertParityCase(9, 32, 4, false);

    var empty: [1]u8 = undefined;
    try std.testing.expectEqual(@as(usize, 65), hexdump.hexDumpToBuffer(test_data_b[0..16], 7, 3, empty[0..0], true));
    try std.testing.expectEqual(@as(usize, 47), hexdump.hexDumpToBuffer(test_data_b[0..16], 7, 3, empty[0..0], false));
    try std.testing.expectEqual(@as(usize, 129), hexdump.hexDumpToBuffer(test_data_b[0..32], 32, 1, empty[0..0], true));
}
