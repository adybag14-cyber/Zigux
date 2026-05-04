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

fn assertFixtureExactCapacityCase(case: fixtures.ExactCapacityCase) !void {
    var exact: [test_hexdump_buf_size]u8 = [_]u8{fill_char} ** test_hexdump_buf_size;
    var roomy: [test_hexdump_buf_size]u8 = [_]u8{fill_char} ** test_hexdump_buf_size;

    const exact_required = hexdump.hexDumpToBuffer(
        test_data_b[0..case.len],
        case.rowsize,
        case.groupsize,
        exact[0 .. case.expected_length + 1],
        case.ascii,
    );
    const roomy_required = hexdump.hexDumpToBuffer(
        test_data_b[0..case.len],
        case.rowsize,
        case.groupsize,
        roomy[0..],
        case.ascii,
    );

    try std.testing.expectEqual(case.expected_length, exact_required);
    try std.testing.expectEqual(case.expected_length, roomy_required);
    try std.testing.expectEqualSlices(u8, case.expected_text.current(), std.mem.sliceTo(exact[0..], 0));
    try std.testing.expectEqualSlices(u8, case.expected_text.current(), std.mem.sliceTo(roomy[0..], 0));
    try std.testing.expectEqual(@as(u8, 0), exact[case.expected_length]);
    try std.testing.expectEqual(@as(u8, 0), roomy[case.expected_length]);

    for (exact[case.expected_length + 1 ..]) |byte| {
        try std.testing.expectEqual(fill_char, byte);
    }
    for (roomy[case.expected_length + 1 ..]) |byte| {
        try std.testing.expectEqual(fill_char, byte);
    }
}

test "phase 6 hexdump module imports cleanly" {
    _ = hexdump;
}

test "phase 6 hexdump exposes uppercase whole-buffer encoding" {
    var encoded: [8]u8 = undefined;
    const text = try hexdump.bin2hexUpper(encoded[0..], test_data_b[0..4]);

    try std.testing.expectEqualSlices(u8, "BE32DB7B", text);
}

test "phase 6 hexdump exposes append-style whole-buffer encoding" {
    var encoded: [12]u8 = [_]u8{'#'} ** 12;
    var rest = try hexdump.bin2hexAppend(encoded[0..], test_data_b[0..2]);
    rest = try hexdump.bin2hexAppendUpper(rest, test_data_b[2..4]);

    try std.testing.expectEqualSlices(u8, "be32DB7B", encoded[0..8]);
    try std.testing.expectEqual(@as(usize, 4), rest.len);
    try std.testing.expectEqualSlices(u8, "####", rest);
}

test "phase 6 hexdump directly covers nibble, byte-pack, and decode helpers" {
    try std.testing.expectEqual(@as(u8, 'b'), hexdump.hexAscHi(0xbe));
    try std.testing.expectEqual(@as(u8, 'e'), hexdump.hexAscLo(0xbe));
    try std.testing.expectEqual(@as(u8, 'B'), hexdump.hexAscUpperHi(0xbe));
    try std.testing.expectEqual(@as(u8, 'E'), hexdump.hexAscUpperLo(0xbe));

    var lower: [4]u8 = [_]u8{'#'} ** 4;
    const lower_rest = try hexdump.hexBytePack(lower[0..], 0xbe);
    try std.testing.expectEqual(@as(usize, 2), lower_rest.len);
    try std.testing.expectEqualSlices(u8, "be", lower[0..2]);

    var upper: [4]u8 = [_]u8{'#'} ** 4;
    const upper_rest = try hexdump.hexBytePackUpper(upper[0..], 0xbe);
    try std.testing.expectEqual(@as(usize, 2), upper_rest.len);
    try std.testing.expectEqualSlices(u8, "BE", upper[0..2]);

    var short: [1]u8 = undefined;
    try std.testing.expectError(hexdump.HexError.DestinationTooSmall, hexdump.hexBytePack(short[0..], 0xbe));
    try std.testing.expectError(hexdump.HexError.DestinationTooSmall, hexdump.hexBytePackUpper(short[0..], 0xbe));

    var decoded: [4]u8 = undefined;
    try hexdump.hex2bin(decoded[0..], "Be32dB7b");
    try std.testing.expectEqualSlices(u8, test_data_b[0..4], decoded[0..]);
    try std.testing.expectError(hexdump.HexError.InvalidSourceLength, hexdump.hex2bin(decoded[0..], "abc"));
    try std.testing.expectError(hexdump.HexError.InvalidHexDigit, hexdump.hex2bin(decoded[0..], "zz00zz00"));
}

