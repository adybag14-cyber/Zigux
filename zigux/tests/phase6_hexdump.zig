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

test "phase 6 hexdump exposes append-style whole-buffer encoding" {
    var encoded: [12]u8 = [_]u8{'#'} ** 12;
    var rest = try hexdump.bin2hexAppend(encoded[0..], test_data_b[0..2]);
    rest = try hexdump.bin2hexAppendUpper(rest, test_data_b[2..4]);

    try std.testing.expectEqualSlices(u8, "be32DB7B", encoded[0..8]);
    try std.testing.expectEqual(@as(usize, 4), rest.len);
    try std.testing.expectEqualSlices(u8, "####", rest);
}
