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

test "phase 6 hexdump direct helper entrypoints stay aligned with the packet" {
    try std.testing.expectEqual(@as(i32, 10), hexdump.hexToBin('a'));
    try std.testing.expectEqual(@as(i32, 15), hexdump.hexToBin('f'));
    try std.testing.expectEqual(@as(i32, -1), hexdump.hexToBin('x'));

    var decoded: [4]u8 = undefined;
    try hexdump.hex2bin(decoded[0..], "be32db7b");
    try std.testing.expectEqualSlices(u8, fixtures.data_b[0..4], decoded[0..]);
    try hexdump.hex2bin(decoded[0..], "BE32DB7B");
    try std.testing.expectEqualSlices(u8, fixtures.data_b[0..4], decoded[0..]);
    try hexdump.hex2bin(decoded[0..], "bE32Db7B");
    try std.testing.expectEqualSlices(u8, fixtures.data_b[0..4], decoded[0..]);
    try std.testing.expectError(hexdump.HexError.InvalidSourceLength, hexdump.hex2bin(decoded[0..], "be32db"));
    try std.testing.expectError(hexdump.HexError.InvalidHexDigit, hexdump.hex2bin(decoded[0..], "be32dz7b"));

    var alias_decoded: [4]u8 = undefined;
    try hexdump.hex2Bin(alias_decoded[0..], "bE32Db7B");
    try std.testing.expectEqualSlices(u8, decoded[0..], alias_decoded[0..]);

    var encoded: [8]u8 = undefined;
    const text = try hexdump.bin2hex(encoded[0..], fixtures.data_b[0..4]);
    try std.testing.expectEqualStrings("be32db7b", text);

    var alias_encoded: [8]u8 = undefined;
    const alias_text = try hexdump.bin2Hex(alias_encoded[0..], alias_decoded[0..]);
    try std.testing.expectEqualStrings(text, alias_text);
}

test "phase 6 hexdump direct pack helpers keep uppercase and lowercase nibble parity" {
    try std.testing.expectEqual(@as(u8, '0'), hexdump.hexAscHi(0x0f));
    try std.testing.expectEqual(@as(u8, 'f'), hexdump.hexAscLo(0x0f));
    try std.testing.expectEqual(@as(u8, 'B'), hexdump.hexAscUpperHi(0xbe));
    try std.testing.expectEqual(@as(u8, 'E'), hexdump.hexAscUpperLo(0xbe));

    var lower: [6]u8 = undefined;
    var upper: [6]u8 = undefined;
    var lower_rest: []u8 = lower[0..];
    var upper_rest: []u8 = upper[0..];
    for (fixtures.data_b[0..3]) |byte| {
        lower_rest = try hexdump.hexBytePack(lower_rest, byte);
        upper_rest = try hexdump.hexBytePackUpper(upper_rest, byte);
    }

    try std.testing.expectEqual(@as(usize, 0), lower_rest.len);
    try std.testing.expectEqual(@as(usize, 0), upper_rest.len);
    try std.testing.expectEqualStrings("be32db", &lower);
    try std.testing.expectEqualStrings("BE32DB", &upper);

    var tiny_lower = [_]u8{0xaa};
    var tiny_upper = [_]u8{0xbb};
    try std.testing.expectError(hexdump.HexError.DestinationTooSmall, hexdump.hexBytePack(tiny_lower[0..], 0x5c));
    try std.testing.expectError(hexdump.HexError.DestinationTooSmall, hexdump.hexBytePackUpper(tiny_upper[0..], 0x5c));
    try std.testing.expectEqual(@as(u8, 0xaa), tiny_lower[0]);
    try std.testing.expectEqual(@as(u8, 0xbb), tiny_upper[0]);
}

test "phase 6 hexdump uppercase bulk parity and grouped-ascii exact-capacity buffers stay aligned" {
    var upper: [8]u8 = [_]u8{0xaa} ** 8;
    var alias_upper: [8]u8 = [_]u8{0xbb} ** 8;

    const direct_upper = try hexdump.bin2hexUpper(upper[0..], fixtures.data_b[0..4]);
    const alias_upper_text = try hexdump.bin2HexUpper(alias_upper[0..], fixtures.data_b[0..4]);
    try std.testing.expectEqualStrings("BE32DB7B", direct_upper);
    try std.testing.expectEqualStrings(direct_upper, alias_upper_text);
    try std.testing.expectEqual(@as(u8, 0xaa), upper[direct_upper.len]);
    try std.testing.expectEqual(@as(u8, 0xbb), alias_upper[alias_upper_text.len]);

    const grouped_ascii_case = fixtures.parity_cases[5];
    try std.testing.expectEqualStrings("ascii rowsize-32 group-2", grouped_ascii_case.name);

    var exact: [114]u8 = undefined;
    var truncated: [113]u8 = [_]u8{fixtures.fill_char} ** 113;

    const exact_required = hexdump.hexDumpToBuffer(
        fixtures.data_b[0..grouped_ascii_case.len],
        grouped_ascii_case.rowsize,
        grouped_ascii_case.groupsize,
        exact[0..],
        grouped_ascii_case.ascii,
    );
    try std.testing.expectEqual(grouped_ascii_case.expected_length, exact_required);
    try std.testing.expectEqualSlices(
        u8,
        grouped_ascii_case.expected_text.current(),
        std.mem.sliceTo(exact[0..], 0),
    );
    try std.testing.expectEqual(@as(u8, 0), exact[exact_required]);

    const truncated_required = hexdump.hexDumpToBuffer(
        fixtures.data_b[0..grouped_ascii_case.len],
        grouped_ascii_case.rowsize,
        grouped_ascii_case.groupsize,
        truncated[0..],
        grouped_ascii_case.ascii,
    );
    try std.testing.expectEqual(grouped_ascii_case.expected_length, truncated_required);
    try std.testing.expectEqualSlices(
        u8,
        grouped_ascii_case.expected_text.current()[0 .. grouped_ascii_case.expected_text.current().len - 1],
        std.mem.sliceTo(truncated[0..], 0),
    );
    try std.testing.expectEqual(@as(u8, 0), truncated[truncated.len - 1]);
}

test "phase 6 hexdump zero-length caller buffers stay NUL terminated without touching trailing bytes" {
    const fill = fixtures.fill_char;

    var ascii_buf = [_]u8{fill} ** 4;
    const ascii_required = hexdump.hexDumpToBuffer(fixtures.data_b[0..0], 32, 8, ascii_buf[0..], true);
    try std.testing.expectEqual(@as(usize, 0), ascii_required);
    try std.testing.expectEqual(@as(u8, 0), ascii_buf[0]);
    for (ascii_buf[1..]) |byte| {
        try std.testing.expectEqual(fill, byte);
    }

    var plain_buf = [_]u8{fill} ** 2;
    const plain_required = hexdump.hexDumpToBuffer(fixtures.data_b[0..0], 16, 1, plain_buf[0..], false);
    try std.testing.expectEqual(@as(usize, 0), plain_required);
    try std.testing.expectEqual(@as(u8, 0), plain_buf[0]);
    for (plain_buf[1..]) |byte| {
        try std.testing.expectEqual(fill, byte);
    }
}
