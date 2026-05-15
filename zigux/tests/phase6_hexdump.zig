const std = @import("std");
const hexdump = @import("hexdump");
const fixtures = @import("phase6_hexdump_vectors");

const test_hexdump_buf_size = fixtures.test_hexdump_buf_size;

fn assertParityCase(case: fixtures.ParityCase) !void {
    var actual: [test_hexdump_buf_size]u8 = undefined;
    var expected: [test_hexdump_buf_size]u8 = undefined;

    const required = hexdump.hexDumpToBuffer(
        fixtures.data_b[0..case.len],
        case.rowsize,
        case.groupsize,
        actual[0..],
        case.ascii,
    );
    const want = fixtures.prepareExpectedLine(expected[0..], case.len, case.rowsize, case.groupsize, case.ascii);

    try std.testing.expectEqual(case.expected_length, required);
    try std.testing.expectEqualSlices(u8, case.expected_text.current(), std.mem.sliceTo(actual[0..], 0));
    try std.testing.expectEqualSlices(u8, want, std.mem.sliceTo(actual[0..], 0));
}

fn assertOverflowCase(case: fixtures.OverflowCase) !void {
    var actual: [test_hexdump_buf_size]u8 = [_]u8{fixtures.fill_char} ** test_hexdump_buf_size;
    const required = hexdump.hexDumpToBuffer(
        fixtures.data_b[0..case.len],
        case.rowsize,
        case.groupsize,
        actual[0..case.buflen],
        case.ascii,
    );

    try std.testing.expectEqual(case.expected_length, required);

    if (case.buflen == 0) {
        for (actual) |byte| try std.testing.expectEqual(fixtures.fill_char, byte);
        return;
    }

    const visible = case.visible_text.current();
    try std.testing.expectEqualSlices(u8, visible, std.mem.sliceTo(actual[0..], 0));

    const terminator_index = @min(case.expected_length, case.buflen - 1);
    try std.testing.expectEqual(@as(u8, 0), actual[terminator_index]);
    for (actual[terminator_index + 1 ..]) |byte| {
        try std.testing.expectEqual(fixtures.fill_char, byte);
    }
}

fn assertLengthCase(case: fixtures.LengthCase) !void {
    try std.testing.expectEqual(
        case.expected_length,
        hexdump.hexDumpLineLength(case.len, case.rowsize, case.groupsize, case.ascii),
    );
    try std.testing.expectEqual(
        case.expected_length,
        hexdump.hexDumpToBuffer(fixtures.data_b[0..case.len], case.rowsize, case.groupsize, &[_]u8{}, case.ascii),
    );
}

fn assertExactFitPerfCase(case: fixtures.PerfCase) !void {
    var actual: [test_hexdump_buf_size]u8 = [_]u8{fixtures.fill_char} ** test_hexdump_buf_size;
    var expected: [test_hexdump_buf_size]u8 = undefined;

    const required = fixtures.expectedLength(case.len, case.rowsize, case.groupsize, case.ascii);
    const written = hexdump.hexDumpToBuffer(
        fixtures.data_b[0..case.len],
        case.rowsize,
        case.groupsize,
        actual[0 .. required + 1],
        case.ascii,
    );
    const want = fixtures.prepareExpectedLine(expected[0..], case.len, case.rowsize, case.groupsize, case.ascii);

    try std.testing.expectEqual(required, written);
    try std.testing.expectEqual(required, hexdump.hexDumpLineLength(case.len, case.rowsize, case.groupsize, case.ascii));
    try std.testing.expectEqualSlices(u8, want, std.mem.sliceTo(actual[0..], 0));
    try std.testing.expectEqual(@as(u8, 0), actual[required]);
    for (actual[required + 1 ..]) |byte| {
        try std.testing.expectEqual(fixtures.fill_char, byte);
    }
}

test "phase 6 hexdump helper packet replays the serialized parity matrix" {
    for (fixtures.parity_cases) |case| {
        try assertParityCase(case);
    }
}

test "phase 6 hexdump helper packet preserves the overflow contract" {
    for (fixtures.overflow_cases) |case| {
        try assertOverflowCase(case);
    }
}

test "phase 6 hexdump helper packet preserves the curated length matrix" {
    for (fixtures.length_cases) |case| {
        try assertLengthCase(case);
    }
}

test "phase 6 hexdump perf cases also pin the exact-fit full-buffer boundary" {
    for (fixtures.perf_cases) |case| {
        try assertExactFitPerfCase(case);
    }
}

test "phase 6 hexdump direct helper aliases stay aligned with the packet" {
    try std.testing.expectEqual(@as(?u8, 10), hexdump.hexToBin('a'));
    try std.testing.expectEqual(@as(isize, 15), hexdump.hex_to_bin('f'));
    try std.testing.expectEqual(@as(?u8, null), hexdump.hexToBin('x'));

    var decoded: [4]u8 = undefined;
    try hexdump.hex2Bin(decoded[0..], "be32db7b");
    try std.testing.expectEqualSlices(u8, fixtures.data_b[0..4], decoded[0..]);
    try std.testing.expectError(error.InvalidLength, hexdump.hex2Bin(decoded[0..], "be32db"));
    try std.testing.expectError(error.InvalidHex, hexdump.hex2bin(decoded[0..], "be32dz7b"));

    var encoded: [8]u8 = undefined;
    const text = hexdump.bin2Hex(encoded[0..], fixtures.data_b[0..4]);
    try std.testing.expectEqualStrings("be32db7b", text);
}
