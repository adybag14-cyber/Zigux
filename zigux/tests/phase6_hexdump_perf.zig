const std = @import("std");
const hexdump = @import("hexdump");
const fixtures = @import("phase6_hexdump_vectors");

const Io = std.Io;

const BenchResult = struct {
    elapsed_ns: u64,
    accumulator: u64,
};

fn validatePerfMatrix() !void {
    const expected = [_]struct {
        label: []const u8,
        len: usize,
        rowsize: usize,
        groupsize: usize,
        ascii: bool,
        reps: usize,
        max_slowdown_pct: u16,
    }{
        .{ .label = "16B-plain-g1", .len = 16, .rowsize = 16, .groupsize = 1, .ascii = false, .reps = 40_000, .max_slowdown_pct = 175 },
        .{ .label = "32B-ascii-g2", .len = 32, .rowsize = 32, .groupsize = 2, .ascii = true, .reps = 10_000, .max_slowdown_pct = 550 },
        .{ .label = "16B-ascii-g4", .len = 16, .rowsize = 16, .groupsize = 4, .ascii = true, .reps = 20_000, .max_slowdown_pct = 550 },
        .{ .label = "16B-ascii-g8", .len = 16, .rowsize = 16, .groupsize = 8, .ascii = true, .reps = 20_000, .max_slowdown_pct = 600 },
    };

    var saw_plain_g1 = false;
    var saw_ascii_g2 = false;
    var saw_ascii_g4 = false;
    var saw_ascii_g8 = false;

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

        if (case.expected_text.current().len == 0) return error.HexdumpPerfMatrixMismatch;
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
        if (!std.mem.eql(u8, case.expected_text.current(), rendered)) {
            return error.HexdumpPerfMatrixMismatch;
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
        } else {
            return error.HexdumpPerfMatrixMismatch;
        }

        for (fixtures.perf_cases[idx + 1 ..]) |other| {
            if (std.mem.eql(u8, case.label, other.label)) return error.HexdumpPerfMatrixMismatch;
        }
    }

    if (!saw_plain_g1 or !saw_ascii_g2 or !saw_ascii_g4 or !saw_ascii_g8) {
        return error.HexdumpPerfMatrixMismatch;
    }
}

fn monotonicNs() !u64 {
    var timespec: std.posix.timespec = undefined;
    switch (std.posix.errno(std.posix.system.clock_gettime(std.posix.CLOCK.MONOTONIC, &timespec))) {
        .SUCCESS => {},
        else => return error.ClockUnavailable,
    }
    return (@as(u64, @intCast(timespec.sec)) * std.time.ns_per_s) + @as(u64, @intCast(timespec.nsec));
}

fn helperAccumulator(required: usize, line: []const u8) u64 {
    if (required == 0) return 0;
    return @as(u64, required) +
        @as(u64, line[0]) +
        @as(u64, line[required - 1]) +
        @as(u64, line[@min(required / 2, required - 1)]);
}

fn runHelperBench(case: fixtures.PerfCase) !BenchResult {
    var line: [fixtures.test_hexdump_buf_size]u8 = undefined;
    var accumulator: u64 = 0;
    const start_ns = try monotonicNs();
    var iter: usize = 0;
    while (iter < case.reps) : (iter += 1) {
        const required = hexdump.hexDumpToBuffer(
            fixtures.data_b[0..case.len],
            case.rowsize,
            case.groupsize,
            line[0..],
            case.ascii,
        );
        accumulator +%= helperAccumulator(required, std.mem.sliceTo(line[0..], 0));
    }
    return .{
        .elapsed_ns = (try monotonicNs()) - start_ns,
        .accumulator = accumulator,
    };
}

fn runReferenceBench(case: fixtures.PerfCase) !BenchResult {
    var line: [fixtures.test_hexdump_buf_size]u8 = undefined;
    var accumulator: u64 = 0;
    const start_ns = try monotonicNs();
    var iter: usize = 0;
    while (iter < case.reps) : (iter += 1) {
        const expected = fixtures.prepareExpectedLine(
            line[0..],
            case.len,
            case.rowsize,
            case.groupsize,
            case.ascii,
        );
        accumulator +%= helperAccumulator(expected.len, expected);
    }
    return .{
        .elapsed_ns = (try monotonicNs()) - start_ns,
        .accumulator = accumulator,
    };
}

fn slowdownPct(helper_ns: u64, reference_ns: u64) u64 {
    if (helper_ns <= reference_ns or reference_ns == 0) return 0;
    return @intCast((@as(u128, helper_ns - reference_ns) * 100) / @as(u128, reference_ns));
}

pub fn main(init: std.process.Init) !void {
    try validatePerfMatrix();

    const io = init.io;
    var stdout_buffer: [4096]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    var failed = false;

    try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_CASE_COUNT={d}\n", .{fixtures.perf_cases.len});

    for (fixtures.perf_cases) |case| {
        var helper_line: [fixtures.test_hexdump_buf_size]u8 = undefined;
        var expected_line: [fixtures.test_hexdump_buf_size]u8 = undefined;

        const required = hexdump.hexDumpToBuffer(
            fixtures.data_b[0..case.len],
            case.rowsize,
            case.groupsize,
            helper_line[0..],
            case.ascii,
        );
        const expected = fixtures.prepareExpectedLine(
            expected_line[0..],
            case.len,
            case.rowsize,
            case.groupsize,
            case.ascii,
        );

        try std.testing.expectEqual(fixtures.expectedLength(case.len, case.rowsize, case.groupsize, case.ascii), required);
        try std.testing.expectEqualSlices(u8, expected, std.mem.sliceTo(helper_line[0..], 0));

        const helper_result = try runHelperBench(case);
        const reference_result = try runReferenceBench(case);
        const slowdown_pct = slowdownPct(helper_result.elapsed_ns, reference_result.elapsed_ns);

        try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_{s}_ITERATIONS={d}\n", .{ case.label, case.reps });
        try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_{s}_HELPER_NS={d}\n", .{ case.label, helper_result.elapsed_ns });
        try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_{s}_REFERENCE_NS={d}\n", .{ case.label, reference_result.elapsed_ns });
        try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_{s}_SLOWDOWN_PCT={d}\n", .{ case.label, slowdown_pct });
        try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_{s}_THRESHOLD_PCT={d}\n", .{ case.label, case.max_slowdown_pct });
        try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_{s}_ACCUMULATOR={d}\n", .{ case.label, helper_result.accumulator });

        if (helper_result.accumulator != reference_result.accumulator) {
            return error.HexdumpPerfAccumulatorMismatch;
        }
        if (slowdown_pct > case.max_slowdown_pct) {
            failed = true;
            try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_{s}=fail\n", .{case.label});
        } else {
            try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_{s}=pass\n", .{case.label});
        }
    }

    try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF={s}\n", .{if (failed) "fail" else "pass"});
    try stdout_writer.interface.flush();

    if (failed) return error.HexdumpPerfRegression;
}

test "phase 6 hexdump perf matrix preflight stays aligned with the documented packet" {
    try validatePerfMatrix();
}
