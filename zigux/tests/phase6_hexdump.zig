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

test "phase 6 hexdump module imports cleanly" {
    _ = hexdump;
}

test "phase 6 hexdump exposes uppercase whole-buffer encoding" {
    var encoded: [8]u8 = undefined;
    const text = try hexdump.bin2hexUpper(encoded[0..], test_data_b[0..4]);

    try std.testing.expectEqualSlices(u8, "BE32DB7B", text);
}

test "phase 6 hexdump serialized linux-derived vectors stay in sync" {
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
    for (fixtures.length_cases) |case| {
        try assertFixtureLengthCase(case);
    }
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