test "phase 6 hexdump replays serialized fixture vectors" {
    for (fixtures.parity_cases) |case| {
        try assertParityCase(case.len, case.rowsize, case.groupsize, case.ascii);
        try assertFixtureParityCase(case);
    }
}

test "phase 6 hexdump overflow contract matches truncation expectations" {
    for (fixtures.overflow_cases) |case| {
        try assertOverflowCase(case.buflen, case.len, case.rowsize, case.groupsize, case.ascii);
        try assertFixtureOverflowCase(case);
    }
}

test "phase 6 hexdump covers normalization and empty-buffer edge cases" {
    try assertParityCase(12, 99, 3, true);
    try assertParityCase(9, 32, 4, false);

    for (fixtures.length_cases) |case| {
        try assertFixtureLengthCase(case);
    }
}

test "phase 6 hexdump proves exact 4-byte grouped output" {
    var linebuf: [test_hexdump_buf_size]u8 = undefined;
    const required = hexdump.hexDumpToBuffer(test_data_b[0..16], 16, 4, linebuf[0..], false);

    try std.testing.expectEqual(@as(usize, 35), required);
    try std.testing.expectEqualSlices(
        u8,
        if (@import("builtin").cpu.arch.endian() == .big)
            "be32db7b 0a1893b2 70bac424 7d83349b"
        else
            "7bdb32be b293180a 24c4ba70 9b34837d",
        std.mem.sliceTo(linebuf[0..], 0),
    );
}

test "phase 6 hexdump proves exact 4-byte grouped ascii output" {
    var linebuf: [test_hexdump_buf_size]u8 = undefined;
    const required = hexdump.hexDumpToBuffer(test_data_b[0..16], 16, 4, linebuf[0..], true);

    try std.testing.expectEqual(@as(usize, 53), required);
    try std.testing.expectEqualSlices(
        u8,
        if (@import("builtin").cpu.arch.endian() == .big)
            "be32db7b 0a1893b2 70bac424 7d83349b  .2.{....p..$}.4."
        else
            "7bdb32be b293180a 24c4ba70 9b34837d  .2.{....p..$}.4.",
        std.mem.sliceTo(linebuf[0..], 0),
    );
}

test "phase 6 hexdump proves exact 8-byte grouped output" {
    var linebuf: [test_hexdump_buf_size]u8 = undefined;
    const required = hexdump.hexDumpToBuffer(test_data_b[0..16], 16, 8, linebuf[0..], false);

    try std.testing.expectEqual(@as(usize, 33), required);
    try std.testing.expectEqualSlices(
        u8,
        if (@import("builtin").cpu.arch.endian() == .big)
            "be32db7b0a1893b2 70bac4247d83349b"
        else
            "b293180a7bdb32be 9b34837d24c4ba70",
        std.mem.sliceTo(linebuf[0..], 0),
    );
}

test "phase 6 hexdump proves exact 2-byte grouped ascii output" {
    var linebuf: [test_hexdump_buf_size]u8 = undefined;
    const required = hexdump.hexDumpToBuffer(test_data_b[0..16], 16, 2, linebuf[0..], true);

    try std.testing.expectEqual(@as(usize, 57), required);
    try std.testing.expectEqualSlices(
        u8,
        if (@import("builtin").cpu.arch.endian() == .big)
            "be32 db7b 0a18 93b2 70ba c424 7d83 349b  .2.{....p..$}.4."
        else
            "32be 7bdb 180a b293 ba70 24c4 837d 9b34  .2.{....p..$}.4.",
        std.mem.sliceTo(linebuf[0..], 0),
    );
}

test "phase 6 hexdump proves exact 8-byte grouped ascii output" {
    var linebuf: [test_hexdump_buf_size]u8 = undefined;
    const required = hexdump.hexDumpToBuffer(test_data_b[0..16], 16, 8, linebuf[0..], true);

    try std.testing.expectEqual(@as(usize, 51), required);
    try std.testing.expectEqualSlices(
        u8,
        if (@import("builtin").cpu.arch.endian() == .big)
            "be32db7b0a1893b2 70bac4247d83349b  .2.{....p..$}.4."
        else
            "b293180a7bdb32be 9b34837d24c4ba70  .2.{....p..$}.4.",
        std.mem.sliceTo(linebuf[0..], 0),
    );
}

test "phase 6 hexdump exact-capacity full-buffer path stays aligned with fixture output" {
    for (fixtures.exact_capacity_cases) |case| {
        try assertFixtureExactCapacityCase(case);
    }
}
