const std = @import("std");
const fixtures = @import("phase6_hexdump_vectors");

fn validatePerfMatrix() !void {
    const expected = [_]struct {
        label: []const u8,
        len: usize,
        rowsize: usize,
        groupsize: usize,
        ascii: bool,
        reps: usize,
        max_slowdown_pct: u64,
        expected_length: usize,
    }{
        .{ .label = "16B-plain-g1", .len = 16, .rowsize = 16, .groupsize = 1, .ascii = false, .reps = 40_000, .max_slowdown_pct = 175, .expected_length = 47 },
        .{ .label = "32B-ascii-g2", .len = 32, .rowsize = 32, .groupsize = 2, .ascii = true, .reps = 10_000, .max_slowdown_pct = 550, .expected_length = 113 },
        .{ .label = "16B-ascii-g4", .len = 16, .rowsize = 16, .groupsize = 4, .ascii = true, .reps = 20_000, .max_slowdown_pct = 550, .expected_length = 53 },
        .{ .label = "16B-ascii-g8", .len = 16, .rowsize = 16, .groupsize = 8, .ascii = true, .reps = 20_000, .max_slowdown_pct = 600, .expected_length = 51 },
    };

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

        const expected_length = fixtures.expectedLength(actual.len, actual.rowsize, actual.groupsize, actual.ascii);
        if (want.expected_length != expected_length) return error.HexdumpPerfMatrixMismatch;
        if (expected_length > fixtures.test_hexdump_buf_size) return error.HexdumpPerfMatrixMismatch;
    }

    for (fixtures.perf_cases, 0..) |case, idx| {
        if (case.len == 0 or case.rowsize == 0 or case.reps == 0 or case.max_slowdown_pct == 0) {
            return error.HexdumpPerfMatrixMismatch;
        }
        if (case.len > case.rowsize) return error.HexdumpPerfMatrixMismatch;

        for (fixtures.perf_cases[idx + 1 ..]) |other| {
            if (std.mem.eql(u8, case.label, other.label)) return error.HexdumpPerfMatrixMismatch;
        }
    }
}

test "phase 6 hexdump perf matrix preflight stays aligned with the documented packet" {
    try validatePerfMatrix();
}
