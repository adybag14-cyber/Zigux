const std = @import("std");
const hexdump = @import("hexdump");
const fixtures = @import("phase6_hexdump_vectors");

pub fn validatePerfMatrix() !void {
    const expected = [_]struct {
        label: []const u8,
        len: usize,
        rowsize: usize,
        groupsize: usize,
        ascii: bool,
        reps: usize,
        max_slowdown_pct: u64,
        expected_text: fixtures.ExpectedText,
    }{
        .{
            .label = "16B-plain-g1",
            .len = 16,
            .rowsize = 16,
            .groupsize = 1,
            .ascii = false,
            .reps = 40_000,
            .max_slowdown_pct = 175,
            .expected_text = fixtures.ExpectedText{
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
            .expected_text = fixtures.ExpectedText{
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
            .expected_text = fixtures.ExpectedText{
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
            .expected_text = fixtures.ExpectedText{
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
            .expected_text = fixtures.ExpectedText{
                .little = "be 32 db 7b 0a 18 93 b2 70 ba c4 24              .2.{....p..$",
                .big = "be 32 db 7b 0a 18 93 b2 70 ba c4 24              .2.{....p..$",
            },
        },
    };

    var saw_plain_g1 = false;
    var saw_ascii_g2 = false;
    var saw_ascii_g4 = false;
    var saw_ascii_g8 = false;
    var saw_ascii_fallback = false;

    if (fixtures.perf_cases.len != expected.len) return error.HexdumpPerfMatrixMismatch;

    for (expected, 0..) |want, idx| {
        const actual = fixtures.perf_cases[idx];
        if (!std.mem.eql(u8, want.label, actual.label)) return error.HexdumpPerfMatrixMismatch;
        if (want.len != actual.len) return error.HexdumpPerfMatrixMismatch;
        if (want.rowsize != actual.rowsize) return error.HexdumpPerfMatrixMismatch;
        if (want.groupsize != actual.groupsize) return error.HexdumpPerfMatrixMismatch;
        if (want.ascii != actual.ascii) return error.HexdumpPerfMatrixMismatch;
        if (want.reps != actual.reps) return error.HexdumpPerfMatrixMismatch;
        if (want.max_slowdown_pct != actual.max_slowdown_pct) return error.HexdumpPerfMatrixMismatch;
        if (!std.mem.eql(u8, want.expected_text.little, actual.expected_text.little)) {
            return error.HexdumpPerfMatrixMismatch;
        }
        if (!std.mem.eql(u8, want.expected_text.big, actual.expected_text.big)) {
            return error.HexdumpPerfMatrixMismatch;
        }
    }

    for (fixtures.perf_cases, 0..) |case, idx| {
        var expected_line: [fixtures.test_hexdump_buf_size]u8 = undefined;
        const rendered = fixtures.prepareExpectedLine(
            expected_line[0..],
            case.len,
            case.rowsize,
            case.groupsize,
            case.ascii,
        );

        if (case.reps == 0 or case.max_slowdown_pct == 0 or case.len == 0) {
            return error.HexdumpPerfMatrixMismatch;
        }
        if (case.len > case.rowsize) return error.HexdumpPerfMatrixMismatch;
        if (case.rowsize != fixtures.normalizedRowsize(case.rowsize)) return error.HexdumpPerfMatrixMismatch;
        if (case.groupsize != fixtures.normalizedGroupsizeForLen(case.len, case.groupsize)) {
            return error.HexdumpPerfMatrixMismatch;
        }
        if (fixtures.expectedLength(case.len, case.rowsize, case.groupsize, case.ascii) != rendered.len) {
            return error.HexdumpPerfMatrixMismatch;
        }
        if (!std.mem.eql(u8, expected[idx].expected_text.current(), rendered)) {
            return error.HexdumpPerfMatrixMismatch;
        }

        if (std.mem.eql(u8, case.label, "32B-ascii-g2")) {
            var exact: [114]u8 = undefined;
            var truncated: [113]u8 = [_]u8{fixtures.fill_char} ** 113;

            const exact_required = hexdump.hexDumpToBuffer(
                fixtures.data_b[0..case.len],
                case.rowsize,
                case.groupsize,
                exact[0..],
                case.ascii,
            );
            if (exact_required != expected[idx].expected_text.current().len) return error.HexdumpPerfMatrixMismatch;
            if (!std.mem.eql(u8, expected[idx].expected_text.current(), std.mem.sliceTo(exact[0..], 0))) {
                return error.HexdumpPerfMatrixMismatch;
            }
            if (exact[exact_required] != 0) return error.HexdumpPerfMatrixMismatch;

            const truncated_required = hexdump.hexDumpToBuffer(
                fixtures.data_b[0..case.len],
                case.rowsize,
                case.groupsize,
                truncated[0..],
                case.ascii,
            );
            if (truncated_required != expected[idx].expected_text.current().len) return error.HexdumpPerfMatrixMismatch;
            if (!std.mem.eql(
                u8,
                expected[idx].expected_text.current()[0 .. expected[idx].expected_text.current().len - 1],
                std.mem.sliceTo(truncated[0..], 0),
            )) {
                return error.HexdumpPerfMatrixMismatch;
            }
            if (truncated[truncated.len - 1] != 0) return error.HexdumpPerfMatrixMismatch;
        }

        if (std.mem.eql(u8, case.label, "16B-plain-g1")) {
            if (saw_plain_g1) return error.HexdumpPerfMatrixMismatch;
            saw_plain_g1 = true;
        } else if (std.mem.eql(u8, case.label, "32B-ascii-g2")) {
            if (saw_ascii_g2) return error.HexdumpPerfMatrixMismatch;
            saw_ascii_g2 = true;
        } else if (std.mem.eql(u8, case.label, "16B-ascii-g4")) {
            if (saw_ascii_g4) return error.HexdumpPerfMatrixMismatch;
            saw_ascii_g4 = true;
        } else if (std.mem.eql(u8, case.label, "16B-ascii-g8")) {
            if (saw_ascii_g8) return error.HexdumpPerfMatrixMismatch;
            saw_ascii_g8 = true;
        } else if (std.mem.eql(u8, case.label, "12B-ascii-fallback")) {
            if (saw_ascii_fallback) return error.HexdumpPerfMatrixMismatch;
            saw_ascii_fallback = true;
        } else {
            return error.HexdumpPerfMatrixMismatch;
        }

        for (fixtures.perf_cases[idx + 1 ..]) |other| {
            if (std.mem.eql(u8, case.label, other.label)) return error.HexdumpPerfMatrixMismatch;
        }
    }

    if (!saw_plain_g1 or !saw_ascii_g2 or !saw_ascii_g4 or !saw_ascii_g8 or !saw_ascii_fallback) {
        return error.HexdumpPerfMatrixMismatch;
    }
}

test "phase 6 hexdump perf matrix preflight stays aligned with the documented packet" {
    try validatePerfMatrix();
}